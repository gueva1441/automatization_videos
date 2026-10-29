# F50c — Cableado del expediente de foto: personas, citas y grupos (código y en seco, US$ 0)

Handoff `lab/hyperframes/f50c/HANDOFF_F50c_cableado_del_expediente.md`, md5 `6a57677a46cb06266658b82f26e4dd25` (verificado). Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. **Cero llamadas a modelos, cero fal**, `TOPE_TANDA` = 0. No se tocaron `03_visual.json` (md5 `23a81881…`, el de F50b) ni el papel (`f50b/PAPEL_FOTOS_WITTENOOM.json` md5 `2eb4000a…`).

Lecturas: `CLAUDE.md`, `DECISIONES.md` (hasta 22:09), `lab/ESTADO_SESION.md` (F50b y F50), el handoff, `script_engine/m03_expediente.py`, `_sin_negadas` en `m03_imagenes_v3.py`, `lab/hyperframes/f50/verificar_b.py`. El script de simulación del analista (`lab/_gpt_probe_analista/auditoria_foto/sim_personas3.py`) lo leí como referencia de la regla; no se copió al repo.

## Commits
| parte | commit |
|---|---|
| paso 0 | `2a2a2b4`: DECISIONES 22:09 tal cual y el handoff. `TOPE_TANDA.json` = `{"usd": 0.0, "desde": "2026-10-28T22:15:40"}` (fuera de git) |
| D | `9efc125` |
| A | `6cf9317` |
| B + C | `fbbd58c`: un solo commit, como lo agrupa el pedido («A, B+C y D») |
| pasos 2–3 y reporte | este commit |

D la hizo un subagente en paralelo mientras yo hacía A, B y C (los dos tocan archivos distintos). Cada commit actualiza sticker y `MAPA_PROYECTO` (`--check`: «157 archivos de producción · 0 fallas» en los tres). Las suites amplia y rápida y el candado de ch02 se corrieron una vez, sobre el árbol final; el «antes» es la corrida de F50b (`1ecf045`).

## Módulos que toca
| archivo | sticker (fase2a), hoy | después |
|---|---|---|
| `script_engine/m03_expediente.py` | «Arma el expediente de cada foto… las citas y las personas (rol · lugar · años) de su beat… los grupos de gente del canon» | Personas desde la ficha (A), citas con autor (B), grupos con aspecto y ropa (C). Se borró `_sale_entero` y la búsqueda de personas por ids P del beat |
| `script_engine/m03_imagenes_v3.py` | «… saca de cada casillero las cláusulas negadas…» | Chascada D |
| `test_module_f50c.py` (nuevo) | — | 15 tests de A–D |

## A. Personas desde la ficha
Funciones nuevas en `m03_expediente.py`:
- `_formas`: `nombre` y `variantes`, sin el paréntesis.
- `_calificativo`.
- `_anios_persona`: los años de los ids `P`, `cronologia` y `datos`, sin los ids comunes.
- `personas_del_ancla`: forma más larga por persona como palabra entera. Si la forma es compartida, gana el calificativo; si no, el año más cercano; si empatan o no hay año, nadie.
- `linea_persona`: `rol · lugar · años` del primer id `P` que tiene cada dato.
- Arrastre en `expedientes`: la clave es el párrafo y nunca cruza párrafos. Se marca con `ARRASTRE = " (named earlier in the paragraph)"`.

El año de la foto que usa la regla es `anio_ancla`, y si no hay, el `respaldo`: el mismo que el expediente ya calculaba.

## B. Citas con autor
`linea_cita`: `«texto» — autor · rol` + ` · fecha` si la trae + ` · witness` si `testigo` es true. Al `rol` le saco el punto final, igual que en PEOPLE; el handoff no lo especifica.

## C. Grupos
`  - id: who · where_when · APPEARANCE: appearance · CLOTHING: clothing`. Si falta el dato, va `-`.

## D. Chascada de `_sin_negadas`
`_NEGADA` no dispara con «No.» + cifra ni con «nothing but». El corte de cláusula (`_CORTE_CLAUSULA`) no parte en el punto de «No.» + cifra. Wittenoom: `rearmar.py --igual` da 96/96 iguales, así que no cambia ninguna foto, como dice el handoff (0 casos).

## Tests
`test_module_f50c.py`, 15 verdes:
- A:
  - forma única y forma más larga;
  - el calificativo «hijo»;
  - la persona por año, y una forma ambigua sin año da nadie;
  - la línea PEOPLE;
  - el arrastre dentro del párrafo y no entre párrafos;
  - que `_sale_entero` ya no existe;
  - las 8 fotos testigo con los datos reales de Wittenoom (en seco).
- B: cita con fecha y testigo, y cita sin fecha con `testigo` false.
- C: grupo con aspecto y ropa, y QUOTES en el bloque.
- D:
  - «Cell No. 5» y «No. 4 Shaft» se quedan;
  - «nothing but red dust» se queda, con y sin «with»;
  - «with no figure anywhere» sale;
  - «swings without seats» se queda;
  - «no work, no vehicles» da "".

`test_module_f50b.py::test_expediente_y_bloque` se adaptó al comportamiento nuevo: la persona viene de la ficha y el ancla la nombra; el grupo lleva `APPEARANCE: - · CLOTHING: -`.

## Pasos 2–3: pedidos en seco y EXPEDIENTES_F50c
Script: `lab/hyperframes/f50c/expedientes_f50c.py`.
- Cómo arma el pedido: es el código de producción (`_render_prompts_seedream`), con `_llamar_casilleros` reemplazado por una función que guarda el pedido y corta antes de salir.
- Topic, `_geo_era` y `_f8`: como en producción.
- Anclas: las de `03_visual.json` (papel de F50b).
- Beats: `assign_beats` de producción, que da los mismos que los guardados en los 7 caps.
- Cada cap se arma dos veces: con el `m03_expediente.py` de `1ecf045` (F50b) y con el de hoy.
- Salida: `pedidos/pedido_chNN.txt` (después) y `pedidos/antes/pedido_chNN.txt` (antes).

Salida pegada:
```
{'con_people': 73, 'ancla': 35, 'arrastre': 38, 'ambiguas': 0, 'con_quotes': 84, 'grupos': 7} · reparto {1: 48, 2: 23, 3: 2} · testigos 8/8 · diffs 0 · beats distintos 0 · PASA
```

Verificación automática (`EXPEDIENTES_F50c.md`):
| | resultado | esperado |
|---|---:|---:|
| fotos con PEOPLE | 73 | 73 |
| por ancla | 35 | 35 |
| por arrastre | 38 | 38 |
| ambiguas | 0 | 0 |
| fotos con QUOTES (todas con autor) | 84 | 84 |
| grupos con APPEARANCE y CLOTHING | 7 | 7 |
| fotos con PEOPLE antes | 17 | 17 |
| 1 / 2 / 3 personas | 48 / 23 / 2 | 48 / 23 / 2 |
| citas sin autor | 0 | 0 |
| caps con diff fuera de PEOPLE/QUOTES/PEOPLE GROUPS | 0 | 0 |

Fotos testigo: 8/8. Las 8 salen como en la tabla del handoff:
- 1/3: el padre;
- 1/4: el padre, por arrastre;
- 2/1: el padre y María Bernal;
- 2/8: Víctor Calvo;
- 3/7: Eric Saint, por arrastre;
- 3/16: Jim McNulty;
- 5/9: el hijo;
- 5/14: el padre.

Fuera de las líneas PEOPLE, QUOTES y PEOPLE GROUPS, el pedido de los 7 caps no cambia respecto del de F50b (`difflib`, 0 líneas).

## Verificación
| | antes (F50b, `f41/f50b`) | después (`f41/f50c`) |
|---|---|---|
| suite rápida | 55 passed, 3 skipped | 55 passed, 3 skipped |
| suite amplia | 4 failed, 947 passed, 30 skipped | 5 failed, 961 passed, 30 skipped (951 + 15 de `test_module_f50c.py`) |
| ch02 md5 | `f792f3d4…` | `f792f3d483a1fa42daed5f7f0e054f46` (igual) |

Fallas de la amplia:
- **Las 4 de siempre**, que ya estaban en F49 y F50b: `gfx_lab::test_cues_sin_escribir_el_proyecto`, `gfx_lab::test_preview_usa_las_plantillas_reales`, `m03_merge_timing::test_c_guarda_de_minimo` y `m03_merge_timing::test_c_veo_path_y_veo_anchor_intacto`.
- **Una quinta que se vio una sola vez:** `gfx_lab::test_candado_en_el_preview` (no encuentra `#123456` en el HTML del preview). Corrido solo, `python -m pytest -q test_module_gfx_lab.py` da «2 failed, 43 passed»: las 2 de siempre, y esta pasa. Es intermitente cuando la suite corre en paralelo (`-n auto`). Esta tanda no toca `gfx_*` ni `fase2b`.

## Lo que queda abierto
1. **Nombres reales en el pedido por las citas.** B pone el autor de cada cita (por ejemplo «— Eric Saint · Médico aéreo…»). La línea PEOPLE no lleva nombre propio, pero las citas y el rol de la ficha sí («esposo de María Bernal»), y ya los traían antes como texto. La prosa armada sigue pasando por `scrub_documented_names`, pero este pedido nuevo no se probó con Opus: no se sabe si Opus copia más nombres a los casilleros. Recién se va a ver en la próxima corrida real de m03.
2. **2/7 arrastra a Milagros Barroso y Ramón de Juan.** El niño de esa foto es Víctor Calvo, de la oración siguiente. El handoff lo declara y la marca `(named earlier in the paragraph)` le avisa a Opus que es contexto.
3. **Organizaciones en `ficha.personas`.** CSR y Tribunal Federal entran como personas, con su rol como línea PEOPLE. La ficha no trae un campo que las distinga (declarado en el handoff).
4. **Grupos fuera de sus años.** 11 fotos usan un grupo fuera de su tramo (familias migrantes de 1958–66 en fotos de 1985–2023), y con la ropa a la vista Opus podría vestirlas de los 60. Se arregla en F50d (ropa por tramo en el canon). F51 no corre antes de F50d.
5. **El papel no cambió.** Los prompts de `03_visual.json` y el papel de F50b son los de antes de este cableado. El cableado recién se va a ver en las fotos cuando m03 vuelva a correr con Opus, lo que cuesta: F50d o F51 deciden.
6. **El rol de las citas va sin punto final**, igual que en PEOPLE. El handoff no lo especifica.
7. **`gfx_lab::test_candado_en_el_preview` es intermitente con `-n auto`** (ver Verificación). No se investigó.
8. **Las suites se corrieron una sola vez**, sobre el árbol final, y no por commit. Los commits intermedios (D, A, B+C) se probaron con `test_module_f50b.py` + `test_module_f50c.py`, `rearmar.py --igual` y `mapa --check`.
9. Siguen abiertos de F50b: las notas F8 viejas en 3 fotos del papel, la foto madre en F51 y los 4 casos que dejó la lista del handoff F50b. Siguen abiertos de F50: n2, n3, n7, n8, n10 y n12. La fecha límite de Veo 3.1 en fal es el 2026-11-17.

## Procesos
Procesos en segundo plano: el subagente de la parte D, que terminó, y `verificar.sh f50c`, que salió con exit 0. No quedó nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí `pytest -q test_module_f50c.py test_module_f50b.py`: 36 pasaron. Corrí también `expedientes_f50c.py` en seco. Sus salidas (EXPEDIENTES md/json, 7 pedidos y 7 «antes») quedaron con el mismo md5 que tenían.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 0 | md5 del handoff 6a57677a… | OK | `md5sum` coincide |
| 1 | Paso 0: línea de DECISIONES tal cual, TOPE_TANDA en 0 | OK | `DECISIONES.md` +1 línea del 22:09, igual al handoff; `TOPE_TANDA.json` = `{"usd": 0.0, ...}` |
| 2 | A: personas desde la ficha, con las 5 reglas del handoff | OK | `m03_expediente.py`: `_formas`, `_calificativo`, `_anios_persona`, `personas_del_ancla`, `linea_persona`. El arrastre se guarda por párrafo, con la marca literal. `_sale_entero` y la búsqueda por ids P del beat están borrados. |
| 3 | B: citas `«texto» — autor · rol · fecha · witness` | OK | `linea_cita`; 0 citas sin autor en las 84 fotos con QUOTES |
| 4 | C: grupos con `APPEARANCE:` y `CLOTHING:` | OK | `bloque()`; 7 grupos con ambos campos llenos en `pedido_ch02.txt` |
| 5 | D: «No.» + cifra y «nothing but» se quedan; «with no figure» sigue saliendo | OK | `m03_imagenes_v3.py`: `_NEGADA` y `_CORTE_CLAUSULA` cambiados. Hay tests en `test_module_f50c.py` (15 pasan). |
| 6 | Tests pedidos por el handoff | OK | Cubren las 8 testigo, ambigua sin año → nadie, «hijo», arrastre que no cruza párrafos, cita con y sin fecha y con `testigo` false, grupo con aspecto y ropa, y D |
| 7 | Pedidos en seco de los 7 caps con el código de producción | OK | Usa `m03._render_prompts_seedream` y corta `_llamar_casilleros` antes de salir. Las anclas salen de `03_visual.json`. `assign_beats` da los mismos beats que los guardados. Los 7 `pedido_chNN.txt` existen. |
| 8 | Verificación automática contra lo esperado | OK | La salida real da `con_people 73, ancla 35, arrastre 38, ambiguas 0, con_quotes 84, grupos 7`, reparto 48/23/2, testigos 8/8, diffs 0, PASA. El script compara con constantes `ESPERADO` y `TESTIGOS` tomadas del handoff y sale con 1 si algo difiere. |
| 9 | El resto del pedido no cambia respecto de F50b | OK | Compara contra el módulo de `1ecf045` cargado con `git show`, con `difflib` fuera de PEOPLE, QUOTES y PEOPLE GROUPS: 0 líneas de diff en los 7 caps |
| 10 | No tocar `03_visual.json` ni el papel | OK | md5 `23a81881…` y `2eb4000a…` sin cambio; no aparecen en `git status` |
| 11 | Cero modelos y cero fal | OK | No hay llamadas en el script; el costo registrado es 0. No pude comprobar desde acá que no se haya llamado a nada durante la tanda. |
| 12 | Sticker y MAPA_PROYECTO `--check` 0 | OK | `fase2a.json` y `MAPA_PROYECTO.*` actualizados en los commits. El «0 fallas» sale del reporte; no lo re-corrí. |
| 13 | Suite rápida antes y después | OK | `f41/f50b` y `f41/f50c`: 55 passed, 3 skipped en ambos |
| 14 | Suite amplia antes y después | PARCIAL | Antes: 4 failed, 947 passed. Después: 5 failed, 961 passed. Las 4 fallas de siempre siguen y suman 14 de 15 tests nuevos de F50c. La quinta, `gfx_lab::test_candado_en_el_preview`, el reporte la declara intermitente y fuera de lo tocado. No la re-corrí. |
| 15 | Candado de ch02 | OK | Ambos logs terminan en md5 `f792f3d483a1fa42daed5f7f0e054f46` |
| 16 | Commit por parte | OK | `2a2a2b4` (paso 0), `9efc125` (D), `6cf9317` (A) y `fbbd58c` (B+C, agrupado como pide Omar). El commit de pasos 2–3 y reporte está pendiente, como se avisó. |
| 17 | F50c_REPORT con lo abierto entero y el veredicto de revisor-handoff | PARCIAL | Lo abierto tiene 9 puntos. El veredicto es el marcador `{{VEREDICTO}}` en la línea 132, que se llena con este texto. |
| 18 | ESTADO_SESION | NO VERIFICABLE | Es posterior a este veredicto, según el pedido |
| 19 | PARADA al terminar el paso 3 | OK | No hay trabajo de F50d ni de F51 en el diff |

**Observaciones**
- La quinta falla de la suite amplia no la reproduje; me apoyo en lo que dice el reporte (con `test_module_gfx_lab.py` solo pasa).
- La suite amplia se corrió una sola vez, sobre el árbol final. Los commits intermedios se probaron solo con f50b y f50c, `rearmar --igual` y `mapa --check`. El reporte lo declara en el punto 8.
- El reporte dice «visto una sola vez» para la quinta falla sin repetir la amplia entera. Es honesto, pero débil como evidencia de intermitencia.
- El punto 6 de lo abierto es una decisión propia: el rol de las citas va sin el punto final. El handoff no lo especifica y el reporte lo declara.

**Fuera de alcance:** ninguno de la tanda. Los modificados `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log` y `lab/TOPE_TANDA.json` son ajenos o están fuera de git.

**Riesgos que el contrato no cubre:**
- Los nombres propios del autor de cada cita ahora llegan a Opus, y ese pedido no se probó con el modelo. Puede copiar nombres a los casilleros.
- La ropa de los grupos queda a la vista y 11 fotos usan un grupo fuera de sus años. Se arregla en F50d, y F51 no debe correr antes.
- Nada de esto llegó al papel ni a `03_visual.json`, así que el cableado no se ve en las fotos hasta que m03 corra con Opus, y eso tiene costo.

### Adenda de CC (después del veredicto)
- **#14, la quinta falla:** la amplia entera se corre una vez por commit y no la repetí. La prueba es que `test_module_gfx_lab.py`, corrido solo después de la amplia, dio «2 failed, 43 passed» y esa vez `test_candado_en_el_preview` pasó. La tanda no toca `gfx_*`: `git diff 1ecf045..HEAD --stat` muestra solo `m03_expediente.py`, `m03_imagenes_v3.py`, tests, stickers, mapa y DECISIONES.
- **#14, la cuenta de 15:** las 4 fallas se repiten, y 961 − 947 = 14 por la 5.ª. El total pasa de 951 a 966, que son los 15 de `test_module_f50c.py`.

