# -*- coding: utf-8 -*-
"""Script generador del Frontend interactivo index.html de Merma Cero.

Genera una página estática premium autocontenida con lógica en JavaScript para 
realizar simulaciones en tiempo real de modelos de Arrhenius, Kelly Sizer y Monte Carlo 48h.
"""
import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Merma Cero — Oráculo Estocástico de Resiliencia Climática</title>
    <meta name="description" content="Tesis tecnológica y simulador de resiliencia alimentaria para economía de subsistencia.">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        /* Modern Reset & CSS Variables */
        :root {
            --bg-color: #030712;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --primary: #38bdf8;
            --primary-gradient: linear-gradient(135deg, #38bdf8 0%, #10b981 100%);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #f3f4f6;
            --text-muted: #9ca3af;
            --glass-blur: blur(16px);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text);
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
            background-image: radial-gradient(circle at 10% 15%, rgba(56, 189, 248, 0.04) 0%, transparent 45%),
                              radial-gradient(circle at 90% 85%, rgba(16, 185, 129, 0.03) 0%, transparent 45%);
            -webkit-font-smoothing: antialiased;
        }

        /* Header & Navigation */
        nav {
            width: 100%;
            height: 70px;
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            background: rgba(3, 7, 18, 0.6);
            border-bottom: 1px solid var(--border-color);
            position: fixed;
            top: 0;
            left: 0;
            z-index: 100;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0 2rem;
        }

        .nav-container {
            width: 100%;
            max-width: 1100px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 800;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: var(--primary);
        }

        .btn-cta {
            background: var(--primary-gradient);
            color: #030712;
            padding: 0.6rem 1.2rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2);
            border: none;
            cursor: pointer;
        }

        .btn-cta:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35);
        }

        /* Hero Section */
        .hero {
            width: 100%;
            max-width: 1100px;
            margin-top: 130px;
            padding: 2rem 1.5rem 4rem 1.5rem;
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 4rem;
            align-items: center;
        }

        @media (max-width: 900px) {
            .hero {
                grid-template-columns: 1fr;
                gap: 2.5rem;
                text-align: center;
            }
        }

        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -0.03em;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #ffffff 40%, #a5f3fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        @media (max-width: 600px) {
            .hero-title {
                font-size: 2.6rem;
            }
        }

        .hero-desc {
            font-size: 1.1rem;
            color: var(--text-muted);
            line-height: 1.6;
            margin-bottom: 2.5rem;
        }

        .hero-actions {
            display: flex;
            gap: 1rem;
        }

        @media (max-width: 900px) {
            .hero-actions {
                justify-content: center;
            }
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text);
            padding: 0.75rem 1.5rem;
            border-radius: 9999px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .hero-preview {
            background: rgba(17, 24, 39, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem;
            backdrop-filter: var(--glass-blur);
            position: relative;
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6);
        }

        .chat-bubble {
            background: #1f2937;
            padding: 1rem;
            border-radius: 18px 18px 18px 2px;
            max-width: 85%;
            font-size: 0.85rem;
            line-height: 1.5;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 1rem;
        }

        .chat-bubble.out {
            background: rgba(56, 189, 248, 0.1);
            border-color: rgba(56, 189, 248, 0.2);
            border-radius: 18px 18px 2px 18px;
            margin-left: auto;
            color: var(--primary);
        }

        /* Main Content Grid */
        main {
            width: 100%;
            max-width: 1100px;
            padding: 0 1.5rem 4rem 1.5rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 900px) {
            main {
                grid-template-columns: 1fr;
            }
        }

        /* Cards & Styling */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            padding: 2.2rem;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }

        .card:hover {
            border-color: rgba(56, 189, 248, 0.2);
            box-shadow: 0 20px 40px -20px rgba(56, 189, 248, 0.1);
            transform: translateY(-2px);
        }

        h2 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            letter-spacing: -0.01em;
        }

        /* Form Controls */
        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        select {
            width: 100%;
            padding: 0.8rem 1rem;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.3s ease;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%239ca3af'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 16px center;
            background-size: 16px;
        }

        select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15);
        }

        .range-container {
            display: flex;
            align-items: center;
            gap: 1.25rem;
        }

        input[type="range"] {
            -webkit-appearance: none;
            appearance: none;
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 9999px;
            outline: none;
            transition: background 0.3s;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
            transition: transform 0.1s ease, background 0.3s;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.25);
            background: #22d3ee;
        }

        .range-value {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            min-width: 3.5rem;
            text-align: right;
            color: var(--primary);
            font-size: 1.05rem;
        }

        /* Results Display */
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.5rem 1.25rem;
            text-align: center;
            transition: border-color 0.3s ease;
        }

        .metric-card:hover {
            border-color: rgba(255, 255, 255, 0.15);
        }

        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--primary);
        }

        .metric-unit {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .alert-box {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.2);
            color: var(--warning);
            border-radius: 14px;
            padding: 1.2rem;
            display: flex;
            align-items: flex-start;
            gap: 0.8rem;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }

        .alert-box.success {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: var(--success);
        }

        .alert-box.danger {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: var(--danger);
        }

        /* SVG/Canvas Chart Container */
        .chart-container {
            width: 100%;
            height: 190px;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            margin-top: 1rem;
            position: relative;
            padding: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Story Section (Quiénes Somos & Misión) */
        .about-section {
            grid-column: 1 / -1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1rem;
        }

        @media (max-width: 900px) {
            .about-section {
                grid-template-columns: 1fr;
            }
        }

        .about-card {
            background: linear-gradient(180deg, rgba(17, 24, 30, 0.8) 0%, rgba(10, 15, 24, 0.8) 100%);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2.2rem;
            position: relative;
            transition: all 0.3s ease;
        }

        .about-card:hover {
            border-color: rgba(16, 185, 129, 0.2);
        }

        .about-text {
            font-size: 0.95rem;
            color: var(--text-muted);
            line-height: 1.7;
            margin-top: 1rem;
        }

        .about-text p {
            margin-bottom: 1.2rem;
        }

        .highlight-text {
            color: var(--text);
            font-weight: 500;
        }

        /* Documentation & Thesis section */
        .doc-section {
            grid-column: 1 / -1;
            margin-top: 1rem;
        }

        .accordion {
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            transition: border-color 0.3s ease;
        }

        .accordion:hover {
            border-color: rgba(255, 255, 255, 0.15);
        }

        .accordion-header {
            background: var(--card-bg);
            padding: 1.1rem 1.5rem;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.95rem;
            user-select: none;
            transition: background 0.3s ease;
        }

        .accordion-header:hover {
            background: rgba(30, 41, 59, 0.8);
        }

        .accordion-content {
            padding: 1.5rem;
            background: rgba(15, 23, 42, 0.3);
            border-top: 1px solid var(--border-color);
            display: none;
            line-height: 1.6;
            color: var(--text-muted);
            font-size: 0.9rem;
            animation: fadeIn 0.4s ease-out;
        }

        .accordion-content code {
            display: block;
            background: rgba(3, 7, 18, 0.6);
            padding: 0.8rem 1rem;
            border-radius: 8px;
            font-family: monospace;
            color: var(--primary);
            margin: 0.75rem 0;
            border: 1px solid rgba(255, 255, 255, 0.03);
            overflow-x: auto;
        }

        .accordion-content ul {
            margin-left: 1.5rem;
            margin-top: 0.5rem;
        }

        .accordion-content li {
            margin-bottom: 0.5rem;
        }

        /* Animations & Entry Effects */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .animated-entry {
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        .delay-1 { animation-delay: 0.15s; }
        .delay-2 { animation-delay: 0.3s; }
        .delay-3 { animation-delay: 0.45s; }

        footer {
            padding: 3rem 2rem;
            color: var(--text-muted);
            font-size: 0.8rem;
            text-align: center;
            border-top: 1px solid var(--border-color);
            width: 100%;
            max-width: 1100px;
            margin-top: 5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        @media (max-width: 600px) {
            footer {
                flex-direction: column;
                gap: 1rem;
                padding: 2rem;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav>
        <div class="nav-container">
            <div class="logo" onclick="window.scrollTo(0,0)">
                <span>🔮</span> Merma Cero
            </div>
            <div class="nav-links">
                <a href="#simulator">Simulador</a>
                <a href="#about">Nosotros</a>
                <a href="#math">Tesis</a>
                <a href="https://wa.me/14155238886?text=join%20have-information" target="_blank" class="btn-cta">Probar en WhatsApp</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero animated-entry">
        <div>
            <h1 class="hero-title">Ciencia de datos para proteger el sustento familiar</h1>
            <p class="hero-desc">Democratizamos la física y la econometría predictiva para la economía popular. Reducimos la merma del 15% al 5% mediante recomendaciones de compra personalizadas enviadas directamente por WhatsApp.</p>
            <div class="hero-actions">
                <a href="https://wa.me/14155238886?text=join%20have-information" target="_blank" class="btn-cta" style="padding: 0.85rem 1.8rem; font-size: 0.95rem;">Chatear con el Oráculo</a>
                <a href="#simulator" class="btn-secondary">Probar Simulador</a>
            </div>
        </div>
        <div class="hero-preview">
            <div class="chat-bubble">
                Hola, vendo pescado en lat 19.43 lon -99.13
            </div>
            <div class="chat-bubble out">
                🔮 <b>Merma Cero — Oráculo Climático</b><br>
                🌡️ <b>Pronóstico:</b> 28.5°C | Humedad: 65%<br>
                ⏳ <b>Vida de Anaquel:</b> 3.2 días est.<br>
                📦 <b>Compra Sugerida:</b> Adquirir el <b>72%</b> del volumen diario habitual para evitar mermas hoy.
            </div>
        </div>
    </section>

    <!-- Main Grid Section -->
    <main id="simulator">
        <!-- Control Panel (Parameters) -->
        <section class="card animated-entry delay-1">
            <h2>⚙️ Parámetros de Operación</h2>
            
            <div class="form-group">
                <label for="category">Categoría del Producto</label>
                <select id="category" onchange="runSimulation()">
                    <option value="seafood">🐟 Pescados y Mariscos (Alta sensibilidad Arrhenius)</option>
                    <option value="flowers">🌸 Flores y Plantas (Humedad favorable)</option>
                    <option value="fruit_vegetables">🥦 Frutas y Verduras (Cinética moderada)</option>
                    <option value="dairy">🧀 Lácteos y Quesos (Decaimiento rápido)</option>
                    <option value="generic">📦 Mercancía General</option>
                </select>
            </div>

            <div class="form-group">
                <label for="temperature">Temperatura Ambiente (°C)</label>
                <div class="range-container">
                    <input type="range" id="temperature" min="0" max="50" step="1" value="25" oninput="updateVal('temp-val', this.value); runSimulation();">
                    <span id="temp-val" class="range-value">25°C</span>
                </div>
            </div>

            <div class="form-group">
                <label for="humidity">Humedad Relativa (%)</label>
                <div class="range-container">
                    <input type="range" id="humidity" min="0" max="100" step="5" value="60" oninput="updateVal('hum-val', this.value + '%'); runSimulation();">
                    <span id="hum-val" class="range-value">60%</span>
                </div>
            </div>

            <div class="form-group">
                <label for="precipitation">Probabilidad de Lluvia (%)</label>
                <div class="range-container">
                    <input type="range" id="precipitation" min="0" max="100" step="5" value="10" oninput="updateVal('precip-val', this.value + '%'); runSimulation();">
                    <span id="precip-val" class="range-value">10%</span>
                </div>
            </div>
            
            <div class="form-group">
                <label for="volatility">Volatilidad Climática Proyectada (GARCH)</label>
                <select id="volatility" onchange="runSimulation()">
                    <option value="1.0">Estable / Promedio (Varianza Condicional ~ 1.0)</option>
                    <option value="1.8">Moderada (Varianza Condicional ~ 1.8)</option>
                    <option value="3.0">Alta / Choque Térmico (Varianza Condicional ~ 3.0)</option>
                </select>
            </div>
        </section>

        <!-- Indicators Panel -->
        <section class="card animated-entry delay-1">
            <h2>📊 Indicadores del Oráculo</h2>
            
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Vida de Anaquel</div>
                    <div id="shelf-life" class="metric-value">--</div>
                    <div class="metric-unit">días est.</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Compra Óptima</div>
                    <div id="optimal-stock" class="metric-value">--</div>
                    <div class="metric-unit">% de habitual</div>
                </div>
            </div>

            <div id="status-alert" class="alert-box">
                <!-- Recommendations are injected here -->
            </div>

            <h2>📉 Distribución de Pérdidas a 48h (Monte Carlo)</h2>
            <div class="chart-container">
                <canvas id="mc-chart"></canvas>
            </div>
        </section>

        <!-- About Us section (Quiénes Somos & Misión) -->
        <section id="about" class="about-section animated-entry delay-2">
            <div class="about-card">
                <h2>🎯 Qué Hacemos (Misión)</h2>
                <div class="about-text">
                    <p class="highlight-text">Democratizar la analítica prescriptiva para los microcomerciantes informales de México.</p>
                    <p>Los pequeños comerciantes populares (tianguistas y puesteros) pierden diariamente entre el 15% y el 35% de sus ingresos por descomposiciones térmicas o desabasto. Las grandes cadenas evitan estas pérdidas mediante software corporativo de millones de dólares.</p>
                    <p><b>Merma Cero</b> cambia las reglas del juego: procesa las coordenadas geográficas de un puesto de mercado, descarga el pronóstico meteorológico satelital y resuelve modelos termodinámicos avanzados directamente para entregar sugerencias sin fricción a través de un mensaje de WhatsApp.</p>
                </div>
            </div>

            <div class="about-card">
                <h2>👤 Quiénes Somos (Origen)</h2>
                <div class="about-text">
                    <p class="highlight-text">Tecnología inspirada en la familia y construida con rigor científico.</p>
                    <p>Detrás de Merma Cero se encuentra <b>Fabio Israel Ríos Gutiérrez</b>, un desarrollador y estudiante de 17 años motivado por proteger el sustento económico de su propia familia. La idea nació al observar cómo las olas de calor afectaban directamente el inventario del puesto de frutas y verduras de su <b>tío Chucho en el tianguis de Colima</b>.</p>
                    <p>Conectando la física clásica de los alimentos con los solvers de volatilidad que se utilizan en Wall Street, Fabio construyó este oráculo estocástico como un acto de soberanía y justicia tecnológica.</p>
                </div>
            </div>
        </section>

        <!-- Math & Documentation Section -->
        <section id="math" class="card doc-section animated-entry delay-3">
            <h2>📖 Marco Teórico y Matemático</h2>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <span>🔬 Cinética de Descomposición Arrhenius Modificada</span>
                    <span>▼</span>
                </div>
                <div class="accordion-content">
                    <p>La constante de velocidad de decaimiento físico ($K$) modela la degradación térmica del producto acoplando la humedad relativa ($H$) como un modulador multiplicativo para incorporar la higroscopía:</p>
                    <code>K(T, H) = K₀ · exp(-Ea / (R · T_Kelvin)) · (1 + α · H)</code>
                    <p>Donde:</p>
                    <ul>
                        <li><b>Ea (Energía de Activación):</b> La energía mínima necesaria para activar la descomposición térmica (específica de cada categoría de alimento).</li>
                        <li><b>α (Coeficiente de Aceleración):</b> Coeficiente empírico de aceleración por humedad relativa. Es positivo en mariscos y lácteos (el exceso de humedad favorece la proliferación bacteriana) y negativo en flores (la humedad protege de la marchitez).</li>
                    </ul>
                </div>
            </div>

            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <span>🎲 Dimensionamiento Kelly Estocástico (Sizing)</span>
                    <span>▼</span>
                </div>
                <div class="accordion-content">
                    <p>Para calcular la cantidad de compra óptima $S^*$ que minimiza las pérdidas sin perder ventas, resolvemos el problema de optimización cuadrática inspirado en la teoría de portafolios (Markowitz Mean-Variance):</p>
                    <code>S* = argmax_Q [ E[Profit(Q)] - λ · Std(Profit(Q)) ]</code>
                    <p>Donde la ganancia unitaria se ve reducida por la degradación del precio de salvamento de acuerdo al decaimiento Arrhenius calculado:</p>
                    <code>Salvage_efectivo = Salvage_base · exp(-K)</code>
                    <p>Además, la media de la demanda proyectada se escala dinámicamente si hay alta probabilidad de precipitaciones (lluvia en el tianguis) o temperaturas de alerta.</p>
                </div>
            </div>

            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <span>📈 Volatilidad Condicional GARCH(1,1)</span>
                    <span>▼</span>
                </div>
                <div class="accordion-content">
                    <p>La volatilidad condicional climática $\sigma_t^2$ refleja la incertidumbre en los cambios abruptos de temperatura extrema. Se modela mediante un proceso autorregresivo estocástico:</p>
                    <code>σ_t² = ω + a · ε_{t-1}² + β · σ_{t-1}²</code>
                    <p>Donde mayor volatilidad proyectada escala la incertidumbre de la demanda diaria, ensanchando el margen de seguridad para evitar compras de alto riesgo en días inestables.</p>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer>
        <div>
            Proyecto Merma Cero — Diseñado por Fabio Israel Ríos Gutiérrez.
        </div>
        <div>
            Código Libre bajo Licencia MIT (Open Source).
        </div>
    </footer>

    <script>
        // Constantes Físicas
        const R_GAS = 8.314;
        const INVENTORY_PARAMETERS = {
            seafood: { Ea: 65000.0, K0: 2.5e10, alpha: 1.2, price: 120.0, cost: 70.0, salvage: 10.0 },
            flowers: { Ea: 55000.0, K0: 8.0e8, alpha: -0.4, price: 50.0, cost: 20.0, salvage: 5.0 },
            fruit_vegetables: { Ea: 48000.0, K0: 4.5e7, alpha: 0.8, price: 40.0, cost: 18.0, salvage: 4.0 },
            dairy: { Ea: 72000.0, K0: 5.0e11, alpha: 0.5, price: 35.0, cost: 22.0, salvage: 2.0 },
            generic: { Ea: 50000.0, K0: 1.0e8, alpha: 0.5, price: 50.0, cost: 25.0, salvage: 5.0 }
        };

        // Generador seedable Mulberry32
        function mulberry32(a) {
            return function() {
                let t = a += 0x6D2B79F5;
                t = Math.imul(t ^ (t >>> 15), t | 1);
                t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
                return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
            }
        }

        // Box-Muller para distribución normal
        function boxMuller(rand) {
            let u = 0, v = 0;
            while(u === 0) u = rand();
            while(v === 0) v = rand();
            return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
        }

        function updateVal(id, val) {
            document.getElementById(id).innerText = val;
        }

        function toggleAccordion(el) {
            const content = el.nextElementSibling;
            const arrow = el.querySelector('span:last-child');
            if (content.style.display === "block") {
                content.style.display = "none";
                arrow.innerText = "▼";
            } else {
                content.style.display = "block";
                arrow.innerText = "▲";
            }
        }

        function runSimulation() {
            const category = document.getElementById('category').value;
            const temperature = parseFloat(document.getElementById('temperature').value);
            const humidity = parseFloat(document.getElementById('humidity').value) / 100.0;
            const precipitation = parseFloat(document.getElementById('precipitation').value) / 100.0;
            const volatility = parseFloat(document.getElementById('volatility').value);

            const params = INVENTORY_PARAMETERS[category];
            
            // 1. Vida de anaquel
            const tempKelvin = temperature + 273.15;
            const exponent = -params.Ea / (R_GAS * tempKelvin);
            const arrhenius = params.K0 * Math.exp(exponent);
            const humMod = 1.0 + params.alpha * humidity;
            const K = Math.max(1e-6, arrhenius * humMod);
            const shelfLife = 1.0 / K;
            
            document.getElementById('shelf-life').innerText = shelfLife.toFixed(1);

            // 2. Optimización stock
            let demandMultiplier = 1.0;
            if (precipitation > 0.3) {
              demandMultiplier -= 0.35 * precipitation;
            }
            if (category === "seafood" && temperature > 32) demandMultiplier *= 0.60;
            else if (category === "flowers" && temperature > 30) demandMultiplier *= 0.70;
            else if (category === "generic" && temperature > 35) demandMultiplier *= 0.80;
            demandMultiplier = Math.max(0.1, demandMultiplier);

            const meanD = 100.0 * demandMultiplier;
            const stdD = 30.0 * Math.max(0.5, demandMultiplier) * Math.sqrt(volatility);

            const prng = mulberry32(42);
            const demands = [];
            for(let i=0; i<1000; i++) {
                let d = meanD + boxMuller(prng) * stdD;
                demands.push(Math.max(0, d));
            }

            const salvageEff = params.salvage * Math.exp(-K);
            let bestQ = 0;
            let maxUtil = -Infinity;

            for(let q=0; q<=200; q++) {
                let sumProfit = 0;
                let profits = [];
                for(let i=0; i<1000; i++) {
                    const sales = Math.min(q, demands[i]);
                    const surplus = Math.max(0, q - demands[i]);
                    const profit = (sales * params.price) + (surplus * salvageEff) - (q * params.cost);
                    profits.push(profit);
                    sumProfit += profit;
                }
                const meanProfit = sumProfit / 1000;
                let varSum = 0;
                for(let i=0; i<1000; i++) {
                    varSum += Math.pow(profits[i] - meanProfit, 2);
                }
                const stdProfit = Math.sqrt(varSum / 1000);
                const utility = meanProfit - 0.5 * stdProfit;

                if (utility > maxUtil) {
                    maxUtil = utility;
                    bestQ = q;
                }
            }

            document.getElementById('optimal-stock').innerText = bestQ.toFixed(0);

            // 3. Bitácora / Alerta
            const alertBox = document.getElementById('status-alert');
            alertBox.className = "alert-box";
            if (shelfLife < 1.5) {
                alertBox.classList.add("danger");
                alertBox.innerHTML = `⚠️ <b>Riesgo Crítico de Merma:</b> La vida de anaquel estimada es menor a 36 horas. Se recomienda reducir tus compras al ${bestQ.toFixed(0)}% del stock promedio diario y resguardar tu producto con refrigeración o hielo seco inmediatamente.`;
            } else if (shelfLife < 3.0) {
                alertBox.classList.add("warning");
                alertBox.innerHTML = `⚠️ <b>Riesgo Moderado:</b> Temperaturas elevadas aceleran el decaimiento. Reduce ligeramente las compras e incrementa sombra o ventilación sobre tu mercancía.`;
            } else {
                alertBox.classList.add("success");
                alertBox.innerHTML = `✅ <b>Operación Segura:</b> Clima propicio para conservación. Tu stock recomendado es del ${bestQ.toFixed(0)}% para suplir la demanda local proyectada.`;
            }

            // 4. Monte Carlo Canvas Drawing (Pérdidas acumuladas a 48h)
            drawChart(category, temperature, humidity, volatility);
        }

        function drawChart(category, temp, hum, vol) {
            const canvas = document.getElementById('mc-chart');
            const ctx = canvas.getContext('2d');
            const w = canvas.width = canvas.offsetWidth;
            const h = canvas.height = canvas.offsetHeight;

            ctx.clearRect(0, 0, w, h);

            // Simular 48h decay factors
            const prng = mulberry32(42);
            const decays = [];
            const volScale = Math.sqrt(vol);
            const params = INVENTORY_PARAMETERS[category];

            for(let i=0; i<500; i++) {
                const shock1 = boxMuller(prng);
                const t1 = Math.min(50, Math.max(0, temp + shock1 * volScale * 0.5));
                const k1 = params.K0 * Math.exp(-params.Ea / (R_GAS * (t1 + 273.15))) * (1 + params.alpha * hum);

                const shock2 = boxMuller(prng);
                const t2 = Math.min(50, Math.max(0, t1 + shock2 * volScale * 0.5));
                const k2 = params.K0 * Math.exp(-params.Ea / (R_GAS * (t2 + 273.15))) * (1 + params.alpha * hum);

                decays.push(1.0 - Math.exp(-(Math.max(1e-6, k1) + Math.max(1e-6, k2))));
            }

            decays.sort((a,b) => a - b);

            // Agrupar en histograma
            const binsCount = 20;
            const bins = new Array(binsCount).fill(0);
            for(let i=0; i<decays.length; i++) {
                const binIdx = Math.min(binsCount - 1, Math.floor(decays[i] * binsCount));
                bins[binIdx]++;
            }

            const maxBin = Math.max(...bins);
            const padding = 20;
            const barW = (w - padding * 2) / binsCount;

            // Dibujar barras del histograma
            for(let i=0; i<binsCount; i++) {
                const barH = (bins[i] / maxBin) * (h - padding * 2);
                const x = padding + i * barW;
                const y = h - padding - barH;

                ctx.fillStyle = i > 15 ? 'rgba(239, 68, 68, 0.6)' : 'rgba(56, 189, 248, 0.6)';
                ctx.fillRect(x, y, barW - 2, barH);
            }

            // Etiquetas del eje X
            ctx.fillStyle = '#94a3b8';
            ctx.font = '10px sans-serif';
            ctx.fillText('0% merma', padding, h - 5);
            ctx.fillText('50%', w / 2 - 10, h - 5);
            ctx.fillText('100% merma', w - padding - 60, h - 5);
        }

        // Ejecutar simulación inicial al cargar
        window.onload = function() {
            runSimulation();
        }
    </script>
</body>
</html>
"""

def generate():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(target_dir, "index.html")
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"[+] Frontend interactivo generado exitosamente en: {target_file}")

if __name__ == "__main__":
    generate()
