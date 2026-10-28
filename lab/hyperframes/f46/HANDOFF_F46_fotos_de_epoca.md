# HANDOFF F46 — Fotos de época: A/B del cap 2 de Wittenoom (lab, sin tocar producción)

Analista, 2026-10-28 02:10. Pedido de Omar (02:00): «generá todo el cap 2, no te preocupes por el gasto».
Tema: Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`.

## Por qué (medido por el analista, US$ 0)
- 25 de las 38 fotos con gente no dicen época ni lugar en sujeto/setting; solo el «1961» del estilo (palabra 4). Seedream viste con ropa actual (jeans, camisas estampadas en el barco del cap 2).
- El canon de época (`step_4e_visual_canon`) se armó con **10 `verified_facts`** del research viejo; el pool v3 tiene 155 datos, 98 eventos, 24 lugares, y la ficha 65 hechos, 71 eventos y **11 escenas** (dónde/quién/qué pasa/sentidos). Nada de eso llega a las imágenes.
- `m03_imagenes_v3.beats_block` manda por beat solo función/emoción/intensidad/imagen_sensorial: **ni la fecha** (que `load_beats` ya lee, `d["fecha"]`) **ni el lugar** del beat.
- Prompts de 157–227 palabras (mediana 192), estilo primero, `mood` abstracto, «faceless» contra caras descritas. La guía de fal para Seedream 5 Lite: orden sujeto → lugar → estilo → luz → técnica; lo de adelante pesa más; > 50 palabras la cola pierde atención; época = ropa y materiales concretos.

## Diseño: una variable por variante
| Variante | Entrada (canon + bloque de beats) | Estructura (orden, mood, estilo) | Costo |
|---|---|---|---|
| **A** | la de hoy | la de hoy | 0 (ya existen: `output/123bbb64…/assets/ch02_flux/ch02_img_*_graded.png`) |
| **B1** | **nueva** | la de hoy | 16 fotos |
| **B2** | nueva (los **mismos slots** de B1, sin volver a llamar a Gemini Pro) | **nueva** | 16 fotos |
A→B1 mide la entrada; B1→B2 mide solo la estructura.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| 16 fotos, mismas anclas | `data/scripts/_steps/123bbb64…/03_visual.json` cap 2 (`image_prompts`) | existe |
| Motor `fal-ai/bytedance/seedream/v5/lite/text-to-image`, payload de producción (`asset_manager._seedream_payload_for`, 2560×1440) | `engine_profiles` + manifest (`flux_meta`) | existe |
| US$ 0,035 por foto | `engine_profiles.cost_usd` (= precio fal) | existe |
| Grade `image_grade.grade` con su perfil por defecto | producción (las A ya están graded) | existe |
| Workers de imagen = `asset_manager.FLUX_MAX_WORKERS` | existe | existe |
| Tope de la tanda **US$ 3,00** | derivado: 32 × 0,035 = 1,12 + canon Flash + 1 llamada de slots Pro + 32 tejidos Flash ≈ 1,5; ×2 margen. Omar 02:00: «el gasto no es problema» | Omar confirma al pegar el prompt |
| Año del estilo por foto | año de la fecha del `dato_central` del beat de la foto; si no tiene, `topic_year` de hoy | derivado (nada nuevo) |
| Largo del prompt B2 | **sin tope**: sale de quitar `mood` y `style`; se mide | — |

## Módulos
Producción: **ninguno se toca** (sin stickers ni mapa). Solo lectura/import: `researcher_steps/step_4e_visual_canon.extract_visual_canon`, `script_engine/m03_visual` (`_build_seedream_prompt_step2`, `_fluidify_item`, `SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3`, esquema de slots), `script_engine/m03_imagenes_v3` (`load_beats`, `assign_beats`, `beats_block`, `style_head`), `engine_profiles.select_profile`, `asset_manager._generate_image_raw`, `script_engine/image_grade`.
Nuevos en `lab/hyperframes/f46/`: `f46_corridas.py` (B1 y B2, con freno), `f46_hoja.py` (hoja de contactos y tabla).

## Paso 0
Anotar en `DECISIONES.md`: «2026-10-28 02:00 · F46: A/B de fotos de época del cap 2 de Wittenoom en lab (entrada nueva y estructura nueva, una variable por variante); el gasto no es problema · Omar · F46».

## Parte 1 — prompts B1 y B2 (texto)
1. **Canon nuevo:** `extract_visual_canon(seed={"seed_title": topic["video_title"]}, angle_blocks={}, verified_facts=<adaptador>, canonical=topic.get("canonical_subject_description"))`. Adaptador (dato, no regla): una entrada `{"fact": …}` por cada `ficha.hechos[].texto`, cada `ficha.cronologia` como «<fecha>: <evento>» y cada `ficha.escenas` como «<donde> — <quien> — <que_pasa> — <sentidos>». Guardar `canon_B.json` en la carpeta. Nada a `topics_db`.
2. **Bloque de beats nuevo** (copia de `beats_block` en el lab, misma salida + 3 líneas por imagen, todas sacadas de ids que el beat ya trae — `dato_central` + `datos_apoyo`):
   - `WHEN:` fechas distintas de esos ids en el pool (`fecha` de datos/cronología/citas), ordenadas;
   - `WHERE:` `lugar` de los items de cronología de esos ids + `nombre` de `pool.lugares` cuyo id esté en esos ids;
   - `CASE-FILE SCENES:` las `ficha.escenas` cuyo `ids` se cruce con esos ids, como «donde · quien · sentidos».
   Simulación del analista sobre ch02 (2 beats): beat 2 → WHEN 1958, 1961-09-16, 1962-09-20, 1962-09-24 · WHERE Madrid, Australia · escena 8 (la entrevista de María Bernal, fotos sepia — **riesgo**: puede meter la entrevista en la foto; dejarla y reportar qué pasó) · beat 3 → WHEN 1930s, 1962-08 · WHERE Australia · escenas 0 (barco desde Málaga, calor y mareos) y 1 (pista de Wittenoom, tierra roja, chapa, madera y uralita).
3. **B1:** mismo flujo de producción del cap 2 (`_build_seedream_prompt_step2` con canon B y el bloque nuevo → Gemini Pro slots → `_fluidify_item` → `style_head` al inicio con el año de la foto + tail igual que hoy). Las anclas y la asignación a beats: **las de 03_visual.json** (no se re-planean).
4. **B2:** los slots de B1 tal cual, tejidos por el mismo `_fluidify_item` con otro orden de formula: `subject, action, gaze_interaction, setting, hard_facts, props_detail, style, color_palette, lighting, shot_scale, camera_angle, lens_technique, text_in_image, aspect_ratio, negations`; **sin `mood`**; el slot `style` se reemplaza por el texto de `style_head(<año de la foto>)` (sin «faceless»); el código **no** antepone el estilo. Candado de cifras igual (fotos 12 y 15 traen `hard_fact_ids`).
5. Salida en texto `PROMPTS_AB.md`: por foto (1–16) ancla, beat, prompt A / B1 / B2 enteros, palabras de cada uno, palabra n.º donde aparece el año y el primer lugar, y si sujeto+setting nombran época o lugar (sí/no). Más el diff de `clothing`/`demographics`/`primary_decade` canon viejo → nuevo.

## Parte 2 — generar y comparar
1. Freno: antes de cada llamada paga, sumar lo gastado en la tanda; si pasa el tope, parar y reportar. Gasto con `cost_tracker` en un id de lab `f46-lab` (nada en `data/scripts/` ni `output/`).
2. 32 fotos (B1 16 + B2 16) **en paralelo** con `_generate_image_raw` y el payload de producción, a `lab/hyperframes/f46/B1/` y `B2/`; grade a `_graded.png` igual que producción.
3. `f46_hoja.py`: una hoja por cada 4 fotos (4 hojas): fila = foto n.º, columnas A | B1 | B2 (las `_graded`), rótulo con n.º y las primeras 8 palabras del ancla. JPG ≤ 2560 px de ancho.
4. Salida en texto: tabla de costos leída de `cost_history` (no estimada) y cualquier foto rechazada por el filtro de seguridad.

## Reglas fijas
- Nada en `data/` (salvo el registro de costos), `output/` ni `topics_db`. Ningún archivo de producción editado.
- Todo lo que pueda ir en paralelo, en paralelo (subagentes y workers al máximo).
- Sin reglas nuevas en ningún prompt de LLM: lo único nuevo son **datos** (canon desde la ficha, WHEN/WHERE/SCENES) y el **orden** de la formula.
- `pytest --collect-only` y `pytest test_*.py` en bloque, prohibidos (ver F42).
- Reporte `F46_REPORT.md`: qué se corrió, salidas de parte 1 y 2, costos reales, lo que queda abierto, veredicto íntegro de `revisor-handoff`. Actualizar `lab/ESTADO_SESION.md`. Commit.

## PARADA al final de la parte 2. No se elige variante ni se toca producción: eso lo deciden Omar y el analista mirando las hojas.
