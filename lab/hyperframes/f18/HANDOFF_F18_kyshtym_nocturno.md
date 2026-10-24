# HANDOFF F18 — Kyshtym / Mayak: la cadena completa en un tema de Omar, sin paradas

Analista · 2026-10-24 · Para CC, en la **misma sesión de F17** (ya tiene el contexto). Base: el trabajo de F17 sin commitear (sobre `fceeee3`, rama `f11-guion-v4`). **Omar duerme: esta tanda corre sin paradas intermedias.** Las decisiones que normalmente le tocan a él las toma el analista por adelantado (abajo) y lo que no está cubierto se decide con la opción más conservadora y se anota.

## 0. Por qué
- Ycuá no salió de la lista de Omar: fue una semilla técnica de F8 (la única verde de tres) y nadie la eligió. Es un tema ajeno al canal (asilos, bases, lugares secretos) y con menores entre las víctimas.
- Omar eligió de su inbox **Kyshtym / Mayak (1957)**: `seed_id b6b84f96-03b7-40cd-8173-414d60514c76`, juez «oro», viral en inglés con 943 k vistas, competencia en español «VACÍO».
- La cadena nueva ya existe entera: research v3 → compuerta → ficha v2 → columna → escaleta v2 → guion v5.1. Es la primera vez que corre completa en un tema nuevo, sin ejemplos de ese tema en los prompts. **Esta es la prueba real.**

## 1. Antes de empezar (cierre de F17)
1. Commiteá F17 como está (código, tests, columna v1 de Ycuá, limpieza de cost_history), con su reporte corto y el veredicto del revisor que ya tenés. Ycuá queda en PARADA 1 para siempre; no se regenera su columna ni se corre nada más de Ycuá. Anotalo en ESTADO_SESION.
2. Semilla: tomá el seed de `data/selected_seeds.json` tal cual y creá el topic por el camino normal (`run_seed`, como en F8 con `f8_semillas.py --seed`), con id `f18-kyshtym-mayak`. Idioma local del research: **ruso** además de inglés y español (documentos desclasificados, prensa rusa, informes del IAEA/OIEA y de la CIA).

## 2. La cadena, sin paradas
| paso | qué | tope |
|---|---|---|
| 1 | Research v3 completo + compuerta (`pool_gate`) | US$ 3.00 |
| 2 | Ficha v2 (prompt de F15, chequeo con los aflojes de F15b) | US$ 0.60 |
| 3 | Columna (prompt F17). **Sin notas.** Una llamada + una regeneración si falla el chequeo | US$ 0.30 |
| 4 | Escaleta v2 con columna (F17); 13 bloqueantes; una regeneración | US$ 0.60 |
| 5 | Guion v5.1 (Sol high) | US$ 0.30 |
| **total** | | **US$ 5.00** |

**Decisiones tomadas por adelantado (para que no pares):**
- **Compuerta amarilla:** seguís igual (la cadena ya corrió con amarillo en F8b). **Compuerta roja:** PARADA, con el `POOL_GATE.md` y las causas (como en F8 S2/S3); no reintentes el research más de **una** vez, y solo si la causa es de descarga (documento que no bajó), no de falta de fuentes.
- **La columna no se le muestra a nadie:** se corre, se guarda `COLUMNA_kyshtym.md`, y sigue. El analista la lee después.
- **Humano:** el que la columna elija. Si la ficha no trae ningún candidato con arco, la columna puede proponer un humano colectivo (los evacuados de un pueblo, los liquidadores) y lo anota.
- **Si el pool trae pocas citas verificadas** (tema soviético de 1957, muchas fuentes son documentos y no testimonios), es normal: no se reintenta por eso. Se reporta la cifra.
- **Sin Orleans ni Ycuá** en esta tanda. Un solo tema.

## 3. Salidas
- `lab/hyperframes/f18/`: `POOL_GATE.md`, `FICHA_kyshtym.md`, `COLUMNA_kyshtym.md`, `ESCALETA_kyshtym.md`, **`NARRACION_kyshtym_f18.md`**, prompts con md5, `costos_f18.json`.
- `compara_f18.html`: no hay versión anterior que comparar; en su lugar, una página con el **embudo** (documentos → ítems del pool → ficha → columna → escaleta → guion), la columna, y el guion por cap con bloqueantes, personas con nombre, escenas usadas y frases marcadas. Legible en el teléfono.
- `F18_REPORT.md`: embudo en números; compuerta y causas; humano y pico elegidos; qué quedó afuera; costo por paso; lo que falló y cómo se resolvió; veredicto íntegro del revisor-handoff.

## 4. Frenos
- Cero reglas nuevas en ficha, columna, escaleta o guion. Si algo del tema nuevo rompe un chequeo que para Ycuá/Orleans no se rompía (por ejemplo, nombres rusos, fechas sin día, cifras en curies), **no lo arregles con una regla**: anotalo en el reporte y seguí con lo que pasó. Lo único permitido es un afloje de formato del mismo tipo que los de F15b (lectura de ids, normalización de cifras), declarado.
- No tocar `config.py`, `topics_db` salvo el topic nuevo, `m03*`, `gfx_*`, voz, producción.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests: solo los que ya existen deben seguir verdes (+ las 5 previas). Esta tanda no agrega código, así que no debería agregar tests; si agregaste un afloje, su test.
- Si el tope total se pasa, PARADA donde esté, con lo que haya, y el reporte.
- Actualizar `lab/ESTADO_SESION.md` al final, con el estado exacto para que Omar lo lea al despertar.

## 5. PARADA (única, al final)
Commit + reporte → PARADA. El analista revisa el diff (que no haya reglas nuevas), lee la ficha, la columna, la escaleta y el guion, y le da a Omar la nota y la decisión: si Kyshtym da ≥ 8, producción.
