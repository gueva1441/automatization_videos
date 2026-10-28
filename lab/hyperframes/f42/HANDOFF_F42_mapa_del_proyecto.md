# HANDOFF F42 — Mapa completo del proyecto (solo lectura, US$ 0)

Analista · 2026-10-27 22:20 · rama `f11-guion-v4` · sesión **nueva** de CC (pedido de Omar).

## Por qué
Omar pidió (22:06) ver **todos** los módulos y fases del proyecto, leídos enteros. Hoy `lab/MAPA_MODULOS.md` cubre solo la capa gfx (unos 25 módulos de unos 114 de producción). En F41 el analista propuso «cablear» algo que ya existía desde junio porque no había mapa del orquestador ni del form.

Este mapa es la base de la **auditoría**, que va en una tanda aparte (F43): debilidades, código muerto y mejoras con archivo:línea.

## Chequeo del analista antes de escribir (skill handoff-analista §0)
- ¿Construye sobre código que se va a reemplazar? No. Es solo lectura; extiende el generador de mapa que ya existe (`lab/tools/mapa_modulos.py` + `mapa_hechos.py`, de F33 §D).
- ¿Alguna decisión de hoy cambia el orden? Sí, dos, y las dos entran en el paso 0:
  - Omar borró el chequeo de RAM.
  - Omar limpió el research.
- Hay una corrida viva: Omar lanzó un tema nuevo desde el form a las 21:58. **No se toca nada de `data/`, `output/` ni `logs/`, y no se cierra ningún python, ffmpeg ni node que no sea de esta tanda.**

## Constantes
| valor | origen | quién |
|---|---|---|
| ninguno nuevo | — | — |

- Número de workers: uno por zona (§B). Si un worker no puede leer enteros todos los archivos de su zona en un solo contexto, la zona se parte. Es derivado del material, no un número fijo.
- Tope de gasto: US$ 0,00 (`lab/TOPE_TANDA.json`). Ninguna llamada a API.

## Módulos que toca (hoy → después)
| archivo | hoy | después |
|---|---|---|
| `lab/tools/mapa_hechos.py` | Saca del código (AST + git) quién importa a quién y en qué commit nació cada archivo, solo para gfx. | Lo mismo para **todo** el código de producción. Además: llamadas por `subprocess` a `*.py`, la secuencia de etapas de `run_pipeline` leída del código, las funciones sin llamador, el último commit con su tanda (prefijo `fNN` del mensaje), y el md5 de cada archivo. |
| `lab/tools/mapa_modulos.py` | Arma `MAPA_MODULOS.md/.json` con los stickers escritos dentro del `.py`. | Arma `lab/MAPA_PROYECTO.md/.json` con los hechos + los stickers leídos de `lab/mapa/stickers/<zona>.json`. Tiene un modo `--check` que falla si un módulo de producción no tiene sticker o si su sticker está viejo. |
| `lab/mapa/stickers/*.json` (nuevo) | — | Un archivo por zona, escrito por su worker después de leer cada archivo entero. |
| `.claude/hooks/guard_mapa.py` + `.claude/commands/tanda.md` + `.claude/hooks/README.md` | Avisan sobre `MAPA_MODULOS` solo si se tocan `gfx_*`/`fase2b`. | Apuntan a `MAPA_PROYECTO`. El aviso vale para cualquier módulo de producción cuyo sticker quede viejo (usa `--check`). |

`lab/MAPA_MODULOS.md/.json` se **borran** (regla 10: lo viejo se borra, no se apaga). Antes de borrarlos, sus stickers de gfx se pasan a `lab/mapa/stickers/fase2b_gfx.json` como punto de partida: el worker de esa zona los relee contra el código y los corrige. `grep -rn MAPA_MODULOS` en `.claude/`, `lab/tools/` y `CLAUDE.md` debe dar 0 al final; en reportes viejos queda como historia.

## Qué es «producción»
Se define por código, no por lista:
- `.py` de la raíz que no empiecen con `_`, `test_` ni `diag`.
- `script_engine/*.py`, `researcher_steps/*.py`, `tools/*.py`.
- Los no-`.py` que la cadena carga: `qa_form.html` y lo que sirva `qa_studio_server`, `gfx_profiles/*.json` (solo nombre y claves; está fuera de git), `script_engine/gfx_templates/`, `.claude/hooks/*`, `.claude/agents/*`, `.claude/commands/*`.

`--check` falla si aparece un archivo de producción sin sticker. Así, un módulo nuevo de mañana no queda afuera del mapa.

## A — Los hechos, por código (CC principal)
1. Extender `mapa_hechos.py` a todo lo de producción:
   - imports (también los que están dentro de funciones);
   - `subprocess` con `*.py` en la lista de comandos (así se ve `run_pipeline` → `fase1_5`/`fase2a`/`fase2b`/`fase3`);
   - funciones definidas y sus llamadores en producción y en tests, por separado;
   - commit de nacimiento, último commit y su tanda;
   - md5.
2. **Secuencia del form, leída de `run_pipeline.py` con AST**, sin copiarla a mano: las etapas de `sequence()` en orden, con el comando de cada una y su compuerta. Si mañana cambia `sequence()`, el mapa cambia solo.
3. **Alcance por etapa:** desde el script de cada etapa, los módulos alcanzables por import. Cada módulo queda marcado así:
   - con las etapas que lo usan;
   - «compartido» si lo usa más de una etapa;
   - «solo herramienta manual» si solo lo alcanzan `gfx_lab_server`, `mixer_server`, `m09_review_server`, `tools/*` u otros puntos de entrada que no lanza el form (la lista de puntos de entrada también sale del código: archivos con `if __name__ == "__main__"`);
   - «huérfano» si nada lo alcanza.
4. Tests: `pytest --collect-only -q` sobre todos los `test_*.py` de la raíz (**no se corren**: hay tests con API y una corrida viva). La salida es una tabla: archivo de test → módulos que importa → «colecta» o «error de import» con el símbolo que falta (esto verifica el a3 de F41).
5. **Salida de A pegada en el reporte:** el JSON de hechos de 3 módulos (`run_pipeline`, `fase1_5`, `m01e_pantalla`) y la tabla de etapas. **PARADA corta** antes de B solo si el prompt no autoriza A → C.

## B — Los stickers, con workers en paralelo (Sonnet medium, uno por zona)
Cada worker:
- lee **enteros** los archivos de su zona y los hechos de A;
- escribe en `lab/mapa/stickers/<zona>.json`, por módulo:
  - `sticker`: qué hace para el video, en lenguaje llano, sin jerga, 1 a 3 oraciones;
  - `recibe` / `entrega`: archivos o datos concretos, con su ruta tipo (`data/scripts/_steps/<id>/01a_escaleta.json`);
  - `modelo`: si llama a un LLM, cuál y para qué;
  - `etapa`: la de A, verificada leyendo el código;
  - `estado`: vivo / solo herramienta manual / huérfano / roto (import que falla), con la línea que lo prueba;
  - `funciones_muertas`: las de A que confirma leyendo, sin contar las que se llaman por nombre en string o por `getattr`;
  - `md5`: el del archivo que leyó (así `--check` detecta sticker viejo);
- escribe aparte `lab/mapa/notas_auditoria_<zona>.md`: lo raro que vio, con archivo:línea. **Sin proponer cambios ni tocar código**: es materia prima para F43.

Zonas (asignación por patrón; los archivos que no caigan en ninguna van a la zona 5, y `--check` confirma que no queda ninguno):
1. **Descubrir y research:** `niche_discoverer`, `nicho_config`, `topic_researcher`, `topic_validator`, `topics_db`, `subtopic_*`, `youtube_scanner`, `transcript_fetch`, `m_judge_seeds`, `evidence`, `learned_patterns`, `fase1.py`, `researcher_steps/*`, `purge_history`, `migrate_*`.
2. **Guion (Fase 1 de la ficha al papel):** `fase1_5`, `m01a_*`, `m01b_*`, `m01c_*`, `m01d_*`, `m01e_*`, `guion_v3_reglas`, `guion_v4`, `nombres`, `num_es`, `name_matching`, `tts_tags`, `video_length`.
3. **Fase 2a (voz, música, imágenes):** `fase2a`, `m02_5_*`, `tts_normalizer`, `audio_*`, `music_*`, `m07_*`, `m03_*`, `foto_madre`, `image_grade`, `vision_validator`, `zoom_judge`, `parallax_*`, `depth_probe`, `art_*`, `engine_profiles`, `flow_*`, `anchor_timing`, `m05_*`, `m06_*`, `voz_*`, `subs_remap`, `patch_sync_map_mixing`, `promote_palette_*`.
4. **fase2b y capa gráfica:** `fase2b`, `gfx_*` (raíz y `script_engine`), `pantalla_*`, `clima`, `aprobacion`, `freeze_check`, `transition_*`, `gfx_lab_server`, `mixer_server`, `gfx_templates/`.
5. **Orquestador, form, fase3 y utilidades:** `run_pipeline`, `qa_studio_server`, `qa_form_markers`, `qa_form.html`, `fase3`, `m09_*`, `csv_exporter`, `version_stamp`, `report_foto_madre_edits`, `config` (solo nombres de claves, nunca valores), `cost_tracker`, `error_handler`, `*_helpers`, `asset_manager`, `tools/*`, `.claude/*`.
6. **Tests, lab y sueltos:** lee la tabla de A.4 y clasifica los `test_*.py`, los `_*.py`/`diag*.py` de la raíz y `lab/**/*.py` así: vivo · historia (lab de una tanda cerrada) · roto a sabiendas (a3 de F41) · roto sin saberlo. No hace sticker por archivo de lab, solo la tabla.

Usá todos los subagentes en paralelo que el trabajo permita (preferencia de Omar). Partí una zona si no entra entera en un contexto.

**Salida de B pegada en el reporte:** el sticker de 2 módulos por zona y el conteo por estado.

## C — El mapa armado y su chequeo (CC principal)
1. `python lab/tools/mapa_modulos.py` → `lab/MAPA_PROYECTO.md` + `.json`, con:
   - **Flujograma** (Mermaid) de la cadena como la corre el form: research → GUION → compuerta del papel → VOZ → ASSETS → VISOR → FONDOS → GUION DE PANTALLA → compuerta → RENDER gfx → fase3. Cada caja lleva su script, los módulos propios de esa etapa y el modelo que paga. Las cajas salen de A.2, no se escriben a mano.
   - Tabla por módulo: sticker · recibe · entrega · modelo · etapa(s) · quién lo llama · nació / último cambio (tanda) · estado.
   - Secciones aparte: «compartidos», «solo herramienta manual», «huérfanos», «rotos», «funciones muertas» y la tabla de tests de A.4.
2. `python lab/tools/mapa_modulos.py --check` → exit 0. Probalo además así: tocá un archivo en una copia temporal fuera del repo, o simulá un md5 distinto, y mostrá que falla con el nombre del módulo. Pegá las dos salidas.
3. Test nuevo `test_module_f42_mapa.py`:
   - `--check` da 0;
   - las etapas de `MAPA_PROYECTO.json` son las de `run_pipeline.sequence` leídas por AST;
   - todo archivo de producción tiene sticker.
4. Actualizar `guard_mapa.py`, `tanda.md` y `hooks/README.md` a `MAPA_PROYECTO` (sección «Módulos que toca»).
5. Borrar `lab/MAPA_MODULOS.md/.json`. `grep -rn MAPA_MODULOS .claude lab/tools CLAUDE.md` = 0.
6. **Chascada** (va en el mismo commit de C): el paso 8 de `tanda.md` tiene valores viejos. Dice candado `38e5ba14…`, «5 fallas previas» y lista `01b*`. Cambialo a los vigentes de `lab/ESTADO_SESION.md` (candado `f792f3d4…`, 2 fallas previas `m03_merge_timing`, `verificar.sh` de F41 con `nullglob`).
7. **Salida de C pegada en el reporte:** el flujograma entero, la tabla de las etapas y los conteos por estado.

## Paso 0 (antes de A)
- Este handoff tal cual en `lab/hyperframes/f42/HANDOFF_F42_mapa_del_proyecto.md`, con su md5 verificado contra el del mensaje.
- Agregar al final de `DECISIONES.md`, tal cual:
  `- 2026-10-27 21:50 · **Sin chequeo de RAM antes del render.** La regla de las 00:30 (< 14 GB → PARADA) queda sin efecto; el orquestador no mide RAM ni cierra programas; si el render falla, el reporte sugiere revisar la RAM (mensaje, no freno). Reemplaza a 2026-10-27 00:30 · Omar · aplicada en e68410a.`
  `- 2026-10-27 22:20 · **F42: mapa completo del proyecto**, regenerable por código (`lab/MAPA_PROYECTO.md`, stickers por zona, `--check` en el hook); reemplaza a `MAPA_MODULOS` (solo gfx). Solo lectura, US$ 0. La auditoría va aparte (F43) sobre el mapa · Omar · F42.`
- Commit del paso 0 por rutas explícitas.

## Reglas fijas
- Solo lectura sobre producción: **ningún** `.py` de producción cambia, excepto los de `lab/tools/` y `.claude/` listados arriba.
- Nada en `data/`, `output/` ni `logs/`. No se lanza qa_studio, `run_pipeline`, `fase*` ni pytest corriendo tests (solo `--collect-only`). No se cierra ningún proceso de Omar: hay una corrida viva del form.
- `config.py` y `.env`: solo nombres de claves, nunca valores en el mapa ni en el reporte.
- Un commit por parte (0, A, B, C), por rutas explícitas; push a `origin/f11-guion-v4`. Sin merge; `main` no se toca.
- En cada commit, la suite rápida y el candado de ch02 **no se corren**: comparten GPU y disco con la corrida viva y esta tanda no toca producción. Decilo en el reporte. Sí corre `test_module_f42_mapa.py`.
- Reporte `lab/hyperframes/f42/F42_REPORT.md`: salidas de A, B y C pegadas; «lo que queda abierto» entero; veredicto íntegro de `revisor-handoff`. `lab/ESTADO_SESION.md` al día. Cerrar los subagentes y shells propios. **PARADA.**
