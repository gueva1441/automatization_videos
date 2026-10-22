# Semillas — estado actual (F8b, 2026-10-22): research arreglado y S2/S3 re-corridas

Arreglos del research (HANDOFF_F8b_F9 §1): la antigüedad se mide por ítem y no por documento; un PDF enlazado tiene
que nombrar el evento; R3 reintenta 2 veces una caída de Pro; R1 reintenta 3 veces y, si Pro no busca, prueba Flash con
búsqueda. S2 y S3 se re-corrieron una vez (research v3 + compuerta, sin escaleta). S1 no se tocó. **No elijo: elige Omar.**
Lo de F8 (primera corrida) queda abajo como historia; los `POOL_GATE_f8.md`, `costo_f8.json` y `run_f8.log` de S2/S3
son de esa corrida.

| | S1 Ycuá Bolaños | S2 Cromañón | S3 Vajont |
|---|---|---|---|
| Compuerta ahora | 🟢 verde (sin cambios) | 🟡 **amarillo** (antes rojo) | 🔴 rojo (antes rojo en 0) |
| datos · citas verificadas · elegibles · eventos con fecha | 214 · 58 · 12 · 49 | **129** · 39 · 5 · 38 | **121** · 9 · **0** · 30 |
| documentos que aportan al pool | 11 | 10 (11 bajados de 13 intentados) | 7 (8 bajados de 19 intentados; 6 en italiano, 2 en inglés) |
| focos de R1 con grounding | — | 3 de 4 (Pro); el 4.º tampoco con Flash | 3 de 4 (Pro); el 4.º tampoco con Flash |
| costo de la re-corrida | — | US$ 0.87 · 16 min | US$ 0.82 · 15 min |

**S2 Cromañón → amarillo (≈ 10 min, 7–8 beats).** Le faltan 21 datos para el verde. Humanos elegibles: Darío Salgado
(bombero a cargo del destacamento; 8 citas), Daniela Sánchez y Christian Romero (sobrevivientes; 4 y 3 citas), Patricio
Martínez (testigo de los recitales previos), María Sol (sobreviviente, testigo en el juicio). Testimonios verificados
fuertes («Tenía un metro y medio de gente arriba mío», Iván; «Sentía en el piso como bultos. Yo sabía conscientemente
que eran chicos», Graciela). Antagonistas con fallo: Chabán, Ibarra, funcionarios de Control Comunal (Fiszbin) y el
subcomisario Díaz (Casación). Esta vez no hubo PDF equivocado ni caída de Pro. Riesgo sensible: MEDIO-ALTO (chicos
aplastados, asfixia): nada de cuerpos, sí zapatillas, humo, la media sombra.

**S3 Vajont → sigue rojo, ahora por una sola métrica: 0 humanos elegibles.** El arreglo de antigüedad funcionó: entraron
documentos de 1971 (la sentencia), 2014–2024 en italiano e inglés, y solo 9 ítems se descartaron por fecha. Pero los
sobrevivientes aparecen con una cita cada uno (Micaela Coletti, presidenta del comité de sobrevivientes: «La sensación
de que la cama cogía velocidad…»; Mauro Corona: «como un millón de camiones que vuelcan un millón de cajas de grava») y
el umbral de elegible pide 3 citas o 3 datos propios. Las fuentes que trajo la búsqueda son institucionales (comisión
de investigación, proceso, ejército de EE. UU.). Qué faltaría: historia oral o libros de testimonios de Longarone/Erto
(no salieron en el grounding). No se reintenta.

**S1 Ycuá Bolaños — sin cambios (verde).** Riesgo para imágenes (m03 §2.3/E): **menores** entre las víctimas y como
testigo (Tatiana Gabaglio tenía 7 años; 23 menciones de hijos, niños o adolescentes). Con las reglas v3, un menor solo
aparece si el pool lo documenta y nunca en daño: preferir sus objetos (zapatos, el carrito, la mochila); ningún cuerpo de
un chico, ni parcialmente oculto; ninguna imagen de un menor como candidata a miniatura.

---

# F8 §3 — Tres semillas por research v3 + compuerta del pool (sin escaleta, guion ni imágenes)

Corridas en paralelo, una vez cada una, sin reintentos (§3). Runner: `lab/hyperframes/f8/f8_semillas.py --seed S#`.
Pools en `data/scripts/_steps/<topic>/` (fuera de git); acá, por semilla: `POOL_GATE.md`, `fuentes.json`,
`manifest.json`, `perfil.json`, `costo.json`, `run.log`. Las tres quedaron en el inbox (`data/selected_seeds.json`); S2 y S3 con la marca `pool_gate` (rojo + motivos), como hace `topic_researcher`.
**No elijo: elige Omar.**

| | S1 Ycuá Bolaños | S2 Cromañón | S3 Vajont |
|---|---|---|---|
| Compuerta | 🟢 verde | 🔴 rojo (solo por datos) | 🔴 rojo (todo en 0) |
| datos · citas verificadas · elegibles · eventos con fecha | 214 · 58 · 12 · 49 | 67 · 30 · 3 · 22 | 0 · 0 · 0 · 0 |
| documentos que aportan ítems al pool | 11 de 12 bajados | 5 de 7 bajados (10 intentados) | 0 de 4 bajados |
| costo medido (cost_tracker) | US$ 1.29 · 20 min | US$ 0.66 · 13 min | US$ 0.33 · 8 min |

## S1 — Ycuá Bolaños, Asunción, 1 de agosto de 2004 · `f8s1-ycua-bolanos` · 🟢 VERDE
1. **Color:** verde con margen en las cuatro métricas (214 datos, 58 citas verificadas literal, 12 elegibles, 49 eventos con fecha; 22 con hora).
2. **Humanos elegibles:** Tatiana Gabaglio (sobreviviente; tenía 7 años y quedó atrapada a las 11:27; 6 citas, 13 datos), Liz Torres (Coordinadora de Víctimas; 9 citas), Digna Cáceres (bioquímica, sobreviviente; 3), Víctor Galeano y Cristian Sosa (sobrevivientes; 3 c/u), Ángela Pujol (madre de dos víctimas; 3), Julia López (familiar; 3), Blas Cristaldo (esposo de una víctima; 2 citas, 7 datos, con su mañana hora por hora desde las 07:00).
3. **Cronología minuto a minuto:** 09:00 fuego en la chimenea del patio de comidas · 11:10 · 11:25 explosión · 11:27 Tatiana atrapada · 14:00 cuerpos en el Tropi Club.
4. **Pico probable:** 11:25, la explosión con la gente intentando salir y los portones cerrados (D88 «Los guardias cerraron los portones»; D91 dos puertas de 2 m donde se pedían 12 m; D94 salidas que abrían hacia adentro).
5. **Contradicción para el cierre:** la pericia (D28, D33) dice que solo 3 puertas estaban cerradas (azotea, mirador, administración) contra los testimonios de portones cerrados por los guardias: el corazón del juicio.
6. **Antagonista:** Juan Pío Paiva (dueño) y sus hijos Víctor Daniel (gerente de salón) y Emiliano (condenado a 10 años); el guardia Daniel Areco. Del lado del Estado: ex intendentes Burt y Riera (habilitación).
7. **Fuentes:** 12 documentos bajados de 20 intentados (11 en español, 1 en inglés; 11 entran al pool): prensa paraguaya de época y de aniversario, pericia, fiscalía. Ninguno en guaraní.
8. **Riesgo de contenido sensible: ALTO.** Menores entre las víctimas y como testigo (Tatiana a los 7 años; 23 menciones de hijos, niños o adolescentes, incluido un intento de suicidio de un chico de 13). Quemaduras, cuerpos identificados en un club deportivo. Para imágenes: objetos (zapatos, carritos, la chimenea), nunca cuerpos de chicos.
9. **Riesgo de canal:** el pool no armó cifras canónicas: la de muertos sale de un solo dato («causó 400 muertes») y hay que fijarla en el guion; nombres reales de condenados vivos (ir con lo que dice el fallo).
10. **Listo para:** escaleta y guion v3 con 12 min (verde).

## S2 — República Cromañón, Buenos Aires, 30 de diciembre de 2004 · `f8s2-cromanon` · 🔴 ROJO (por poco)
1. **Color:** rojo solo por `datos` = 67 (amarillo pide 75, verde 150). Las otras tres pasan el verde: 30 citas verificadas, 3 elegibles, 22 eventos con fecha.
2. **Humanos elegibles:** Darío Salgado (bombero a cargo del destacamento; 6 citas, 5 datos), Eduardo Salinas (escapó del boliche; 3 citas), Alberto Urcullo (padre de María Sol, abogado; 3 datos).
3. **Pico probable:** 23:00, la bengala («tres tiros») contra la media sombra del techo (D31, D47), con 4 de las 6 puertas de emergencia cerradas (D49) y las barras antipánico atadas con alambre (D33).
4. **Antagonista:** Omar Chabán (gerenciador); del Estado, Aníbal Ibarra («Si ustedes me preguntan si esto se pudo haber evitado, yo les digo que sí y me hago cargo», verificada) y el área de Habilitaciones (Calderini, Torres); un subcomisario por coimas.
5. **Qué faltó (no es falta de tema, es la tubería):** (a) R1 sin grounding en 3 de 4 búsquedas (Pro contestó de memoria aun con los 2 reintentos): 10 URLs reales; (b) F05 era un «PDF enlazado» equivocado: R2 bajó el folleto institucional de la editorial Perfil (294 k caracteres, 0 menciones del tema) en lugar de la nota de las pericias; (c) F08 (Clarín 2006) se cayó en R3 por una desconexión de Pro y no se reintentó; (d) F10 (The Guardian) sin copia en Wayback; (e) F03 no nombra el evento al principio y quedó fuera.
6. **Lo que no hay:** la sentencia del juicio ni el informe de la Legislatura (no salieron en el grounding).
7. **Riesgo de contenido sensible: MEDIO-ALTO.** 194 muertos, muchos adolescentes y jóvenes; una zona «plaza blanda para niños» en el primer piso; María Sol Urcullo murió en el Hospital Italiano a las 00:08. Asfixia por humo: imágenes de humo y zapatillas, nunca cuerpos.
8. **Riesgo de canal:** música, banda con nombre (Callejeros) y familias muy activas: tono cuidado.
9. **Si Omar la quiere:** con (b) y (c) arreglados el pool pasaría muy probablemente a amarillo o verde (F05 era la pieza más larga de las pericias). Pero §3 dice no reintentar: queda en el inbox con el motivo.
10. **Listo para:** nada todavía (rojo).

## S3 — Vajont, Italia, 9 de octubre de 1963 · `f8s3-vajont` · 🔴 ROJO (todo en 0)
1. **Color:** rojo con 0 en las cuatro métricas.
2. **Humanos elegibles:** ninguno (no se extrajo nada).
3. **Pico probable (por el tema, no por el pool):** 22:39, la ola sobre Longarone.
4. **Antagonista (por el tema, no por el pool):** la SADE y sus ingenieros (proceso de L'Aquila).
5. **Qué faltó, causa 1 — búsqueda:** R1 sin grounding en 3 de 4 focos: 4 URLs reales (Il Post 2023, TV2000, damsafety.org 2019, Storia e Futuro 2014). La búsqueda en italiano sí se pidió (el `idioma_local` del seed manda; ver DECISIONES D18).
6. **Qué faltó, causa 2 — la regla de antigüedad (hallazgo):** `doc_contamination` descarta todo documento de más de 20 años después del evento. Para 1963, eso es todo lo escrito después de 1983: los 3 documentos bajados (2014, 2019, 2023) quedaron fuera y R3 no leyó nada. La regla sirve para Orleans (2005 + 20 = 2025) y rompe cualquier tema histórico. Propuesta (no aplicada; es research, fuera de F8): medir la antigüedad sobre la fecha de cada ÍTEM (lo que ya hace `contamination`) y no sobre el año del documento, o subir el margen para eventos de más de 40 años.
7. **Qué faltó, causa 3:** F02 (TV2000) es un PDF que no nombra el evento al principio.
8. **Multilingüe:** no se pudo medir: no hubo extracción. `detect_lang` ahora reconoce italiano (antes no estaba).
9. **Riesgo de contenido sensible: ALTO.** ~2,000 muertos, muchos niños de Longarone; cuerpos en el barro.
10. **Listo para:** nada (rojo); vale volver a correrla solo después de cambiar la regla de antigüedad.
