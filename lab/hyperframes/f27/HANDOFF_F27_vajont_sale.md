# HANDOFF F27 — Que salga el video de Vajont, y tres cortes en la reparación del guion

Analista · 2026-10-25 · Para CC. Base: `26c0065` (rama `f11-guion-v4`). Dos partes; **A primero, B después**. Tope: Gemini US$ 4 · imágenes ≤ 100 · Claude US$ 0 (B no llama a Claude). **PARADA al final de B** con el video en disco.

## 0. Por qué
- F26 §B: m03 cayó dos veces en el cap 1 porque Flash devolvió una respuesta **sin texto** y `gemini_helpers._try_json_parse` hizo `None.strip()`. Un helper que revienta el video entero por una imagen es un bug del helper, no del gancho. m03 ya tiene guardia y backstop por imagen (F8: «si siguen, se saca la frase»); hay que dejar que lleguen ahí.
- F26 §A.3: la reparación (e) **borró la oración** de Kuleshov en vez de quitar el nombre; y el editor m01c, que corre si el crudo trae un bloqueante, **se llevó la promesa del gancho** (−98 palabras). Con el tope ya como métrica (F25c), m01c no tiene razón de estar en el camino v4: sale, como salió la columna.
- Métrica: la voz real va a **2.4 palabras/s** (980.8 s para 2,355 palabras), no a 2.05. El «≈ min» de los reportes estaba inflado un 17 %.

## A. Tres arreglos de código (0 API; tests sin red)
1. **`gemini_helpers`: respuesta vacía = fallo de parseo.**
   - `_try_json_parse(raw_text)`: si `raw_text` es `None` o queda vacío después de `strip()`, lanzar `_JsonParseError(("", "", JSONDecodeError("respuesta vacía", "", 0)))`. Así `_parse_with_retry` re-llama hasta `PARSE_MAX_ATTEMPTS` y, si sigue vacía, propaga el `ValueError` de siempre (mismo mensaje, con «respuesta vacía» en el texto).
   - Guardar el motivo: donde se lee `.text` de la respuesta, capturar `candidates[0].finish_reason` (y `prompt_feedback.block_reason` si existe) y ponerlos en el log y en el dump de JSON inválido. Nada más cambia en el helper.
   - m03: confirmar (sin tocar m03) que `_fluidify_with_leakage_guard` **atrapa** ese `ValueError` por imagen y pasa al backstop, como hace con cualquier otro fallo de re-tejido. Si no lo atrapa —si hoy un `ValueError` del helper sube hasta `process_topic`— agregar el `except ValueError` **solo** en `_fluidify_item`/`_fluidify_with_leakage_guard`, con el motivo en el log, y que la imagen siga por el backstop. Ese es el único cambio de lógica permitido en m03, y va anotado en el reporte con el diff.
   - Test: un `get_text_fn` que devuelve `None` tres veces → `ValueError` con «respuesta vacía»; uno que devuelve `None` y después JSON válido → el dict.
2. **Reparación (e): el nombre se quita, la oración se queda.**
   - En `guion_v4` (edición de la oración, ~l. 1022), cuando el motivo es (e) el pedido dice: «La cita va SIN el nombre: reemplazá el nombre por su rol como viene en los datos (un operario, un testigo, un ingeniero) o por «alguien que estuvo ahí». No saques la oración.» Para los otros motivos, el pedido queda como está.
   - La guardia léxica de m01c sigue aplicando igual.
   - Test: párrafo con «Kuleshov recuerda…» y motivo (e) → la oración sigue, sin «Kuleshov», con un rol.
3. **m01c sale del camino v4.**
   - En `reparar`, la pasada `editor_pass` **no corre** (ni con bloqueantes); queda detrás de `--editor` en `fase1_5` para leer, con el aviso «[editor v4] fuera del camino desde F27». La función no se borra.
   - Los tests que fijaban «si `bl0`, corre el editor» se adaptan; ningún chequeo cambia.
4. **Métrica:** `PALABRAS_POR_SEG = 2.4` con el comentario «F27: medido en Vajont F26 (2,355 palabras → 980.8 s)». Los tests que fijaban 2.05 se adaptan.
5. Suite rápida y amplia verdes (las 5 de siempre, previas). Commit A.

## B. Vajont: retomar desde m03 hasta el mp4
1. `lab/hyperframes/f26/b/f26b_produccion.py --etapa guion`: reusa voz y música de F26 (no se vuelve a pagar); corre normalizer → m07 (música fija a los `*_curated`, como en F26) → **m03** → paso0 → assemble. Si el cap 1 vuelve a fallar en m03, que el reporte diga el `finish_reason` y qué hizo el backstop con esa imagen. **Tres intentos** de m03 como máximo (US$ ~1.2 cada uno).
2. `--etapa imagenes` (fase2a, Seedream 5.0 Lite): plan de 92 a 10.75 s como en F26. Tope 100 incluyendo re-hechuras del guardia de visión.
3. `--etapa render` (fase2b con gfx, identidad `misterio`). Si el gfx falla una vez con 16.3 min → `--etapa render_sin_gfx` y anotarlo. Salida: `output/f8s3-vajont/video_vajont_f26.mp4` (o donde fase2b lo deje; la ruta exacta en el reporte).
4. QA Studio / `compara` como siempre. **No publicar.**
5. Si un paso que no sea m03 falla dos veces, PARADA de B con el log.

## Frenos
- Cero reglas de estilo, cero chequeos nuevos. Prompts: solo la línea del motivo (e) en A.2.
- m03/gfx/voz: solo lo que dice A.1 (un `except` por imagen) y parámetros; cada cambio con su diff en el reporte.
- Sin merge, sin publicar, sin borrar; `.env`, `config.py`, `lab/_gpt_probe_analista/` no se commitean (el hook lo frena igual).
- `lab/ESTADO_SESION.md` al final.

## Reporte `lab/hyperframes/f27/F27_REPORT.md`
A: diffs de los 4 puntos y los tests. B: por etapa, hecho / costo / qué se trabó; m03 cap 1: `finish_reason` y qué hizo el backstop; imágenes generadas y re-hechas; duración final del mp4; gfx sí/no; ruta del video. Veredicto íntegro del revisor-handoff. **PARADA.**
