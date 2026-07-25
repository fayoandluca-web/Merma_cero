# 📋 Plan Estratégico — Proyecto Merma Cero
**Autor:** Fabio Israel Ríos Gutiérrez
**Versión:** 1.0 · Julio 2026
**Estado del proyecto:** MVP técnico terminado → fase de lanzamiento y comercialización

> *"Cuando tienes algo bien planificado y escrito, ya tienes la mitad del trabajo."*
> La mitad técnica está hecha. Este documento planifica la otra mitad: lanzamiento, negocio, impacto y posicionamiento.

---

## 0. Dónde estamos hoy (línea base honesta)

**✅ Terminado (la mitad "difícil"):**
- Motor cuantitativo real: Arrhenius (cinética de merma) + GARCH(1,1) (volatilidad climática) + Kelly/Markowitz (sizing) + Monte Carlo (VaR/CVaR 95%).
- Arquitectura hexagonal limpia (dominio / aplicación / infraestructura).
- Adaptadores listos: Open-Meteo (clima, con fallback offline), SQLite, JSON, **Twilio (código completo)**, WhatsApp mock, Gemini (con fallback en español).
- Blindaje de seguridad: validación Pydantic E.164, rate limiting Token Bucket, censura de stack traces, minimización de datos.
- 13 tests unitarios + test de paridad JS↔Py. CLI interactivo + webhook FastAPI.
- Documentación: TESIS_MANIFIESTO.md, ANÁLISIS.md, marco legal.

**❌ Lo que falta (la mitad "de lanzamiento"):**
- Twilio en producción real (credenciales + número aprobado + **plantillas HSM** para alertas proactivas fuera de la ventana de 24 h).
- Cero usuarios reales todavía. Cero métricas de impacto medidas.
- Sin modelo de negocio ni unit economics definidos.
- Sin identidad de marca, landing, ni estrategia de contenido.
- Sin dossier para premios ni loop de calibración con datos reales.

---

## 1. Visión

> **Que ningún comerciante de la economía popular mexicana pierda dinero por no tener acceso a la misma inteligencia predictiva que usan las grandes cadenas.**

Merma Cero democratiza — vía un simple mensaje de WhatsApp — la ciencia de datos (termodinámica + econometría) que hoy solo está al alcance de corporativos con equipos de PhDs. Es tecnología como herramienta de **justicia económica**.

## 2. Misión

Construir y sostener un oráculo climático-financiero gratuito o de bajísimo costo que le diga a cada tianguista, en lenguaje natural y sin fricción: **cuánto comprar hoy, cuánto le durará el producto, y cómo protegerlo** — reduciendo la merma del 15–35% a menos del 5% del ingreso diario.

## 3. Valores / principios rectores
1. **Fricción cero** — si no cabe en un mensaje de WhatsApp, no sirve.
2. **Impacto medible** — cada peso salvado se cuenta y se puede auditar.
3. **Honestidad cuantitativa** — modelos reales, no "consejos genéricos"; se admite la incertidumbre (VaR/CVaR).
4. **Soberanía tecnológica** — funciona offline (fallbacks), minimiza datos, no depende de un solo proveedor.

---

## 4. Objetivos (matriz corto / mediano / largo plazo)

### 🎯 Tus objetivos declarados
| # | Objetivo | Horizonte |
|---|----------|-----------|
| O1 | Terminar configuración WhatsApp + Twilio → comercial y funcional | Corto (Jul–Ago 2026) |
| O2 | Escribir manifiesto/tesis extenso del proyecto | Corto–Mediano (Ago–Sep 2026) |
| O3 | Lanzar y llegar a ≥200 usuarios | Mediano (Sep 2026–Feb 2027) |
| O4 | Participar en Premios Lidera (distintivo Lidera) | Mediano (según convocatoria) |
| O5 | Conseguir financiamiento | Largo (2027+) |
| O6 | Crear contenido → crecimiento de imagen personal aprovechando el proyecto | Transversal / continuo |

### ➕ Objetivos que te faltan (mi recomendación)
| # | Objetivo faltante | Por qué es crítico |
|---|-------------------|--------------------|
| O7 | **Instrumentar métricas de impacto** (pesos salvados, kg de merma evitada, CO₂/metano evitado) | Sin números medidos, no hay tesis creíble, ni caso ESG, ni argumento para premios ni financiamiento. Es la moneda de todo lo demás. |
| O8 | **Loop de calibración con datos reales** ("¿acertó la predicción de ayer? Sí/No") | Convierte el modelo de "teórico" a "validado". Es tu ventaja científica y tu defensa ante escépticos. |
| O9 | **Definir modelo de negocio y unit economics** (Twilio cobra por conversación; ¿gratis subsidiado, freemium, patrocinado, o B2B2C con asociaciones de comerciantes?) | 200 usuarios enviando mensajes = costos reales de Twilio/Gemini. Necesitas saber si es sostenible antes de escalar. |
| O10 | **Piloto controlado (caso cero)** con tu tío Chucho + 5–10 vendedores del tianguis de Colima | Prueba real, testimonios en video, datos de impacto, y la historia humana que vende premios y financiamiento. |
| O11 | **Cumplimiento legal/comercial mínimo** (aviso de privacidad, términos, opt-in explícito de WhatsApp, políticas de Meta/Twilio para no ser baneado) | Si es "comercial", esto deja de ser opcional. Meta banea remitentes sin opt-in. |
| O12 | **Identidad de marca** (nombre público, logo, paleta, narrativa de una línea) | Necesaria para landing, contenido, premios e imagen personal. Actualmente solo existe el nombre en código. |
| O13 | **Estrategia de adquisición de usuarios** concreta (no "que lleguen solos") | 200 usuarios no aparecen; se consiguen con alianzas a líderes de mercado, asociaciones de comerciantes, y referidos. |
| O14 | **Resolver la tensión open-source vs. comercial** (el manifiesto dice "código libre" pero O1 dice "comercial") | **Decisión tomada: postergar a propósito hasta la Fase 2**, cuando el piloto dé datos reales de costos y adopción. No se decide "a ciegas"; se mantienen las 3 opciones vivas (gratis+grants / B2B2C / freemium) y se elige con evidencia. |
| O15 | **Registro de riesgos y plan de contingencia** | Dependencia de APIs, precisión del modelo, adopción, costos, baneo de WhatsApp. |

---

## 5. Roadmap por fases

### **Fase 0 — Construcción (✅ COMPLETADA)**
MVP técnico, modelos, arquitectura, tests, documentación base.

### **Fase 1 — Producto real + Piloto (Jul–Ago 2026)** · *foco: O1, O7, O8, O10, O11*
- [ ] Crear cuenta Twilio → activar **WhatsApp Sender** (Sandbox primero para pruebas).
- [ ] Cargar credenciales reales en `.env` (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`).
- [ ] Diseñar y **someter plantillas HSM** a aprobación de Meta (para alertas proactivas fuera de la ventana de 24 h — obligatorio para el cron de `/alerts/trigger`).
- [ ] Implementar **flujo de opt-in** explícito (mensaje de bienvenida + consentimiento).
- [ ] Instrumentar en SQLite: log de cada predicción + campo "¿acertó? sí/no" + pesos estimados salvados (O7, O8).
- [ ] Desplegar en un host accesible (Railway/Render/VPS) + configurar webhook con dominio HTTPS.
- [ ] **Piloto Colima:** onboarding manual de tío Chucho + 5–10 vendedores. Recolectar testimonios y datos 2–4 semanas.
- [ ] Redactar aviso de privacidad + términos mínimos (O11).

### **Fase 2 — Manifiesto, marca y validación (Ago–Sep 2026)** · *foco: O2, O12, O14*
- [ ] Ampliar `TESIS_MANIFIESTO.md` a tesis formal: introducción, marco teórico (Arrhenius/GARCH/Kelly con citas), metodología, **resultados del piloto con datos reales**, discusión, conclusiones, referencias, anexos.
- [ ] Definir identidad de marca: nombre público, logo, paleta, tagline (O12).
- [ ] Landing page (reusar tu `exportar_web.py`/`index.html`) con: problema, solución, resultados del piloto, testimonios, CTA de "prueba en WhatsApp".
- [ ] **Decidir aquí** (no antes) el modelo open-source vs. comercial + licencia, con los datos del piloto de Fase 1 (O14). Opciones en mesa: (a) gratis + grants, (b) B2B2C con asociaciones/municipios, (c) freemium.
- [ ] Escalar a ~50 usuarios activos.

### **Fase 3 — Escala a 200 + Premios + Contenido (Oct 2026–Feb 2027)** · *foco: O3, O4, O6, O13*
- [ ] Ejecutar estrategia de adquisición (ver §7) hasta **≥200 usuarios**.
- [ ] Preparar y **postular al distintivo Lidera / Premios Lidera** (dossier + video + métricas de impacto) — *verificar convocatoria, fechas y requisitos exactos.*
- [ ] Lanzar contenido "build-in-public" bilingüe (ver §9): la historia del tío Chucho, el detrás de la ciencia, hitos de usuarios.
- [ ] Reporte de impacto acumulado (pesos salvados totales, merma evitada, testimonios).

### **Fase 4 — Sostenibilidad y financiamiento (2027+)** · *foco: O5, O9*
- [ ] Consolidar unit economics con datos reales de 200 usuarios (O9).
- [ ] Buscar financiamiento (ver §8): grants de impacto/ESG, incubadoras, concursos, patrocinio.
- [ ] Expansión: nuevas categorías (lácteos, frutas, verduras), nuevas regiones, panel para líderes de mercado.

---

## 6. Métricas de éxito (KPIs)

| KPI | Meta Fase 1 | Meta Fase 3 |
|-----|-------------|-------------|
| Usuarios registrados | 10 (piloto) | **≥200** |
| Usuarios activos semanales | 8 | ≥120 |
| Consultas / semana | ~50 | ≥800 |
| **Pesos salvados estimados (acumulado)** | Medir baseline | Reportable para premios |
| **Precisión de predicción** (aciertos / total) | Establecer baseline | ≥70% |
| Retención D30 | — | ≥40% |
| Costo por usuario activo / mes (Twilio+IA) | Medir | Definir umbral sostenible |

---

## 7. Estrategia de adquisición → 200 usuarios (O13)

1. **Caso cero verificable:** tío Chucho como testimonio ancla (video + antes/después en pesos).
2. **Alianzas con líderes de tianguis:** un líder de mercado que confíe = 20–50 comerciantes de golpe. Ir a los tianguis en persona.
3. **Asociaciones de comerciantes / uniones populares:** presentación del servicio gratis.
4. **Referido incentivado:** "invita a otro marchante y ambos ganan X".
5. **Prensa local Colima + redes:** la historia humana es viral por naturaleza.
6. **QR físico** en puestos piloto: "Escanéame para no perder dinero por el calor".

---

## 8. Financiamiento (largo plazo — O5)

**Encaja perfecto en la taxonomía de impacto** (ya lo documentaste: ODS 12.3, CPEUM Art. 5/25, ESG). Rutas:
- **Grants de impacto social / foodtech / climate-tech** (fundaciones, aceleradoras de impacto).
- **Concursos y premios con bolsa** (además de Lidera): hackathons, premios de innovación social juvenil, UNAM/gobierno.
- **Incubadoras universitarias** (UNAM tiene programas de emprendimiento).
- **Patrocinio corporativo** (bancos/fintech con agenda de inclusión financiera; telefónicas con agenda de conectividad).
- **Modelo B2B2C:** cobrar a asociaciones de comerciantes / gobiernos municipales una licencia, servicio gratis para el comerciante.
> **Requisito transversal para TODAS estas rutas:** métricas de impacto medidas (O7) + validación del modelo (O8). Sin números, no hay cheque.

## 9. Marca personal y contenido (O6 — transversal)

Aprovecha que eres **un programador de 17 años que aplica física y econometría para ayudar a su familia** — es una narrativa poderosísima y auténtica.
- **Build-in-public:** documenta el journey (código, ciencia, usuarios reales, aprendizajes) en X/LinkedIn/TikTok.
- **Series de contenido:** "La ciencia detrás", "El tianguis y los datos", "De 2,500 pesos perdidos a cero".
- **Reusa tu estándar:** ya tienes proyectos como R1-15 Máquina de Contenido (1 idea→5 formatos) — aplícalo aquí.
- **Objetivo doble:** cada pieza construye tu imagen **y** capta usuarios/aliados/financiadores.
- **Credencialízalo:** convierte hitos en credenciales para tu CV/becas (encaja con tu proyecto R8-3 Máquina de Credenciales).

## 10. Riesgos y mitigaciones (O15)

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Baneo de WhatsApp por falta de opt-in | Alto | Opt-in explícito + plantillas aprobadas (Fase 1). |
| Modelo predice mal → pierde confianza | Alto | Loop de calibración (O8); admitir incertidumbre; empezar con categorías bien parametrizadas. |
| Costos Twilio/IA insostenibles a escala | Medio | Unit economics tempranos (O9); fallback local de Gemini ya reduce costos de IA. |
| Baja adopción (comerciantes desconfían de la tech) | Alto | Caso cero + aliado líder de mercado; fricción cero ya diseñada. |
| Dependencia de Open-Meteo/Gemini | Medio | Ya tienes fallbacks offline — mantenerlos. |
| Tensión open-source vs. comercial sin resolver | Medio | Decidir licencia/modelo en Fase 2 (O14). |

---

## 11. Próximas 2 semanas (acciones concretas)

1. Crear cuenta Twilio + activar Sandbox de WhatsApp y **probar un mensaje real** a tu propio número (validar `twilio_adapter.py` end-to-end).
2. Definir las 2–3 **plantillas HSM** de alerta y prepararlas para someter a Meta.
3. Añadir en SQLite el logging de impacto (predicción + acierto + pesos salvados) — instrumentación de O7/O8.
4. Agendar el onboarding de tío Chucho como usuario #1 del piloto.
5. Verificar **convocatoria, fechas y requisitos** exactos de los Premios Lidera / distintivo Lidera.

---

*Documento vivo. Actualizar al cierre de cada fase.*
