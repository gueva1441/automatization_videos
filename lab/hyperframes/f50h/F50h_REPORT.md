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

