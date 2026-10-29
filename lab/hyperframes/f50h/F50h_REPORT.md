# F50h — Prueba L contra C del prompt de foto (lab) · etapas 0 y 1 · PARADA

Handoff `lab/hyperframes/f50h/HANDOFF_F50h_prueba_L_contra_C.md`, **md5 `897bc08a1d01ec8c245bf91dde8c4835`** (verificado). Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`.
- Producción no se tocó: ni `script_engine/`, ni `03_visual.json`, ni topics_db.
- **US$ 0:** ni fal ni modelos.
- Por pedido de Omar se hicieron **solo las etapas 0 y 1**. Las etapas 2 (fotos) y 3 (hojas y visión) esperan su OK.

## Qué pasó, en llano
- Están en texto los 3 armados de las 20 fotos de la prueba:
  - **L**, el prompt de hoy;
  - **C**, el corto en el orden de la guía de fal;
  - **C+ép**, el corto con el estilo «como una foto real de ese año».
- C queda ~22 % más corto que L (mediana 131 contra 167,5 palabras) y con menos oraciones (9 contra 13).
- C sigue lejos de las 2–4 oraciones de la guía de fal, como anticipó el analista: lo largo son los casilleros de Opus que se conservan.
- Antes de gastar en fotos, el analista revisa los 60 en texto y Omar da el OK.

## Commits
| etapa | commit |
|---|---|
| 0 | `de7f3e8` |
| 1 | `d218880` |
| reporte y ESTADO | este commit |

## Etapa 0
- md5 del handoff: `897bc08a1d01ec8c245bf91dde8c4835`.
- `DECISIONES.md`, al final y tal cual: se comprobó con código que el texto, entre las comillas invertidas del handoff, está idéntico.

  «- 2026-10-29 02:03 · **F50h:** prueba L contra C del prompt de foto en lab (20 fotos de Wittenoom × 3 armados × 2 fotos, Seedream 5.0 Lite, tope US$ 5): L = armar de hoy con aspecto; C = mismos casilleros sin mirada/objeto/paleta ni STYLE_TAIL, en el orden de la guía de fal con una oración de estilo en prosa de igual contenido; C+ép = C con estilo «como una foto real de ese año». Hoja ciega para Omar y puntaje por elemento con Gemini Flash; gana la que Omar elige en más fotos (empate → visión). Si gana C+ép, el estilo por época queda como decisión aparte (2026-10-28 10:34) · Omar · F50h»

## Etapa 1 — los 60 prompts en texto (US$ 0)
`lab/hyperframes/f50h/f50h.py --prompts` produce `PROMPTS_F50h.json` y `PROMPTS_F50h.md`.

**Cómo se arma:**
- **Fotos:** las 20 del handoff.
- **Casilleros y año:** el `raw_llm_prompt` y el `anio` del 03_visual.json vivo, leídos con `f50g/rearmar.fotos`.
- **Grupos:** los `people_groups` del topic.
- **L:** el `prompt` del papel de F50g.
- **C:** toma de `m03_imagenes_v3.armar(slots, anio, grupos)` las partes que comparte con L: sujeto y acción, aspecto, lugar y año, cartel, plano y cierre. Por eso tiene las mismas reglas de lugar y año, plano y cartel, y el `_sin_negadas` sobre los casilleros. Las junta en el orden del handoff:

  sujeto + acción → aspecto → lugar + año → cartel → luz → plano → estilo → cierre

  La luz es `oracion(_sin_negadas(lighting))`, sin `color_palette`. No entran mirada, objeto, paleta, `style_head` ni `STYLE_TAIL`. El estilo es la oración del handoff con `{anio}`.
- **C+ép:** igual que C, con la oración de estilo de C+ép.
- **Post-proceso, igual que L:** `f8_backstop` (con la escala del beat y `documented_people`) y `_sacar_frases_con_texto`.

Salida pegada:
```
L = guardado 20/20 · palabras mediana {'L': 167.5, 'C': 131.0, 'C+ép': 139.0} · máx {'L': 273, 'C': 196, 'C+ép': 204} · oraciones mediana {'L': 13.0, 'C': 9.0, 'C+ép': 9.0}
```

**Verificación L = guardado: 20/20.** En las 20 fotos, el `prompt` del papel de F50g es igual a `rearmar_una(..., grupos)` y al `prompt` del 03_visual.json vivo.

| | L | C | C+ép |
|---|---:|---:|---:|
| palabras, mediana | 167.5 | 131.0 | 139.0 |
| palabras, mín · máx | 115 · 273 | 87 · 196 | 95 · 204 |
| oraciones, mediana | 13 | 9 | 9 |

Coincide con la simulación del analista: L con mediana 167,5 y máximo 273; C con mediana 131 y máximo 196, de 8 a 10 oraciones. La 1/2 en C da 159 palabras, igual que su ejemplo, y el texto también coincide. La simulación no tenía el post-proceso F8. Lo medí: en las 20 fotos, `f8_backstop` + `_sacar_frases_con_texto` no cambian ni una palabra de C ni de C+ép.

Por foto (palabras y oraciones, L · C · C+ép):

| foto | año | plano | grupos | cartel | palabras | oraciones |
|---|---|---|---|---|---|---|
| 1/2 | 1962 | wide | spanish_migrant_families | — | 209 · 159 · 167 | 13 · 9 · 9 |
| 1/3 | 1962 | medium | spanish_migrant_families, mine_and_mill_workers | — | 206 · 162 · 170 | 14 · 10 · 10 |
| 1/4 | 1962 | extreme_wide | — | WITTENOOM | 161 · 115 · 123 | 12 · 8 · 8 |
| 2/9 | 1962 | medium | spanish_migrant_families | — | 170 · 132 · 140 | 13 · 9 · 9 |
| 2/11 | 1962 | extreme_wide | — | — | 130 · 93 · 101 | 12 · 8 · 8 |
| 2/15 | 1962 | detail | mine_and_mill_workers | — | 157 · 127 · 135 | 13 · 9 · 9 |
| 3/3 | 1943 | wide | company_managers, prospectors_mine_owners | AUSTRALIAN BLUE ASBESTOS | 205 · 160 · 168 | 14 · 10 · 10 |
| 3/6 | 1948 | medium | mine_and_health_officials, company_managers | — | 192 · 149 · 157 | 14 · 10 · 10 |
| 3/10 | 1957 | medium | mine_and_mill_workers | — | 200 · 152 · 160 | 13 · 9 · 9 |
| 4/1 | 1963 | wide | town_children | — | 168 · 130 · 138 | 13 · 9 · 9 |
| 4/11 | 1963 | close | spanish_migrant_families | — | 155 · 124 · 132 | 13 · 9 · 9 |
| 4/12 | 1963 | detail | spanish_migrant_families | 7 July 1963 | 170 · 138 · 146 | 13 · 9 · 9 |
| 5/1 | 1966 | detail | — | MINE TO CLOSE | 164 · 115 · 123 | 12 · 8 · 8 |
| 5/8 | 1985 | medium | airport_police, spanish_migrant_families | — | 174 · 143 · 151 | 13 · 9 · 9 |
| 5/13 | 1991 | wide | spanish_migrant_families | — | 167 · 136 · 144 | 13 · 9 · 9 |
| 5/16 | 2023 | close | spanish_migrant_families | — | 273 · 196 · 204 | 13 · 9 · 9 |
| 6/5 | 2024 | medium | spanish_migrant_families | — | 158 · 128 · 136 | 13 · 9 · 9 |
| 6/15 | 2016 | detail | — | CABINET IN CONFIDENCE | 115 · 87 · 95 | 12 · 8 · 8 |
| 7/7 | 2023 | wide | banjima_traditional_owners | — | 157 · 128 · 136 | 13 · 9 · 9 |
| 7/9 | 2023 | medium | banjima_traditional_owners | — | 167 · 127 · 135 | 13 · 9 · 9 |

Los prompts enteros de 1/2, 3/3 y 7/7 (L, C y C+ép) están en `PROMPTS_F50h.md`. Las 60 versiones están en `PROMPTS_F50h.json`.

C de la 1/2, como muestra:
```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## Verificación
| | antes (F50g-A, `f41/f50g`) | después (`f41/f50h`) |
|---|---|---|
| suite rápida | 55 passed, 3 skipped | 55 passed, 3 skipped |
| suite amplia | 4 failed, 991 passed | 4 failed, 991 passed (las 4 de siempre) |
| ch02 md5 | `f792f3d4…` | `f792f3d483a1fa42daed5f7f0e054f46` (igual) |

No se tocó ningún archivo de producción, así que `MAPA_PROYECTO` no cambia.

## Lo que queda abierto
1. **Etapas 2 y 3, a la espera del OK de Omar:**
   - 60 llamadas a Seedream 5.0 Lite con `num_images` 2 (120 fotos, ≤ US$ 4,20);
   - las hojas ciegas;
   - la visión con Gemini Flash (≤ US$ 0,30).
   - En `f50h.py` solo está `--prompts`. Las otras entradas (`--fotos`, `--hojas`, `--vision`, `--tabla`) se escriben con el OK.
2. **C no llega a la guía de fal** (2–4 oraciones). Queda en 8–10, porque conserva tal cual el sujeto, la acción, el aspecto y el lugar de Opus. La prueba mide si igual rinde mejor que L.
3. **Repeticiones que C conserva:**
   - en la 1/2, el sujeto dice «olive-skinned» y el aspecto «olive to light skin»;
   - en la 3/3, «of British descent» va en el sujeto y en las 2 oraciones de aspecto.

   Sacarlas es otra variable.
4. **C+ép solo cambia la oración de estilo** (+8 palabras). Si gana, el estilo por época queda como decisión aparte (DECISIONES 2026-10-28 10:34).
5. **La lista de 20 deja afuera** la 6/3 y la 7/11 (bug «Court», F50g-B) y los cuadros Veo 1/1 y 7/1. Lo fija el handoff.
6. **Condición para la etapa 2:** `armar_c` reusa las partes de `armar`. Si F50g-B o F51 cambian `armar` antes, hay que volver a correr `--prompts` y confirmar L = guardado antes de gastar.
7. **De tandas anteriores:**
   - F50g-B: el bug «Court», el corte Veo y `anio_final`;
   - la foto madre en F51;
   - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
`verificar.sh f50h` corrió en primer plano. No se lanzaron subagentes: era un solo script chico, con su verificación automática. No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE (etapas 0 y 1)

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 del handoff = 897bc08a… | OK | `md5sum` da 897bc08a1d01ec8c245bf91dde8c4835; el REPORT lo registra |
| 2 | Etapa 0: línea de DECISIONES tal cual, al final | OK | Comparación por código: la línea sacada del handoff == última línea de DECISIONES.md (True). El commit de1f3e8/de7f3e8 agrega solo esa línea |
| 3 | C en el orden de la spec (8 partes) | OK | f50h.py:52-55: sujeto(subject+action) → aspecto → lugar_anio → texto(cartel) → luz → tecnica → estilo → cierre. Coincide con handoff partes 1 a 8 |
| 4 | Reutilizar `armar` es fiel a «la misma regla que armar» | OK | Llama a `v3.armar(slots, anio, grupos)["partes"]` (m03_imagenes_v3.py:626-655) y toma las mismas partes que L. Es la regla misma, no una copia, y `_sin_negadas` ya viene aplicado a los casilleros de prosa. Se descartan mirada, objeto y estilo (style_head+STYLE_TAIL) |
| 5 | Luz sin color_palette y con `_sin_negadas` | OK | f50h.py:52 `oracion(_sin_negadas(lighting))`, sin palette |
| 6 | No entran gaze, props, palette, style_head, STYLE_TAIL | OK | No están en la lista de `partes` de `armar_c` |
| 7 | Mismo post-proceso que L | OK | `post()` f50h.py:58-65 = `f8_backstop` + `_sacar_frases_con_texto`, con escala y `documented` del topic, como `rearmar_una` |
| 8 | C+ép = C con la oración de estilo cambiada | OK | `ESTILO_EP` (f50h.py:36) es la oración del handoff literal; solo cambia el parámetro `estilo` |
| 9 | L = guardado 20/20 | OK | f50h.py:87-89 compara el `prompt` del papel con `rearmar_una(..., grupos)` y con el 03_visual vivo. Corrí `--prompts`: «L = guardado 20/20». Es una verificación doble |
| 10 | Números en el código | OK | Solo la lista de 20 fotos y las 2 oraciones de estilo, ambas del handoff. No hay cortes propios. «2–4 oraciones» aparece en el .md solo como referencia, como pide el handoff |
| 11 | Producción intacta | OK | `git diff 244089b..HEAD --stat` toca DECISIONES.md, el handoff, PROMPTS_F50h.json/.md y f50h.py. Nada de script_engine, 03_visual ni topics_db |
| 12 | Sin llamadas a APIs (US$ 0) | OK | f50h.py importa solo `m03_imagenes_v3`, `m03_visual`, `topics_db` y `rearmar`, y no usa fal ni modelos. El .md y el REPORT declaran US$ 0 |
| 13 | Nada de etapas 2 y 3 | OK | `main()` solo implementa `--prompts`; el resto imprime «esperan el OK». No hay fotos, llave ni hojas |
| 14 | El .md trae lo pedido | OK | PROMPTS_F50h.md tiene la tabla por foto (20 filas con palabras y oraciones de L, C y C+ép), el resumen de mediana, mín y máx, los 3 prompts enteros de 1/2, 3/3 y 7/7, y la verificación 20/20 |
| 15 | Determinismo | OK | Reejecuté `--prompts` y PROMPTS_F50h.json/.md quedaron idénticos byte a byte (`cmp`) |
| 16 | Medidas | OK | L mediana 167,5 y máx 273; C mediana 131 y máx 196; 8 a 10 oraciones. Todo coincide con la simulación del analista |

Observaciones (no cambian el veredicto):
- F50h_REPORT.md tiene el marcador {{VEREDICTO}} sin completar, y ESTADO_SESION no está actualizado. Ambos quedan para después de este veredicto.
- La suite rápida y el candado ch02 no los corrí; el handoff dice que no deberían moverse porque no hay cambios de producción. NO VERIFICABLE por mí.
- El REPORT dice que F8 no cambió nada medible en estas 20 fotos. No lo verifiqué: no comparé el prompt con y sin F8.

Fuera de alcance: ninguno en los commits de(7f3e8 y d218880). Los modificados sin commitear (diag_234_cap4.py, lab/TOPE_TANDA.json, f28a.log) vienen del estado previo. Sin commitear de esta tanda: F50h_REPORT.md y lab/hyperframes/f41/f50h/ (logs).

Riesgos que el contrato no cubre:
- C sigue en mediana 131 palabras y 9 oraciones, lejos de las 2–4 oraciones de la guía de fal. La prueba mide ese caso, pero no una versión de verdad corta.
- `armar_c` depende de las claves internas de `armar()["partes"]`. Si F50g-B o F51 cambian `armar`, esta prueba deja de ser reproducible.

### Adenda de CC (después del veredicto)
- **El post-proceso F8 en C:** lo medí antes del veredicto, con un script en seco. Para cada una de las 20 fotos comparé `armar_c(...)` contra `post(armar_c(...))`, en C y en C+ép, y no hubo ninguna diferencia (lista vacía). El reporte da ahora ese dato exacto.
- **Suite rápida y candado:** corrieron en `lab/hyperframes/f41/f50h/`. Rápida 55 passed y 3 skipped; amplia 991 passed más las 4 previas; ch02 `f792f3d483a1fa42daed5f7f0e054f46`.
- **Riesgo 2:** si F50g-B o F51 cambian `armar` antes de las etapas 2 y 3, hay que regenerar `--prompts` y volver a verificar L = guardado antes de gastar. Queda como condición de la etapa 2.


---

# F50h — etapas 2 y 3 (Omar OK 2026-10-29 02:30) · PARADA: la llave sigue cerrada

## Qué pasó, en llano
- **Fotos:** se generaron las 120 fotos (20 fotos × 3 armados × 2 imágenes). Las 60 llamadas a Seedream salieron bien al primer intento.
- **Hojas:** una por foto, a ciegas. Cada columna es una letra (A, B, C) sorteada por foto, y la llave que dice qué armado es cada letra está guardada aparte, sin abrir.
- **Visión:** Gemini Flash puntuó las 120 fotos, elemento por elemento; 119 dan puntaje y 1 quedó como hueco.
- **Gasto:**
  - registrado: US$ 4,2123;
  - real, contando los tokens de la visión: **~US$ 4,93 de 5,00**. La visión costó ~US$ 0,73 y no los 0,30 estimados, porque Gemini razona mucho por foto, y `track_gemini_vision` registra una tarifa fija de US$ 0,0001 por llamada.
- **Falta:** que Omar elija una letra por foto. Recién ahí se abre la llave (etapa 4, que se pide aparte).

## Commits (etapas 2 y 3)
| etapa | commit |
|---|---|
| 2: fotos | `96942e9` |
| 3: hojas y visión | `b1776c2` |
| reporte y ESTADO | este commit |

## Antes de gastar
`f50h.py --prompts` de nuevo (abierto 6):
```
L = guardado 20/20 · palabras mediana {'L': 167.5, 'C': 131.0, 'C+ép': 139.0} · máx {'L': 273, 'C': 196, 'C+ép': 204} · oraciones mediana {'L': 13.0, 'C': 9.0, 'C+ép': 9.0}
```
`PROMPTS_F50h.json` queda con el mismo md5 que en la etapa 1 (`532062d4…`).

## Etapa 2 — fotos (`f50h.py --fotos`)
**Cómo se corrió:**
- **Llamadas:** 60 (20 fotos × L, C, C+ép), en paralelo con `asset_manager.FLUX_MAX_WORKERS` workers.
- **Por llamada:** `generar_2` es `f49_corridas.generar_1` con `num_images` 2 (constante del handoff): el mismo payload de producción (`_SYNC_PAYLOAD_BUILDERS["seedream"]`), el mismo endpoint y el mismo `track_seedream`. La única diferencia es que guarda las 2 imágenes, porque `generar_1` guarda solo la primera.
- **Freno:** como el de F49, contra el tope de US$ 5,00, con lo ya gastado en `cost_history` (`f50h-lab`) más lo reservado en vuelo.
- **Reintento:** uno, si hay rechazo o error.
- **A ciegas:**
  - Cada foto tiene su sorteo de letras con `random.SystemRandom` (sin semilla).
  - Las imágenes quedan en `fotos/<cap>_<foto>/<letra>_<n>.png`.
  - La llave (`llave.json`) está fuera de git (`.git/info/exclude`) y no se abrió.
  - Ningún archivo commiteado nombra una variante: lo comprobé con grep sobre `fotos_resultado.json`, `fotos.log` y los json y logs de la visión.
- **Las 120 png quedan fuera de git**, como en F49.
- **Sin grade:** las fotos no pasaron por `image_grade.grade`, porque el handoff no lo pide. Son las mismas condiciones para las 3 variantes.

Salida:
```
fotos: 60/60 llamadas ok · 120 png · cost_history f50h-lab = US$ 4.2000
```
- Hubo 0 huecos y 0 rechazos.
- Costo: 60 × 2 × US$ 0,035 = **US$ 4,20**, igual a la constante del handoff.

## Etapa 3 — hojas, visión y tabla
**Hojas** (`--hojas`): 20 jpg en `hojas/hoja_<cap>_<foto>.jpg`, de 3888×1586, en git.
- Cada hoja tiene 2 filas × 3 columnas: A, B y C, con la foto 1 arriba y la 2 abajo.
- Cada celda lleva su rótulo (`A1`…`C2`), y arriba de la hoja va el ancla en español.
- El estilo es el de las hojas de F49.

**Visión** (`--vision`):
- **Cliente y modelo:** los de `gfx_critic` (`config.gemini_client`, `api.gemini_model` = gemini-2.5-flash), con `temperature` 0 y salida JSON, como `gfx_critic`.
- **Prompt:** el del handoff, exacto.
- **Llamadas:** una por png, en paralelo.
- **Lo que ve el modelo:** solo la imagen y la lista de elementos; no ve la variante, el prompt ni el nombre del archivo.
- **Elementos:** se arman por código desde los casilleros de cada foto, como dice el handoff. La lista de anacronismos sale de `f50f/canon_f50f.json`.

Salida:
```
visión: 119/120 ok · huecos 1 · cost_history f50h-lab = US$ 4.2122
```
- **5/13 C1:** la primera respuesta no sirvió y salió bien en su reintento, dentro de `--vision`.
- **Hueco 4/11 A1:** Gemini devolvió la respuesta vacía en los 2 intentos (`resp.text` = None). Queda como hueco, como dice la regla.
- **7/7 A2:** el JSON se parseó, pero el modelo copió literal el `"<id>"` del ejemplo en vez de los ids, así que no se puede asignar a los elementos.
  - Lo traté como un JSON que no parsea, con su único reintento: `--vision-repetir` vuelve a pedir solo las respuestas guardadas que no sirven y tienen un intento libre.
  - Salida: «repetidas: ['7/7 A2: ok'] · cost_history f50h-lab = US$ 4.2123».
  - La validación de ids (`_valida`) también quedó en `--vision`, para la próxima corrida.
- **Revisión del analista (la 7/7 de espaldas):** `appearance_banjima_traditional_owners` da `not_visible` en 5 de los 6 png (A1, A2, B2, C1, C2) y `yes` en B1. No hubo ningún `no`.

**Tabla** (`--tabla`): `VISION_F50h.json` y `VISION_F50h.md`, por letra y no por variante. Puntaje por png = sí / (sí + no), con `not_visible` aparte.

| letra | puntaje medio | png medidos | not_visible | invented_text | huecos |
|---|---:|---:|---:|---:|---:|
| A | 0.873 | 39 | 51 | 5 | 1 |
| B | 0.903 | 40 | 47 | 5 | 0 |
| C | 0.887 | 40 | 55 | 4 | 0 |

**Ojo con el total por letra:** las letras se sortearon foto por foto, así que la «A» de una foto no es el mismo armado que la «A» de otra. Mientras la llave siga cerrada, el total por letra no compara variantes. Lo pide así el handoff para no abrirla; la comparación por variante sale en la etapa 4, con la llave. La tabla por foto completa está en `VISION_F50h.md`.

## Costo real
| paso | registrado (cost_history `f50h-lab`) | real |
|---|---:|---:|
| fotos: 120 × US$ 0,035 | 4,2000 | 4,2000 |
| visión: 123 llamadas (120 + 2 reintentos dentro de `--vision`, el de 4/11 A1, que siguió vacío, y el de 5/13 C, que salió bien en el segundo intento, + 1 de `--vision-repetir`, la 7/7 A2) | 0,0123 (tarifa fija de `track_gemini_vision`) | **~0,733**: 83 049 tokens de entrada y 283 249 de salida con razonamiento, a US$ 0,30 / 2,50 por millón (precios de gemini-2.5-flash en `cost_tracker`). La llamada vacía del hueco no trae uso y no suma |
| **total** | **4,2123** | **~4,93** (tope 5,00) |

## Verificación (etapas 2 y 3)
- Suite rápida: 55 passed, 3 skipped.
- Suite amplia: 4 failed, 991 passed (las 4 de siempre). Logs en `f41/f50h_23`.
- ch02: `f792f3d483a1fa42daed5f7f0e054f46`, igual.
- No se tocó ningún archivo de producción.

## Lo que queda abierto (etapas 2 y 3)
1. **Omar elige una letra por foto** mirando `hojas/`. Después, en una etapa 4 pedida aparte, CC abre la llave, cruza las elecciones con la visión y escribe el resultado. La regla del handoff: gana la que Omar elige en más fotos; si hay empate, decide el puntaje de visión.
2. **La etapa 3 pasó su presupuesto propio:** el handoff la estimaba en ≤ US$ 0,30 y costó ~0,73 real. El tope global de US$ 5,00 se respetó (~4,93), con un margen de ~0,07. Además, `track_gemini_vision` registra una tarifa fija de US$ 0,0001 por llamada, que no refleja el uso real. El freno usó la cifra registrada y el total real quedó en ~4,93, cerca del tope de 5,00. Si se repite una visión así, hay que medir por tokens (`track_gemini_response`) o apagar el razonamiento. Es una decisión del analista.
3. **El elemento `era` tiene un sesgo:** usa la lista de anacronismos del canon entera, como manda el handoff. Esa lista trae «contemporary clothing» y otras cosas de la época de la mina, así que en las fotos de 2016–2024 el elemento se contradice. Pesa igual en las 3 variantes, así que la comparación no se tuerce, pero el puntaje absoluto de esas fotos baja.
4. **Huecos:** queda 1 de 120 (4/11 A1, respuesta vacía de Gemini).
5. **Las fotos no tienen grade de producción.** Son iguales para las 3 variantes.
6. **Los png están fuera de git,** en `lab/hyperframes/f50h/fotos/` (`.git/info/exclude`), igual que `llave.json`.
7. **De la etapa 1 y de antes:**
   - C no llega a 2–4 oraciones;
   - repeticiones entre el sujeto y el aspecto;
   - F50g-B (Court, corte Veo, `anio_final`);
   - la foto madre en F51;
   - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos (etapas 2 y 3)
Corrieron:
- `--fotos` en segundo plano (exit 0);
- `--hojas`, `--vision`, `--vision-repetir` y `--tabla` en primer plano;
- `verificar.sh f50h_23`.

No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff (etapas 2 y 3)
**Primer veredicto** (el revisor todavía no había visto esta sección del reporte):

VEREDICTO: CUMPLE CON OBSERVACIONES

Solo lectura. Corrí `--prompts` (en seco) y `--tabla`. No abrí llave.json ni llamé a ninguna API.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Antes de gastar, L = guardado 20/20 | OK | `--prompts` hoy: «L = guardado 20/20 · mediana L 167,5 / C 131 / C+ép 139». Los archivos de etapa 1 no cambiaron en git. |
| 2 | VISION_PROMPT idéntico al del handoff | OK | Comparé por script el bloque de handoff l.93-100 contra `f50h.py` l.331-338, con `{{ }}` des-doblado: `True`, diff vacío. |
| 3 | generar_2 fiel a generar_1 | OK | `f50h.py` l.175-202 vs `f49_corridas.py` l.105-132. Mismo `select_profile("seedream")`, `_SYNC_PAYLOAD_BUILDERS["seedream"]`, `num_images`=2, URL, headers, timeout 240, rechazo de contenido y `track_seedream`. Guarda las 2 imágenes como `<letra>_1/_2.png`, y la descripción del tracker ya no lleva el prompt. |
| 4 | 60 llamadas, 120 png, letras al azar por foto | OK | `fotos_resultado.json`: 60 «ok», todas al intento 1, 0 huecos. `fotos.log`: «120 png · US$ 4,2000». Las letras salen de `SystemRandom` y la llave se escribe en un archivo aparte. |
| 5 | Tope US$ 5,00 | OK | Freno antes de cada llamada de fotos (l.238), con lo reservado en vuelo. Costo medido de punta a punta: fotos 4,2000, más 0,0122 de visión registrada a tarifa fija = 4,2123 en `cost_history`. |
| 6 | Costo real de la visión | PARCIAL | Recalculé desde los tokens del crudo: 82.366 de entrada y 281.534 de salida más pensamiento. A las tarifas públicas de gemini-2.5-flash (mis valores, no del handoff) da ≈ US$ 0,73, o sea ≈ 0,733 como dice el reporte. Total real ≈ 4,93, bajo el tope de 5,00. Pero el handoff presupuestó la etapa 3 en ≤ 0,30 y la real es ≈ 0,73. El tope global se respetó; el de etapa no. El freno de `--vision` y `--vision-repetir` mira el costo del tracker (≈ 0,0001 por llamada) y nunca habría frenado por el gasto real. Margen final ≈ 0,07. |
| 7 | Visión: cliente y modelo de gfx_critic, sin variante, prompt ni nombre de archivo | OK | `_vision_una` usa `api.gemini_model`, `gemini_client`, `track_gemini_vision`, `temperature=0.0` y JSON, igual que `gfx_critic.py` l.106-109. Manda solo el png y el prompt. |
| 8 | Elementos de visión por código desde los casilleros | OK | `elementos()` l.341-356 genera subject, action, `appearance_<grupo>`, place, era (con el `anachronism_blocklist` de `canon_f50f.json`), lighting, shot, y sign o no_text según haya cartel. |
| 9 | 7/7 A2 con «<id>» literal | OK | `_valida` (l.375-381) trata las respuestas con ids que no son los pedidos como no parseables. `--vision-repetir` re-pide solo las que tienen un intento libre. En el crudo, 7/7 A2 quedó con `intentos`=2, `descartada` con los «<id>» y respuesta válida. |
| 10 | Hueco 4/11 A1 | OK | Dos intentos, ambos `TypeError` por respuesta vacía. Queda con `hueco` y `intentos`=2. En la tabla aparece como «1 hueco» en la letra A (39 png medidos), sin reintento extra. |
| 11 | 7/7 de espaldas → not_visible | OK | `VISION_F50h.json`: `appearance_banjima_traditional_owners` da not_visible en A1, A2 y C1, y yes en B1. Coincide con el «5 de 6» del reporte; no verifiqué la cifra completa. |
| 12 | Hojas 2×3 con rótulos y ancla | OK | `hojas()` l.292-327: 2 filas × 3 columnas (A, B, C; arriba la foto 1, abajo la 2), rótulos `A1`…`C2` y el ancla en español arriba (del papel f50g). 20 jpg en git; `hoja_7_7.jpg` mide 3888×1586, consistente con 3 columnas de 1280 y 2 filas. No las miré una por una. |
| 13 | Tabla por letra, no por variante | OK | `--tabla` reproduce `VISION_F50h.json/.md` sin diff en git. Totales: A 0,873 · B 0,903 · C 0,887. |
| 14 | Ninguna variante de una letra en archivos commiteados | OK | Grep de «C+ép», «"L"» y «variante» en `fotos_resultado.json`, `fotos.log`, `vision.log`, `VISION_F50h.json`, el crudo: 0. En `VISION_F50h.md`, 1 coincidencia, que es la frase «no por variante». `git ls-files` no lista llave.json ni las png. `.git/info/exclude` tiene `llave.json` y `fotos/`. `PROMPTS_F50h.json` (etapa 1) lleva L/C/C+ép por foto, pero sin letras. |
| 15 | Producción intacta | OK | `git diff 6d2a875..HEAD --stat` sin `script_engine/`, `03_visual.json` ni topics_db: solo los 27 archivos de `lab/hyperframes/f50h/`. |
| 16 | Ningún número fuera de la tabla de constantes | OK | `TOPE_USD`, `NUM_IMAGES` y 120 (`max_workers` de visión) vienen del handoff. Los números de layout de las hojas (margen 12, cabecera 110, calidad 88, ancho 1280, fuentes) son estética del modelo F49 y no afectan la medida. |
| 17 | F50h_REPORT.md etapas 2 y 3, ESTADO, veredicto íntegro | NO VERIFICABLE | `F50h_REPORT.md` sigue en la versión de 6d2a875 (sin diff; no tiene la sección «etapas 2 y 3» ni el marcador). Esto lo dijiste vos como pendiente. Verifiqué solo que el costo estimado (~0,733 y ~4,93) coincide con mis números. Faltan por revisar el texto del reporte, el ESTADO y el commit de ambos. |

Observaciones:
- El crudo (`VISION_F50h_crudo.json`) conserva la respuesta descartada de 7/7 A2, con los «<id>» literales. Es dato de proceso, no de variante.
- La etapa 3 superó su presupuesto propio (0,30) con ≈ 0,73. El reporte debe decirlo explícito, no solo «~4,93 de 5,00».
- El `invented_text` lo juzga el modelo con el prompt del handoff y se cuenta por png. No hay filtro por código para las fotos con cartel; el handoff lo delega al prompt.

Fuera de alcance: ninguno. Lo no commiteado es `lab/hyperframes/f41/f50h_23/` (logs de las suites) y el reporte, como anunciaste.

Riesgos que el contrato no cubre:
- El costo en `cost_history` subestima la visión (≈ 0,012 registrado contra ≈ 0,73 real). Cualquier tracker o freno futuro que se base en él verá ≈ 4,21 cuando el gasto real es ≈ 4,93.
- El puntaje por letra mezcla elementos `not_visible` (47 a 55 por letra) fuera del denominador. Las letras difieren por décimas (0,873 a 0,903) y hay 1 hueco en A, así que la visión es un desempate débil.
- 120 hilos simultáneos en visión pudieron causar los vacíos de respuesta (4/11 A1, 5/13 C). No es un problema de contrato.

**Actualización del revisor** (después de leer esta sección):

VEREDICTO: CUMPLE CON OBSERVACIONES (el veredicto anterior sigue en pie. Ya leí la sección «etapas 2 y 3» de F50h_REPORT.md, l.166-282, y cierra el punto 17 que había marcado NO VERIFICABLE).

Tabla del veredicto anterior, con el # 6 y el # 17 actualizados. Los demás quedan igual: prompt de visión idéntico al handoff, generar_2 fiel a generar_1, 60/60 llamadas ok y 120 png, freno contra el tope, letras al azar con llave aparte y sin abrir, hojas 2×3 con rótulos y ancla, elementos de visión por código, tratamiento de 7/7 A2 y del hueco 4/11 A1, producción intacta y ningún número fuera de la tabla de constantes. Ver el veredicto anterior para la evidencia de cada uno.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 6 | Costo real de la visión y tope | OK | Mi recálculo desde los tokens del crudo da ≈ US$ 0,73. El reporte dice ~0,733 y total real ~4,93 de 5,00. Admite que la visión superó la estimación de 0,30 y que `track_gemini_vision` registra una tarifa fija, así que el freno usó la cifra registrada (reporte, «Costo real» y abierto 2). El tope global se respetó. |
| 17 | Reporte etapas 2 y 3, ESTADO, veredicto íntegro | PARCIAL | La sección existe y cubre la salida de cada etapa, el costo real, lo abierto y el 7/7 de espaldas. Falta el marcador `{{VEREDICTO_23}}` (pendiente de pegar este veredicto), el commit del reporte y el ESTADO. No verifiqué el ESTADO. |

Observaciones nuevas sobre el reporte:
- **Llamadas de visión:** el reporte dice «122 llamadas (120 + 1 reintento del hueco + 1 de `--vision-repetir`)». Pero 5/13 C también tiene `intentos` 2 en el crudo sin ser hueco, y el costo registrado, 4,2123 − 4,2000 = 0,0123 a 0,0001 por llamada, implica 123. El reporte no menciona esa llamada de 5/13 C. Es un descuadre menor de conteo; no afecta el costo real.
- **Tokens:** el reporte cita 83.049 de entrada y 283.249 de salida. Yo sumé 82.366 y 281.534 sobre las respuestas finales del crudo. La diferencia es compatible con contar también las respuestas descartadas (7/7 A2 y el reintento de 5/13 C). No lo pude confirmar.
- **Sesgo del elemento `era`:** el reporte lo declara. Es la lista completa de anacronismos del canon, como manda el handoff, y trae «contemporary clothing», así que contradice a las fotos de 2016–2024. Pesa igual en las 3 variantes.
- **Verificaciones de suites:** el reporte cita suite rápida 55 passed, amplia 991 passed + 4 failed y ch02 f792f3d4. No las corrí (no se me permitía). Los logs están en `lab/hyperframes/f41/f50h_23/`.

Fuera de alcance: ninguno. Está sin commitear `F50h_REPORT.md` (la sección nueva) y `lab/hyperframes/f41/f50h_23/`, como anunciaste.

Riesgos que el contrato no cubre:
- El `cost_history` queda subregistrado en la visión (≈ 0,012 contra ≈ 0,73 real), con un margen real bajo el tope de ≈ 0,07. Un freno futuro basado en el tracker no habría frenado.
- Los totales por letra (0,873 / 0,903 / 0,887, con 47 a 55 `not_visible` por letra) mezclan variantes distintas foto a foto. Con la llave cerrada no comparan variantes, y las diferencias son de décimas.
- Antes de commitear el reporte hay que reemplazar `{{VEREDICTO_23}}` por este veredicto, y no dejar el marcador.

### Adenda de CC (después del veredicto)
- **Conteo de llamadas:** corregido a 123. Son las 120, 2 reintentos dentro de `--vision` (4/11 A1, que siguió vacía, y 5/13 C1, que salió bien) y 1 de `--vision-repetir` (7/7 A2). La 5/13 C1 quedó agregada en la etapa 3.
- **Tokens:** los 83 049 / 283 249 suman el campo `tokens` de cada respuesta final más el `tokens_reintento` de la 7/7 A2. La respuesta descartada de la 5/13 C1 dentro de `--vision` no guardó su uso, así que el costo real puede estar un poco por debajo de lo gastado. Igual queda dentro del margen al tope, de ~0,07.
- **Presupuesto propio de la etapa 3:** el punto 2 de lo abierto dice ahora explícito que superó la estimación de ≤ US$ 0,30.
- **Marcador y ESTADO:** este texto reemplaza `{{VEREDICTO_23}}`. ESTADO va en el mismo commit.

