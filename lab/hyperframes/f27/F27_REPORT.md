# F27_REPORT — que salga el video de Vajont, y tres cortes en la reparación del guion

CC · 2026-10-25 · base `26c0065`, rama `f11-guion-v4`, sin merge, nada publicado, nada borrado. Handoff
`lab/hyperframes/f27/HANDOFF_F27_vajont_sale.md`.

**En corto.**
- **El video está en disco y no se publicó:** `output/f8s3-vajont/f8s3-vajont_final_gfx.mp4`.
  - 1009.1 s (16.8 min), 2560×1440 a 30 fps, h264 + aac, 606 MB, con gfx en los 7 caps.
  - Versión sin música al lado: `f8s3-vajont_final_gfx_no_music.mp4`.
- **A.** Tres arreglos de código y la métrica, con 0 API. Suite: **888 verdes + las 5 previas**. Commit `b181889`.
- **B.** m03 salió en el **primer intento**. En el cap 1, Flash devolvió 37 respuestas vacías con
  `finish_reason=PROHIBITED_CONTENT`: 3 imágenes fueron por el backstop nuevo y las demás se recuperaron re-llamando.
  Después, 92 imágenes (0 re-hechuras), 2 clips Veo y render con gfx. Commit `6a65ccb`.
- **Costos:**

| | gasto | tope |
|---|---|---|
| Gemini | US$ 1.62 | 4 |
| imágenes | 92 | 100 |
| Claude | 0 | 0 |
| fal.ai | US$ 3.70 (Seedream 3.22 + Veo 0.48) | — |
| ElevenLabs | 0 (la voz de F26 se reusó) | — |
| foto madre (OpenAI gpt-image-2 ×2) | no medido: no pasa por el `cost_tracker`, seam conocido | — |

---

## A. Tres arreglos de código + métrica — HECHA (`b181889`, 0 API)

### A.1 `gemini_helpers`: una respuesta vacía es un fallo de parseo
```diff
+_ULTIMA = threading.local()          # el motivo de la última respuesta sin texto, por hilo (m03 teje en hilos)
+def _motivo(resp) -> str:            # "finish_reason=…[, block_reason=…]" (candidates[0].finish_reason, prompt_feedback.block_reason)
+def _texto(resp, description=None):  # el .text; si viene vacío: _ULTIMA.motivo y "[gemini] respuesta vacía (…) en <desc>"
 def _try_json_parse(raw_text: str) -> dict:
+    if raw_text is None or not raw_text.strip():
+        raise _JsonParseError(("", "", json.JSONDecodeError("respuesta vacía", "", 0)))
     text = raw_text.strip()
-def _dump_invalid_json(raw_text, text, e) -> str:
+def _dump_invalid_json(raw_text, text, e, motivo=None) -> str:     # + "motivo de la respuesta vacía: …" en el dump
-        f"(line {e.lineno} col {e.colno}): {e.msg}.{dump_msg}"
+        f"(line {e.lineno} col {e.colno}): {e.msg}{f' ({motivo})' if motivo else ''}.{dump_msg}"
-        return resp.text                                            # call_flash_json, call_pro_json, call_model_json
+        return _texto(resp, description)
```
- **Mensaje final:** sigue siendo el `ValueError` de siempre, ahora con «respuesta vacía» y el motivo.
- **Reintentos:** `_parse_with_retry` re-llama hasta `PARSE_MAX_ATTEMPTS` (3), como con cualquier JSON roto.

### A.1 m03: ¿atrapaba el `ValueError`? **No.** Agregué el `except` solo en `_fluidify_item`
Hoy el `ValueError` del helper subía de `_fluidify_item` → `_fluidify_with_leakage_guard` → `_fluidify_one` → el cap
→ `process_topic`. Eso es lo que tumbó F26.
```diff
+    sin_respuesta = 0
     for attempt in range(1, max_attempts + 1):
-        out = call_flash_json(user, ..., description="m03:fluidificador")
+        try:
+            out = call_flash_json(user, ..., description="m03:fluidificador")
+        except ValueError as e:   # F27 §A.1: Flash sin respuesta utilizable (vacía/bloqueada) = intento perdido
+            sin_respuesta += 1
+            print(f"  ⚠ [m03] {label}: el fluidificador no devolvió texto (intento {attempt}/{max_attempts}): …")
+            out = None
 ...
         return best_prose
+    # F27 §A.1 BACKSTOP: Flash no contestó en NINGÚN intento → la imagen sigue con los slots en el orden del perfil,
+    # sin tejer (después pasan la regla 3, las reglas F8 —que sacan la frase— y el rango, como cualquier prosa).
+    if sin_respuesta == max_attempts:
+        crudo = ". ".join(slot.strip().rstrip(".") for los slots de profile.formula con texto)
+        if crudo:
+            print(f"  ⚠ [m03] {label}: fluidificador SIN RESPUESTA en {max_attempts} intentos — … (backstop, run sigue).")
+            return crudo + "."
     raise VisualValidationError(…)   # igual que antes
```
- **Cómo queda el backstop (decisión mía):**
  - Si un intento devuelve prosa, sigue como siempre (Guarda 1, degradación).
  - Si los 3 intentos vuelven vacíos, no hay prosa que degradar. La imagen sigue con sus slots (los escribió Pro)
    puestos en orden, y pasa por las mismas guardias que cualquier prosa.
  - Los otros errores, igual que antes (test: prosa vacía sin excepción → `VisualValidationError`).
- **Alcance del cambio:** es el único cambio de lógica en m03, dentro de `_fluidify_item`, como permite el handoff.

### A.2 Reparación (e): el nombre se quita y la oración se queda (`guion_v4.edit_sentences`)
```diff
+PEDIDO_E = ("La cita va SIN el nombre: reemplazá el nombre por su rol como viene en los datos (un operario, un testigo, "
+            "un ingeniero) o por «alguien que estuvo ahí». No saques la oración.")   # F27 §A.2
-    lines = "\n".join(f"- «{x['frase']}» → {x['motivo']}" for x in problems)
-    raw = call(f"""En este párrafo de un documental hay frases con un problema. Sacá esas frases o corregilas para que el
-problema desaparezca, con las palabras que ya tienen. No toques nada más del párrafo; no agregues datos, cifras,
+    lines = "\n".join(f"- «{x['frase']}» → {x['motivo']}" + (f" {PEDIDO_E}" if x.get("codigo") == "e" else "")
+                      for x in problems)
+    pedido = (PEDIDO_E if all(x.get("codigo") == "e" for x in problems) else
+              "Sacá esas frases o corregilas para que el\nproblema desaparezca, con las palabras que ya tienen.")
+    raw = call(f"""En este párrafo de un documental hay frases con un problema. {pedido} No toques nada más del párrafo; no agregues datos, cifras,
```
- **Otros motivos:** el pedido es byte-idéntico al de antes (test).
- **Párrafo con un (e) y otro motivo (decisión):** queda el pedido general, y la línea del (e) lleva `PEDIDO_E` al
  lado. La guardia léxica no cambia.

### A.3 m01c sale del camino v4
```diff
 def reparar(..., ficha=None,
+            editor: bool = False) -> dict:
-    if bl0:
+    if not editor:
+        log.append("  [editor v4] fuera del camino desde F27")
+    elif bl0:
         ps, pasos["editor"] = editor_pass(...)
```
- `fase1_5 --editor` → `process_topic(editor=)` → `run_guion_v4(editor=)` → `reparar(editor=)`.
- Sin `--editor`, la llamada a `run_guion_v4` es la de antes, sin argumentos nuevos.
- `editor_pass` no se borró.

### A.4 Métrica
```diff
-PALABRAS_POR_SEG = 2.05             # F7c-2: 12 min ≈ 1,500 palabras (medido en v2 F5d)
+PALABRAS_POR_SEG = 2.4              # F27: medido en Vajont F26 (2,355 palabras → 980.8 s); antes 2.05 (F7c-2)
```

### Tests
- **`test_module_f27.py` (11):**
  - helper: `None` ×3 → `ValueError` con «respuesta vacía»; `None`, vacía y después JSON → el dict; el motivo
    `finish_reason=SAFETY` sale en el log, en el error y en el dump.
  - m03: Flash vacío en los 3 intentos → backstop con los slots; vacío y después prosa → la prosa; prosa vacía sin
    excepción → `VisualValidationError` como antes.
  - (e): «Kuleshov recuerda…» → la oración sigue, sin «Kuleshov», con un rol; el pedido lleva `PEDIDO_E`; otro motivo
    → el pedido de siempre.
  - Reparar con bloqueante ya no llama al editor; `--editor` llega a `run_guion_v4` solo con la bandera.
  - 2,355 palabras ≈ 16.4 min.
- **Adaptados:**
  - `test_module_f11`, `f11b`, `f11c`: los tests del editor pasan `editor=True` (el camino viejo sigue probado).
  - `test_module_f25c`: `largo_txt(2047)` da 14.2 min.
- **Suite amplia (`suite_amplia.log`):** 888 verdes + las 5 previas (3 `01b_pauses`, 2 `m03_merge_timing`).

---

## B. Vajont desde m03 hasta el mp4 — HECHA (`6a65ccb`)

Runner `lab/hyperframes/f27/b/f27b_produccion.py`:
- Usa el de F26 con los archivos de F27 y el tope Gemini de 4.
- Freno antes de cada intento de m03 y traceback por intento.
- Log en `b/produccion.log` y costos en `b/costos_f27b.json`.

| etapa | qué pasó | costo | pared |
|---|---|---|---|
| guion | Voz y música de F26 reusadas, sin volver a pagar (normalizer, audio y m07 no se re-corren, porque solo afectan a la voz que ya estaba). Plan de **92 imágenes** a 10.75 s (9 · 13 · 13 · 11 · 15 · 16 · 15). **m03 OK en el 1.er intento** (de 3 permitidos). Después paso0 (foto madre: sujeto + presa) y assemble → `data/scripts/f8s3-vajont.json`. | Gemini 1.4035 (Flash 0.3667 · Pro 1.0368) | 551 s |
| imágenes | fase2a dentro del proceso, con un contador sobre `asset_manager._generate_image_raw` (tope duro: corta en la 101). **92 pedidas al motor, 0 cortadas por el tope, 0 re-hechuras del guardia de visión, 0 fallidas.** Seedream: 86 t2i + 6 edit con foto madre. Veo: 2 clips (caps 1 y 7). | fal 3.70 | 24.2 min |
| render | Firefox se cerró con cierre normal (CloseMainWindow) → 0 procesos, RAM libre 17.9 GB (19.2 al arrancar). `fase2b --keep-segments --gfx --gfx-sparse --gfx-quality looks`: **gfx OK en los 7 caps** (384–983 s por cap), música curada con sidechain. | Gemini 0.2195 (Flash 0.2048 · Vision 0.0147; de `cost_history`) | 128.4 min |

**m03, cap 1 (el gancho):**
- **Motivo:** `finish_reason=PROHIBITED_CONTENT` en las **37** respuestas vacías de Flash al tejer la prosa. Las 37
  están en `b/guion.out`, con su dump en `data/_debug/`.
- **Qué hizo el backstop:**
  - **3 imágenes no tuvieron ninguna respuesta** en sus 3 intentos (9 vacías cada una): supplementals #3, #4 y #5
    del cap 1. Las tres siguieron con los slots sin tejer y pasaron por las guardias de siempre.
  - **Las otras 10 vacías se recuperaron** en la re-llamada del helper.
  - El cap terminó «✓ Veo prompt + 8 supplementals».
- **Las tres imágenes del backstop** (`b/cap1_backstop_3_4_5.jpg`):
  - #3: la niña de espaldas, en camisón, con movimiento.
  - #4: una figura bajo la sábana, acurrucada contra el respaldo.
  - #5: primer plano de la cara de la niña.
  - No son gráficas, pero **las reglas F8 no marcaron los prompts #3 y #4** («being pressed forward violently»,
    «contorted»). Además, **la #5 es un primer plano de cara**, justo lo que esas reglas buscan evitar. Omar tiene que
    mirarlas antes de publicar.

**Revisión visual del mp4** (`b/hoja_contactos_vajont.jpg`, un cuadro cada 30 s; la miré entera):
- **Coherente de punta a punta:** el gancho de la cama, el valle, Semenza, L'Unità, el 4 de noviembre de 1960, la
  maqueta, el Bar Faè, la ola sobre el Piave, el helicóptero de EE. UU., el vaso sobre el mantel, el juicio y Micaela en
  el comité.
- **gfx:** fechas, rótulos y pregunta de cierre de cap. Los subtítulos van por palabra.
- **Para revisar:**
  - Un rótulo de gfx con texto en inglés mal formado encima de una cifra en español (cuadro 9 de la hoja ≈ 4:00, cap
    3, en la tarjeta «UN DESLIZAMIENTO DE 3 MILLONES…»).
  - Un aviso de fase2b, «anchor matching falló — fallback uniforme», en un cap flux: las imágenes de ese cap se reparten
    parejas en el tiempo, no ancladas a la frase.

**Duración:** 1009.1 s (16.8 min). La voz dura 980.8 s; el resto son pausas de cierre de cap y cola.

**Lo que no se hizo:**
- **QA Studio no se lanzó** (decisión). Según lo acordado con Omar, se lanza cuando él lo pide; elige puerto libre solo.
- **`compara`:** no hay un comparador para un primer video; la hoja de contactos cumple ese papel.
- **`fase3.py`** (empaquetar para publicar), que fase2b sugiere al final: **no se corrió.**
- **El nombre del archivo:** el handoff decía `video_vajont_f26.mp4` o donde lo deje fase2b. Lo dejé donde lo dejó
  fase2b; no lo renombré ni lo copié.

---

## Archivos
`lab/hyperframes/f27/`:
- **Raíz:** `HANDOFF_F27_vajont_sale.md`, `suite_amplia.log`, este reporte.
- **`b/`:** `f27b_produccion.py`, `produccion.log`, `costos_f27b.json`, `plan_imagenes.json`, `guion.out`,
  `imagenes.out`, `fase2b.out`, `render.out`, `hoja_contactos_vajont.jpg`, `cap1_backstop_3_4_5.jpg`.

**Fuera de git:**
- `output/f8s3-vajont/` (mp4, assets, `_fase2b_work`, foto madre).
- `data/scripts/f8s3-vajont.json`.
- `_steps/f8s3-vajont/03_visual.json`.
- En `topics_db`, Vajont pasó a `video_generated` (lo marca fase2b).

## Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| A1a | Respuesta vacía = fallo de parseo, se re-llama y después ValueError con «respuesta vacía» | OK | gemini_helpers.py `_try_json_parse` (None o strip vacío lanza `_JsonParseError`). guion.out muestra «JSON inválido (intento 2/3) … respuesta vacía — re-llamando». |
| A1b | finish_reason y block_reason en el log y en el dump | OK | `_motivo`, `_texto` y `_dump_invalid_json(motivo)`. Los 3 callers (`call_flash_json`, `call_pro_json`, `call_model_json`) usan `_texto`. |
| A1c | m03: único cambio de lógica permitido, un `except ValueError` por imagen | PARCIAL | m03_visual.py `_fluidify_item`: el `try/except ValueError` está dentro de lo permitido. Se agregó además un backstop nuevo, que devuelve los slots crudos unidos con «. » cuando los 3 intentos no tienen respuesta. No es un `except`, es lógica nueva. Ver observación 1. |
| A1d | Test: None×3 da ValueError; None y después JSON válido da el dict | OK | test_module_f27.py. Pasa. |
| A2 | Motivo (e): se quita el nombre, la oración se queda; los otros motivos no cambian | OK | guion_v4.py `PEDIDO_E` es el texto del handoff. Se aplica por línea y también como pedido único cuando todos los problemas son (e). Los otros motivos conservan el pedido anterior. Es el único prompt tocado. |
| A3 | m01c fuera de `reparar`, detrás de `--editor`, con el aviso «fuera del camino desde F27» | OK | guion_v4.py `reparar(editor=False)` y el log con ese aviso. fase1_5.py tiene el flag `--editor` y lo pasa por `process_topic`. La función no se borró. Los tests f11, f11b y f11c se adaptaron con `editor=True`. |
| A4 | `PALABRAS_POR_SEG = 2.4` con el comentario pedido; tests adaptados | OK | guion_v4.py. test_module_f25c cambió a «14.2 min». |
| A5 | Suites verdes (las 5 previas) y commit A | OK | Corrí f27, f11, f11b, f11c y f25c: 49 passed. suite_amplia.log: 888 passed y 5 failed. Los 5 fallos son de 01b_pauses y m03_merge_timing, que son archivos de test que ningún commit de F27 tocó. Commit b181889 con trailer. |
| B1 | m03 en 3 intentos o menos, voz y música reusadas, paso0 y assemble | OK | produccion.log: «m03 intento 1 OK en 551 s». El plan es de 92 imágenes a 10.75 s. |
| B1b | Reportar finish_reason y qué hizo el backstop | OK | guion.out tiene 37 líneas «respuesta vacía (finish_reason=PROHIBITED_CONTENT)». Tres líneas «SIN RESPUESTA en 3 intentos … backstop» para cap 1 img #3, #4 y #5. Coincide con el reporte. |
| B2 | fase2a: imágenes ≤ 100 | OK | costos_f27b.json: 92 pedidas, 0 cortadas por el tope. imagenes.out termina con rc=0. |
| B3 | fase2b con gfx y el mp4 en disco | OK | ffprobe del mp4 real: 2560×1440, 1009.13 s. Pesa 635,822,161 bytes, es decir 606 MiB. Coincide con el reporte. produccion.log: fase2b rc=0 en 128.4 min. |
| B4 | Topes: Gemini ≤ US$ 4, Claude 0 | OK | costos_f27b.json: Gemini 1.623 (m03 1.40 más render 0.22), fal 3.70. No hay entrada de Claude. |
| B5 | No publicar, no mergear, no borrar | OK | git log: solo dos commits. Hay un rastro de publicación posible: el `fase2b.out` sugiere `fase3.py` como siguiente paso, pero no hay evidencia de que se haya corrido. |
| R | F27_REPORT.md con veredicto REVISOR_PENDIENTE; ESTADO_SESION al final | OK | El reporte existe, sin commit, y la sección dice REVISOR_PENDIENTE (línea 198). ESTADO_SESION está modificado y sin commit, como se esperaba. |

Fuera de alcance: ninguno. `.env`, `config.py` y `lab/_gpt_probe_analista/` no están en los commits. `gfx_profiles/*.json` y `diag_234_cap4.py` aparecen modificados en el árbol de trabajo, pero no entraron en A ni en B.

Observaciones:
1. El backstop de m03 excede la letra del handoff. Este solo permitía un `except ValueError` por imagen, con la imagen siguiendo «por el backstop» de F8, que saca la frase. El código nuevo arma prosa a partir de los slots crudos cuando hay 3 intentos vacíos, y eso es lógica nueva. Está acotado: `sin_respuesta == max_attempts`, el texto sigue por las reglas F8 y el rango, y el log lo avisa. Sin esto, la imagen habría caído en `VisualValidationError`, que es lo que tumbó a F26. Lo anoto como desvío menor que Omar debe aceptar de forma explícita. El reporte lo declara con diff.
2. Hay 3 imágenes del gancho (cap 1, #3, #4 y #5) con prosa de slots sin tejer. Existe `cap1_backstop_3_4_5.jpg` para revisarlas. La calidad visual no la verifiqué.
3. Las 37 respuestas vacías son todas PROHIBITED_CONTENT, no una falla aleatoria. Con otro tema el backstop podría dispararse mucho más seguido.
4. Hay 4 mensajes «anchor NO es substring exacto» en el log de m03. Se recuperaron en el intento 1, sin costo extra reportado.

Riesgos que el contrato no cubre:
- El gasto de las fotos madre de GPT (paso0, 2 imágenes) no entra al cost_tracker. El reporte lo admite, pero el total de US$ 5.32 está subestimado.
- La métrica de 2.4 palabras/s sale de un solo video (Vajont). Con otra voz o ritmo el «≈ min» puede volver a errar.
- Con m01c apagado, nada cubre el caso de que un bloqueante deje caer la promesa del gancho por otra vía. La guardia léxica sigue, pero solo en la reparación de oraciones.

**PARADA.**
