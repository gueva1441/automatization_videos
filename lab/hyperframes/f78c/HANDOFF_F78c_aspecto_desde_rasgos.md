# HANDOFF F78c — el texto de la escena describe a la persona con SUS rasgos (no el canon genérico) + lab de motor para las manos

Rama `f11-guion-v4`, base `a6ff9a9` (F78b B). Topic de prueba: Colza `c4934b7d-3f54-448f-ba5f-539dc744f0d8`.
Omar aprobó 2026-11-04 20:30 ET («si dale»). Anotar en DECISIONES.md con esa fecha.
Usá tantos subagentes en paralelo como permita el trabajo.

## Por qué (causa raíz, medida en disco)
1. El texto de cada foto /edit lo escribe Opus en los casilleros de m03 (`script_engine/m03_visual.py`, bloque `PERSONAS DOCUMENTADAS`). Ahí recibe `appearance_canon` = «a middle-aged Spanish man» y nada más; entonces INVENTA pelo y cuerpo: ch07_supp_07 «dark short practical hair» (Carmen; su madre tiene trenza larga), ch06_img_14 «dark greying hair» (Arcadio; su madre tiene pelo negro rizado, barba, corpulento). Ese texto contradice la foto de referencia y le gana.
2. `rasgos.json` (F78a) ya tiene el aspecto fijo de cada persona, sale SOLO del canon (entrada = name/role/era/appearance_canon/grupo_appearance) y tiene cache por md5. No depende de m03 → se puede pedir antes de m03.
3. Las manos deformes de Arcadio: el texto YA dice «deformed hands / stiff fingers», la variante YA las tiene, y Nano Banana 2 Lite /edit igual las suaviza. Hipótesis a medir: el motor Lite. Por eso la Etapa B compara contra Nano Banana 2 completo.

## Tabla de constantes
| valor | origen | quién |
|---|---|---|
| 5 fotos del lab: ch01_img_01, ch01_supp_05, ch06_img_14, ch04_img_12, ch07_supp_07 | las 4 de control de F78b + la foto de arranque del clip del gancho | analista, OK Omar 20:30 |
| motor Lite `google/nano-banana-2-lite/edit` | `engine_profiles.py` (F68) | ya existe |
| motor completo (Nano Banana 2, /edit) | id y precio: leelos de la página de fal y declaralos en el reporte; NO entran a producción en esta tanda | Omar 20:30 (opción b) |
| fotos del motor completo: solo las 3 de Arcadio (ch01_img_01, ch01_supp_05, ch06_img_14) | las manos son el problema medido | analista |
Ningún número nuevo en código de producción.

## Módulos que toca
- `script_engine/m03_visual.py` — hoy: el bloque PERSONAS DOCUMENTADAS lleva `appearance_canon` genérico. Después: si la persona tiene rasgos (cache `foto_madre/rasgos.json` vía `foto_madre.rasgos_personas`), la línea `appearance_canon:` se REEMPLAZA por `appearance: <rasgos>` (no se suman las dos). Persona sin rasgos → la línea vieja tal cual. Edad y `condition <años>` no cambian.
- `foto_madre.py` — hoy: la entrada de `rasgos_personas` se arma dentro de `generate_fotos_madre_personas`. Después: esa construcción de la entrada sale a una función pública (p. ej. `entrada_rasgos(topic)`) que usan m03 y foto_madre, para que el md5 coincida y la segunda llamada salga del cache (0 llamadas extra). Nada más cambia.
- Cambiar la frase de cabecera del bloque: «en la prosa usar appearance_canon» → «en la prosa usar appearance (o appearance_canon si no hay)». Es la ÚNICA edición de texto de prompt; no se agrega ninguna regla. Pegá el antes/después completo de esa línea en el reporte.
- `lab/hyperframes/f78c/` — script del lab, hoja, reporte.

## Etapa A — código (sin generar nada)
1. Lo de arriba + tests (rasgos mockeados; ninguna llamada a la red): con cache → línea `appearance:` y sin `appearance_canon`; sin cache/persona sin rasgos → línea vieja; md5 de la entrada igual desde m03 y desde foto_madre.
2. Si m03 corre antes de que exista `output/<tid>/foto_madre/`, la función de rasgos la crea (ya lo hace con `mkdir`). Si la llamada de rasgos falla, m03 sigue con `appearance_canon` y deja un WARN (no frena el cap).
3. Salida en texto: el bloque PERSONAS DOCUMENTADAS de Colza antes y después, completo, pegado en el reporte. Esperado (simulado por el analista con `rasgos.json` real):

| persona | antes (appearance_canon) | después (appearance) |
|---|---|---|
| Jesús Sancho Rof | a middle-aged Spanish man | Broad oval face … thick dark-rimmed glasses, stocky build |
| Antonio Muro Fernández Cavada | a middle-aged Spanish man | Long narrow face … full dark moustache, lean wiry build |
| Arcadio Fernandez | a middle-aged Spanish man | Round full face … thick short curly black hair, short full black beard, heavyset |
| Angela Menseger | a middle-aged Spanish woman | Soft heart-shaped face … shoulder-length wavy dark brown hair |
| Jesús Lozano | a six-year-old Spanish boy | Small round face … short straight black hair with a blunt fringe |
| Carmen Cortés | a fourteen-year-old Spanish girl | Oval face … long dark brown hair tied back in a single braid, slender |
| Mercedes García | a young adult Spanish woman | Angular face … long straight black hair, thin wire-rimmed glasses |

Commit A.

## Etapa B — lab (NADA de producción se reemplaza)
Todo se escribe en `lab/hyperframes/f78c/b/`; `output/<tid>/assets`, `03_visual.json`, `data/scripts/<tid>.json` y QA Studio NO se tocan (verificalo con md5 antes/después y pegalo).
1. Para las 5 fotos: casilleros de nuevo con Opus por la función de producción de una foto (`_f8_refill` o la que use QA Studio), con el bloque de la Etapa A y la misma ancla/beat, nota vacía. Armado con `armar_item`. Guardá el prompt nuevo junto al viejo.
2. Generar con la referencia que hoy usa cada foto (la variante de F78b o la madre limpia, según `_madres_para_item`):
   - V1 = prompt nuevo + Lite: las 5.
   - V2 = prompt nuevo + Nano Banana 2 completo: las 3 de Arcadio.
   - V0 = la foto actual de producción (sin costo).
   Si un motor rechaza por moderación, anotalo; sin respaldo Seedream en el lab (queremos ver el motor puro).
3. Hoja `ETAPA_F78c.html`: por foto, fila V0 | V1 | V2 con la referencia al lado y los dos prompts (viejo/nuevo) debajo. Salida en texto: tabla foto → prompt viejo (subject) → prompt nuevo (subject).
4. Costo real por servicio en `b/costo.json` y en el reporte.

## Reglas fijas
- Sin hardcode; sin reglas nuevas en prompts (solo la cabecera de arriba).
- Nada se borra: lo que reemplaces en código va con sus tests viejos actualizados; nada de flags que dejen las dos lógicas.
- Subagente `revisor-handoff`: su veredicto íntegro en el reporte. ESTADO_SESION.md después del veredicto.

## PARADA
Al terminar B. No correr la Etapa C de F78a ni regenerar nada de producción. Omar y el analista miran la hoja y deciden: (1) si el texto con rasgos va a producción — eso implica rehacer los casilleros de TODAS las fotos con persona antes de la Etapa C, y (2) si el motor completo reemplaza a Lite para fotos con persona.

## ADENDA de auditoría del analista (manda sobre el cuerpo)
1. El bloque vive en `_format_seedream_canon_block(topic, anios)`, que hoy solo recibe `topic`. Para encontrar `foto_madre/rasgos.json` hace falta la carpeta del video: declará cómo la obtenés (id del topic = id del video en Colza, ambos `c4934b7d…`; si no es siempre así, pasala como argumento desde quien llama). No inventes una ruta fija.
2. La entrada de rasgos hoy se arma en `foto_madre.generate_fotos_madre_personas` (~l.632: name/role/era/appearance_canon/grupo_appearance). Esa construcción exacta es la que sale a la función pública; probá en un test que el md5 desde m03 = el md5 de `rasgos.json` de Colza (`md5_entrada` actual) → 0 llamadas nuevas en Colza.
3. Periféricos que heredan el bloque (esperado, pero declaralo en el reporte): el clip Veo/Omni (`_render_prompts_seedream_veo`), los refills de m03 (`_f8_refill`), QA Studio (editor de foto) y m09_packaging (miniaturas, l.~423). Ninguno se regenera en esta tanda.
4. El lab de la Etapa B NO regenera el clip del gancho aunque cambie ch01_img_01: solo la foto.

## ADENDA 2 (2026-11-04 20:55, respuesta a la PARADA de CC) — manda sobre el cuerpo y la adenda 1
Va la opción (a) de CC: m03 SOLO lee `rasgos.json`, y únicamente si su `md5_entrada` coincide con la entrada armada desde el `03_visual.json` en disco, con la misma función pública de foto_madre. Si no coincide o no existe, m03 deja la línea vieja `appearance_canon` + WARN, y nunca llama a rasgos. Se anula «pedir rasgos antes de m03» del cuerpo y el punto 2 de la Etapa A.
Topic nuevo: la primera pasada de m03 sale genérica. Si el lab gana, el paso automático que vuelve a llenar los casilleros de las fotos con persona después de la foto madre va en otra tanda (decisión 1 de Omar). No va en esta.
