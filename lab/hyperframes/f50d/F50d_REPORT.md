# F50d — Época por tramo en el canon (A, C, B) · **PARADA en B: D no corrió**

Handoff `lab/hyperframes/f50d/HANDOFF_F50d_epoca_por_tramo.md`, md5 `a96dca00e3c5c35b291738281e047156` (verificado). Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Tope US$ 3,00. Gastado **US$ 0,0989**: las 3 llamadas del canon. Cero fotos, cero clips, cero Opus.

**Qué pasó, en llano.**
- El código de A y de B está hecho y probado.
- El canon nuevo (C) **no salió como espera el handoff**: la corrida que queda en producción trae tramos solo hasta 1966, y la ropa de las familias españolas solo para 1962–1971.
- La verificación de B **falló**, porque con el canon rehecho cambian otras partes del bloque del canon, no solo ERA y CLOTHING. Por la regla, PARADA ahí: **D (Opus sobre Wittenoom, ~US$ 2) no se corrió**.
- Aunque B hubiera pasado, con este canon las fotos de 1971–2024 de los caps 5–7 seguirían recibiendo la época 1958-1966.

Lecturas: `CLAUDE.md`, `DECISIONES.md` (hasta 22:30), `lab/ESTADO_SESION.md` (F50c), el handoff, `step_4e_visual_canon.py`, `fase1_5.asegurar_canon`/`_step_cost`, los bloques de canon de `m03_visual.py`, `m03_expediente.bloque`.

## Commits
| parte | commit |
|---|---|
| paso 0 | `8463dfb`: DECISIONES 22:30 tal cual y el handoff. `TOPE_TANDA.json` = `{"usd": 3.0, "desde": "2026-10-28T22:34:32"}` (fuera de git) |
| A + marca | `16eeb84` |
| C | `b3222fb` |
| B | `20b3e8b` |
| reporte | este commit |

En paralelo, el código de B lo hizo un subagente mientras yo hacía A, la marca y C. Cada commit tiene su sticker y `MAPA_PROYECTO --check` con 0 fallas.

## Módulos
| archivo | sticker, hoy | después |
|---|---|---|
| `researcher_steps/step_4e_visual_canon.py` (research) | «Arma el canon visual… people_groups: quiénes son, dónde y cuándo, cómo se ven y cómo se visten» | + `era_visual_canon.periods`, grupos con `clothing_by_period`, `pedido_canon` y `marca_canon` |
| `fase1_5.py` (guion) | «… el canon visual con canon_ficha_md5 en topics_db» | la marca es md5(ficha + pedido + esquema) |
| `script_engine/m03_visual.py` (fase2a) | «… le pide a Claude Opus que llene la ficha…» | el bloque ERA trae los tramos del cap |
| `script_engine/m03_expediente.py` (fase2a) | «… grupos de gente del canon con su aspecto y su ropa» | la ropa va por tramo |

## A. El canon por tramo y la marca (salida)
- **Esquema** (`VISUAL_CANON_SCHEMA_FICHA`):
  - `era_visual_canon.periods` es una lista de `{years, clothing, technology, vehicles_machinery, interiors}`.
  - El grupo cambia `clothing` por `clothing_by_period`, una lista de `{years, clothing}`.
  - Los campos únicos de la época **se quedan**: los leen `m05_judge`, `m06_classifier` y `m03_imagenes_v3`.
  - `_VISUAL_CANON_SCHEMA`, el viejo, queda intacto (lo comprueba un test).
  - `extract_visual_canon` guarda `periods` como lista limpia, porque `_clean_era_canon` solo deja los campos planos.
- **Las 3 líneas del pedido**, tal cual del handoff. Las comprueba `test_f50d_a_las_tres_lineas_del_pedido`:
  - después de `- interiors: …` entra `- periods: una entrada por cada tramo del material en que cambian la ropa, la tecnología, los vehículos o los interiores; years "AAAA-AAAA" y esos 4 campos para ese tramo (EN). Si el tema es de una sola época, una sola entrada.`;
  - `- where_when: dónde y en qué años aparecen, todos los años en que el material los muestra, también décadas después (EN, una frase)`;
  - `- clothing_by_period: una entrada por cada tramo de años en que el material muestra a ese grupo; years "AAAA-AAAA" y clothing: ropa, peinado y accesorios de ESE grupo en ESE tramo, ese clima y esa clase social (EN, una frase)`. La línea vieja de `clothing` ya no está.
- **Marca:** `step_4e.marca_canon(topic, ficha, ficha_bytes)` = md5(ficha + `pedido_canon(...)` + esquema en JSON). `asegurar_canon` la usa con la misma clave `canon_ficha_md5`.
  - Test: una letra de `TEXTO_S5` o un byte de la ficha cambian la marca.
  - `test_module_f50a` se adaptó a la marca nueva.
  - En Wittenoom: `b02aa6f8` → `696c0995`.
- Tests: `test_module_f50d.py` (A: 4 tests) y `test_module_f50a.py` (5), todos verdes.

## C. Varianza del canon (salida, `CANON_VARIANZA.md`)
`canon_varianza.py`: 3 llamadas en paralelo.
- La corrida 1 es `fase1_5.asegurar_canon`: queda en topics_db y en `05_visual_canon.json`.
- Las corridas 2 y 3 son `canon_desde_ficha`, sin guardar.
- El costo de las 3 va en una sola sesión de cost_tracker (`f50d-canon-varianza`): 0,0269 + 0,0325 + 0,0395 = **US$ 0,0989**. Hace falta una sola sesión porque el tracker es único por proceso.
- En `01_v3_costos.json` queda un paso «canon (F50d, 3 corridas en paralelo; la 1 queda)» con ese total.
- Antes de correr guardé una copia del canon: `f50d/antes/topic_wittenoom.json` y `05_visual_canon.json`.

| corrida | grupos | periods | primary_decade · spans |
|---|---:|---|---|
| 1 (producción) | 11 | 1937-1957 · 1958-1966 | 1960s · 1937-2026 |
| 2 | 6 | 1937-1966 · 1966-2026 | 1960s · 1937-2026 |
| 3 | 6 | 1937-1966 · 1978-2026 | 1950s · 1937-2026 |

- Solo `spanish_migrant_families` sale en las 3.
- Su ropa por tramo:
  - corrida 1: 1962-1971;
  - corrida 2: 1958-1971;
  - corrida 3: 1958-1966 · 1971-present.
- Lo que esperaba el analista:
  - un tramo 1937–1966, uno de 1966 a los 90 y uno de los 2000 a 2026;
  - las familias con ropa de 1958–66 y otra para 1985–2023.
- **La corrida 1 no lo cumple:** no tiene ningún tramo después de 1966, y las familias tienen una sola ropa, de 1962-1971.
- La corrida 2 tiene un tramo 1966-2026, pero un solo tramo para las familias. La 3 es la que más se acerca: hasta 2026 y las familias con 1971-present.
- No se forzó: se adoptó la 1, como manda el handoff.
- Flash no siempre respeta `AAAA-AAAA`. Vinieron «1950s-1970s», «2000s-present», «1971-present» y «1979-2000s». B los lee (`_tramo`).

## B. El pedido de m03 por tramo (salida, `PEDIDOS_F50d.md`) → **FALLA: PARADA**
Código (subagente):
- `_format_seedream_canon_block(topic, anios)` imprime, en vez de las 4 líneas únicas, una tanda por cada `period` que cruza los años de las fotos del cap.
  - Formato: cabecera `  period AAAA-AAAA:` y las 4 líneas con la misma alineación.
  - Año de cada foto = `anio_ancla`, si no `respaldo[0]`, del expediente. `_render_prompts_seedream` se los pasa a `_build_seedream_prompt_step2`.
- **Regla cuando ningún tramo cruza** (decisión nuestra, el handoff no la fija): foto por foto, si ninguno cruza su año, entra el más cercano, y en un empate los dos. Un cap sin años legibles recibe todos. Un `years` ilegible no cruza; si ninguno es legible, salen los campos únicos.
- `_tramo` lee un año, una década («1950s» = 1950–1959) y «present/now/today» = año actual.
- Sin `periods` (topic viejo), el bloque sale byte a byte igual que antes (lo comprueba un test).
- `_format_visual_canon_block` está muerto, sin callers: no se tocó. El pedido del movimiento Veo no lleva canon.
- `m03_expediente.bloque`: `CLOTHING: AAAA-AAAA: …; AAAA-AAAA: …` desde `clothing_by_period`. La lectura del `clothing` único del grupo se borró.
- Tests: `test_module_f50d.py` (B: 10), y `test_module_f50c.py` adaptado al formato nuevo.

Pedidos en seco (`pedidos_f50d.py`, la llamada a Opus se corta antes de salir), contra `f50c/pedidos/`:

| cap | años de las fotos | periods que entran | canon nuevo: líneas era / grupo / resto | fuera del canon entero y de los grupos | grupos | código solo (canon de antes): era / grupo / resto |
|---|---|---|---|---:|---:|---|
| 1 | 1961 1962 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |
| 2 | 1961 1962 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |
| 3 | 1943 … 1962 | 1937-1957 · 1958-1966 | 18 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |
| 4 | 1961 1963 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |
| 5 | 1963 … 1993 | **1958-1966** | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |
| 6 | 1988 … 2016 | **1958-1966** | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |
| 7 | 2021 2023 2024 | **1958-1966** | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 |

- **Código solo** (el código de F50d con el canon de antes): el pedido es igual al de F50c salvo las 7 líneas CLOTHING, que pasan a `CLOTHING: -` porque el canon viejo no trae `clothing_by_period`. El código no toca nada más.
- **Canon nuevo** (la comparación del handoff): con el canon que C rehízo cambian, además del bloque ERA y la parte CLOTHING:
  - el resto del bloque del canon (lugar puntual, personas documentadas, anacronismos, objetos), 87 líneas;
  - el resto de las líneas de grupo: los grupos pasan de 7 a 11, con otro `who`, `where_when` y `appearance`.
- Fuera del bloque del canon entero y de las líneas de grupo: **0 líneas** en los 7 caps.
- La verificación del handoff exige que fuera del bloque ERA y de CLOTHING no cambie nada. **No se cumple → PARADA con el diff** (en `PEDIDOS_F50d.md`, por cap y por zona). No la «arreglé» para que dé.
- El handoff ordena C antes de B, y C rehace el canon entero, así que esta verificación no podía pasar con el canon nuevo. Lo dejo para que decidan el analista y Omar.
- **El resultado de fondo tampoco sirve todavía:** en los caps 5, 6 y 7 entra solo `1958-1966`, porque el canon de producción no tiene tramos después de 1966 y la regla elige el más cercano.

## D. No corrió
Por la PARADA de B. No hay papel nuevo, ni medidas 1–4, ni gasto de Opus. `03_visual.json` y el papel de F50b no se tocaron.

## Verificación
| | antes (F50c, `f41/f50c`) | después (`f41/f50d`) |
|---|---|---|
| suite rápida | 55 passed, 3 skipped | 55 passed, 3 skipped |
| suite amplia | 5 failed, 961 passed, 30 skipped | 4 failed, 976 passed, 30 skipped (+14: los de `test_module_f50d.py`) |
| ch02 md5 | `f792f3d4…` | `f792f3d483a1fa42daed5f7f0e054f46` (igual) |

Fallas de la amplia: las 4 de siempre, que ya estaban en F49, F50b y F50c (`gfx_lab::test_cues_sin_escribir_el_proyecto`, `gfx_lab::test_preview_usa_las_plantillas_reales` y `m03_merge_timing` ×2). La intermitente de F50c (`gfx_lab::test_candado_en_el_preview`) esta vez no apareció. También pasaron los tests de m03 y F8 que corrió el subagente (`test_module_m03_*` y `test_module_f8*`: 41 verdes y las 2 de `m03_merge_timing` de siempre).

## Lo que queda abierto
1. **Decisión pendiente (Omar y analista): cómo seguir con el canon.** Opciones que veo, sin elegir:
   - (a) adoptar la corrida 3 (o la 2) en vez de la 1;
   - (b) volver a pedir el canon hasta que traiga tramos después de 1966; cada corrida cuesta ~US$ 0,03;
   - (c) reforzar el texto del pedido (p. ej. pedir un tramo por cada década de las fotos), que es un cambio de regla y va con el simulador.
   - Hoy topics_db tiene la corrida 1.
2. **Decisión pendiente: la verificación de B.** Con el canon rehecho, ¿alcanza «0 líneas fuera del canon entero y de los grupos»? ¿O hay que comparar con otro canon?
3. **La regla de «ningún tramo cruza» (el más cercano) es nuestra:** el handoff no la fija. Con el canon de hoy le da 1958-1966 a fotos de 2024; otra opción sería no imprimir época. Para revisar.
4. **D** queda entera para la próxima tanda: m03 con Opus, el papel nuevo y las 4 medidas, con ~US$ 2,1 del tope sin usar.
5. **Varianza de Flash:** entre corridas, el número de grupos (11 / 6 / 6) y los tramos cambian mucho. Con una sola llamada, el canon de un tema depende de la suerte.
6. **`present` depende de la fecha:** `_tramo` usa el año actual para «present».
7. **Los campos únicos de la época** siguen en el canon y los leen m05, m06 y m03_imagenes_v3. No se migraron a tramos.
8. **El canon de producción cambió (11 grupos) pero `03_visual.json` no.** Las fotos que salgan de él ya no coinciden con el canon de topics_db hasta que corra m03.
9. `data/cost_history.json` no es UTF-8 puro (hay bytes cp1252): ya pasaba antes; `papel.py` lo tolera.
10. Siguen abiertos de F50c (nombres reales por las citas, 2/7, organizaciones en la ficha), de F50b (notas F8 viejas, foto madre en F51) y de F50 (n2, n3, n7, n8, n10, n12). Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
Procesos en segundo plano: el subagente de B (terminó, en dos vueltas), las 3 llamadas de C (terminaron) y `verificar.sh f50d` (exit 0). No quedó nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

La PARADA en B es la lectura correcta. D no debía correr y no corrió. Los tests pasan y el candado de los archivos intocables se sostiene.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 0 | md5 del handoff a96dca00… | OK | `md5sum` coincide |
| 1 | Paso 0: línea de DECISIONES tal cual | OK | `DECISIONES.md`, commit 8463dfb, texto idéntico al handoff. `lab/TOPE_TANDA.json` = 3,00 (sin commitear, como corresponde) |
| 2 | A: esquema (`periods`; `clothing_by_period` reemplaza a `clothing` en el grupo; campos únicos se quedan) | OK | `researcher_steps/step_4e_visual_canon.py`: `_GRUPO_SCHEMA`, `_PERIODO_SCHEMA`, `VISUAL_CANON_SCHEMA_FICHA` |
| 3 | A: las 3 líneas exactas del pedido | OK | `where_when`, `clothing_by_period` y `periods` coinciden carácter por carácter con el handoff. `periods` va tras `interiors`. |
| 4 | Marca = md5(ficha + pedido + esquema), con test | OK | `marca_canon`; `asegurar_canon` la usa (`fase1_5.py`); `test_module_f50d.py`. Corrí `pytest f50d f50a f50c f50b`: 55 passed. |
| 5 | C: 3 corridas en paralelo, corrida 1 vía `asegurar_canon`, las otras 2 no a topics_db | OK | `CANON_VARIANZA.md`; la marca 696c0995 está en topics_db y la copia previa en `antes/`. US$ 0,0989, muy por debajo del tope de 3,00. |
| 6 | C: canon como espera el handoff | NO se cumple, y se reportó | La corrida 1 no tiene tramos después de 1966. `spanish_migrant_families` solo trae 1962-1971, sin ropa de 1985-2023. Las corridas 2 y 3 sí cubren el período tardío. La regla «se reporta, no se fuerza» se respetó. |
| 7 | B: código (bloque ERA por tramos, CLOTHING por tramo, `clothing` único borrado) | OK | `script_engine/m03_visual.py` (`_lineas_epoca`, `_periods_del_cap`); `script_engine/m03_expediente.py:205`, sin lectura de `clothing` único. Sin `periods`, imprime los campos únicos como antes. |
| 8 | B: 7 pedidos en seco y diff contra f50c | OK | Corrí `pedidos_f50d.py`. Salida: "fallas" en los 7 caps, "resto" = 87 líneas por cap. |
| 9 | B: verificación honesta | OK | Con el canon de antes, el código solo da 0 líneas fuera de CLOTHING (14 líneas crudas por cap). Con el canon nuevo cambian además el bloque del canon entero y los grupos (7 → 11), y 0 líneas fuera de eso. El script calcula esa medida aparte y no esconde nada. |
| 10 | PARADA en B, D no corre | OK | El handoff dice «si cambia otra cosa: PARADA», y Omar repitió «PARADA con el diff». |
| 11 | 03_visual.json md5 23a81881… y PAPEL_FOTOS_WITTENOOM.json md5 2eb4000a… sin cambios | OK | `md5sum` coincide con los dos valores |
| 12 | Sticker y MAPA, suites amplia/ch02, REPORT, ESTADO | NO VERIFICABLE | Solo corrí las 4 suites f50. Las suites rápida y amplia, el candado de ch02, `--check 0` y el veredicto pegado en `F50d_REPORT.md` quedan pendientes; en el reporte solo vi el marcador `{{VEREDICTO}}` (línea 141). |

Observaciones:
1. La verificación del handoff dice que solo cambian el bloque ERA y las líneas CLOTHING. Eso es incompatible con rehacer el canon (la marca lo fuerza), porque el canon rehecho cambia otros bloques y los grupos. Es un defecto del handoff, no de CC. Aun así, la PARADA correcta exige que Omar decida si acepta el canon nuevo como «cambio esperado».
2. Los caps 5–7 (fotos de 1971 a 2024) reciben el período 1958-1966, porque el canon de producción no trae tramos posteriores. Es justo el problema que F50d quería arreglar, y con la corrida 1 no queda arreglado.
3. `_tramo` (interpreta «1950s», «present») y el respaldo «el tramo más cercano si ninguno cruza» son diseño de CC; el handoff no los pide. Son razonables y tienen test, pero deben declararse como decisión nueva.
4. Los commits trajeron `canon_varianza.py` y los 7 pedidos de `codigo_solo/`; son entregables de apoyo, no fuera de alcance.

Fuera de alcance: ninguno. Los `M` sin commitear (`diag_234_cap4.py`, `lab/TOPE_TANDA.json`, `lab/hyperframes/f28/a/f28a.log`) ya estaban antes de la tanda.

Riesgos que el contrato no cubre:
- El canon se guardó en producción con la corrida 1, que es la de peor cobertura posterior a 1966. Al rehacerlo, Flash puede dar otra cosa; el handoff no tiene criterio de reintento.
- Con 11 grupos, los 7 pedidos crecen en tamaño y puede cambiar el comportamiento de Opus; D, que lo mediría, no corrió.

### Adenda de CC (después del veredicto)
- **#12:** las suites y el candado estaban corridos antes del veredicto, y sus números están en la tabla «Verificación» (logs en `lab/hyperframes/f41/f50d/`):
  - rápida 55;
  - amplia 976 + las 4 fallas previas;
  - ch02 `f792f3d4…`;
  - `MAPA --check` 0 en cada commit.
  ESTADO se actualiza en el commit de este reporte.
- **Observación 3:** `_tramo` y la regla del más cercano ya figuran como decisión nuestra en «Lo que queda abierto», punto 3.

