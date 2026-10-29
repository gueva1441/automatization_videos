# F51f — la frase del cartel con una sola forma gramatical (y Wittenoom rearmado sin LLM) · PARADA

CC → Omar / analista · 2026-10-29 · rama `f11-guion-v4` · **US$ 0** (sin fal, sin LLM) · handoff `HANDOFF_F51f_carteles.md`, md5 `e24ce12d00ae33af3b7c36b509bccd1a` (coincide).

## Commits
| etapa | commit | qué |
|---|---|---|
| 0 | `afa2678` | DECISIONES 12:54 tal cual (incluye el handoff) |
| 1 | `ee908b5` | `frase_cartel` nueva + chascada, tests, contrato F51a ajustado, sticker y MAPA |
| 2 | `426409a` | `rearmar_f51f.py`, `REARMADO_F51f.md`, copia `f51f/antes/`, papel nuevo |
| cierre | (este) | reporte, ESTADO, logs de `lab/hyperframes/f41/f51f/` |

## Etapa 0
`tail -1 DECISIONES.md`:
```
- 2026-10-29 12:54 · **F51f:** la frase del cartel va «… in clear crisp {font} lettering» (sin repetir «lettering/letters»; sin font, «in clear crisp lettering»; una sola palabra → «The word … is»); Wittenoom se rearma sin LLM. Los grupos sin aspecto (4/3, 5/9) y los casilleros escritos como narración (1/2, 5/15, 6/8) se dejan así y se ven en QA Studio después de generar · Omar · F51f
```

## Etapa 1 — código y tests
`m03_imagenes_v3.frase_cartel` (la regla reemplaza a la vieja):
- `font` → `_minuscula_media`, sin puntuación final, y sin la última palabra si es «lettering» o «letters»;
- `en` = « in clear crisp {font} lettering» (sin font: « in clear crisp lettering»), sin la coma de antes;
- las 3 aperturas iguales; con la preposición, un texto de una sola palabra va «The word "X" is written …».

**Los 8 de Wittenoom, tal como salen del código** (casilleros del 03_visual de F51d-A); son la tabla del handoff:

| foto | font | frase |
|---|---|---|
| 3/3 | painted block lettering | The words "Australian Blue Asbestos" are written on the truck's door panel in clear crisp painted block lettering. |
| 3/5 | typewriter | The typed line on the letter in the platen reads "Extremely dangerous" in clear crisp typewriter lettering. |
| 4/12 | handwritten ink | The words "7 July 1963" are written along the white border of the photograph in clear crisp handwritten ink lettering. |
| 5/1 | bold serif newsprint headline | The front page of the folded newspaper reads "WITTENOOM MINE CLOSES" in clear crisp bold serif newsprint headline lettering. |
| 6/10 | highway sign sans-serif | The word "WITTENOOM" is written on the fallen sign panel in the dust in clear crisp highway sign sans-serif lettering. |
| 6/16 | block stencil | The words "ROAD CLOSED" are written on the sign fixed to the barricade in clear crisp block stencil lettering. |
| 7/10 | carved | The words "Federal Court" are written over the entrance in clear crisp carved lettering. |
| 7/13 | block | The words "DANGER ASBESTOS" are written on the warning sign in clear crisp block lettering. |

**Tests:**
- `test_module_f51f.py` (12): los 8 fonts reales + «Metal block letters» → «in clear crisp metal block lettering» + sin font, cada uno con un solo «lettering» y sin «, in clear»; las 3 aperturas; una palabra («WITTENOOM»).
- `test_module_f50b.py` y `test_module_f51a.py` a la forma nueva. Sus casos usan textos de una palabra («X», «DANGER»), así que también pasan a «The word … is».
- f50b + f51a–f51f: **49 passed** · rápida 55.

**Contrato F51a ajustado** (`lab/hyperframes/f51a/contrato.py`):
- Lo esperado ahora es el C de F50h con la frase vieja del cartel cambiada por la nueva. La frase vieja sale de `_frase_cartel_f50h`, una copia en el contrato de la función de producción hasta F51f.
- Además, cada foto con cartel tiene que cumplir que el C de F50h sin la frase vieja sea igual al prompt de producción sin la nueva.
```
**20/20 byte a byte iguales a PROMPTS_F50h.json → C (con la frase del cartel de F51f)**

Carteles: 5 fotos, solo cambia la oración del cartel en 5/5
- 1/4 ok: «The words "WITTENOOM" are written on the roadside town sign in the foreground in painted block letters, in clear crisp lettering.» → «The word "WITTENOOM" is written on the roadside town sign in the foreground in clear crisp painted block lettering.» · diff contra F50h: - words + word - are + is + clear + crisp - letters, - in - clear - crisp
- 3/3 ok: «… in hand-painted block letters, in clear crisp lettering.» → «… in clear crisp hand-painted block lettering.» · diff contra F50h: + clear + crisp - letters, - in - clear - crisp
- 4/12 ok: «… reads "7 July 1963" in handwritten ink, in clear crisp lettering.» → «… in clear crisp handwritten ink lettering.» · diff contra F50h: - handwritten - ink, - in + handwritten + ink
- 5/1 ok: «… reads "MINE TO CLOSE" in bold 1960s newsprint headline, in clear crisp lettering.» → «… in clear crisp bold 1960s newsprint headline lettering.» · diff contra F50h: + clear + crisp - headline, + headline - in - clear - crisp
- 6/15 ok: «… reads "CABINET IN CONFIDENCE" in block print, in clear crisp lettering.» → «… in clear crisp block print lettering.» · diff contra F50h: - block - print, - in + block + print
```
(La numeración de las fotos del contrato es la de F50h, no la de F51d-A.) Sticker de `m03_imagenes_v3` y `mapa_modulos.py --check`: 157 archivos · 0 fallas.

## Etapa 2 — Wittenoom rearmado sin LLM
- Copia: `lab/hyperframes/f51f/antes/03_visual.json` (md5 `72fdd85c…`, el de F51d-A).
- **No usé `f50g/rearmar.py --escribir`.** Tiene tres problemas: pisa `REARMADO_F50g.md`, que está en git; se niega a escribir porque ya existe `f50g/antes/03_visual.json`, también en git; y su chequeo «sin grupos = guardado» ya no puede dar, porque cambió el cartel. En su lugar escribí `lab/hyperframes/f51f/rearmar_f51f.py`, que usa el mismo `rearmar_una`, los casilleros que dejó m03 en F51d-A y los `grupos` del topic vivo, sin llamar a Opus.
- **Chequeo previo, que da PARADA sin escribir si falla:** cada foto tiene que quedar igual o, si tiene cartel, ser el prompt guardado con la frase vieja cambiada por la nueva. Resultado:
  ```
  fotos 96 · con cartel 8 · cambian 8 (3/3, 3/5, 4/12, 5/1, 6/10, 6/16, 7/10, 7/13) · fuera del cartel 0 []
  escrito data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\03_visual.json (8 fotos)
  ```
- **Diff de campos** entre `antes/` y el `03_visual` nuevo, en todo el JSON: 8 campos y los 8 son `prompt` (3/3, 3/5, 4/12, 5/1, 6/10, 6/16 en `image_prompts`; 7/10 y 7/13 en `supplemental_image_prompts`). `sensible` y `motivos` no cambian. md5 `72fdd85c…` → `0d57b6ba…`.
- **Formato:** m03 escribe el JSON con CRLF, porque usa `write_text` en Windows. El primer intento de escritura lo frenó la guarda de formato del script, sin escribir nada. Ajusté la guarda y volví a escribir con el mismo formato.
- **Mi error:** después de escribir, volví a correr el script en seco sobre el archivo ya rearmado. Como comparaba el archivo contra sí mismo, dio PARADA y pisó `REARMADO_F51f.md` con esa versión. No escribió el `03_visual`. Le agregué `--desde-antes`, que arma el reporte desde la copia de `antes/`, y regeneré `REARMADO_F51f.md` con eso. Comprobé que los 8 prompts del reporte son iguales a los del archivo vivo.
- `REARMADO_F51f.md` tiene las 8 frases antes y después y los 8 prompts enteros.
- **Papel nuevo:** `python lab/hyperframes/f50/papel.py --salida lab/hyperframes/f51f/` →
  ```
  fotos 96 (antes 96) · fuentes {'1) el casillero `year` del modelo': 96} · rehechas 0 (video 0) · carteles 8 · US$ 2.2653
  ```
  Contra el papel de F51d-A cambian 16 líneas: las 8 frases de cartel, cada una en dos lugares. El US$ 2,2653 es el gasto de m03 en F51d-A, que el papel lee de `01_v3_costos`; esta tanda no gastó nada.

## Al cerrar
`bash lab/hyperframes/f41/verificar.sh f51f` (logs en `lab/hyperframes/f41/f51f/`):
```
md5: f792f3d483a1fa42daed5f7f0e054f46 *output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4
rapida: 55 passed, 3 skipped in 3.03s
amplia: 4 failed, 1019 passed, 30 skipped, 4 warnings in 71.31s (0:01:11)
FAILED test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto - Assertion...
FAILED test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto
FAILED test_module_m03_merge_timing.py::test_c_guarda_de_minimo - AssertionEr...
FAILED test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales - asser...
```
- Candado ch02 `f792f3d4…` sin cambio; rápida 55.
- Amplia: 1019 passed + 4 failed. Son las 4 previas de siempre (`m03_merge_timing` ×2 y `gfx_lab` ×2). La cuenta: 1007 de F51d-A + 12 de `test_module_f51f.py` = 1019.
- Contrato F51a ajustado: 20/20, con solo la oración del cartel en las 5 fotos que lo tienen.
- Cero fal y cero LLM: `cost_history` no tiene entradas nuevas del tema (ver adenda).

## Lo que queda abierto
1. **Solo se rearmó Wittenoom.** Los `03_visual.json` de otros temas conservan la frase vieja del cartel hasta que se vuelvan a armar.
2. **El contrato F51a tiene ahora una copia de la frase vieja del cartel** (`_frase_cartel_f50h`) para armar lo esperado. Además depende de `f51d/antes/03_visual.json` (abierto 6 de F51d-A).
3. **`f50g/rearmar.py` ya no sirve para escribir producción:** su `--escribir` se niega mientras exista `f50g/antes/`, y su chequeo «sin grupos = guardado» no puede dar con el cartel nuevo. Para rearmar quedó `f51f/rearmar_f51f.py`; para el reporte después de escribir, hay que usar `--desde-antes`.
4. **De la lista del handoff, sin hacer:** el cartel en plano extreme wide (3/3), el idioma del texto escrito a mano (4/12, fecha en inglés en una foto de familia española), y los grupos sin aspecto y los casilleros narrativos, que se ven en QA Studio.
5. **Siguen de antes:** el prompt de video Veo con la guía de Google (tanda aparte); la foto madre con el canon nuevo (F51d-B); el cap 3 sin reconciliación temporal (F51d-A); los scripts de lab rotos de F51c y `_lab_name_scrub.py`; y las 4 fallas previas de la suite.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Etapa 0: handoff md5 e24ce12d…; DECISIONES lleva la línea tal cual | OK | `md5sum` da e24ce12d00ae33af3b7c36b509bccd1a; `tail -1 DECISIONES.md` es la línea 12:54 literal |
| 2 | `frase_cartel`: «in clear crisp {font} lettering»; saca «lettering/letters» final; sin font «in clear crisp lettering»; una palabra → «The word … is»; 3 aperturas intactas | OK | `git diff 51c6128 HEAD -- script_engine/m03_imagenes_v3.py`: 11+/7-, y es el único cambio en script_engine |
| 3 | Los 8 carteles de Wittenoom salen como la tabla del handoff | OK | `REARMADO_F51f.md` tiene las 8 formas pedidas, cada una 2 veces (antes y después). Las 8 son `painted block`, `typewriter`, `handwritten ink`, `bold serif newsprint headline`, `highway sign sans-serif`, `block stencil`, `carved` y `block` |
| 4 | Tests: F50b reescrito y `test_module_f51f.py` nuevo | OK | Corrí `pytest test_module_f51f.py test_module_f50b.py test_module_f51a.py`: 36 passed |
| 5 | Contrato F51a ajustado (C de F50h con la frase vieja cambiada por la nueva) | OK | Corrí `contrato.py`: «20/20 byte a byte iguales a PROMPTS_F50h.json → C (con la frase del cartel de F51f)» |
| 6 | Etapa 2: copia previa en `f51f/antes/` | OK | `lab/hyperframes/f51f/antes/03_visual.json` existe (3472 líneas en el diff) |
| 7 | Rearmado sin LLM; solo cambian las 8 fotos con cartel y solo en la oración del cartel | OK | Mi diff de campos JSON entre `antes/` y el vivo da 8 diferencias, las 8 en `.prompt`: `image_prompts` 3/3, 3/5, 4/12, 5/1, 6/10 y 6/16, y `supplemental_image_prompts` 7/10 y 7/13. `rearmar_f51f.py --desde-antes` da «fuera del cartel 0 []» |
| 8 | Papel nuevo y los 8 prompts enteros | OK | `PAPEL_FOTOS_WITTENOOM.json` y `.md` en `f51f/`; `REARMADO_F51f.md` con los prompts |
| 9 | Candado ch02 f792f3d4… | OK | Recalculé el md5: f792f3d483a1fa42daed5f7f0e054f46 |
| 10 | Suites rápida y amplia | NO VERIFICABLE | No corrí `verificar.sh`. El reporte da rápida 55 y amplia 1019 passed + 4 failed, las mismas 4 previas. Falta mirar `lab/hyperframes/f41/f51f/` o el log del scratchpad |
| 11 | No tocar canon, casilleros, `anio_final`, corte Veo ni `cost_tracker`; US$ 0 | OK | El diff 51c6128..HEAD no incluye `cost_tracker` ni el canon. El archivo vivo solo cambia en 8 `prompt`. Sin fal ni LLM no lo puedo comprobar del todo: es lo que dicen el reporte y `cost_history` |
| 12 | `F51f_REPORT.md` con lo abierto entero y el veredicto | PARCIAL | Existe y tiene 5 puntos abiertos. Es el estado esperado: la línea final sigue en `{{VEREDICTO}}`, a rellenar con este texto |

Fuera de alcance: ninguno de fondo. Hay tres cosas que el handoff no nombra, aunque son coherentes con las etapas:
- `lab/mapa/stickers/fase2a.json` y `lab/MAPA_PROYECTO.json/.md` (sticker y mapa, declarados en el commit ee908b5).
- `lab/hyperframes/f51f/rearmar_f51f.py`, script nuevo. El handoff decía «`f50g/rearmar.py --escribir` o lo que corresponda».
- `f51f/ENTRADA_ANALISTA_2026-10-29e.md` y el reporte, sin commit.
Los M previos de `diag_234_cap4.py`, `lab/TOPE_TANDA.json` y `f28a.log` ya estaban en el status inicial y no son de esta tanda.

Observaciones:
- Un error del propio CC, que el reporte admite: volvió a correr el script en seco sobre el archivo ya rearmado y pisó `REARMADO_F51f.md` con una PARADA. Lo regeneró con `--desde-antes`, y yo verifiqué que el reporte coincide con el vivo.
- El `03_visual` quedó en CRLF y la guarda de formato de `rearmar_f51f.py` se ajustó a mano.

Riesgos que el contrato no cubre:
- Los demás temas conservan la frase vieja del cartel hasta que se rearmen (abierto 1).
- El contrato F51a depende de una copia de la frase vieja (`_frase_cartel_f50h`) y de `f51d/antes/03_visual.json`.
- `f50g/rearmar.py` queda inútil para escribir producción.

### Adenda de CC (después del veredicto)
- **#10, suites:** `verificar.sh f51f` las corrió y su salida está pegada en «Al cerrar». Candado ch02 `f792f3d4…`, rápida 55 passed, amplia 1019 passed + 4 failed. Las 4 fallas son las mismas que en `lab/hyperframes/f41/f51d/suite_amplia.log`: `m03_merge_timing::test_c_guarda_de_minimo`, `m03_merge_timing::test_c_veo_path_y_veo_anchor_intacto`, `gfx_lab::test_cues_sin_escribir_el_proyecto` y `gfx_lab::test_preview_usa_las_plantillas_reales`.
- **#11, cero fal y cero LLM:** después del m03 de F51d-A (12:37:14), `cost_history` solo tiene dos registros de `ba6c3cac` por US$ 0,00, a las 12:40 y a las 13:01. Son los candados ch02 de `verificar.sh` en F51d-A y F51f. Del tema 123bbb64 no hay ningún registro nuevo.
- **Fuera de alcance, `ENTRADA_ANALISTA_2026-10-29e.md`:** no lo escribí yo y queda sin commit, como manda la regla de la cadena sobre los `ENTRADA_ANALISTA_*.md`.
- **CRLF:** la primera guarda de formato frenó la escritura sin escribir nada. El ajuste reproduce el mismo formato con el que m03 escribe el archivo, y el diff de campos lo confirma: 8 campos `prompt` y nada más.
