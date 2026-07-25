# 🔮 Análisis Técnico, Físico y de Ciberseguridad de Merma Cero

Este documento detalla los fundamentos científicos, matemáticos y arquitectónicos bajo los cuales opera el motor estocástico del **Oráculo Merma Cero**.

---

## 1. Fundamentos Matemáticos y Físicos

### A. Cinética de Descomposición Arrhenius Modificada
La pérdida física de los alimentos perecederos y plantas ocurre por reacciones químicas (desnaturalización, proliferación bacteriana, oxidación). La constante de velocidad de reacción ($K$) se modela clásicamente mediante la **Ecuación de Arrhenius**:

$$K = K_0 \cdot \exp\left(-\frac{E_a}{R \cdot T_{\text{Kelvin}}}\right)$$

En **Merma Cero**, acoplamos la humedad relativa ($H$) como un modulador multiplicativo de la cinética para incorporar las propiedades higroscópicas y de evaporación del producto:

$$K(T, H) = K_0 \cdot \exp\left(-\frac{E_a}{R \cdot (T_{\text{Celsius}} + 273.15)}\right) \cdot (1 + \alpha \cdot H)$$

Donde:
- $E_a$: Energía de activación ($\text{J/mol}$).
- $K_0$: Factor pre-exponencial de colisiones.
- $R$: Constante universal de gases ($8.314 \, \text{J/mol}\cdot\text{K}$).
- $\alpha$: Coeficiente empírico de aceleración por humedad.
- $H$: Humedad relativa $[0.0, 1.0]$.

La **vida de anaquel estimada** (Shelf Life) es el inverso multiplicativo:

$$\text{Shelf Life} = \frac{1}{K(T, H)}$$

### B. Proyección de Volatilidad Climática GARCH(1,1)
La variabilidad climática representa el riesgo sistemático del comerciante informal. Para modelar la volatilidad condicional de la temperatura $\sigma_t^2$ utilizamos un proceso autorregresivo **GARCH(1,1)**:

$$\sigma_t^2 = \omega + \alpha \cdot \varepsilon_{t-1}^2 + \beta \cdot \sigma_{t-1}^2$$

Donde:
- $\omega = 0.05$ (Varianza incondicional basal).
- $\alpha = 0.15$ (Impacto de choques climáticos recientes).
- $\beta = 0.80$ (Persistencia de la volatilidad histórica).
- $\varepsilon_t = T_t - \mu_t$ (Residuos frente a la media estacional climática).

### C. Dimensionamiento Kelly Modificado (Markowitz Mean-Variance)
Para determinar la cantidad de compra óptima $S^*$ que minimiza las pérdidas por merma sin comprometer el abastecimiento de la demanda, resolvemos el problema de optimización cuadrática:

$$S^* = \operatorname{arg\,max}_Q \left[ \mathbb{E}[\text{Profit}(Q)] - \lambda \cdot \operatorname{Std}(\text{Profit}(Q)) \right]$$

Bajo las siguientes restricciones y transformaciones:
1. **Pérdida de Salvamento:** El valor de salvamento base de la mercancía no vendida ($L_{\text{base}}$) se degrada exponencialmente por la constante de decaimiento Arrhenius calculada:
   $$L_{\text{efectivo}} = L_{\text{base}} \cdot e^{-K}$$
2. **Modulación de Demanda por Clima:** La media de la demanda normal se reduce por factores climáticos (ej. lluvia del tianguis, calor extremo).
3. **Escalamiento de Incertidumbre:** La varianza de la demanda se escala de forma proporcional al desvío estándar de volatilidad climática proyectado por el proceso GARCH(1,1).

---

## 2. Decisiones de Arquitectura de Software

El sistema sigue estrictamente la **Arquitectura Hexagonal (Puertos y Adaptadores)** para garantizar desacoplamiento y testabilidad:

```
                  [ Webhook HTTP (FastAPI) ]
                              │
                              ▼
                       [ Puertos de Entrada ]
                              │
                              ▼
  [ Dominio (models.py) ] ◄───[ Casos de Uso (OraculoUseCase) ]
                              │
                              ▼
                       [ Puertos de Salida ]
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
     [ SQLite Repo ]   [ OpenMeteo API ]   [ Twilio / WhatsApp ]
```

### Principios de Diseño
1. **Zero Fricción (Falkland Law):** Registro implícito del vendedor y autodetección automática del producto e incluso coordenadas decimales a partir de mensajes de texto en lenguaje natural.
2. **Robustez y Resiliencia:** Fallback automático a climatología estacional en caso de fallo de red/API climática de OpenMeteo. Autorecuperación e inicialización ante corrupción de la base de datos local.

---

## 3. Modelo de Seguridad y Ciberseguridad

1. **Blindaje de Entradas (Pydantic Boundaries):** Todo payload de webhook se sanitiza y valida en longitud y formato regex estricto antes de procesarse (Zero Trust).
2. **Clipping Físico (Murphy's Law):** Los solvers numéricos aplican límites fijos a las variables de entorno (temperatura acotada a $[0, 50]^\circ\text{C}$ y humedad a $[0.0, 1.0]$) para mitigar desbordamientos de pila o inestabilidad en estimadores estadísticos NumPy.
3. **Protección Sybil (Token Bucket Rate Limiting):** Algoritmo de Token Bucket persistente por número telefónico para repeler ataques de denegación de servicio (DoS) a las APIs de IA externas.
4. **Protección contra Inyección Lógica:** Los identificadores telefónicos se validan con el estándar regex E.164. Las queries de persistencia SQLite utilizan consultas parametrizadas para evitar inyección SQL (OWASP A03).
