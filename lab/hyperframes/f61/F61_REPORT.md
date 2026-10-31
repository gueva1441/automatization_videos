# F61 — variedad de planos: quitar R7 y el tope del 25 % de m03, medir en texto

Rama `f11-guion-v4` · handoff `HANDOFF_F61_planos.md` (md5 9892c940db0e7b84f189a7b3e8ed249b, verificado) · 2026-10-30 · cero fotos, clips o voz · PARADA B.

## Etapa 0 — impacto y registro (US$ 0)

### 0.1 DECISIONES.md
Las 2 líneas del handoff (22:34 y 22:36) agregadas tal cual, CRLF (201 saltos, 201 CRLF), como ítems `- …` al final del archivo.

### 0.2 Impacto aguas abajo — confirmado con grep (un subagente por pregunta, solo lectura)
| lector | hallazgo | frena |
|---|---|---|
| miniaturas `m09_packaging.prompts_paquetes` | `m09_packaging.py:425,436-437` → `m3._render_prompts_seedream(...)`; esa función pasa `system_instruction=SYSTEM_INSTRUCTION_CASILLEROS` fijo (`m03_visual.py:680-681`), que sale de `_si_casilleros()` ← `SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3` ← `SYSTEM_INSTRUCTION_VISUAL_SEEDREAM` (l. 172; R7 en la l. 183). m09 no usa la v2 directamente en ningún lado (grep: solo l. 172 y 221). **Las miniaturas heredan el cambio** (arco «hook»: close/medium). El comentario de la l. 218-219 («El SI de arriba (v2 y m09) no cambia») era falso en lo de m09 → **chascada: corregido** (ver Etapa A). El comentario gemelo de `test_module_f8.py:232` (`# v2 y m09`) queda como está (es un comentario de test). | no |
| gfx `gfx_style.suggest_movement` (l. 34-50) | `wide = "wide" in shot` (wide y extreme_wide valen igual); con persona y no-wide → «acercar»; close/detail → «acercar»; wide + multitud → paneo; wide + lugar → 3D (`already_out=True` en `movement_for`, l. 59) o alejar; resto → acercar. **Más medium/close ⇒ más «acercar», menos paneo/3D**; ningún chequeo exige una cuota (`identity_violations` l. 153-174 no cuenta movimientos); el alejar de apertura/cierre es por posición (l. 62-63). `gfx_lab_server.py:355,361` reutiliza `suggest_movement` solo para mostrar. | no |
| QA Studio «rehacer foto» | `qa_studio_server.py:940-941` `_editar_con_opus` llama a `_call_with_validation_retry` **sin** `system_instruction=`; `m03_visual.py:1783/1817` y `:314-319` pasan `None`; `claude_helpers.py:169-170` omite `system` con None. Solo toma el enum `VALID_SHOT_SCALES` (l. 946-949). **Sin cambio.** | no |
| `humano_medio`, `exceso_humano_medio`, `human_medium` | Código: solo `m03_imagenes_v3.py:457-459, 508, 529-534` y `m03_visual.py:801, 817-819, 836`. Fuera: ningún .py (producción, tests de la raíz, lab, `_lab_*`), ningún doc vivo, ningún sticker. Solo registros de corridas viejas (`_auditoria`/`antes`/`despues` en json de lab) y `lab/mapa/hechos.json:23305` (mapa generado). Llamadores indirectos sin leer la clave: `test_module_f8.py:219,225` (`video_audit`) y `:318-337` (`_f8_fix_video`). | no |
| otros lectores de `shot_scale` | `engine_profiles.py:84` (orden de slots del prompt: solo lee), `gfx_lab_server.py:361` (UI), `qa_studio_server.py:946-949` (enum). fase2b, flow_director, parallax, depthflow: sin `shot_scale`. **Ninguno depende de que dominen los planos generales.** | no |

**Sin PARÁ**: no hay lector fuera de la lista del handoff que dependa de los planos generales.

### 0.3 Comparabilidad
`f60/a3/03_visual_a3.json`: `_f8_imagenes.antes = despues = {total 96, motivos {documento en escritorio: 1}, exceso_motivos [], cuerpos [], humano_medio 10, caps_sin_establecimiento []}`, `rehechas: []`; `_f8_rehecha` por cap: ninguna. El runner A3 pasa por `assign_visual_prompts` → `_f8_fix_video`; B.1 hereda el mismo camino. Antes (96 fotos): wide 57 · extreme_wide 15 · medium 13 · detail 8 · close 3 (75 % plano general, 3 close).

## Etapa A — código

### A.1 `script_engine/m03_visual.py` l. 183 (byte a byte)
```
- - shot_scale: one of extreme_wide|wide|medium|close|detail. WIDE/EXTREME_WIDE dominates for establishing/architecture/scale/mass events; medium/close ONLY for one human emotion or one texture detail (R7).
+ - shot_scale: one of extreme_wide|wide|medium|close|detail, following the VISUAL ARC OF THIS CAP block when it is present.
```
La l. 184 (`camera_angle … (R7)`) no se toca. Chascada 0.2 (comentario l. 218-219):
```
- # y de contenido sensible. El SI de arriba (v2 y m09) no cambia.
+ # y de contenido sensible. El SI v2 de arriba no cambia; m09 (miniaturas, `prompts_paquetes`) entra por
+ # `_render_prompts_seedream` y hereda el SI de casilleros (F61: el comentario viejo «v2 y m09 no cambia» estaba desactualizado).
```

### A.2 `script_engine/m03_imagenes_v3.py` l. 485, regla 4 de `COMPOSITION_RULES_V3`
```
- 4. At most a QUARTER of the images show a person in medium shot; prefer places, objects, distance and silhouettes.
-    Every cap has at least ONE establishing / exterior image (the place seen from outside or from above).
+ 4. Every cap has at least ONE establishing / exterior image (the place seen from outside or from above).
```

### A.3 / A.4 Lo borrado (y lo que queda de «D5»)
- `m03_visual._f8_fix_video`: el bucle `for cap, i in cur["exceso_humano_medio"]` con la nota «NO person in medium shot: a wide shot of the place, people small, far or absent» (3 líneas); la clave `"humano_medio": len(a["humano_medio"])` de `_brief`; docstring «(D1 motivos, E cuerpos, D5 humanos en plano medio)» → «(D1 motivos, E cuerpos)».
- `m03_imagenes_v3`: la función `human_medium()` entera (3 líneas + 2 en blanco); en `video_audit`: `hm`, el `if human_medium(it): hm.append(...)`, `lim = int(0.25 * total)` y las claves `humano_medio` / `exceso_humano_medio` del retorno; docstring: «(D1, D5, E)» → «(D1 motivos y E cuerpos para las personas; D5 solo el establecimiento por cap)», sin las dos claves, + nota F61.
- Quedan intactos: `establishing()`, `caps_sin_establecimiento`, `F8_NOTE_ESTABLISHING`, `F8_NOTE_CERRADA`, `_f8_fix_cap`, la oración «Every cap has at least ONE establishing…», `VISUAL_INTENT_BY_INTENT` / `_visual_arc_block`, la regla del ítem [1] del gancho, reglas 1-3 y 5-12, D1, E, R5, `DOCTRINE_PEOPLE`, `F8_FIX_PASSES = 2`. Ninguna constante nueva; «0.25» y «a QUARTER» borrados sin reemplazo.
- Diff: `m03_imagenes_v3.py` +13/−24 líneas con docstring, `m03_visual.py` +5/−7 (las dos en CRLF, conservado).

### A.5 Test nuevo `test_module_f61.py` (3 tests)
SI de casilleros sin «dominates», «ONLY for one human emotion», «QUARTER», «prefer places, objects, distance»; con «Every cap has at least ONE establishing» y la línea nueva de `shot_scale` (y la de `camera_angle (R7)` intacta); `video_audit` sin `exceso_humano_medio`/`humano_medio`, con `caps_sin_establecimiento` y `establishing()`; `_f8_fix_video` sin la nota de plano medio, con motivos y cuerpos; `_visual_arc_block` presente.

### A.6 Tests borrados y declarados (fallaban antes de F61)
- `test_module_138a_doctrina_compartida.py` (l. 25 sha1 del SI del seal 678abea y l. 60 `m09._HERO_SYSTEM`) y `test_module_137_thumbs_ley1.py` (l. 24 `m09._HERO_SYSTEM`): corridos antes de tocar código → `AttributeError: module 'script_engine.m09_packaging' has no attribute '_HERO_SYSTEM'` (borrado en F58). Son scripts (`main()`), no los recoge `verificar.sh`. Borrados con `git rm`, no re-sellados.
- **Declaración (no estaba en el handoff):** `test_module_f8.py::test_pasada_de_video_rehace_excesos_menos_el_cuadro_veo` (l. 316-337) **falló** tras la A.3: su fixture (5 ítems `medium` + «a man», pasillo en 1:0, 1:1, 2:0, 2:1, 7:0) pasaba porque el bucle D5 rehacía también `1:1` (segunda aparición de «pasillo»); sin ese bucle el tercer «pasillo» cae en el cuadro Veo del cap 7, que por diseño nunca se rehace → `exceso_motivos == [(7, 0, 'pasillo')]`. El test prueba motivos y el cuadro Veo, no D5: cambio mínimo de fixture, `7: [it("A corridor at night.")]` → `7: [it("A yard at night.")]`, con comentario F61. Sus 4 aserciones siguen valiendo (motivos a 0, cuadro Veo intacto, notas con «Motifs already used twice», `problems`). El handoff decía que seguía verde: no era así por esa dependencia indirecta.
- `pytest -q test_module_f61.py test_module_f8.py`: 22 passed; con f50b, f60_a3 y f60_bc: 78 passed.

### A.6 Suites (`lab/hyperframes/f41/f61/`)
ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado) · rápida 53 passed, 3 skipped · amplia **1334 passed**, 31 skipped, 3 xfailed, 4 failed = las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2). Stickers de `m03_visual` y `m03_imagenes_v3` (zona fase2a) actualizados; MAPA 158 archivos · 0 fallas.

### Veredicto de revisor-handoff — Etapas 0 + A (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

Revisé solo Etapas 0 y A. No ejecuté nada que llame a LLM o fal. El md5 del handoff coincide: 9892c940db0e7b84f189a7b3e8ed249b.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | 0.1 DECISIONES: 2 líneas (22:34 y 22:36) tal cual, CRLF | OK | Las 2 líneas del handoff están como ítems exactos en el archivo. Terminan en `\r\n`. `file` dice "CRLF line terminators". El diff solo agrega esas 2 líneas. |
| 2 | 0.2 Los 4 lectores confirmados con archivo:línea; ningún lector extra que dependa de planos generales | OK | F61_REPORT §0.2 da archivo:línea para cada uno. Mi grep de `shot_scale` en .py fuera de m03 y lab encontró `engine_profiles.py:84`, `gfx_lab_server.py:361`, `qa_studio_server.py:949` y `gfx_style.py:39`. CC los listó todos. No hay un lector nuevo. `humano_medio` y `human_medium`: ningún .py fuera de m03 los lee. |
| 3 | Chascada: comentario l. 218 corregido | OK | `m03_visual.py` l. 218-220: el comentario ya no dice "v2 y m09 no cambia". |
| 4 | A.1 byte a byte | OK | `m03_visual.py` l. 183 es exactamente `- shot_scale: one of extreme_wide\|wide\|medium\|close\|detail, following the VISUAL ARC OF THIS CAP block when it is present.` La l. 184 `camera_angle … (R7)` sigue igual. |
| 5 | A.2 regla 4 sin la primera oración | OK | `m03_imagenes_v3.py` l. 480: `4. Every cap has at least ONE establishing / exterior image (the place seen from outside or from above).` Las reglas 5 y siguientes siguen como estaban. |
| 6 | A.3 `_f8_fix_video`: sin bucle `exceso_humano_medio`, sin `humano_medio` en `_brief`, docstring corregido | OK | `m03_visual.py` l. 801-835. Quedan los bucles de motivos y cuerpos y el filtro de `VEO_CHAPTERS`. `F8_FIX_PASSES = 2` intacto (l. 773). |
| 7 | A.4 `video_audit`: sin `human_medium()`, `hm`, `lim`, `0.25` ni las claves en el retorno | OK | Diff de `m03_imagenes_v3.py`. El retorno es `{total, motivos, exceso_motivos, cuerpos, exceso_cuerpos, caps_sin_establecimiento}`. `establishing()` y `caps_sin_establecimiento` siguen. |
| 8 | Lo que no se toca sigue intacto | OK | El diff no toca `VISUAL_INTENT_BY_INTENT`, `_visual_arc_block`, el ítem [1] del gancho, las reglas 1, 2, 3, 5 y 6, D1, E, R5, `DOCTRINE_PEOPLE`, `_f8_fix_cap`, `F8_NOTE_*` ni `establishing()`. |
| 9 | Ninguna constante nueva | OK | El diff no agrega constantes. |
| 10 | A.5 test nuevo | OK | `test_module_f61.py`, 3 tests. El primero cubre las 4 frases ausentes, "Every cap has at least ONE establishing" presente y la l. 184 intacta. El segundo cubre `video_audit` sin `exceso_humano_medio` y con `caps_sin_establecimiento`. El tercero cubre `_f8_fix_video` (sin nota de plano medio, con motivos y cuerpos). |
| 11 | Tests 138a y 137 borrados con `git rm` y declarados, sin re-sellar | OK | `git status` muestra `D ` (staged) en ambos. F61_REPORT §A.6 los declara. Los stickers y el MAPA ya no los asocian a módulos. |
| 12 | Cambio en `test_module_f8.py` (declaración de CC) | OK, razón correcta | Ver observación 1. |
| 13 | Suites | OK | `f41/f61/onlycap_ch02_nogfx.log`: md5 `f792f3d483a1fa42daed5f7f0e054f46`. `suite_rapida.log`: 53 passed. `suite_amplia.log`: 1334 passed, 4 failed (`m03_merge_timing` ×2, `gfx_lab` ×2). Esas 4 fallas ya aparecían en `f60a/suite_amplia.log`. |
| 14 | Stickers y MAPA | OK | Los md5 de `fase2a.json` (feb7e45f… para `m03_visual`, 93128e21… para `m03_imagenes_v3`) coinciden con los md5 reales de los archivos. `MAPA_PROYECTO.md` está actualizado. |

**Fuera de alcance:** ninguno de lo que toca F61 (`m03_visual.py`, `m03_imagenes_v3.py`, `test_module_f8.py`, `test_module_f61.py`, `DECISIONES.md`, stickers, MAPA, los dos tests borrados). El resto de `git status` (`diag_234_cap4.py`, `f28a.log` y los untracked) viene de antes; no lo atribuyo a F61 y no lo audité en detalle.

**Observaciones**
1. **Fixture de `test_module_f8.py` (l. 331), un solo cambio de palabra: "A corridor at night." → "A yard at night."** Lo juzgo mínimo y la razón es correcta. Con `MOTIF_MAX=2` (`m03_imagenes_v3.py:218`), la fixture tenía 5 ítems con pasillo: 1:0, 1:1, 2:0, 2:1 y 7:0. El exceso real caía en 2:0, 2:1 y 7:0. El cap 7 es de Veo (`VEO_CHAPTERS=(1,7)`) y su imagen 0 se filtra de las notas, así que nunca se rehace. Antes, el bucle D5 borrado hacía que la corrida terminara limpia por una vía indirecta. Sin D5, el exceso del cuadro Veo del cap 7 queda en `despues`. El test prueba motivos y cuadro Veo, no D5, y sus 4 aserciones se mantienen. El handoff decía que seguía verde; eso era incorrecto, y CC lo declaró.
2. La docstring de `video_audit` (`m03_imagenes_v3.py` l. 504) todavía nombra `humano_medio` y "25 %" como nota histórica. No es código ni constante, pero el grep literal de `humano_medio` no queda en cero en ese archivo.
3. Las 4 fallas de la suite amplia son previas, por lo que vi en el log de F60a. No verifiqué por qué fallan.
4. Los dos comentarios que dicen "v2 y m09" en `test_module_f8.py:232` quedan sin tocar. CC lo declaró y es un comentario de test.

**Riesgos que el contrato no cubre:** (a) Sin la regla R7 ni el tope, el único control sobre los planos medios en el prompt es el bloque VISUAL ARC, que se omite si el cap no tiene `narrative_intent`; en ese caso el modelo elige libre. (b) Las miniaturas y el movimiento gfx cambian de reparto de encuadre. Se declaró y no frena, pero no hay test que lo acote. (c) No leí `f61_run.log` ni nada de la Etapa B; es posible que el runner de B comparta código con lo revisado.

#### Adenda de CC
- **Obs. 2:** la mención de `humano_medio` en la docstring de `video_audit` es la nota «F61: sin `humano_medio` ni el tope del 25 %»: documenta lo borrado; no hay código ni constante. Se deja.
- **Riesgo (a):** es lo que dice el handoff («when it is present»: sin `narrative_intent` el modelo elige libre); en Wittenoom los 7 caps traen intent (B.2). **Riesgo (b):** declarado en 0.2, sin test por decisión del handoff («una variable por vez»). **Riesgo (c):** la Etapa B tiene su propio veredicto abajo.

## Etapa B — medición en texto (PARADA B)

B.1 Runner `lab/hyperframes/f61/etapa_f61_m03.py` (copia de `f60/etapa_a3_m03.py`: mismas entradas f54/antes + pool f44/B, ficha y _perfil de producción, canon A3 inyectado por CANON_KEYS, anclas fijas de `f60/a/03_visual_despues.json`, 7 caps en paralelo por `assign_visual_prompts` → `_f8_fix_video`; salidas en `f61/`: `03_visual_f61.json`, `etapa_f61.json`, `etapa_f61.log`). Sobre la copia `f60/base` (el 03_visual previo de la copia respaldado en `f61/03_visual_copia_antes_f61.json`); nunca topics_db ni `_steps` reales. **Cero fotos, clips o voz.** m03 7 caps: **135.6 s · US$ 2.3101** (cost_tracker); caps con `_plan_anchors` real: [] (anclas fijas en los 7); **pares por ancla 96/96** con el antes. Prompts de casilleros capturados: 12 (8 con el bloque VISUAL ARC OF THIS CAP: los 7 caps + 1 re-hechura; los 4 restantes son el escritor de movimiento del clip, `_VEO_MOTION_SYSTEM`, que no lleva ese bloque). Dos system instructions distintos: el de casilleros sin «dominates»/«QUARTER» y con «following the VISUAL ARC…» = True; el otro es `_VEO_MOTION_SYSTEM` (clips), ajeno a F61.

### B.2 Tablas antes (`f60/a3/03_visual_a3.json`) → después (`f61/03_visual_f61.json`), 96 fotos cada uno (image_prompts + supps + image_f8)

| | extreme_wide | wide | medium | close | detail | plano general |
|---|---|---|---|---|---|---|
| antes | 15 | 57 | 13 | 3 | 8 | **75 %** |
| después | 12 | 35 | 37 | 7 | 5 | **49 %** |

Por cap (antes → después; extreme_wide · wide · medium · close · detail):

| cap | narrative_intent | antes | después |
|---|---|---|---|
| 1 | hook | 1 · 1 · 1 · 1 · 1 | 0 · 1 · 2 · 1 · 1 |
| 2 | setup | 2 · 12 · 2 · 0 · 0 | 2 · 7 · 7 · 0 · 0 |
| 3 | rising_tension | 1 · 11 · 3 · 0 · 1 | 2 · 3 · 8 · 1 · 2 |
| 4 | rising_tension | 3 · 8 · 2 · 1 · 0 | 1 · 6 · 7 · 0 · 0 |
| 5 | shock | 2 · 7 · 2 · 1 · 4 | 1 · 3 · 7 · 5 · 0 |
| 6 | resolution | 2 · 11 · 2 · 0 · 1 | 3 · 8 · 4 · 0 · 1 |
| 7 | outro | 4 · 7 · 1 · 0 · 1 | 3 · 7 · 2 · 0 · 1 |

Fotos con persona documentada (`persona` no vacío) — antes: 1 · 21 · 10 · 1 · 0 (33) → después: 0 · 11 · 24 · 2 · 0 (37). Las personas pasan de 2/3 en plano general a 2/3 en medium/close.

`camera_angle` top 6 — antes: [['eye-level', 14], ['low angle', 6], ['high aerial angle', 5], ['eye-level from behind', 2], ['high angle from a ridge', 2], ['high angle looking down', 2]] → después: [['eye-level', 20], ['low angle for scale', 3], ['high aerial angle', 3], ['low angle at ground level', 2], ['slightly low angle', 2], ['eye-level from behind', 2]].

`caps_sin_establecimiento` — antes: [] → después: [] (todos los caps conservan su establecimiento).

Re-hechuras del video (`_f8_imagenes.rehechas`, motivos/cuerpos) — antes: [] → después: []. `_f8` después: antes {'total': 96, 'motivos': {'pasillo': 2, 'documento en escritorio': 1}, 'exceso_motivos': [], 'cuerpos': [], 'exceso_cuerpos': [], 'caps_sin_establecimiento': []} → después {'total': 96, 'motivos': {'pasillo': 2, 'documento en escritorio': 1}, 'exceso_motivos': [], 'cuerpos': [], 'exceso_cuerpos': [], 'caps_sin_establecimiento': []} (motivos «pasillo» 2 = tope, sin exceso).

Re-hechuras por cap (`_f8_rehecha`) — antes: {} → después: {'TIGHTEST framing of the cap (shot_scale close or detail) on ': 1} (una CERRADA: la foto `cerrada` del beat no vino en close/detail a escala humana y `_f8_fix_cap` la rehizo; ESTABLISHING / BODY_HOOK / ARMA: 0 en los dos).

Cambios de `shot_scale` foto a foto (misma ancla): {'close→close': 2, 'wide→medium': 23, 'medium→medium': 11, 'extreme_wide→wide': 5, 'detail→detail': 4, 'wide→wide': 28, 'wide→extreme_wide': 5, 'extreme_wide→extreme_wide': 7, 'medium→close': 1, 'wide→detail': 1, 'extreme_wide→medium': 2, 'close→wide': 1, 'detail→close': 3, 'extreme_wide→close': 1, 'detail→medium': 1, 'medium→wide': 1}. Lo que más pasa: wide→medium 23; también 5 wide→extreme_wide y 5 extreme_wide→wide (ruido de Opus entre corridas); 2 close/detail que se abrieron (close→wide 1, detail→medium 1).

Lectura: el plano general baja de 75 % a 49 %, el medium se triplica (13 → 37), close pasa de 3 a 7, detail baja de 8 a 5. Los caps `rising_tension` (3-4) y `shock` (5) son los que más se cierran (cap 5: 9 general / 2 medium / 5 cerradas → 4 / 7 / 5), `setup` (2) se reparte mitad y mitad y `outro` (7) queda casi igual (wide 7, extreme_wide 3): el arco por tipo de cap manda, como pedía el handoff. No hubo re-hechuras del video ni caps sin establecimiento.

### B.3 10 prompts completos del después

**[close/detail de mayor emotional_rank] `chapters[4].img[15]` · cap 5 · close · Eye-level over-the-shoulder, slightly behind her · R1 · persona [] · 2022** — ancla: «Uno de los hijos dice que ese sitio les cambió la vida para siempre. Daniel no fue el prim»
```
An elderly Spanish widow in her eighties, slight frail build, silver hair pinned back, light olive weathered skin, wearing a dark wool cardigan over a plain blouse, seen from over her shoulder. She sits very still, bent toward a crowded cluster of old sepia family photographs, her body leaning toward one small print of a young miner's bandaged foot. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. A modest Madrid apartment sitting room decades after the mine, an old sideboard and wall densely covered with framed and loose sepia prints from the Wittenoom years, 2022. Hard high-contrast side light from a single narrow window, deep shadows swallowing the rest of the room. Close shot, eye-level over-the-shoulder, slightly behind her, 85mm lens, shallow depth of field, the bandaged-foot print sharp and her silhouette softly in focus. A grainy 35mm documentary photograph taken in 2022, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[close/detail de mayor emotional_rank] `chapters[2].img[11]` · cap 3 · detail · high angle over the counter · R2 · persona [] · 1958** — ancla: «Siete meses después, con unos equipos reductores de polvo ya instalados, el suplemento sal»
```
An open company pay ledger on a pay-office counter, a newly fitted dust extractor fan visible through the window. The dust-allowance column freshly cut down, pencil figures crossed through. Company pay office at Wittenoom, 1958, timber counter, corrugated-iron walls. The column header of the open ledger reads "DUST ALLOWANCE" in clear crisp typed serif ledger heading lettering. Hard slanting window light, deep shadow across half the ledger. Detail shot, high angle over the counter, macro lens, shallow depth of field. A grainy 35mm documentary photograph taken in 1958, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

**[close/detail de mayor emotional_rank] `chapters[4].img[7]` · cap 5 · close · Over-the-shoulder, slightly high angle onto the document · R2 · persona ['Daniel Écija hijo'] · 1985** — ancla: «Mil novecientos ochenta y cinco. Un aeropuerto australiano, un puesto de control. El agent»
```
A fair-skinned Anglo-Australian police officer in his 40s, medium build, in 1980s police uniform and peaked cap; an early-20s Spanish man with olive skin and dark hair across the counter, out of focus. The officer opens the passport, reads the birthplace and lowers his head toward the page. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. 1985 Australian airport passport checkpoint, laminate counter, glass booth. The birthplace line of the open passport reads "WITTENOOM" in clear crisp typed block capitals lettering. Hard overhead fluorescent light, high contrast shadows. Close shot, over-the-shoulder, slightly high angle onto the document, shallow depth of field, passport sharp, traveller soft. A grainy 35mm documentary photograph taken in 1985, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

**[medium con persona] `chapters[0].supp[0]` · cap 1 · medium · eye-level, like a family roll-film snapshot · None · persona ['Daniel Écija', 'María Bernal'] · 1962** — ancla: «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que »
```
Spanish migrant family posing outdoors: a mid-20s Spanish man, slim, dark wavy hair, dust-coated cotton work shirt and trousers, one foot bandaged white; a young adult Spanish woman, slim, dark hair, cotton print dress and cardigan, standing close at his shoulder. The family stands still for a portrait, everyone facing the camera while the man's bandaged foot sits forward on the red ground. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Front of a corrugated iron and fibro company house in Wittenoom, 1962, red dirt yard surfaced with blue-grey tailings. Hard cold overcast daylight, flat and shadowless. Medium shot, eye-level, like a family roll-film snapshot, deep depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[medium con persona] `chapters[0].supp[1]` · cap 1 · medium · eye-level, frontal · None · persona ['Daniel Écija'] · 1962** — ancla: «El hombre se llama Daniel Écija y es minero.»
```
A mid-20s Spanish miner, light olive tanned skin, slim build, dark wavy hair, dust-coated cotton work shirt with sleeves rolled, work trousers, one boot on and one foot wrapped in a white bandage. He stands posing against a corrugated iron wall, shoulders squared, the bandaged foot planted slightly forward. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Red earth yard beside a corrugated iron company house, Wittenoom mining town, 1962. Hard cold overcast daylight, flat and shadowless. Medium shot, eye-level, frontal, 85mm lens, shallow depth of field isolating the man from the iron wall. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[medium con persona] `chapters[1].img[1]` · cap 2 · medium · slightly low angle · R3 · persona ['Daniel Écija', 'María Bernal'] · 1962** — ancla: «Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos.»
```
A slim mid-20s Spanish groom in a dark suit and a young adult Spanish bride in a modest white dress and veil, with family behind. The newlyweds step out of a church door onto stone steps after the Thursday wedding. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Stone steps of a Madrid parish church, September 1962, plain baroque doorway. Soft overcast September daylight. Medium shot, slightly low angle, shallow depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[cap 5 (shock)] `chapters[4].img[14]` · cap 5 · medium · Eye-level · R1 · persona [] · 2023** — ancla: «Décadas más tarde, María está en una habitación rodeada de fotografías en sepia. Entre ell»
```
An elderly Spanish widow in her 80s, olive skin lined and weathered, white hair, small frail build, in a plain dark cardigan. Sits in a room surrounded by sepia family photographs, speaking of clinging to her husband. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Present-day Madrid home interior crowded with framed sepia family photographs, 2023. Hard single window light, high contrast across the photographs. Medium shot, eye-level, 50mm lens, moderate depth of field. A grainy 35mm documentary photograph taken in 2023, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[cap 5 (shock)] `chapters[4].img[12]` · cap 5 · medium · Eye-level · R2 · persona ['Daniel Écija'] · 1991** — ancla: «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La pal»
```
A gaunt Spanish man in his mid-50s, olive skin, greying dark hair, thin frame, in a 1990s cardigan, beside a Spanish doctor in a white coat. Sits on the edge of the examination couch as the diagnosis of mesothelioma is spoken. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Madrid clinic consulting room, 1991, beige walls, steel furniture. Hard light from a single window plus the cold lightbox glow. Medium shot, eye-level, 50mm lens, moderate depth of field. A grainy 35mm documentary photograph taken in 1991, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[cap 2 (setup)] `chapters[1].img[13]` · cap 2 · wide · eye-level at child height · R1 · persona ['Víctor Calvo'] · 1962** — ancla: «Hay polvo por todas partes. Ese niño cuenta que nunca había visto tanto polvo.»
```
A slim young Spanish boy, around eight, in shorts and sandals, red dust coating his legs and hair. The boy stands on the airstrip as a gust swirls dust around the arriving passengers. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Pilbara mining-town airstrip, 1962, parked propeller plane and adults with suitcases behind. Harsh midday Pilbara sun diffused by airborne dust. Wide shot, eye-level at child height, shallow depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**[cap 2 (setup)] `chapters[1].img[15]` · cap 2 · wide · eye-level · R1 · persona [] · 1962** — ancla: «De esa tierra sacan crocidolita, el asbesto azul, un mineral que se paga bien porque aguan»
```
A 1960s tipper truck in a mining-town street, a young adult Spanish woman in a cotton print dress watching from a doorway. The truck dumps blue asbestos tailings across the road as a fine dust drifts toward the houses. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Residential street of an operating Pilbara asbestos town, 1962, mill dust cloud on the ridge. Harsh midday Pilbara sun through hanging dust. Wide shot, eye-level, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### B.4 Costo real
m03 7 caps: **US$ 2.3101** (cost_tracker, Opus; el handoff estimaba ≈ 2,3). Etapas 0 y A: US$ 0. Total F61: **US$ 2.3101**.

### Veredicto de revisor-handoff — Etapa B (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

El md5 del handoff coincide (9892c940…). Recontando los dos json, todas las cifras de la tabla B.2 salen idénticas al reporte. Las observaciones 1 a 4 son de forma o de atribución y no cambian ninguna cifra.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| B.1a | Runner copia de `etapa_a3_m03.py` con las mismas entradas | OK | `diff` entre los dos runners: cambian solo las salidas, el bloque de tablas y los asserts de código F61. Se mantienen `REF` = `f60/a/03_visual_despues.json`, el canon A3 inyectado por `CANON_KEYS`, `BASE` = `f60/base` y el mismo `TID`. |
| B.1b | 7 caps en paralelo por `assign_visual_prompts`, anclas fijas | OK | El log dice "caps con `_plan_anchors` real: []", así que las anclas fueron las fijas en los 7 caps. El diff elimina `CAPS = range(1,8)`, pero el reporte afirma los 7 caps y el json trae 7. 96 de 96 pares por ancla. |
| B.1c | Cero fotos, clips o voz | OK | `grep` en el runner: no hay generate, fal, asset, flux ni tts. La única mención de costo es `cost_tracker.start_video` (línea 138). |
| B.2a | `shot_scale` total y por cap | OK | Recontado. Antes: 15/57/13/3/8. Después: 12/35/37/7/5. Cada fila por cap coincide con el reporte. |
| B.2b | Intent por cap | OK | El log da {1 hook, 2 setup, 3 y 4 rising_tension, 5 shock, 6 resolution, 7 outro}. El intent sale de `skeleton`, no del `03_visual`, donde `narrative_intent` es None. |
| B.2c | Fotos con persona | OK | Antes 33: wide 21, medium 10, close 1, extreme_wide 1. Después 37: wide 11, medium 24, close 2. Coincide. |
| B.2d | `camera_angle` top 6 | OK | Idéntico al reporte, antes y después. |
| B.2e | `caps_sin_establecimiento` y rehechas | OK | Vacíos antes y después. `rehechas` del video es []. `_f8_rehecha`: antes ninguna, después una CERRADA. |
| B.3 | 10 prompts completos y del después | OK | Los 10 de `prompts10` existen textualmente en `03_visual_f61.json` (comprobación True ×10). Cantidades: 3 close/detail, 3 medium con persona, 2 del cap 5 y 2 del cap 2. |
| B.4 | Costo real | OK | `etapa_f61.json` da usd 2.3101 y 135.6 s. `cost_history` termina en 2.310064. |
| Aislamiento | Producción intacta | OK con reserva | `topics_db.json` tiene mtime del 29-oct 20:38. No hay nada de hoy después de las 22:50 en `_steps/` ni en `data/scripts/<tid>.json`. Ver observación 3 sobre `data/cost_history.json` y `output/`. |

**Fuera de alcance:** el runner solo escribe en `f60/base` y en `f61/`. Sin embargo, `data/cost_history.json` (mtime 22:57:53; está en gitignore) y archivos de `output/ba6c3cac…/_fase2b_work/` (ch02 mp4, ass, `gfx_lab_ch02`; mtime 22:55–22:56) cambiaron después de las 22:50. Lo de `output/` no pertenece al runner.

**Observaciones:**
1. **Atribución del "antes" en `_f8_imagenes`.** El reporte presenta como "antes" el `_f8.antes` del archivo nuevo (motivos con "pasillo": 2). El `_f8_imagenes` real del a3 tiene otros motivos (sin "pasillo"; `humano_medio`: 10). Los motivos no coinciden entre archivos; las rehechas y `caps_sin_establecimiento` sí, y quedan en [].
2. **Selección de los 10 prompts.**
   - Los 3 close/detail son 1 R1 y 2 R2. Hay otro R2 de cap 5 (`img13`) y varios R3 que no entraron; el criterio de desempate no está declarado.
   - Los 3 medium con persona son los 3 primeros por orden, sin criterio. Dos son del cap 1 y uno del cap 2.
3. **Escritura fuera de lab.** `cost_tracker.start_video` escribió en `data/cost_history.json`. Es el mismo mecanismo que usó A3, pero el reporte afirma "nunca topics_db ni `_steps` reales" y no menciona este archivo. Lo de `output/` ch02 hay que atribuirlo a otro proceso, o confirmarlo.
4. **Orden de los system instructions.** El log muestra `si_ok = [True, False]`. El reporte lo explica: el segundo es `_VEO_MOTION_SYSTEM`, ajeno a F61. No lo pude verificar contra el código, pero es coherente con los 4 prompts sin bloque VISUAL ARC.
5. **Lectura de CC ("el arco por tipo de cap manda"; 75 % → 49 %).**
   - Los números del plano general son fieles: (15+57)/96 = 75 % y (12+35)/96 ≈ 49 %.
   - Cap 5 es fiel: 9 general / 2 medium / 5 cerradas pasa a 4 / 7 / 5.
   - "Rising_tension son los que más se cierran" es correcto en general (cap 3: 12 → 5), pero en cap 4 baja menos (11 → 7).
   - El reporte omite que en el cap 5 la cantidad de cerradas no sube: close pasa de 1 a 5, pero detail de 4 a 0, así que el total es 5 y 5. El cambio del cap 5 es solo de general a medium.
   - "Outro queda casi igual" es cierto. El cap 6 (resolution) también casi no se mueve (13 → 11 en general), y el reporte no lo menciona.
   - El peso real del efecto está en wide→medium (23 fotos). Hay ruido entre corridas: 5 wide→extreme_wide y 5 extreme_wide→wide. La causalidad "manda el arco" es plausible pero no está aislada: con una sola corrida y sin control no se puede separar del ruido de Opus.

**Riesgos que el contrato no cubre:**
- Una sola corrida de Opus y una sola historia: no hay medida de varianza entre corridas.
- Medium pasa de 13 a 37, que puede ser el otro extremo. La tabla no dice si esos medium con persona son del tipo "retrato posado" repetitivo; eso solo se ve en fotos.
- El gasto en `cost_history.json` queda registrado bajo el `TID` de producción (31 entradas con ese id), lo que ensucia el historial de costos real de ese video.

#### Adenda de CC
- **Obs. 1:** la línea «_f8 antes/después (después)» es la auditoría interna de la corrida nueva (antes y después de sus propias pasadas de re-hechura); el `_f8_imagenes` real del A3 está en §0.3 (motivos «documento en escritorio» 1, `humano_medio` 10, rehechas []). Los motivos difieren porque los prompts son otros; lo comparable (rehechas y `caps_sin_establecimiento`) es [] en los dos.
- **Obs. 2:** criterio usado y no declarado: dentro de cada grupo, orden por `emotional_rank` (R1 < R2 < R3) y después orden de guion; los 3 medium con persona van en orden de guion sin más criterio (las supps del cap 1 no tienen `emotional_rank`). El R2 de `cap 5 img13` quedó afuera por orden de guion. Queda dicho para el analista; los 96 ítems están en `03_visual_f61.json`.
- **Obs. 3:** `cost_tracker.start_video(TID)` escribe `data/cost_history.json` bajo el TID de producción, igual que el runner A3 (así lo heredó la copia); el handoff pedía «mismo paso» y el archivo está en gitignore. Lo de `output/ba6c3cac…/_fase2b_work/` es el render de ch02 de `verificar.sh` (suites f61, 22:55-22:56), no del runner. Si el analista prefiere un `video_id` de lab para el costo (como en B+C), es una línea del runner.
- **Obs. 5:** correcto: en el cap 5 el total de cerradas queda 5 = 5 (close sube, detail baja) y el cap 6 (resolution) casi no se mueve (13 → 11 general); el efecto principal es wide → medium (23 fotos); una sola corrida, sin varianza. Queda para la lectura del analista (PARADA B).

## PARADA B
Nada de fotos ni producción. El analista lee la tabla B.2 y los 10 prompts de B.3 y le dice a Omar si sale sano o se fue al otro extremo.
