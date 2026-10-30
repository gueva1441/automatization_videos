# HANDOFF F59 — QA Studio arregla con la máquina de producción (foto y clip) + 2 chascadas

Rama `f11-guion-v4` (main no se toca). Analista → CC. Fecha 2026-10-30. v2 (auditado por subagente: 25 correcciones incorporadas).

## Para qué (en llano)
En QA Studio, Omar escribe qué cambiar de una foto o de un clip. Hoy:
- **Foto:** Flash reescribe el prompt FINAL en inglés con reglas viejas (`_FIX_REWRITE_INSTRUCTION`: «Seedream 4.5», texto solo en español, no conoce el armado C), pisa solo el `.png` crudo (el video usa el `_graded.png`, así que el arreglo nunca llega al video) y no pasa la foto madre.
- **Clip:** `_clipfix_core` rehace la FOTO inicial y deja el movimiento intacto (al revés de lo que dice el cuadro), sin foto final ni `voz_clip` (F57), con una instrucción escrita para Veo.

Después de F59:
```
FOTO: pedido de Omar → Opus edita los CASILLEROS (JSON, solo los que el armado usa) → armar_item (scrub + texto + armado C + aspecto del canon + backstops, la misma función que m03)
      → Seedream (con foto madre si el ítem la trae) → grade (_graded.png) → guarda en 03_visual.json y en el guion vivo
CLIP: pedido de Omar → Opus edita el MOVIMIENTO aprobado → foto final de producción (se reusa si existe) → _generate_clip (Gemini Omni Flash → Kling)
      → guarda el movimiento nuevo en 03_visual.json y en el guion vivo
```

## Decisiones (Etapa 0 las anota en `DECISIONES.md`)
- 2026-10-30 08:18 · F58b se cancela: el título/texto de miniatura lo elige Omar entre los 3 paquetes en QA; no hay verificador de coherencia · Omar
- 2026-10-30 08:22 · **F59:** «rehacer foto» de QA Studio = Opus (`MODELO_CASILLEROS`) edita los casilleros y el código rearma con la misma función que m03 (`armar_item`), con foto madre y grade como producción; se borran `_FIX_REWRITE_INSTRUCTION`, `_build_fix_user_prompt`, el camino Flash y `test_module_137c_fix_recetario.py` · Omar
- 2026-10-30 08:22 · **F59:** «rehacer clip» toca solo el movimiento (Opus lo edita) y usa la cadena de producción (foto final F57 + `_generate_clip` G→K); la foto inicial no se toca; se borran `_FIX_CLIP_REWRITE_INSTRUCTION`, `_build_clipfix_user_prompt` y el paso que rehacía la foto · Omar
- 2026-10-30 08:22 · **F59:** los hints de los cuadros son los aprobados el 2026-10-29 21:13 (`lab/_gpt_probe_analista/PENDIENTE_C_QA_hint.md`) · Omar
- 2026-10-30 08:22 · **F59 chascadas:** `COMPOSICION_MINIATURA` = «The main subject fills the right half of the frame; the left half is dark, uncluttered negative space.» (reemplaza la parte «la foto pone a la persona en la mitad derecha» de F58 2026-10-29 23:23); `foto_final_del_clip` pierde el parámetro muerto `video_prompt_aprobado` · Omar
- 2026-10-30 · **F59 (analista, dentro de 08:22):** a) la foto inicial de un cap con clip no se rehace desde QA en F59 (hoy no tiene botón ni la resuelve `resolve_fix_entry`; m06 no copia `image_f8`) → abierto; b) lo que QA edita se guarda en `03_visual.json` (la fuente que m06 vuelve a copiar) y en `data/scripts/<tid>.json` (el guion vivo), para que un m06 nuevo no lo pise; c) `people_group` no lo edita Opus (queda fijo por código: el aspecto sale del canon); d) lo que el scrub de producción saca del pedido (p. ej. «jaw clenched», `HANDS_FACE`) se le informa a Omar en la respuesta del fix, sin tocar el scrub · analista

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Modelo del editor de foto y de movimiento = `MODELO_CASILLEROS` (claude-opus-5-5), esfuerzo `guion_v4.ESFUERZO[MODELO_CASILLEROS]` | `m03_visual.py:133`, `guion_v4.py:66` | Omar 2026-10-28 / hoy 08:22 |
| Reintentos del editor = `MAX_RETRY_ATTEMPTS` (3) | `m03_visual.py:873` | proyecto |
| Segundos del clip en el pedido = `VEO_CLIP_DURATION_SEC` (8.0), formateado como `video_prompt._segundos()` | `m03_visual.py:846` | proyecto |
| Motores de clip = `api.video_engines` (G → K) | `config.py:75` | Omar F53b |
| **Nueva:** `CASILLEROS_EDITABLES = (*_PROSA, "shot_scale", "text_in_image", "year")` en `m03_imagenes_v3.py` | derivada del código: las claves que `armar`/`f8_backstop` leen (`_PROSA` l. 621 + `shot_scale`, `text_in_image` en línea) + `year` (lo usa `anio_final`); `people_group` fuera (decisión c) | analista, derivada |
| Textos de los hints | `PENDIENTE_C_QA_hint.md` | Omar 2026-10-29 21:13 |
| Oración de composición | arriba | Omar hoy 08:22 |
Sin tope de dólares: el gasto se informa (DECISIONES 2026-10-29 16:08).

## Módulos que toca
| Módulo | Hoy | Después |
|---|---|---|
| `script_engine/m03_visual.py` | el armado de cada ítem (scrub_slots + fix_text_slot, l. ~676–683; armar → f8_backstop → `_sacar_frases_con_texto` → `raw_llm_prompt`/`prompt`/`sensible`/`motivos`, l. ~690–715) vive dentro del bucle de casilleros | sale a `armar_item(it, anio, grupos, escala, lang, composicion="", sin_cartel=False) -> it` (incluye scrub + fix_text_slot; deja `_f8_slots_scrub`, `_f8_problemas`, `_f8_texto_fuera`, `texto_en_imagen`). `anio_final(e, it)` con `exps` se queda en m03, fuera. Salida byte-idéntica |
| `script_engine/m03_imagenes_v3.py` | — | `CASILLEROS_EDITABLES` |
| `qa_studio_server.py` + `qa_studio.html` | `_fix_core` Flash; `_clipfix_core` Veo; placeholders genéricos; textos «Veo» (html ~803/814/816) | editores nuevos; hints; textos sin «Veo» |
| `script_engine/m09_packaging.py` + `asset_manager.py` + `lab/hyperframes/f57/clip_b.py` | chascadas | `COMPOSICION_MINIATURA` nueva (y su comentario l. 76–77); `foto_final_del_clip` sin `video_prompt_aprobado` en firma y en TODAS las llamadas |

Usá todos los subagentes paralelos que la tanda permita (Etapa 0 en paralelo; tests en paralelo).

---

## Etapa 0 — solo lectura y docs (US$ 0) · PARADA 0
1. Anotar las 6 decisiones de arriba en `DECISIONES.md` (raíz) con su hora.
2. **Cuadros vacíos de la galería — confirmar la causa ya encontrada:** `QAState._flux_imgs`/`_supp_imgs` (qa_studio_server.py ~185–195) hacen glob `chNN_img_*.png` y agarran también los `*_graded.png` (por eso 32 = 16 + 16; ch01 = 8); `resolve_image` (l. ~215) los rechaza por `_IMG_NAME_RE` (l. ~76) y `_img_idx` da 0 → cuadros vacíos. Medí por cap (cuadros dibujados, PNG crudos, graded, ítems en el guion vivo y en 03_visual) y confirmá o corregí. **No se arregla en F59**: va como chascada propuesta al reporte.
3. **Copia de lab de Wittenoom** (`123bbb64-9fca-4395-8bf4-57d60e219ef1`) en `lab/hyperframes/f59/base/` para `QAState(tid, base_dir=…)`: `data/scripts/<tid>.json` armado desde `03_visual.json` por `m06_assembler` (sin LLM), con `voz_clip` en los caps con clip sacado de `m3.voz_del_clip(narración, veo_position, ventana)` como `lab/hyperframes/f57/clip_b.py` (usá la narración del guion vivo, no `01b_narration.json` del 30-oct: sus anclas no calzan con 03_visual), y `output/<tid>/assets` copiado. Sin LLM, sin fotos. Si algo de esto pide gastar, PARÁ y decí por qué.
4. Salida 0 en texto: tabla de cuadros vacíos + causa confirmada; árbol de la copia de lab; ítems de prueba candidatos para B2 (ver Etapa B). **PARADA 0.**

## Etapa A — código (US$ 0) · PARADA A
**A1 · reestructura sin cambio de comportamiento.** Sacar `armar_item` (tabla de módulos). Test contra una copia fija en `lab/hyperframes/f59/` (no contra datos vivos): con los casilleros de `03_visual.json`, el `anio` del ítem, `people_groups` de `data/topics_db.json`, `escala` de `load_beats` y `lang = place_language(topic)`, da `prompt`/`raw_llm_prompt`/`sensible`/`motivos` byte-idénticos para los caps 2–6, los supp de los caps 1 y 7 y la foto del clip (`image_f8`). Commit aparte.

**A2 · editor de foto.** `_fix_core(state, topic_id, cap, img_name, pedido, *, deps inyectables)`:
1. `resolve_fix_entry` **agrega** `casilleros` (`raw_llm_prompt` parseado), `anio`, `anio_fuente`, `beat`, `foto_madre_ref` cuando están (si no, `None`); no cambia lo que ya devuelve (lo usan `_reseed_core` y sus tests). Si faltan `casilleros` o `anio`, `_fix_core` devuelve `(False, "guion viejo: correr m03 de nuevo")`.
2. Opus con `PEDIDO_EDITAR_CASILLEROS` (abajo), mandando solo las claves de `CASILLEROS_EDITABLES` que el ítem tenga; esquema de salida = objeto con esas mismas claves. Llamada: `_call_with_validation_retry(..., caller=_llamar_casilleros, checklist="")` con un validador que lance `VisualValidationError` si no es objeto, faltan/sobran claves o un casillero de prosa queda vacío; `claude_helpers.ClaudeError` → `(False, motivo)`. Sin generar si no pasa.
3. Casilleros finales = los del ítem con las claves editadas encima (las no editables vuelven tal cual por código, `people_group` incluido).
4. `anio, fuente = v3img.anio_final({"respaldo": (it["anio"], it["anio_fuente"])}, casilleros_nuevos)` (la regla de producción: valida 4 dígitos y cae al del ítem).
5. Contexto sin LLM y sin `asegurar_canon`: `topic = fase1_5._load_topic_by_id(tid)`; `grupos = {g["id"]: g for g in topic["people_groups"]}`; `escala = bool(beat del ítem en v3img.load_beats(topic, STEPS_DIR)[cap] → "escala")`; `lang = v3img.place_language(topic)`. (No usar `m09_packaging.topic_produccion`: llama a `asegurar_canon`, que puede llamar a Opus y reescribir topics_db.)
6. `armar_item(...)` → prompt final. Backups (`_qa_backups/`): PNG crudo, `_graded.png`, `03_visual.json` y `data/scripts/<tid>.json`. Generar con `am._generate_flux_image_at(prompt, "", out, use_ultra, seed=_seed_for_subject(...), foto_madre_data_uris=…)` resolviendo `foto_madre_ref` contra `foto_madre_registry` del guion como asset_manager.py ~861–870. Después **grade** igual que `_apply_grade` (asset_manager.py ~1312): `image_grade.grade(src, image_grade.params())` → `<stem>_graded.png`.
7. Guardar el ítem (casilleros, `raw_llm_prompt`, `prompt`, `anio`, `anio_fuente`, `_f8_*`) en `03_visual.json` y en el guion vivo; `_invalidate_baked`.
8. Respuesta a Omar: ok/motivo + **lo que el scrub sacó** (`_f8_slots_scrub`, `_f8_problemas`) en texto llano («tu pedido decía X; el filtro de caras lo saca»).
9. Se borran `_FIX_REWRITE_INSTRUCTION`, `_build_fix_user_prompt`, el import de Flash del fix y `test_module_137c_fix_recetario.py`. `test_qa_studio.py`: se reescriben los de fix_core (~380, 402, 417, 439, 450, 463) y se extiende `build_topic` con `raw_llm_prompt`/`anio`/`anio_fuente`; tests nuevos con deps inyectadas (sin red): casilleros editados → `armar_item` con el `anio` correcto → grade → los 2 archivos guardados + backups; `people_group` intacto; guion viejo → mensaje; 3 validaciones fallidas → no genera; scrub informado.

**A3 · editor de clip.** `_clipfix_core(state, topic_id, cap, pedido, *, deps)`:
1. `resolve_clip_entry` **agrega** `voz_clip` (o "") y `_final` (si existe); el chequeo va en `_clipfix_core`: sin `voz_clip` → `(False, "guion viejo: correr m03 de nuevo")` (no el 400 «el cap no tiene clip Veo regenerable» de `/fix_clip`, l. ~1924, que queda solo para caps sin clip).
2. Opus con `PEDIDO_EDITAR_MOVIMIENTO` (abajo), esquema `{"movimiento": string}`, mismo mecanismo de reintento que A2.
3. `foto_final_del_clip(foto_inicial, image_prompt, voz_clip, out_path=<_final>)` (reusa si existe).
4. Backup del mp4; `am._generate_clip(foto_inicial, movimiento_nuevo, out_clip, image_prompt=…, ancla=voz_clip, foto_final=final["path"])`. Rechazo de G y K → `(False, "filtro: <rechazos literales>")`, mp4 viejo intacto.
5. Guardar `video_prompt` nuevo en `03_visual.json` y en el guion vivo (con backups); `_invalidate_baked`.
6. Se borran `_FIX_CLIP_REWRITE_INSTRUCTION` (l. ~975–1011, con el bloque «⚠ DORMIDO» ~967–974), `_build_clipfix_user_prompt`, el paso que rehacía la foto, `generate_veo_fn`. Tests que se reescriben o borran: `test_qa_studio.py` clipfix (~517, 562, 573, 588) y el fixture `_clipfix_deps`; el guard compartido `_FIX` (~604) se queda con las deps nuevas; `test_module_f57.py:370` (busca el texto literal de la llamada a `generate_veo_fn`). Tests nuevos: foto inicial intacta, el motor recibe el movimiento nuevo y `voz_clip`, `_final` existente reusada, rechazo de G y K → mensaje y mp4 intacto.

**A4 · front.** `qa_studio.html` l. ~508: placeholders = los textos de `PENDIENTE_C_QA_hint.md` tal cual, con las comillas dobles escapadas (`&quot;`) porque van dentro de `placeholder="${…}"`. Textos «Veo» (~803, 814, 816) → «clip». Sticker `lab/mapa/stickers/orquestador.json` (~555/563) al día.

**A5 · chascadas.** `COMPOSICION_MINIATURA` nueva + su comentario (m09 l. 76–77) + `test_module_f58.py:253`. `foto_final_del_clip` sin `video_prompt_aprobado`: firma, asset_manager ~1210, `lab/hyperframes/f57/clip_b.py:80`, `test_module_f57.py` ~268/288/304 y el doble `def final(...)` (~323). Ojo: `video_prompt.escribir(..., video_prompt_aprobado, ...)` es otro parámetro, vivo: no se toca.

**A6 · suites:** rápida, amplia (`lab/hyperframes/f41/verificar.sh`), md5 de ch02 `--only-cap` (`f792f3d4…`), MAPA `--check` y stickers de los módulos tocados.

Salida A en texto: los 2 pedidos como quedaron en el código; `CASILLEROS_EDITABLES` resuelta; tabla antes → después de cada función; un ejemplo (de los tests) de casilleros antes/después y de movimiento antes/después; suites. **PARADA A.**

## Etapa B — prueba real en Wittenoom · PARADA B (con OK del analista a la A)
Sobre la copia de lab de la Etapa 0, llamando `_fix_core`/`_clipfix_core` directo con `QAState(tid, base_dir=lab/hyperframes/f59/base)` (no `_start_fix`: usa los globales), dentro de `cost_tracker.start_video('f59_parte_b')`:
1. **Composición (una variable):** rearmar los 3 paquetes de F58 con sus casilleros (`raw_llm_prompt` de `publish/metadata.json`), su `anio`, `sin_cartel=True`, `escala=False` (metadata no trae beat; con False sale byte-idéntico al de F58) y la oración nueva, **sin LLM**; 3 fotos (≈ US$ 0,105). Hoja `hoja_paquetes_f59.jpg` al lado de la de F58.
2. **Foto:** un ítem `medium` con una persona visible de la copia de lab (candidatos de la Etapa 0, p. ej. ch02_img_04); primero la foto «antes» desde sus casilleros de 03_visual con la misma semilla (≈ US$ 0,035), después `_fix_core` con el pedido «que mire hacia la cámara, con el ceño fruncido» (ajustalo a quien esté en la foto). Pegar: casilleros antes/después, prompt antes/después (diff), lo que informó el scrub, foto antes y después lado a lado.
3. **Clip:** `_clipfix_core` sobre ch01 con el pedido «cámara quieta, solo sube el polvo, lento». Pegar: movimiento antes/después, prompt que fue al motor, motor, rechazos, SSIM inicial/final, segundos, US$.
Gasto desglosado por servicio. Imágenes y mp4 no van a git. Reporte `lab/hyperframes/f59/F59_REPORT.md` con «lo que queda abierto» y veredicto íntegro de `revisor-handoff`. **PARADA B.**

---

## Pedido del editor de foto — `PEDIDO_EDITAR_CASILLEROS` (íntegro)
```
Editás los casilleros de una foto de un video documental de historia oscura. Los CASILLEROS son un JSON en inglés que después arma el código en el prompt de la foto. El ANCLA es la oración de la narración que la foto muestra. Omar pide un cambio en español.

Devolvé el mismo JSON, con las mismas claves. Cambiá solo los casilleros que el pedido toca; los demás van copiados tal cual. Escribí lo que se ve, en inglés: si el pedido saca algo, nombrá qué ocupa su lugar. Si el pedido es una emoción, escribila como gesto visible. Si el pedido choca con el ANCLA, hacé lo más cercano que el ANCLA permita.

ANCLA:
{ancla}

CASILLEROS:
{casilleros}

PEDIDO DE OMAR:
{pedido}
```
Salida: esquema objeto con las claves de `CASILLEROS_EDITABLES` presentes en el ítem.
Revisión simulada (ítem `medium` con persona, pedido «que mire hacia la cámara, con el ceño fruncido»): solo llegan `subject`, `action`, `setting`, `lighting`, `camera_angle`, `lens_technique`, `shot_scale`, `text_in_image`, `year`; `gaze_interaction` no está (no llega a la foto desde F51), así que Opus escribe la mirada y el ceño en `subject`/`action`; si escribe un gesto que `HANDS_FACE` borra, A2.8 lo informa.

## Pedido del editor de movimiento — `PEDIDO_EDITAR_MOVIMIENTO` (íntegro)
```
Editás el movimiento de un clip de {segundos} segundos de un video documental de historia oscura. El MOVIMIENTO aprobado está en inglés; la VOZ es lo que se oye durante el clip. Omar pide un cambio en español.

Devolvé el MOVIMIENTO con el cambio aplicado, en inglés y de largo parecido; lo que el pedido no toca va igual. Escribí lo que pasa en cámara y en la escena (si el pedido dice que algo no se mueva, escribí que queda quieto).

VOZ:
{voz_clip}

MOVIMIENTO:
{movimiento}

PEDIDO DE OMAR:
{pedido}
```
Salida: esquema `{"movimiento": string}`. `{segundos}` = `VEO_CLIP_DURATION_SEC` formateado como `video_prompt._segundos()`.
Revisión simulada (ch01 de 03_visual, pedido «cámara quieta, solo sube el polvo, lento»): el aprobado empieza «A slow, somber documentary shot on grainy 35mm film… The camera makes a very slow push-in…» → debería salir con «The camera holds completely still… fine dust rises slowly…» y el resto igual. `_generate_clip` después lo pasa como `intento_movimiento` a `video_prompt.escribir` (producción, sin cambios).

## Reglas fijas
- No tocar prompts de producción (casilleros de m03, `video_prompt.escribir`, guion, scrubs). Los 2 pedidos nuevos reemplazan a 2 instrucciones viejas (~85 líneas) que se borran.
- Lo viejo se borra con sus tests, no se apaga.
- Ningún número nuevo sin origen.
- PARADA al final de cada etapa; la B espera el OK del analista.

## Abiertos que deja F59
- La foto inicial de un cap con clip no se rehace desde QA (decisión a).
- Cuadros vacíos de la galería: causa confirmada en la Etapa 0; el arreglo va en la próxima tanda.
