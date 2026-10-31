# HANDOFF F61 — variedad de planos: quitar R7 y el tope del 25 % de m03, medir en texto

Modelo → CC: Opus medium. Subagentes en paralelo donde el trabajo lo permita (Etapa 0: un subagente por pregunta; Etapa B: los 7 caps a la vez, CAP_MAX_WORKERS).

## Por qué (lo que jode al espectador)
En la corrida F60 A3 de Wittenoom (`lab/hyperframes/f60/a3/03_visual_a3.json`, 96 fotos: image_prompts + supplementals + image_f8): wide 57 · extreme_wide 15 · medium 13 · detail 8 · close 3 → **75 % plano general, 3 primeros planos**. Treinta minutos de fotos de lejos cansan. Con F60 las personas ya salen ancladas a su foto madre: alejar la cámara ya no esconde un defecto, esconde las caras y la emoción, que es lo que retiene.

## Causa (medida por el analista, auditada)
Tres textos empujan a lejos; los tres entran a la MISMA llamada de casilleros (`_render_prompts_seedream`, l. 681; los caps con clip por `_render_prompts_seedream_veo`, l. 1944; producción entra por `assign_visual_prompts`):
1. **R7 en el system instruction** — `m03_visual.py` l. 183 (cadena `SYSTEM_INSTRUCTION_VISUAL_SEEDREAM` l. 172 → `_V3` l. 220 → `_si_casilleros` l. 286 → `SYSTEM_INSTRUCTION_CASILLEROS`): «WIDE/EXTREME_WIDE dominates for establishing/architecture/scale/mass events; medium/close ONLY for one human emotion or one texture detail (R7)».
2. **Regla 4 de `COMPOSITION_RULES_V3`** — `m03_imagenes_v3.py` l. 485, que entra al mismo system instruction por `m03_visual.py` l. 228: «At most a QUARTER of the images show a person in medium shot; prefer places, objects, distance and silhouettes.»
3. **El tope en código** — `m03_imagenes_v3.video_audit` l. 532 `lim = int(0.25 * total)` + `m03_visual._f8_fix_video` l. 817–819: lo que pasa el 25 % se rehace con «NO person in medium shot: a wide shot of the place, people small, far or absent». En la A3 `humano_medio = 10` contra un tope de 24 → 0 re-hechuras hoy; frenaría el arreglo apenas se vayan 1 y 2.

Contradicen la tabla de encuadre por tipo de cap que ya existe, `VISUAL_INTENT_BY_INTENT` (l. 518–526), que entra en el **user prompt** como bloque «VISUAL ARC OF THIS CAP» según el `narrative_intent` del cap (`_build_seedream_prompt_step2`, l. 559 y 597): `rising_tension` «Tighter framing», `shock` «Close-up or extreme close-up», `consequences` «Medium framing». En Wittenoom los caps 3–4 son `rising_tension` y el 5 `shock`, y salen en wide igual.

## Constantes
| valor | origen | quién |
|---|---|---|
| se BORRA `0.25` (tope en `video_audit`) y su gemelo «a QUARTER» del prompt | regla 4 de F8 (`COMPOSITION_RULES_V3`); sin línea en DECISIONES | Omar 2026-10-30 22:36 (quitar) |
| `F8_FIX_PASSES = 2` | existente (m03_visual l. 772) | sin cambio (sigue para motivos y cuerpos) |
| ninguna constante nueva | — | — |

## Módulos tocados
- `script_engine/m03_visual.py` (escribe los casilleros de cada foto): hoy empuja a wide (R7) y rehace planos medios → después: el bloque VISUAL ARC OF THIS CAP decide el encuadre; `_f8_fix_video` sigue con motivos (D1) y cuerpos (E).
- `script_engine/m03_imagenes_v3.py` (reglas de composición y auditoría del video entero): hoy pide «a lo sumo un cuarto» y cuenta el exceso → después: sin esa oración ni el conteo.
- Tests: uno nuevo; ningún test vigente usa lo borrado.

## Reglas fijas
- Rama `f11-guion-v4`; `main` no se toca.
- **«D5» nombra dos cosas en el código.** Se borra SOLO la parte humano-en-plano-medio. Quedan intactos: `establishing()`, `caps_sin_establecimiento`, `F8_NOTE_ESTABLISHING`, `F8_NOTE_CERRADA`, `_f8_fix_cap` (l. 784–797) y la segunda oración de la regla 4 («Every cap has at least ONE establishing / exterior image…»).
- No se tocan: `VISUAL_INTENT_BY_INTENT` / `_visual_arc_block` (l. 518–545), la regla del ítem [1] del gancho (l. 561–571), las reglas 1, 2, 3, 5 y 6 de `COMPOSITION_RULES_V3` (manos, sin macro de cara, conteos, armas, pico), D1 motivos, E cuerpos, R5, `DOCTRINE_PEOPLE` (grupos: otra corrida; una variable por vez), l. 184 `camera_angle`.
- Cero fotos, cero clips, cero voz en esta tanda.
- Sin tope de dólares; el gasto se informa al final.

## Etapa 0 — impacto y registro (US$ 0)
0.1 Anotar en `DECISIONES.md` (CRLF, tal cual):
- `2026-10-30 22:34 · F60 se cierra como está; madres de niños (edad) y madres del mismo tipo parecidas → lista «se arregla si se repite» (no afectan la retención) · Omar`
- `2026-10-30 22:36 · F61: se quitan de m03 la regla R7 (plano general domina; medio/cerca solo para una emoción o textura), la oración «a lo sumo un cuarto de fotos con persona en plano medio» de COMPOSITION_RULES_V3 y el tope en código del 25 % con su re-hechura a plano general; el encuadre lo decide la tabla por tipo de cap que ya existe (VISUAL ARC OF THIS CAP); se mide con m03 en texto sobre Wittenoom · Omar · F61`
0.2 Impacto aguas abajo, ya auditado por el analista; CC lo **confirma** con grep y lo pega en el reporte (si encuentra un lector más, PARÁ antes de la A):
- miniaturas: `m09_packaging.prompts_paquetes` (l. 420–436) usa `_render_prompts_seedream` → sus fotos también cambian de encuadre (arco «hook», close/medium). Declarado, no frena. El comentario de m03_visual l. 218 («El SI de arriba (v2 y m09) no cambia») está viejo: corregirlo (chascada);
- gfx: `gfx_style.suggest_movement` (l. 39–47) lee `shot_scale` → más medium/close = más «acercar», menos paneo/alejar. Declarado, no frena;
- QA Studio «rehacer foto» (`qa_studio_server.py` l. 1007–1098) usa `PEDIDO_EDITAR_CASILLEROS` + `armar_item`, no este system instruction → sin cambio;
- `humano_medio`, `exceso_humano_medio`, `human_medium`: sin lectores fuera de m03_visual y m03_imagenes_v3.
0.3 Comparabilidad (dato, ya medido): el runner A3 llama a `assign_visual_prompts`, que corre `_f8_fix_video`; la A3 tiene `_f8_imagenes.rehechas: []` (0 re-hechuras). El «antes» es comparable y B.1 hereda el mismo camino.

## Etapa A — código
A.1 `m03_visual.py` l. 183, reemplazar la línea entera por (byte a byte):
`- shot_scale: one of extreme_wide|wide|medium|close|detail, following the VISUAL ARC OF THIS CAP block when it is present.`
(«when it is present»: `_visual_arc_block` devuelve vacío si el cap no tiene `narrative_intent`; ahí el modelo elige libre.)
A.2 `m03_imagenes_v3.py` l. 485, regla 4 de `COMPOSITION_RULES_V3`: borrar la primera oración. Antes:
```
4. At most a QUARTER of the images show a person in medium shot; prefer places, objects, distance and silhouettes.
   Every cap has at least ONE establishing / exterior image (the place seen from outside or from above).
```
Después:
```
4. Every cap has at least ONE establishing / exterior image (the place seen from outside or from above).
```
A.3 `m03_visual._f8_fix_video` (l. 800–837): borrar el bucle de `exceso_humano_medio` (l. 817–819) y la clave `humano_medio` de `_brief`; docstring sin «D5 humanos en plano medio».
A.4 `m03_imagenes_v3.video_audit`: borrar `human_medium()` (l. 457–459), `hm`, `lim`, `humano_medio` y `exceso_humano_medio` del retorno y del docstring (l. 506–508: que diga D1 y E para personas; `caps_sin_establecimiento` sigue).
A.5 Test nuevo `test_module_f61.py`: el system instruction de casilleros no contiene «dominates», «ONLY for one human emotion», «QUARTER» ni «prefer places, objects, distance»; sí contiene «Every cap has at least ONE establishing»; `video_audit` no devuelve `exceso_humano_medio` y sigue devolviendo `caps_sin_establecimiento`.
A.6 Suites como siempre (ch02 md5, rápida, amplia). **Fallas previas a F61, NO son regresión:** `test_module_138a_doctrina_compartida.py` (l. 25 y 60: sha1 del SI y `m09._HERO_SYSTEM`, que ya no existe desde F58) y `test_module_137_thumbs_ley1.py` (l. 24, mismo `_HERO_SYSTEM`). Se borran (lo viejo se borra; prueban un camino que F58 borró) y se declaran. `test_module_f8.py` l. 316–337 sigue verde (los motivos disparan la re-hechura).
Salida en texto: diff de A.1 y A.2 antes/después y lista de lo borrado.

## Etapa B — medición en texto (≈ US$ 2,3; la A3 costó 2,28 según `etapa_a3.json`)
B.1 Runner `lab/hyperframes/f61/etapa_f61_m03.py` = copia de `lab/hyperframes/f60/etapa_a3_m03.py` (mismas entradas, canon A3, anclas fijas de `a/03_visual_despues.json`, 7 caps en paralelo, mismo paso por `assign_visual_prompts`) con salidas en `f61/`.
B.2 Tabla en texto, antes (`f60/a3/03_visual_a3.json`) contra después:
- `shot_scale` total y por cap junto a su `narrative_intent` (Wittenoom: 1 hook · 2 setup · 3–4 rising_tension · 5 shock · 6 resolution · 7 outro);
- fotos con persona documentada (`persona` no vacío): `shot_scale` antes/después;
- `camera_angle`: las 6 más comunes;
- `caps_sin_establecimiento` antes/después;
- re-hechuras del video (`_f8_imagenes.rehechas`: motivos, cuerpos) **y** por cap (`_f8_rehecha`: ESTABLISHING / CERRADA / BODY_HOOK / ARMA) antes/después.
B.3 Pegar 10 prompts completos del después: los 3 `close`/`detail` de mayor `emotional_rank`, 3 `medium` con persona, 2 del cap 5 (shock), 2 del cap 2 (setup).
B.4 Costo real.

## PARADA B
Nada de fotos ni producción. El analista lee la tabla y los 10 prompts y le dice a Omar si sale sano o se fue al otro extremo.
