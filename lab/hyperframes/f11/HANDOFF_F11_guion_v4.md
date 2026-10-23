# HANDOFF F11 — Guion v4: menos reglas, oficio, reparar por edición

Analista nuevo · 2026-10-23 · Para CC. Base: `b8ff4ef` (rama `f10-integracion-v3`). Rama nueva **`f11-guion-v4`** desde `b8ff4ef`.
Alcance: **SOLO narración.** Nada de imágenes, voz, audio, m03, assemble, fase2a/2b, render, QA Studio ni producción.

## 0. Por qué (validado del disco)
- Hoy un guion v3 pasa por **~43 chequeos duros** (16 en `m01b_guionista.review`, 12 en `m05.cap_review`, 15 en `guion_v3_reglas.review_v3`) + 48 puntos de validación en la escaleta. El prompt del guionista tiene **22 reglas numeradas + 7 de prosa + 10–11 `instrucciones_guionista`** + objetivo de palabras por beat y por párrafo (55–80) + «tiene que sonar literal» en cada dato.
- Las duras de las corridas buenas, clasificadas (`revision_despues` del editor):
  - Orleans F7c-3 (8.5/10): 21 = literal/declarado 7 · largo ±15 % 5 · párrafo sin id 5 · 3-gramas 2 · otras 2.
  - Ycuá v1 (8/10): 20 = literal/declarado 6 · largo 3 · párrafo sin id 3 · comillas 2 · otras 6.
  - Ycuá ajuste: 26, con cap 3 vacío (beats 4–5 salteados).
  - **≈ 70 % son contabilidad de ids y largo: no se oyen.** Con los 5 bloqueantes de abajo, la v1 de Ycuá tendría 0–3.
- El bucle: `write()` reintenta el texto COMPLETO con hasta 25 duras como feedback; `best_of` elige el que rompe menos; el editor se rechaza si sube el conteo. Se optimiza el conteo, no el texto.
- Reglas sobreajustadas al tema: rol solo preso/guardia (Orleans); `replace_repeated_dates` con «1 de agosto»/«ese domingo» por defecto (Ycuá); lista de juicios con «milagro», «masacre»; y las `instrucciones_guionista` de Ycuá (un incendio de supermercado) dicen «un preso», «una guardia». Además le piden decir **sin nombre** a Q20 de **Liz Torres, que es el humano**.

## 1. Diseño v4 (no se agrega NINGUNA regla; todo lo que decide sale de funciones existentes)
**1.1 Guionista: una llamada (Pro), sin best-of, sin bucle de feedback.** Prompt corto:
- Encabezado: tema, humano (nombre y rol), promesa del gancho, pico, cierre humano.
- Escaleta por cap: palabras objetivo **del cap** (no por beat ni por párrafo); por beat: función, emoción, imagen sensorial, dato central, apoyos, «queda abierta», cierre. El cliffhanger va como dato del último beat, no como regla.
- Línea de cada dato = texto + fecha + marca **como dato** (no como orden): `VERIFICADA` / `SIN VERIFICAR (sin nombre)` / `PANTALLA (no va en la voz)` / `CIFRA OFICIAL`. Sin «tiene que sonar literal». La cita: solo el fragmento.
- **Sin** `instrucciones_guionista` como lista (su contenido ya vive en las marcas). Excepción: si el autor de una cita SIN VERIFICAR es el humano de la escaleta, NO se marca «sin nombre»; se reporta en §4.
- **Oficio, 8 líneas exactas:** (1) gancho = la imagen del beat 1 y después la promesa; (2) seguimos a un humano con nombre; (3) frases cortas antes del golpe; (4) cita literal, ≤ 25 palabras, con quién la dijo; (5) el narrador no habla del video; (6) hechos, citas y preguntas, no juicios; (7) la fecha completa una vez, después «ese día / esa noche»; (8) la última frase es una cita o una pregunta.
- Sistema: el `SYSTEM` actual de m01b (está bien escrito). Esquema de salida: `{"parrafos": [{"beat", "texto"}]}` — **sin `ids_usados`**: los ids se calculan después con `m05.used_items(texto, pool, hard=False)` para el contrato (m03/gfx los leen).
- Reportá tokens del prompt v4 contra v3.

**1.2 Bloqueantes (los únicos que frenan; nada más rechaza, ni se le devuelve al modelo):**
| # | bloqueante | función existente |
|---|---|---|
| a | cifra o cita no respaldada por el pool | `m05.invented_numbers` (con `verified_facts`) + `m05.false_quotes` |
| b | rol de persona incorrecto | `guion_v3_reglas.role_problems` (limitado a preso/guardia: declararlo) |
| c | estructura: beat faltante, cap vacío, cap fuera de ±25 % de su objetivo, video > `max_words` | lógica de `review` (beats/vacío/largo con 0.75/1.25) |
| d | contaminación (otro evento/lugar) | `m05.contamination` |
| e | cita SIN VERIFICAR con el nombre del autor | el bloque de `review` (sin la excepción del humano: §1.1) |
Implementación: `script_engine/guion_v4.py::bloqueantes(topic, esc, parrafos) -> list[dict]` (código, cap, beat, frase, motivo). Sin regex nuevas.

**1.3 Reparación por edición (máx. UNA ronda; nunca se vuelve a llamar al guionista completo):**
- (c) beat faltante / cap vacío / corto → `m01d.regenerate_cap_v3` SOLO de ese cap, notas = solo el texto del bloqueante, `permitidos` = ids de los beats del cap. 1 intento.
- (a)(b)(d)(e) → edición sobre la oración (patrón de `m01d.cut_phrases`, guardia léxica de m01c): sacar o corregir esa frase, nada más.
- Después: una pasada del editor m01c existente con sus blandas (eco, juicios de lista, cierre), pero el criterio de aceptación por párrafo pasa a ser **«no sube `bloqueantes` + guardia léxica»** (no el conteo de duras).
- Fechas repetidas: `replace_repeated_dates` generalizado — `day`/`year` desde la fecha del evento central del pool y «ese <día de la semana>» calculado con `datetime` (sin «domingo» fijo). Determinista.
- Si después de la ronda quedan bloqueantes: **no hay segunda ronda**: se reporta y PARADA.

**1.4 Métricas (en el reporte, nunca rechazan):** todo lo demás de `review` + `review_v3` + `cap_review` se corre y se muestra tal cual (densidad, adjetivos, 3-gramas, frases > 30, frase corta por beat, fechas por cap, juicios de lista, tráiler, fotos, eco, cliffhanger, humano en ≥ 3 caps, nombre completo, ancla del gancho, párrafo sin id, ids declarados), con conteo «duras v3 re-medidas» para comparar.

**1.5 Cableado:** `fase1_5 --v3 --guion v4` (o `topic["guion_version"] == 4`) → m01b = `guion_v4.write` → reparación → `m01d.particionar` → juez. **El camino v3 queda byte-idéntico** (test que lo pruebe con un `call` falso).

## 2. Prueba de convergencia (obligatoria, sin notas ni parches)
- Escaletas fijas, las de las versiones buenas, para aislar el guionista (no se llama a la escaleta):
  - Orleans `ba6c3cac-f7r3`: `01a_escaleta.json` (md5 `2f794418…`, = F7c-3, 8 beats, humano Reed).
  - Ycuá `f8s1-ycua-bolanos`: `01a_escaleta_v1.json` (md5 `e1ba1a48…`, 12 beats, Liz Torres). **No** la del ajuste.
- **Dos corridas independientes por tema** (A y B) para medir la lotería: 4 corridas. Sin `escaleta_notas`, sin notas del analista.
- Salidas con sufijo `_v4A` / `_v4B` en `_steps/<topic>/` y en `lab/hyperframes/f11/`; **no** pisar `_v1`, `_ajuste`, ni los archivos vigentes de F7c-3; no escribir en `topics_db`.
- `NARRACION_<topic>_v4A.md` / `_v4B.md` (texto limpio por cap, como `NARRACION_ycua_v1.md`).
- **`lab/hyperframes/f11/compara_v3_v4.html`** (autocontenida, legible en el teléfono):
  - Dos secciones: Orleans (v3 = F7c-3) y Ycuá (v3 = v1).
  - Por cap, una fila con 2 columnas de texto: **v3 actual | v4 A**; al lado de cada texto: palabras/objetivo, bloqueantes (con la frase marcada) y métricas.
  - Arriba, tabla resumen por versión: bloqueantes (v3 re-medida con §1.2 también), duras v3 re-medidas, palabras, citas, humano por nombre en N caps, cierre (cita/pregunta), costo.
  - v4 B: solo en la tabla resumen + un desplegable con su texto.
  - Marcado en color de las frases con fecha repetida, juicio de lista, eco, tráiler (para que se vean sin leer el JSON).
- Copia del html y de los `.md` en `lab/hyperframes/f11/`.

**Criterio (lo mide el reporte; decide Omar con el analista):** bloqueantes finales 0–2 en las 4 corridas, ningún cap vacío, A y B sin diferencia de bloqueantes > 2. La nota de lectura la da el analista.

## 3. Frenos
- Solo narración. Prohibido tocar: `m01a_escaleta.py`, `researcher_steps/*`, `evidence.py`, `m05_narrative.py`, `guion_v3_reglas.py` (solo importar; el cambio de `replace_repeated_dates` va como función nueva en `guion_v4.py`), `m02_5`, `tts_*`, `m03*`, `m07`, `fase2a/2b`, `gfx_*`, `config.py`.
- **Cero reglas nuevas**: ninguna regex ni lista nueva que rechace. Si algo falta, se anota en §4 del reporte, no se programa.
- No commitear los modificados de siempre (`diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json`) ni `topics_db_pre_f7b.json`.
- **Tope de costo US$ 2.00** para toda la tanda (4 corridas + reparaciones + juez). Si se pasa, PARADA.
- No correr `f10_quirurgico_ycua.py`. Sin merge a `main`.
- Tests: `test_module_f11.py` (bloqueantes con casos de las corridas guardadas, v3 byte-idéntico, reparación sin segunda ronda). Suites existentes verdes + las 5 fallas previas.
- `lab/ESTADO_SESION.md`: actualizar (el encabezado todavía dice rama `f6-guion-v3`; corregirlo).

## 4. Reporte `lab/hyperframes/f11/F11_REPORT.md`
1. Tokens del prompt v3 vs v4; costo por corrida.
2. Tabla resumen (la del html).
3. Qué reparó la ronda única (por bloqueante: antes → después) y qué quedó.
4. Lo que el v4 no ve y v3 sí (honesto), y el caso Q20/Liz Torres.
5. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista lee los guiones v4 del disco y le da a Omar nota 1–10 y comparación contra v3 antes de que Omar los lea. Nada de producción.
