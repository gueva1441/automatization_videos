# HANDOFF F51c — tres bugs del armado de fotos: «Court», el corte de la zona Veo y el paso 1 de `anio_final`

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · **US$ 0**: sin fal ni LLM · 4 etapas y PARADA.

## Por qué, con datos (simulado por el analista sobre Wittenoom)
1. **«Court».** `name_matching.scrub_documented_names` cambia por un descriptor cualquier apellido de `documented_people` que aparezca en el prompt. En Wittenoom, «Court», apellido de un político documentado, choca con «Supreme Court»: la 6/3 sale «…1988 Perth Supreme a State premier whose government rejected…».
   - Medido sobre los casilleros crudos de las 96 fotos, con el canon viejo y con el nuevo (22 personas en los dos): **1 foto con coincidencia (6/3, «Court»), y 0 con un nombre real de persona.** Opus no escribe nombres propios: la regla R3a del pedido de casilleros ya lo pide.
   - El borrado solo rompe. Omar, 2026-10-29 00:07: **QUITAR, no agregar reglas.**
2. **Corte de la zona Veo.** La zona Veo es la parte de la narración que acompaña al clip de 8 s. Hoy `m03_visual` la corta con una cuenta de caracteres (l. ~2174, `int(8.0 × chars/s)`), y el corte cae a mitad de palabra:

| cap | posición | corte de hoy | oración más cercana | Δ |
|---|---|---|---|---|
| 1 | start | «paredes de \| chapa.» → la primera foto de apoyo arranca en «chapa.» | después de «chapa.» | +6 caracteres ≈ 0,44 s |
| 7 | end | «salud y seguri \| dad pública».» → la última foto de apoyo termina en «seguri» | después de «pública».» | +13 caracteres ≈ 0,94 s |

   `fase2b` pone el clip Veo con su duración real y arranca las fotos de apoyo después del clip (l. 1061–1078), con una guarda para el ancla que cae antes (l. 801). Mover el corte menos de 1 s no cambia los tiempos del video: solo cambia qué texto ve cada prompt.
3. **Paso 1 de `anio_final`.** Hoy la prioridad la tiene «el primer año escrito en el ancla» sobre el `year` de Opus. En las 96 fotos hay 29 que usan el paso 1, y en 28 Opus da el mismo año. **La única que difiere, la 3/16, la acierta Opus:** el ancla dice «En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión», o sea 1962, y el paso 1 pone 1961. Opus ya ve ese año en el expediente («YEAR: 1961», `m03_expediente` l. 196) y lo corrige con el contexto. El regex no puede leer «al año siguiente». **Voto del analista:** borrar el paso 1 y que el orden quede `year` de Opus → respaldo del expediente. Requiere el OK de Omar (etapa 0).

## Orden re-derivado
- ¿Construye sobre código que ya se decidió reemplazar? No. Borra 2 caminos viejos y arregla 1 corte.
- ¿Alguna decisión de hoy cambia el orden? No. F51d (regenerar Wittenoom) necesita los 3 arreglos antes de volver a correr m03.

## Módulos que toca
| módulo | hoy | después |
|---|---|---|
| `script_engine/name_matching.py` | `scrub_documented_names` + `iter_name_patterns` (lo usa `m05_judge`) | se borra `scrub_documented_names` y su descriptor (`_neutral_descriptor`, si nadie más lo usa); `iter_name_patterns` se queda |
| `script_engine/m03_imagenes_v3.py` | `f8_backstop` llama al borrado de nombres; `anio_final` con paso 1 «dicho en el ancla» | `f8_backstop` sin el borrado y sin el parámetro `documented` (se actualizan sus llamadas); `anio_final` = 1) `year` de Opus (1800–2100) → 2) respaldo del expediente, con fuentes renumeradas |
| `script_engine/m03_visual.py` | `_carve_veo_zones` corta en el carácter `veo_zone_chars` | el corte se mueve al final de oración más cercano (mismo regex `[.!?…]+` que `_sentence_content_spans`); sin final de oración en la narración, al espacio más cercano; empate → el que deja la zona Veo más corta (el clip dura 8 s fijos: el texto de la zona nunca pasa al después del clip); se borra el import del borrado |
| tests: `test_module_f50b.py` (anio_final), `test_module_f51c.py` nuevo | — | ver etapa 2 |
| `DECISIONES.md` | — | 2 líneas (etapa 0) |

**No se toca:** `m03_visual` l. 645 (el tramo del canon por foto), que sigue eligiendo con `anio_ancla`. En la 3/16, 1961 y 1962 caen en el mismo tramo. Alinearlo es otra variable y va a la lista. Tampoco se toca el expediente: Opus sigue viendo «YEAR: …».

**Lab:** `lab/hyperframes/f50g/rearmar.py` y `f51a/contrato.py` llaman a `f8_backstop` con `documented`. Se actualizan para que el contrato F51a siga corriendo. Los demás scripts de lab que se rompan se listan, sin tocarlos. `_lab_name_scrub.py`, en la raíz, se borra porque solo prueba la función borrada.

## Constantes
| valor | origen | quién |
|---|---|---|
| 8 s del clip Veo | `VEO_CLIP_DURATION_SEC`, `m03_visual.py` l. 842 (ya existe) | sin cambios |
| regex de fin de oración `[.!?…]+` | `_sentence_content_spans`, `m03_visual.py` (ya existe) | sin cambios |
| años válidos 1800–2100 | `anio_final`, handoff F48 §Constantes (ya existe) | sin cambios |

No hay números nuevos.

## Etapa 0 — DECISIONES
md5 de este handoff en el reporte. Al final de `DECISIONES.md`, tal cual:
```
- 2026-10-29 12:10 · **F51c:** a) se borra `scrub_documented_names` (en Wittenoom, 0 nombres reales en 96 fotos y 1 falso positivo, «Court»); b) el corte de la zona Veo va al final de oración más cercano (sin oración, al espacio más cercano; empate → zona Veo más corta); c) `anio_final` pierde el paso 1 «dicho en el ancla»: manda el `year` de Opus y después el respaldo del expediente (en 29 fotos con paso 1, 28 coinciden con Opus y en la que difiere, 3/16, acierta Opus) · Omar · F51c
```
Commit. Salida: `tail -1`.

## Etapa 1 — código (US$ 0)
1. `name_matching`: antes de borrar, `grep` de `scrub_documented_names` y `_neutral_descriptor` en todo el repo. Si queda algún uso en producción además de `m03_imagenes_v3` y el import de `m03_visual`, PARADA.
2. `f8_backstop` sin el borrado ni el parámetro. Se actualizan las llamadas: `m03_visual` l. ~693, `rearmar.py` y `contrato.py`.
3. `anio_final` sin el paso 1. Se actualizan el docstring y los textos de `anio_fuente`.
4. `_carve_veo_zones` con el corte movido (regla de arriba). Firma y retorno sin cambios.

## Etapa 2 — tests
- `f50b`: `test_anio_final_en_orden` reescrito al orden nuevo. Ancla con año + `year` distinto → gana `year`. `year` inválido → respaldo.
- `f51c` nuevo:
  - (a) una foto con el apellido de una persona documentada pasa por `f8_backstop` sin cambios;
  - (b) `_carve_veo_zones` con las narraciones **reales** de los caps 1 y 7 de Wittenoom (`01b_narration.json`) y su `veo_zone_chars` real (`sync_map`) → el corte cae justo después de «chapa.» (cap 1, start) y después de «pública».» (cap 7, end), y ninguna zona empieza ni termina a mitad de palabra;
  - (c) una narración sin punto → corta en un espacio;
  - (d) el empate → zona Veo más corta.
- El contrato F51a sigue en 20/20: ninguna de sus 20 fotos es 6/3, 7/11 ni 3/16.

## Etapa 3 — en seco sobre Wittenoom (sin escribir)
`lab/hyperframes/f51c/rearmar_todo.py`: rearma en memoria las 96 fotos con el código nuevo y el canon vivo (F51b), con el año recalculado por `anio_final`. Salida, `lab/hyperframes/f51c/REARMADO_F51c.md`:
- qué fotos cambian contra el rearmado de F51a, y por cuál de los 3 arreglos. Se espera: 6/3 (vuelve «Supreme Court»), 7/11 si su texto lleva «Court», 3/16 (1961 → 1962). Cualquier otro cambio → listarlo con su motivo;
- los prompts enteros de 6/3, 7/11 y 3/16, antes y después;
- los cortes Veo nuevos de los caps 1 y 7: los últimos 40 caracteres de la zona Veo y los primeros 40 de las fotos de apoyo (cap 1), y al revés para el cap 7. Son solo los cortes: las anclas que eligió Opus no se recalculan sin LLM.

**Ojo:** las 20 fotos con ids de grupo viejos (F51b, abierto 2) no van a pegar aspecto en este rearmado. Es lo esperado, no es de esta tanda: se arregla en F51d al correr m03 de nuevo.

## Al cerrar
- Suite rápida, suite amplia (`lab/hyperframes/f41/verificar.sh`), candado ch02 (`f792f3d4…`) y contrato F51a.
- Commit por etapa con F51c. ESTADO_SESION y `lab/hyperframes/f51c/F51c_REPORT.md`, con lo abierto entero y el veredicto íntegro de `revisor-handoff`.
- **PARADA.**

## Reglas fijas
- Sin fal y sin LLM. No escribir `03_visual.json`, el canon ni topics_db.
- No tocar `cost_tracker` (F51e) ni el pedido del canon.
- Ninguna regla nueva aparte de las 3 de arriba. Subagentes en paralelo: tests, grep y rearmado.

## Lista (no se hace aquí)
- `m03_visual` l. 645: el tramo del canon por foto sigue usando `anio_ancla`. Alinearlo con `anio_final` es otra variable.
- `_lab_name_scrub.py` (borrado) y los scripts de lab que dependan de `scrub_documented_names` → listarlos.
