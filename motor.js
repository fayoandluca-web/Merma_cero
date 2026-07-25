// -*- coding: utf-8 -*-
/**
 * Motor de cálculo Merma Cero en JavaScript.
 * Es un espejo numérico y lógico del dominio desarrollado en Python (models.py).
 */

const R_GAS_CONSTANT = 8.314;

const INVENTORY_PARAMETERS = {
  seafood: {
    Ea: 65000.0,
    K0: 2.5e10,
    alpha: 1.2,
    default_price: 120.0,
    default_cost: 70.0,
    default_salvage: 10.0,
  },
  flowers: {
    Ea: 55000.0,
    K0: 8.0e8,
    alpha: -0.4,
    default_price: 50.0,
    default_cost: 20.0,
    default_salvage: 5.0,
  },
  fruit_vegetables: {
    Ea: 48000.0,
    K0: 4.5e7,
    alpha: 0.8,
    default_price: 40.0,
    default_cost: 18.0,
    default_salvage: 4.0,
  },
  dairy: {
    Ea: 72000.0,
    K0: 5.0e11,
    alpha: 0.5,
    default_price: 35.0,
    default_cost: 22.0,
    default_salvage: 2.0,
  },
  generic: {
    Ea: 50000.0,
    K0: 1.0e8,
    alpha: 0.5,
    default_price: 50.0,
    default_cost: 25.0,
    default_salvage: 5.0,
  }
};

const RISK_AERSION_LAMBDA = 0.5;

class LCG {
  constructor(seed = 42) {
    this.state = seed !== 0 ? seed : 1;
  }
  nextDouble() {
    this.state = (48271 * this.state) % 2147483647;
    return this.state / 2147483647.0;
  }
}

function boxMuller(lcg) {
  let u1 = 0.0;
  while (u1 === 0.0) u1 = lcg.nextDouble();
  let u2 = 0.0;
  while (u2 === 0.0) u2 = lcg.nextDouble();
  return Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
}

class DecayKinetics {
  static calculateDecayRate(category, temperature, relativeHumidity) {
    const params = INVENTORY_PARAMETERS[category] || INVENTORY_PARAMETERS["generic"];
    
    // Clipping de temperatura
    let temp = temperature;
    if (temp > 50.0) temp = 50.0;
    if (temp < 0.0) temp = 0.0;
    
    // Clipping de humedad
    let humidity = relativeHumidity;
    if (humidity > 1.0) humidity = 1.0;
    if (humidity < 0.0) humidity = 0.0;

    const tempKelvin = temp + 273.15;
    const exponent = -params.Ea / (R_GAS_CONSTANT * tempKelvin);
    const arrheniusFactor = params.K0 * Math.exp(exponent);
    const humidityFactor = 1.0 + params.alpha * humidity;
    const decayRate = arrheniusFactor * humidityFactor;

    return Math.max(1e-6, decayRate);
  }

  static calculateShelfLife(category, temperature, relativeHumidity) {
    const decayRate = this.calculateDecayRate(category, temperature, relativeHumidity);
    return 1.0 / decayRate;
  }
}

class GARCHVolatilityModel {
  static projectVariance(historicalTemperatures, seasonalMeans, omega = 0.05, alpha = 0.15, beta = 0.80) {
    const n = historicalTemperatures.length;
    if (n < 2 || seasonalMeans.length !== n) {
      const denom = 1.0 - alpha - beta;
      return denom > 0 ? omega / denom : 1.0;
    }

    const residuals = [];
    for (let i = 0; i < n; i++) {
      residuals.push(historicalTemperatures[i] - seasonalMeans[i]);
    }

    // Calcular varianza poblacional para igualar a numpy.var(ddof=0)
    let mean = 0;
    for (let i = 0; i < n; i++) mean += residuals[i];
    mean /= n;
    
    let variance = 0;
    for (let i = 0; i < n; i++) {
      variance += Math.pow(residuals[i] - mean, 2);
    }
    variance = n > 0 ? variance / n : 1.0;
    if (variance <= 0) variance = 1.0;

    let currentVariance = variance;
    for (let i = 1; i < n; i++) {
      const epsilonSq = Math.pow(residuals[i - 1], 2);
      currentVariance = omega + alpha * epsilonSq + beta * currentVariance;
    }

    const lastEpsilonSq = Math.pow(residuals[n - 1], 2);
    return omega + alpha * lastEpsilonSq + beta * currentVariance;
  }
}

class KellyMermaSizer {
  static optimizeStock(
    category,
    temperature,
    relativeHumidity,
    precipitationProbability,
    baseDemandMean = 100.0,
    baseDemandStd = 30.0,
    historicalTemperatures = null,
    seasonalMeans = null,
    simSamples = 1000,
    seed = 42
  ) {
    const params = INVENTORY_PARAMETERS[category] || INVENTORY_PARAMETERS["generic"];
    const price = params.default_price;
    const cost = params.default_cost;
    const salvageBase = params.default_salvage;

    const decayRate = DecayKinetics.calculateDecayRate(category, temperature, relativeHumidity);
    const salvageEffective = salvageBase * Math.exp(-decayRate);

    let weatherDemandMultiplier = 1.0;
    if (precipitationProbability > 0.3) {
      weatherDemandMultiplier -= 0.35 * precipitationProbability;
    }

    if (category === "seafood") {
      if (temperature > 32.0) weatherDemandMultiplier *= 0.60;
    } else if (category === "flowers") {
      if (temperature > 30.0) weatherDemandMultiplier *= 0.70;
    } else if (category === "generic") {
      if (temperature > 35.0) weatherDemandMultiplier *= 0.80;
    }

    weatherDemandMultiplier = Math.max(0.1, weatherDemandMultiplier);

    const adjustedMean = baseDemandMean * weatherDemandMultiplier;
    let adjustedStd = baseDemandStd * Math.max(0.5, weatherDemandMultiplier);

    // GARCH Volatility scaling
    let histTemps = historicalTemperatures;
    let seasMeans = seasonalMeans;
    if (!histTemps || histTemps.length < 2) {
      histTemps = [];
      seasMeans = [];
      for (let i = 0; i < 10; i++) {
        histTemps.push(temperature + Math.sin(i));
        seasMeans.push(temperature);
      }
    }

    const forecastVar = GARCHVolatilityModel.projectVariance(histTemps, seasMeans);
    const longTermVar = 0.05 / (1.0 - 0.15 - 0.80);
    const volatilityMultiplier = Math.sqrt(forecastVar / longTermVar);
    adjustedStd = adjustedStd * Math.max(0.5, Math.min(2.5, volatilityMultiplier));

    const lcg = new LCG(seed);
    const demands = [];
    for (let i = 0; i < simSamples; i++) {
      let d = adjustedMean + boxMuller(lcg) * adjustedStd;
      if (d < 0) d = 0;
      demands.push(d);
    }

    const maxQSearch = Math.floor(Math.max(10.0, adjustedMean * 2.5));
    let bestQ = 0;
    let maxUtility = -Infinity;

    for (let q = 0; q <= maxQSearch; q++) {
      let profitSum = 0;
      const profits = [];

      for (let i = 0; i < simSamples; i++) {
        const demand = demands[i];
        const sales = Math.min(q, demand);
        const surplus = Math.max(0.0, q - demand);
        const profit = (sales * price) + (surplus * salvageEffective) - (q * cost);
        profits.push(profit);
        profitSum += profit;
      }

      const meanProfit = profitSum / simSamples;
      
      let varianceSum = 0;
      for (let i = 0; i < simSamples; i++) {
        varianceSum += Math.pow(profits[i] - meanProfit, 2);
      }
      const stdProfit = Math.sqrt(varianceSum / simSamples);
      const utility = meanProfit - RISK_AERSION_LAMBDA * stdProfit;

      if (utility > maxUtility) {
        maxUtility = utility;
        bestQ = q;
      }
    }

    return bestQ;
  }
}

class MonteCarloMermaSimulator {
  static simulate48hDecay(
    category,
    temperature,
    relativeHumidity,
    precipitationProbability,
    forecastVariance,
    simSamples = 1000,
    seed = 42
  ) {
    const lcg = new LCG(seed);
    const decayFactors = [];
    const volScale = Math.sqrt(forecastVariance);

    for (let i = 0; i < simSamples; i++) {
      const shockD1 = boxMuller(lcg);
      let t1 = temperature + shockD1 * volScale * 0.5;
      if (t1 > 50.0) t1 = 50.0;
      if (t1 < 0.0) t1 = 0.0;

      const k1 = DecayKinetics.calculateDecayRate(category, t1, relativeHumidity);

      const shockD2 = boxMuller(lcg);
      let t2 = t1 + shockD2 * volScale * 0.5;
      if (t2 > 50.0) t2 = 50.0;
      if (t2 < 0.0) t2 = 0.0;

      const k2 = DecayKinetics.calculateDecayRate(category, t2, relativeHumidity);

      const accumDecay = 1.0 - Math.exp(-(k1 + k2));
      decayFactors.push(accumDecay);
    }

    decayFactors.sort((a, b) => a - b);

    let sum = 0;
    for (let i = 0; i < simSamples; i++) sum += decayFactors[i];
    const meanDecay = sum / simSamples;

    const varIndex = Math.floor(simSamples * 0.95);
    const var95 = decayFactors[varIndex];

    let cvarSum = 0;
    let cvarCount = 0;
    for (let i = varIndex; i < simSamples; i++) {
      cvarSum += decayFactors[i];
      cvarCount++;
    }
    const cvar95 = cvarCount > 0 ? cvarSum / cvarCount : var95;

    return {
      expected_decay_48h: meanDecay,
      var_95_decay_48h: var95,
      cvar_95_decay_48h: cvar95
    };
  }
}

// Soporte CLI para test de paridad
if (require.main === module) {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  rl.on('line', (line) => {
    try {
      const input = JSON.parse(line);
      const action = input.action;
      let result = null;

      if (action === "calculate_decay_rate") {
        result = DecayKinetics.calculateDecayRate(input.category, input.temperature, input.relative_humidity);
      } else if (action === "calculate_shelf_life") {
        result = DecayKinetics.calculateShelfLife(input.category, input.temperature, input.relative_humidity);
      } else if (action === "project_variance") {
        result = GARCHVolatilityModel.projectVariance(input.historical_temperatures, input.seasonal_means);
      } else if (action === "optimize_stock") {
        result = KellyMermaSizer.optimizeStock(
          input.category,
          input.temperature,
          input.relative_humidity,
          input.precipitation_probability,
          100.0,
          30.0,
          input.historical_temperatures,
          input.seasonal_means,
          input.sim_samples || 1000,
          input.seed || 42
        );
      } else if (action === "simulate_48h_decay") {
        result = MonteCarloMermaSimulator.simulate48hDecay(
          input.category,
          input.temperature,
          input.relative_humidity,
          input.precipitation_probability,
          input.forecast_variance,
          input.sim_samples || 1000,
          input.seed || 42
        );
      }
      console.log(JSON.stringify({ status: "success", data: result }));
    } catch (err) {
      console.log(JSON.stringify({ status: "error", message: err.message }));
    }
  });
}

module.exports = {
  DecayKinetics,
  GARCHVolatilityModel,
  KellyMermaSizer,
  MonteCarloMermaSimulator
};
