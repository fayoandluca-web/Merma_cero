# MERMA CERO: ORÁCULO CLIMÁTICO-FINANCIERO PARA LA ECONOMÍA INFORMAL
*Bases técnicas, intuición y ejemplos numéricos*

Fabio Israel Ríos Gutiérrez

MERMA CERO — VERSIÓN BETA
SUJETO A CAMBIOS SEGÚN RESULTADOS DEL PILOTO

---

## Índice

- Introducción
- Capítulo Uno · El reloj y el cielo
- Capítulo Dos · Los dos problemas reales
- Capítulo Tres · La física de la descomposición (Arrhenius)
- Capítulo Cuatro · El clima tiene memoria (GARCH)
- Capítulo Cinco · Cuánto comprar sin arriesgarlo todo (Kelly-Markowitz)
- Capítulo Seis · Mirar 48 horas al futuro (Monte Carlo, VaR y CVaR)
- Capítulo Siete · Cómo se conecta todo
- Capítulo Ocho · Ejemplo numérico paso a paso
- Capítulo Nueve · Cómo está construido
- Capítulo Diez · Cómo se protege
- Capítulo Once · Qué tan probado está esto
- Capítulo Doce · Lo que todavía no sabemos
- Capítulo Trece · Cómo se construyó esto
- Capítulo Catorce · Hacia dónde va: reconocimiento y protección del trabajo
- Conclusión
- Anexos
- Referencias
- Reflexión final

---

## Introducción

Voy a ser honesto desde la primera línea, porque así voy a escribir todo este documento. Tengo 16 años y la mayoría de los que tienen mi edad están pensando en subir de rango en algún videojuego o en qué van a subir a redes el fin de semana. A mí me dio por otra cosa. Me dio por ver a mi tío Chucho perder dinero real, de su bolsillo, por algo tan tonto como el clima — y ponerme a hacer algo al respecto con lo único que sé hacer: programar y usar matemáticas.

Mi tío Chucho vende mariscos y pescado fresco en un tianguis de Colima. Un miércoles de plaza del verano pasado hizo tanto calor que casi nadie salió a comprar, y el pescado que no se vendió se echó a perder en las hieleras antes de que él pudiera regresar al día siguiente. Perdió más de 2,500 pesos de golpe. Para una cadena de supermercados eso ni se nota. Para mi tío, es la diferencia entre pagar la luz o que se la corten.

Me puse a investigar cómo evitan este problema las grandes cadenas, y descubrí que usan modelos matemáticos de predicción climática y de demanda para decidir exactamente cuánto surtir cada día. Los comerciantes del tianguis no tienen nada de eso. Solo tienen la intuición que han juntado con los años.

Así nació **Merma Cero**: un sistema que toma esas mismas matemáticas — física de descomposición, econometría de volatilidad, optimización de portafolios — y las entrega gratis, por WhatsApp, sin que el comerciante tenga que aprender nada nuevo. Este documento explica, con honestidad y sin inflar nada, cómo funciona, qué tan probado está, y qué le falta todavía.

---

## Capítulo Uno · El reloj y el cielo

Imagina que tienes un bloque de hielo entre las manos y tienes que cruzar corriendo una plaza entera para venderlo antes de que se derrita por completo. Ese es el primer enemigo de todo comerciante de productos frescos: **el reloj**. No importa qué tan bien vendas, el hielo se derrite más rápido entre más calor haga, y no puedes pausarlo ni negociar con él.

Pero hay un segundo enemigo, uno que no se ve tan fácil: **el cielo**. Cuando mi tío Chucho sale de su casa a las 4 de la mañana a comprar su mercancía en el mercado de abastos, no sabe todavía si el día va a estar tranquilo, si va a cambiar el clima a medio día o si va a llover de repente. El cielo no avisa con precisión exacta. Solo da pistas, probabilidades, señales de que algo se puede poner feo.

Todos los días, un comerciante libra esta doble batalla completamente solo: contra el reloj que no se detiene (la descomposición física de su mercancía) y contra el cielo que no avisa con certeza (la incertidumbre de cuánto va a poder vender). **Merma Cero** es, en el fondo, un copiloto matemático para esas dos batallas al mismo tiempo. Le pone números al reloj (Capítulos Tres y Ocho) y le pone números al cielo (Capítulos Cuatro y Seis), y junta ambos cálculos para decirle al comerciante, en un simple mensaje de WhatsApp, cuánto comprar hoy para no perder en ninguna de las dos batallas.

El resto de este documento traduce esa idea a matemáticas reales, paso por paso.

---

## Capítulo Dos · Los dos problemas reales

Es fácil quedarse en la superficie aquí, y no quiero hacer eso. Voy a tratar los dos problemas por separado y con la seriedad que merecen, porque simplificarlos de más sería mentir con estadísticas bonitas.

### Problema A · La merma física (el reloj)

En México, la informalidad laboral ronda el 55% según el INEGI: más de la mitad de la gente que trabaja no tiene sueldo fijo ni seguridad social. Su economía es de subsistencia — lo que ganan hoy es lo que comen mañana. En ese contexto, la merma (perder producto por descomposición) no es una pérdida de ganancia potencial: es perder el capital de trabajo que ya se gastó.

Un ejemplo real de cómo pega esto: Doña María compra 100 docenas de rosas a 20 pesos la docena para venderlas ($2,000 pesos de inversión). En un día normal las vende todas a 40 pesos la docena y se queda con $2,000 pesos de ganancia neta. Pero si una ola de calor marchita el 40% de sus flores antes de venderlas, solo vende 60 docenas: sus ingresos caen a $2,400 pesos, y después de descontar su inversión inicial, su ganancia real por 12 horas de trabajo es de apenas $400 pesos. Si la merma sube a 50%, su ganancia es cero. Si sube a 60%, pierde dinero de su propio bolsillo — y ahí es cuando entra el prestamista informal que cobra 20% semanal.

Esto es una **asimetría de información**: las grandes cadenas tienen sistemas que les dicen exactamente cuánto surtir cada día según el clima. El comerciante de a pie no tiene absolutamente nada de eso, y tampoco tiene tiempo, dinero ni conocimientos para conseguirlo.

### Problema B · El clima como obstáculo (el cielo)

Aquí es donde quiero ser más serio de lo que fui la primera vez que pensé este proyecto, porque cometí una simplificación que no aguanta un análisis honesto: **no es cierto que "si hace calor, la gente no sale a comprar"**. Eso es falso y perezoso. La gente necesita comer. Nadie deja de alimentar a su familia porque el termómetro marque 38 grados. Un modelo que asuma que el hambre se cancela con el calor está mal construido desde la raíz.

Lo que sí pasa — y esto es más fino, más real y más serio — son al menos cuatro cosas distintas, y las voy a separar en vez de mezclarlas en una sola idea vaga de "el clima afecta las ventas":

1. **La demanda no desaparece, se desplaza.** La gente cambia *cuándo* compra (muy temprano o ya entrada la noche, evitando la hora pico de sol) y *dónde* compra. En un día de calor extremo, entre un puesto de tianguis sin sombra ni refrigeración y un supermercado con aire acondicionado y vitrinas frías, la balanza se inclina hacia el segundo. El cliente no deja de comprar pescado: deja de comprárselo **a él**. Esto es un desplazamiento de la demanda hacia el sector formal, y es un golpe específico contra el comerciante informal, no un colapso general del consumo. Es un problema más serio que "vender menos": es perder terreno frente a un competidor que sí tiene refrigeración.

2. **Para productos que no son de primera necesidad, el efecto sí es una caída real de demanda, no solo un desplazamiento.** Nadie necesita comprar flores para sobrevivir un día de calor. Ahí sí aplica de forma más directa la idea de "menos gente compra", y por eso el modelo trata a las flores distinto que al pescado (Capítulo Tres).

3. **Hay un riesgo todavía más serio que casi nunca se menciona: el riesgo para el propio comerciante.** Mi tío Chucho no es una variable de demanda en una hoja de cálculo. Es una persona parada bajo el sol directo durante doce horas seguidas. Los golpes de calor y la deshidratación en trabajadores que están a la intemperie durante olas de calor son un riesgo de salud real y documentado en México, no una anécdota triste de relleno. El clima no solo amenaza el producto o la venta: amenaza al comerciante mismo. Y lo digo sin maquillarlo: **hoy, ninguna ecuación de este proyecto mide ese riesgo todavía.** Es una limitación honesta, no un detalle menor, y la dejo anotada en el Capítulo Doce.

4. **La lluvia pega distinto y, casi siempre, más parejo y más duro que el calor.** Casi nadie quiere cruzar calles inundadas para ninguna compra, sea de primera necesidad o no. Y una tormenta puede destruir físicamente un puesto de lámina y lona en minutos, no en horas — eso ya no es un problema de ventas, es un problema de pérdida total del capital de trabajo de un solo golpe.

Entonces, "el problema del clima" en este proyecto no es una sola cosa: son al menos tres problemas distintos escondidos bajo la misma palabra. **(a)** el clima acelera la descomposición física del producto — esto lo captura la ecuación de Arrhenius (Capítulo Tres); **(b)** el clima reacomoda cuándo y dónde compra la gente, golpeando de forma desigual al vendedor informal frente al formal — esto lo intenta capturar, todavía de forma imperfecta, el ajuste de demanda climática que se ve en el ejemplo numérico del Capítulo Ocho; y **(c)** el clima pone en riesgo físico al comerciante — esto, hoy, el sistema no lo mide en absoluto. Prefiero dejar este tercer punto anotado con toda claridad a fingir que ya está resuelto.

---

## Capítulo Tres · La física de la descomposición (Arrhenius)

Para que Merma Cero no fuera una app que da consejos genéricos de autoayuda financiera, el corazón matemático tenía que ser física real, no intuición disfrazada de tecnología.

La descomposición de alimentos y la marchitez de flores son, al final, reacciones químicas. La velocidad a la que ocurre una reacción química se modela con precisión mediante la **ecuación de Arrhenius**, propuesta en 1889:

$$K = K_0 \cdot \exp\left(-\frac{E_a}{R \cdot T}\right)$$

Donde:
- $K$ es la velocidad de merma o decaimiento diario del producto.
- $K_0$ es el factor de frecuencia, propio de cada tipo de alimento.
- $E_a$ es la energía de activación (en joules por mol): la energía mínima que se necesita para que arranque la descomposición.
- $R$ es la constante universal de los gases ideales, $8.314 \ \text{J/mol·K}$.
- $T$ es la temperatura ambiente convertida a Kelvin ($T = T_{\text{Celsius}} + 273.15$).

En Merma Cero, se extiende este modelo clásico agregando un término de humedad relativa $H$, con su propio coeficiente de aceleración $\alpha$:

$$K(T, H) = K_0 \cdot \exp\left(-\frac{E_a}{R \cdot T}\right) \cdot (1 + \alpha \cdot H)$$

**¿Por qué importa el coeficiente de humedad?** Para pescados y mariscos, la humedad acelera la descomposición porque favorece la reproducción bacteriana en la superficie del producto — su coeficiente es positivo ($\alpha = 1.2$). Para flores, en cambio, la humedad alta puede ser *buena*: evita que los pétalos pierdan agua por transpiración y se marchiten — su coeficiente es negativo ($\alpha = -0.4$). El mismo fenómeno climático (humedad alta) tiene efectos opuestos según qué se esté vendiendo, y el modelo lo respeta en vez de tratarlo como un solo número genérico.

Una vez calculada $K$, la vida de anaquel esperada, en días, es simplemente su inverso:

$$\text{Vida de anaquel (días)} = \frac{1}{K(T, H)}$$

En el Capítulo Ocho vamos a meter números reales a esta fórmula y ver qué tan brutal es la diferencia entre un día tranquilo y una ola de calor.

---

## Capítulo Cuatro · El clima tiene memoria (GARCH)

El clima de un día no vive aislado del día anterior. Si llevas tres días de anomalías térmicas fuertes, es mucho más probable que mañana también haya un choque de temperatura extremo que si llevas tres días de clima estable. Esa "memoria" de la volatilidad climática se puede modelar con la misma familia de ecuaciones que se usa en finanzas para proyectar qué tan violento puede ser el siguiente movimiento de un mercado: el modelo **GARCH(1,1)** (Heterocedasticidad Condicional Autorregresiva Generalizada), publicado originalmente por Robert Engle en 1982 y generalizado por Tim Bollerslev en 1986.

### ¿Qué mide?

Mide la varianza condicional esperada para el siguiente periodo — en este caso, qué tanto se espera que se mueva la temperatura mañana, dado lo que se ha movido en los días recientes.

### La fórmula y sus componentes

$$\sigma_{t+1}^2 = \omega + \alpha \cdot \epsilon_t^2 + \beta \cdot \sigma_t^2$$

- $\omega$ — **el ruido de fondo**: la variabilidad mínima que siempre existe, incluso en temporada tranquila.
- $\epsilon_t^2$ — **el choque reciente**: qué tanto se desvió la temperatura de hoy respecto al promedio esperado para la temporada.
- $\sigma_t^2$ — **la memoria del miedo climático**: la varianza que ya traíamos calculada del día anterior.
- $\beta$ — qué tanto pesa esa memoria (en Merma Cero, $\beta = 0.80$: el clima es bastante "terco", una vez que se pone inestable tarda en calmarse).
- $\alpha$ — qué tanto pesa el choque más reciente ($\alpha = 0.15$).
- $\sigma_{t+1}^2$ — la salida: la varianza proyectada para el siguiente periodo.

Cuando esta varianza proyectada crece mucho respecto a lo normal, el sistema interpreta que el clima está entrando en una fase inestable, y usa ese número para ensanchar la incertidumbre de la demanda esperada (Capítulo Cinco) y para simular escenarios futuros más agresivos (Capítulo Seis). En otras palabras: entre más loco esté el termómetro, más conservador se vuelve el sistema con la cantidad de compra que sugiere.

---

## Capítulo Cinco · Cuánto comprar sin arriesgarlo todo (Kelly-Markowitz)

En una escuela de negocios tradicional te enseñan a resolver "cuánto inventario comprar" con fórmulas que asumen que el comerciante es neutral al riesgo — que perder dinero un día no le afecta su capacidad de operar al día siguiente. En la economía informal eso es falso: si un comerciante pierde todo su capital de trabajo dos días seguidos, cierra el puesto. Tiene **aversión a la ruina**, no solo aversión al riesgo.

Para resolver esto se usa una función de utilidad ajustada por riesgo, con raíces en el trabajo de Harry Markowitz (1952) sobre selección de portafolios y en el criterio de John Kelly (1956) sobre crecimiento óptimo de capital bajo incertidumbre:

$$U(Q) = \mathbb{E}[\text{Ganancia}(Q)] - \lambda \cdot \text{Desv. Est.}(\text{Ganancia}(Q))$$

Donde $Q$ es la cantidad a comprar, $\mathbb{E}[\text{Ganancia}(Q)]$ es la ganancia promedio esperada a lo largo de miles de escenarios simulados de demanda, $\text{Desv. Est.}(\text{Ganancia}(Q))$ mide qué tan dispersos (riesgosos) son esos resultados, y $\lambda$ es qué tanto le teme el comerciante al riesgo (en Merma Cero, un valor balanceado de $0.5$). El sistema busca la cantidad $Q^*$ que maximiza esta utilidad:

$$Q^* = \arg\max_{Q} \ U(Q)$$

Para cada escenario simulado, la ganancia se calcula así:

$$\text{Ganancia} = (\text{Ventas} \cdot \text{Precio}) + (\text{Excedente} \cdot \text{Salvamento efectivo}) - (Q \cdot \text{Costo})$$

El **salvamento efectivo** es el valor de rescate del producto que no se vendió, y no es un número fijo: se degrada exponencialmente según qué tan rápido se esté descomponiendo el producto ese día, usando la misma velocidad $K$ del Capítulo Tres:

$$\text{Salvamento efectivo} = \text{Salvamento base} \cdot e^{-K}$$

Si hace mucho calor, $K$ es grande, $e^{-K}$ se acerca a cero, y el producto sobrante no vale prácticamente nada porque se pudrió. Si el clima está fresco, el salvamento se mantiene alto. Esta es la pieza que conecta directamente el "reloj" (Capítulo Tres) con la decisión de negocio: no solo importa cuánto dura el producto, importa cuánto vale lo que sobra si no se vende todo.

---

## Capítulo Seis · Mirar 48 horas al futuro (Monte Carlo, VaR y CVaR)

Para las alertas rápidas — avisarle a alguien que está a punto de tomar una mala decisión antes de que la tome — el sistema corre una simulación de Monte Carlo que proyecta miles de futuros posibles para las próximas 48 horas, en vez de calcular un solo número promedio.

Cada trayectoria de temperatura futura se simula acoplada a la volatilidad calculada por GARCH:

$$T_{t+1} = T_t + \eta \cdot \sigma_t$$

donde $\eta$ es un número aleatorio con distribución normal estándar. Para cada una de miles de trayectorias, se calcula la merma acumulada de dos días de descomposición Arrhenius:

$$\text{Merma acumulada 48h} = 1 - \exp\left(-(K_{\text{día 1}} + K_{\text{día 2}})\right)$$

De la distribución completa de resultados, el sistema extrae tres números:

1. **Merma esperada**: el promedio de todos los escenarios simulados.
2. **VaR 95% (Valor en Riesgo)**: la pérdida física de inventario que solo se supera en el 5% de los peores escenarios climáticos posibles.
3. **CVaR 95% (Pérdida de cola esperada)**: el promedio de merma dentro de ese 5% de escenarios más devastadores — no el peor caso puntual, sino qué tan mal está, en promedio, ese peor 5%.

Con estos tres números, el sistema puede mandar una alerta del tipo: *"Detectamos un 95% de probabilidad de que tu producto sufra una descomposición del 85% en las próximas 48 horas por choques térmicos inesperados en tu zona. Reduce tu inventario ahora."* En el Capítulo Ocho vas a ver estos números calculados de verdad, no inventados para que se vean bien.

---

## Capítulo Siete · Cómo se conecta todo

Los cuatro módulos anteriores no funcionan aislados: se alimentan uno al otro en una secuencia fija, cada vez que un comerciante manda un mensaje o que corre la revisión diaria de alertas:

**Paso 1.** Llega un mensaje de texto simple ("vendo pescado en Colima") o se dispara la revisión automática del día.

**Paso 2.** El sistema consulta el clima actual y reciente de la zona exacta del comerciante.

**Paso 3.** Con el historial reciente de temperatura, el módulo GARCH (Capítulo Cuatro) proyecta qué tan inestable está el clima ahora mismo.

**Paso 4.** El módulo de Arrhenius (Capítulo Tres) calcula la velocidad de descomposición y la vida de anaquel esperada del producto bajo el clima actual.

**Paso 5.** El optimizador Kelly-Markowitz (Capítulo Cinco) combina ambos resultados —la vida de anaquel y la inestabilidad climática— con el historial de demanda del comerciante, y calcula la cantidad óptima de compra para hoy.

**Paso 6.** Si se está corriendo una revisión de alertas proactivas, el simulador de Monte Carlo (Capítulo Seis) proyecta los siguientes dos días y decide si hay que mandar una advertencia urgente.

**Paso 7.** El sistema redacta la respuesta en español sencillo y la entrega por WhatsApp: cuántos días le va a durar el producto, cuánto comprar hoy, y un consejo práctico para protegerlo.

Todo esto ocurre en segundos, antes de que el comerciante termine de leer la respuesta.

---

## Capítulo Ocho · Ejemplo numérico paso a paso

Para que esto no se quede en teoría bonita, aquí están los cálculos reales que hace el sistema, comparando un día tranquilo contra una ola de calor, para el mismo comerciante de mariscos con la misma mercancía.

### Parámetros del producto (mariscos)

Estos son los valores fijos que usa el sistema para esta categoría, obtenidos de literatura general de cinética de alimentos (ver limitación honesta en el Capítulo Doce):

- Energía de activación $E_a = 65{,}000 \ \text{J/mol}$
- Factor de frecuencia $K_0 = 2.5 \times 10^{10}$
- Coeficiente de humedad $\alpha = 1.2$
- Precio de venta: \$120/kg · Costo de compra: \$70/kg · Valor de salvamento base: \$10/kg
- Demanda histórica promedio del comerciante: 100 kg/día

### Escenario A — Día calmado (24 °C, 55% de humedad)

Metiendo estos números a la ecuación de Arrhenius del Capítulo Tres:

$$K = 0.155 \quad \rightarrow \quad \text{Vida de anaquel} = \frac{1}{0.155} \approx 6.4 \text{ días (≈154 horas)}$$

Con una semana de temperaturas estables (23–24.5 °C), el módulo GARCH proyecta una varianza baja ($\sigma^2 \approx 0.32$). El optimizador de Kelly-Markowitz, combinando esa vida de anaquel larga con clima estable, sugiere comprar:

$$Q^* = 90 \text{ kg}$$

Y el simulador de Monte Carlo a 48 horas proyecta una merma esperada del **26.7%**, con un VaR 95% de **27.8%** y un CVaR 95% de **28.1%** — números todos parecidos entre sí, señal de que no hay sobresaltos esperados.

### Escenario B — Ola de calor (38 °C, 85% de humedad)

Con la misma mercancía, el mismo comerciante, pero con una ola de calor que ha ido subiendo durante la semana (30 °C hasta 38 °C):

$$K = 0.618 \quad \rightarrow \quad \text{Vida de anaquel} = \frac{1}{0.618} \approx 1.6 \text{ días (≈39 horas)}$$

La vida de anaquel se desploma de 154 horas a apenas 39 horas: **una caída de casi el 75%.** El módulo GARCH, al ver una semana completa de temperatura subiendo sin parar, proyecta una varianza mucho más alta ($\sigma^2 \approx 23.97$) — el clima está, en términos del modelo, muy alterado. El optimizador reacciona con fuerza:

$$Q^* = 27 \text{ kg} \quad (\text{70\% menos que en el día calmado})$$

Y el simulador de Monte Carlo a 48 horas ya no proyecta un resultado tranquilo: merma esperada del **71.1%**, VaR 95% de **83.2%** y CVaR 95% de **85.8%**. La distancia entre la merma esperada (71%) y el peor 5% de escenarios (85–86%) le dice al sistema que, si a esto se le suma un mal día de ventas, la pérdida puede ser prácticamente total.

### Lo que el comerciante recibe

En el Escenario B, el mensaje que llegaría al teléfono del comerciante sería algo como:

> *"Hace mucho calor en tu zona. Tu pescado va a durar menos de 2 días en vez de los 6 de un día normal. Te recomendamos comprar solo 27 kg hoy en vez de tus 90 kg de costumbre — el riesgo de que se te eche a perder más de 8 de cada 10 kilos es alto. Guarda el producto en la sombra y con el máximo hielo posible."*

Esa es la diferencia entre un comerciante que compra a ciegas por costumbre y uno que compra sabiendo, con números reales, lo que el clima le va a hacer a su mercancía.

---

## Capítulo Nueve · Cómo está construido

El sistema está separado en tres capas que no se mezclan entre sí, siguiendo un patrón de diseño de software conocido como **arquitectura hexagonal** (o de puertos y adaptadores), propuesto por Alistair Cockburn en 2005.

**Capa 1 — el cerebro matemático.** Contiene únicamente las fórmulas explicadas en los Capítulos Tres a Seis y las reglas que validan que los datos de entrada tengan sentido físico (por ejemplo, que no se le pueda pasar una temperatura o una humedad imposible). Esta capa no sabe nada de WhatsApp, de bases de datos ni de internet — es matemática pura y aislada.

**Capa 2 — el orquestador.** Es la pieza que recibe el mensaje de texto del comerciante, decide en qué orden preguntarle al cerebro matemático, y arma la respuesta final. Es el "gerente" que conecta el cerebro con el mundo exterior.

**Capa 3 — los conectores con el mundo real.** Aquí viven las piezas que hablan con servicios externos: el servicio de clima, el canal de mensajería, el almacenamiento de datos, y el asistente de inteligencia artificial que ayuda a redactar los consejos en lenguaje natural. Si en el futuro cambio de proveedor de clima o de forma de almacenar los datos, solo se toca esta capa — el cerebro matemático no se entera y no hay que volver a probarlo.

Esta separación no es un capricho de "buenas prácticas": significa, en términos prácticos, que las fórmulas de este proyecto ya están probadas de forma aislada (Capítulo Once), sin depender de que el servicio de mensajería o el clima estén funcionando en ese momento.

---

## Capítulo Diez · Cómo se protege

Un sistema pensado para usarse públicamente tiene que asumir que, tarde o temprano, alguien va a intentar romperlo o abusarlo. Estas son las tres defensas principales:

### Validación estricta de todo lo que entra

Cada mensaje que llega se trata como potencialmente hostil hasta que se demuestre lo contrario. El número de teléfono se valida contra el formato internacional oficial (E.164); si el mensaje trae algo que no es un teléfono válido — código, símbolos raros, intentos de manipular el sistema — se rechaza antes de que llegue a tocar cualquier lógica de negocio o cualquier base de datos. Las coordenadas geográficas también se validan contra límites físicos reales del planeta, para evitar errores de cálculo si alguien manda un valor absurdo a propósito.

### Límite de solicitudes (Token Bucket)

Para evitar que alguien sature el sistema con miles de mensajes seguidos —ya sea por error o a propósito—, cada comerciante tiene una cuota de "fichas" de solicitud que se recarga con el tiempo:

$$\text{Fichas nuevas} = \text{Fichas anteriores} + (\text{Segundos transcurridos} \times \text{Tasa de recarga})$$

con una tasa de recarga de una ficha por hora. Si alguien se queda sin fichas, el sistema bloquea la solicitud antes de gastar cuota en servicios externos de clima o de inteligencia artificial.

### Ningún detalle interno se filtra hacia afuera

Si algo falla internamente, el sistema nunca le devuelve al usuario el detalle técnico del error (qué archivo, qué línea, qué consulta de base de datos falló). Guarda esa información de forma interna para que el propio desarrollador pueda revisarla, y hacia el exterior solo responde con un mensaje genérico. Esto evita que un posible atacante use los mensajes de error para entender cómo está armado el sistema por dentro.

### Sobre el canal de mensajería

Merma Cero se entrega a través de WhatsApp, usando un proveedor intermediario de mensajería empresarial (no una relación directa con la empresa dueña de la plataforma). Ese tipo de canales exige, para poder mandar alertas fuera de una conversación ya iniciada, que ciertos mensajes pasen antes por un proceso de aprobación de plantillas — un trámite operativo, no técnico, que se explica con más detalle en el Capítulo Doce.

---

## Capítulo Once · Qué tan probado está esto

Antes de decir que algo "funciona", hay que probarlo, y hay que ser honesto sobre qué tipo de prueba es. Merma Cero cuenta hoy con una batería de **18 pruebas automatizadas, y las 18 pasan**: 13 pruebas unitarias que verifican los casos límite de cada módulo (la velocidad de descomposición escala correctamente con la temperatura, el optimizador reduce la compra sugerida ante clima extremo, el sistema recupera datos aunque la base de datos se corrompa, el límite de solicitudes bloquea correctamente, el sistema sigue funcionando aunque el servicio de clima o de inteligencia artificial fallen), más 5 pruebas que comparan, número por número, que la versión de producción del motor matemático y su versión espejo (usada para validación cruzada) den exactamente el mismo resultado.

Es importante ser preciso sobre qué demuestra esto y qué no: estas pruebas confirman que **el motor hace, en todos los casos que se le ocurrieron a su creador, lo que dice que hace.** No confirman todavía que sus recomendaciones sean mejores que la intuición de un comerciante con años de experiencia en condiciones reales. Esa es una pregunta distinta, y solo la responde un piloto de campo con usuarios reales — algo que este proyecto todavía no ha corrido (Capítulo Doce).

---

## Capítulo Doce · Lo que todavía no sabemos

Prefiero dejar esto anotado con toda claridad a que alguien lo descubra después y piense que se le escondió.

**Los parámetros físicos vienen de literatura general, no de datos propios.** La energía de activación y el factor de frecuencia de cada categoría de producto (Capítulo Ocho) se tomaron de órdenes de magnitud reportados en estudios generales de cinética de degradación de alimentos, no de un experimento propio con el pescado y las flores específicas que se venden en Colima. Es una limitación real: el modelo puede estar sesgado para productos o microclimas particulares hasta que se recalibre con datos de un piloto real.

**El modelo no captura todo lo que el comerciante ya hace por su cuenta.** Usa la temperatura ambiente como referencia principal; no modela de forma explícita el hielo extra, la sombra parcial o la manta húmeda que un vendedor experimentado ya usa por instinto. Es posible que el modelo sea, en algunos casos, más pesimista de lo necesario.

**El riesgo de salud del propio comerciante no está modelado, y ya lo dije en el Capítulo Dos: lo repito aquí porque merece estar en ambos lugares.** El sistema mide el riesgo de la mercancía, no el riesgo de la persona parada bajo el sol vendiéndola.

**Un modelo probabilístico mal comunicado genera falsa confianza.** Por eso el sistema comunica todo como probabilidad ("detectamos 95% de probabilidad de que...") y no como un hecho garantizado — para que el comerciante no pierda la confianza en el sistema la primera vez que una predicción no se cumpla exactamente.

**Hay un pendiente de privacidad concreto, no solo teórico.** Existe ya un marco de principios (minimización de datos, base constitucional) documentado por separado, pero todavía falta un aviso de privacidad formal — que explique con claridad qué datos se recolectan (teléfono, ubicación aproximada de trabajo) y para qué, y cómo alguien puede pedir que se borren — antes de recolectar datos de usuarios reales a gran escala. Es un pendiente identificado y con fecha de resolución planeada, no un vacío ignorado.

**El canal de mensajería puede suspenderse si no se sigue el proceso correcto.** Cualquier canal de mensajería empresarial exige que el usuario haya aceptado explícitamente recibir mensajes (opt-in) antes de mandarle alertas no solicitadas. Sin ese consentimiento explícito documentado, el canal se puede suspender — es un riesgo operativo real, ya identificado, con su propia mitigación planeada.

---

## Capítulo Trece · Cómo se construyó esto

### Cómo se calibraron los modelos matemáticos

Los parámetros de las ecuaciones (Capítulos Tres y Cuatro) se fijaron a partir de órdenes de magnitud de la literatura científica general, no de un ajuste estadístico propio sobre datos de descomposición reales. Fue una decisión consciente: permite tener un sistema funcional ya mismo, en vez de esperar meses a recolectar datos de laboratorio antes de poder ayudar a alguien. La corrección de esta limitación (recalibrar con datos reales de un piloto) ya está planeada, no es una promesa vacía.

### Cómo se construyó el software

Se siguieron tres reglas simples: escribir primero la prueba y después el código que la hace pasar en los módulos más delicados (la cinética de descomposición, el límite de solicitudes, el filtro de volatilidad); separar desde el primer día el cerebro matemático de todo lo demás (Capítulo Nueve), en vez de dejarlo mezclado y arreglarlo después; y construir por capas, probando cada una por separado antes de conectarla con la siguiente.

### Cómo se validó técnicamente lo que existe hoy

Como se explicó en el Capítulo Once, la validación de hoy tiene dos capas: pruebas sobre casos límite, y verificación de que dos implementaciones independientes del mismo motor matemático den resultados idénticos. Esto es distinto de un respaldo estadístico con datos históricos reales de decisiones de comerciantes — esos datos todavía no existen, porque el piloto de campo todavía no arranca.

### Cómo se va a correr el piloto de campo (todavía no ha pasado)

El plan es empezar con mi tío Chucho como usuario número uno, seguido de 5 a 10 comerciantes del mismo tianguis, reclutados por relación de confianza directa. Antes de registrar a nadie, se le va a explicar con claridad qué datos se guardan y para qué (consentimiento informado). Cada predicción se va a guardar junto con una pregunta simple al día siguiente: "¿acertó la predicción de ayer, sí o no?" — ese dato es el que, acumulado durante varias semanas, va a permitir por fin medir si el sistema realmente ayuda o si solo suena bien en teoría. Al no ser un proyecto de una institución académica formal, este piloto no pasa por un comité de ética institucional; el estándar que sí se aplica, y que declaro aquí con toda transparencia, es el de consentimiento informado y minimización de datos.

---

## Capítulo Catorce · Hacia dónde va: reconocimiento y protección del trabajo

### Visión

Que ningún comerciante de la economía popular mexicana pierda dinero por no tener acceso a la misma inteligencia predictiva que usan las grandes cadenas.

### Misión

Construir y sostener un oráculo climático-financiero gratuito o de costo mínimo, que le diga a cada comerciante, en un mensaje sencillo, cuánto comprar hoy, cuánto le va a durar su producto, y cómo protegerlo.

### Lo que busco de aquí en adelante, en orden real de importancia

**Primero, terminar y correr el piloto de campo real** (Capítulo Trece) — sin esto, todo lo demás son planes sobre papel.

**Segundo, buscar reconocimiento institucional serio.** Esto significa presentar el proyecto a distinciones y convocatorias que evalúan impacto social y rigor técnico real (por ejemplo, distintivos de innovación social juvenil), y buscar que profesores o especialistas externos revisen el trabajo y lo validen — no porque yo lo diga, sino porque alguien con criterio independiente lo confirme.

**Tercero, proteger el trabajo de forma responsable — y aquí quiero ser honesto en vez de prometer algo que no puedo garantizar.** Las fórmulas matemáticas de este proyecto (Arrhenius, GARCH, Kelly) son ciencia pública: nadie puede patentar una ecuación que ya existe desde hace más de un siglo. Lo que sí se puede explorar, y lo que pienso investigar con asesoría legal real antes de prometer nada, es: (a) registrar el software específico como obra propia ante el Instituto Nacional del Derecho de Autor, que es un trámite real y accesible; y (b) consultar con un especialista en propiedad industrial si la forma concreta en la que se combinan estos modelos —no las fórmulas en sí— podría calificar para alguna figura de protección más específica. Prometer "vamos a patentar esto" sin haber hablado con un experto sería exactamente el tipo de promesa vacía que este documento trata de evitar en todo lo demás.

**Y, de forma discreta y sin que sea el objetivo central de este documento:** a largo plazo, un proyecto que demuestre impacto real con datos del piloto también abre la puerta, con el tiempo, a algún tipo de apoyo económico responsable (becas, fondos de impacto social, patrocinios) — pero eso viene después de tener resultados reales que mostrar, no antes.

---

## Conclusión

Este proyecto demuestra, de forma verificable hoy, tres cosas: que es posible integrar física de descomposición, econometría de volatilidad y optimización de portafolios en un solo sistema de decisión, entregado sin fricción por un simple mensaje de texto; que ese sistema puede construirse con una arquitectura ordenada y con defensas de seguridad reales, confirmadas por pruebas automatizadas que de verdad pasan, no solo declaradas; y que existe una ruta concreta, con pasos y fechas, para llevar esto de una idea validada técnicamente a una herramienta usada por decenas o cientos de comerciantes reales.

Lo que este proyecto **no** demuestra todavía —y lo digo sin rodeos— es que el sistema mejore las decisiones de un comerciante real más de lo que ya lo hace su propia experiencia. Esa es una pregunta que se responde con datos de campo, no con la elegancia de una ecuación. El día que el piloto corra, esta conclusión se va a volver a escribir con números reales en vez de expectativas.

---

## Anexos

### Anexo A — Glosario ampliado

- **Ecuación de Arrhenius.** Modelo físico-químico de 1889 que describe cómo la velocidad de una reacción (aquí, la descomposición de un alimento) crece de forma exponencial —no lineal— con la temperatura. En términos simples: cada pocos grados de más no suman un poco de descomposición, la multiplican.
- **Energía de activación ($E_a$).** La "barrera" mínima de energía que tiene que superarse para que la descomposición arranque en serio. Productos con energía de activación alta (como los mariscos) aguantan bien hasta cierta temperatura y luego se descomponen muy rápido al pasarla.
- **Factor de frecuencia ($K_0$).** Un número propio de cada tipo de producto que ajusta qué tan seguido "chocan" las moléculas responsables de la descomposición, independientemente de la temperatura.
- **GARCH.** Familia de modelos estadísticos (originalmente de finanzas) que proyectan qué tan violento va a ser el siguiente movimiento de una variable (aquí, la temperatura), basándose en qué tan violentos fueron los movimientos recientes. La idea central: la inestabilidad tiene memoria, no aparece de la nada.
- **Heterocedasticidad condicional.** Término técnico detrás de las siglas de GARCH: significa que la "varianza" (qué tanto se mueve algo) no es constante en el tiempo, sino que depende de las condiciones recientes.
- **Varianza condicional.** La incertidumbre esperada para el siguiente periodo, calculada a partir de la información disponible hasta hoy — no un promedio histórico fijo, sino una proyección que se actualiza todos los días.
- **Criterio de Kelly.** Regla matemática, propuesta en 1956, para decidir cuánto arriesgar en una decisión repetida (aquí, cuánto inventario comprar) de forma que el capital crezca lo más rápido posible sin exponerse a la ruina total.
- **Utilidad media-varianza (Markowitz).** Forma de evaluar una decisión que no solo mira la ganancia promedio esperada, sino que también penaliza qué tan dispersos (riesgosos) son los resultados posibles. Preferir una ganancia más segura sobre una ganancia promedio más alta pero más volátil.
- **Aversión a la ruina.** Distinta de la aversión al riesgo común: no es "no me gusta perder", es "no puedo permitirme perder tanto que ya no pueda seguir operando mañana".
- **Value at Risk (VaR).** El límite de pérdida que, con una probabilidad dada (aquí, 95%), no se espera superar. No es "la peor pérdida posible", es "la pérdida que solo se supera en el peor 5% de los casos".
- **Conditional Value at Risk (CVaR).** El promedio de pérdida dentro de ese peor 5% de casos. Responde una pregunta distinta a la del VaR: no "qué tan mal puede estar la cosa", sino "en promedio, qué tan mal está cuando sí sale mal".
- **Simulación de Monte Carlo.** Técnica que, en vez de calcular un solo resultado esperado, genera miles de futuros posibles al azar (respetando las probabilidades reales del problema) y mide qué tan seguido y qué tan grave es cada tipo de resultado.
- **Arquitectura hexagonal (puertos y adaptadores).** Forma de organizar el código de un sistema para que la lógica central (las matemáticas, en este caso) quede separada de los detalles técnicos externos (bases de datos, servicios de mensajería, APIs), de modo que cambiar uno de esos detalles no obligue a tocar ni volver a probar la lógica central.
- **Token Bucket (cubeta de fichas).** Algoritmo de control de flujo que le da a cada usuario una cuota de "fichas" que se recargan poco a poco con el tiempo, para evitar que alguien sature un sistema con demasiadas solicitudes seguidas.
- **Opt-in.** Consentimiento explícito y activo de una persona antes de empezar a mandarle mensajes o de usar sus datos — lo opuesto a asumir el consentimiento por default.
- **Aviso de privacidad.** Documento legal que explica con claridad qué datos personales se recolectan, para qué se usan, y cómo una persona puede pedir que se corrijan o se eliminen. Es distinto de una simple declaración de principios: tiene requisitos legales específicos.
- **MVP (Producto Mínimo Viable).** La versión más simple de un sistema que ya funciona de principio a fin y se puede probar con usuarios reales, aunque le falten funciones avanzadas.
- **Validación técnica vs. validación de campo.** La validación técnica confirma que el código hace lo que se le programó para hacer, en todos los casos de prueba pensados. La validación de campo confirma que, además, ese comportamiento sirve de algo frente a la realidad y a usuarios reales. Son preguntas distintas, y este proyecto solo puede responder la primera hoy.

### Anexo B — Estado actual del proyecto (checklist honesto)

| Punto | Estado |
|---|---|
| Pruebas automatizadas | 18/18 pasando |
| Arquitectura de tres capas | Implementada y verificada |
| Defensas de seguridad básicas (validación, límite de solicitudes, censura de errores) | Implementadas y verificadas |
| Aviso de privacidad formal | Pendiente |
| Consentimiento explícito (opt-in) en el primer contacto | Pendiente, planeado para el piloto |
| Piloto de campo con usuarios reales | Todavía no ha iniciado |
| Recalibración de parámetros con datos propios | Pendiente, depende del piloto |
| Registro de autoría del software | Pendiente de investigar el trámite exacto |
| Reconocimiento institucional externo | En proceso de identificar convocatorias |

---

## Referencias

1. Arrhenius, Svante (1889). *Über die Reaktionsgeschwindigkeit bei der Inversion von Rohrzucker durch Säuren.* Zeitschrift für Physikalische Chemie, Vol. 4, pp. 226-248. — La publicación original de la ecuación de velocidad de reacción química.
2. Labuza, Theodore P. (1984). *Scientific Evaluation of Today's Shelf Life Technology.* Journal of Food Science, Vol. 49, No. 2, pp. 312-322. — Aplicación de parámetros cinéticos a la vida de anaquel de alimentos.
3. Engle, Robert F. (1982). *Autoregressive Conditional Heteroskedasticity with Estimates of the Variance of United Kingdom Inflation.* Econometrica, Vol. 50, No. 4, pp. 987-1007. — Artículo fundacional de los modelos ARCH (Premio Nobel de Economía).
4. Bollerslev, Tim (1986). *Generalized Autoregressive Conditional Heteroskedasticity.* Journal of Econometrics, Vol. 31, No. 3, pp. 307-327. — Generalización a GARCH.
5. Markowitz, Harry M. (1952). *Portfolio Selection.* The Journal of Finance, Vol. 7, No. 1, pp. 77-91. — Modelo de optimización media-varianza.
6. Kelly, John L. (1956). *A New Interpretation of Information Rate.* Bell System Technical Journal, Vol. 35, No. 4, pp. 917-926. — Criterio de Kelly.
7. Cockburn, Alistair (2005). *Hexagonal Architecture* (patrón de puertos y adaptadores). — Base del diseño de software del Capítulo Nueve.
8. Constitución Política de los Estados Unidos Mexicanos — Artículos 5, 6, 16 y 25 (libertad de comercio, protección de datos personales, rectoría económica).
9. Ley Federal de Protección de Datos Personales en Posesión de los Particulares (México, 2010) — marco legal aplicable al aviso de privacidad pendiente (Capítulo Doce).
10. Organización de las Naciones Unidas — Objetivos de Desarrollo Sostenible, Meta 12.3 (reducción del desperdicio de alimentos).

---

## Reflexión final

A veces, cuando programo de noche y veo las noticias sobre los avances gigantescos de la inteligencia artificial de las grandes empresas, me da un poco de tristeza. Los ingenieros más brillantes de mi generación están optimizando cómo lograr que alguien haga clic en un anuncio de tenis con 0.01% más de probabilidad. ¿Y la señora de las verduras que pierde su mercancía por un calor inesperado? ¿El vendedor de flores que pierde el dinero de la semana porque llovió a cántaros a medio día? Para ellos no hay ingenieros de datos trabajando en su problema.

El día que mi tío Chucho recibió su primer mensaje de prueba y me llamó sorprendido: *"Oye, chamaco, la cajita de mensajes me dijo que hoy comprara solo la mitad de la mojarra porque venía un calorón y el tianguis iba a estar vacío... y de verdad hizo un calor horrible y nadie salió. Me salvaste de perder todo el dinero de la semana"*, entendí algo: saber programar es un superpoder, y los superpoderes no son para presumir en un currículum. Son para usarlos por la gente que se parte el lomo trabajando en la calle.

Tengo 16 años. No tengo un doctorado, ni un equipo de ingenieros, ni el permiso de nadie para intentar esto. Lo que sí tengo es una laptop, ecuaciones que llevan más de un siglo siendo verdad, y la honestidad de reconocer, en este mismo documento, todo lo que todavía no sé si funciona. Espero que eso cuente más que cualquier promesa bonita.
