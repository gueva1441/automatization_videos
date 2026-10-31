# HANDOFF F60 Etapas B + C — madre por persona + secuencia en producción (caps flux y caps con clip)

Rama `f11-guion-v4`. `main` no se toca. **Base:** `HANDOFF_F60_madre_personas_secuencia.md` §Etapa B y §Etapa C (leelas enteras). Este documento las **actualiza** con lo aprendido en 0b, A, A2 y A3; donde choquen, manda este. Usá tantos subagentes en paralelo como el trabajo permita. Sin tope de dólares; el costo se reporta después.

## Qué cambió desde el handoff base (lo que manda)
1. **Cola, no síncrono** (0b): la llamada de secuencia va por `queue.fal.run`; `request_id`/`status_url`/`response_url` se guardan en disco ANTES de esperar (reanuda sin re-pedir si ya existe), y se espera con la función de poll de `asset_manager`. `_clip_poll` pasa a llamarse `_fal_queue_poll` (la usan clip e imagen de secuencia; `_flux_poll` NO se toca); su único llamador de producción es asset_manager.py:~648; sin alias (el lab `etapa0b_secuencia.py` queda roto y no se re-corre: declaralo). La madre t2i de persona también va por la cola, misma función.
   - Pedidos en disco: `output/<vid>/_secuencia/pedidos.json`, clave = md5 del lote (prompts + refs en orden); si la clave existe con `request_id`, se reanuda sin re-pedir; si los ítems cambiaron, la clave cambia y se pide de nuevo.
2. **Prompt de la madre (B.1)** — ya no se recorta nada: desde A3 `appearance_canon` trae solo el aspecto fijo. Se quita el PARÁ de B.1. Prompt en código, sin LLM:
   ```
   Head-and-shoulders portrait of {appearance_canon}, {ROPA_MADRE}. {appearance del people_group (regla del handoff base)} Neutral expression, facing the camera, plain mid-grey background, soft even light. {ESTILO_C con el año de la madre} {NO_TEXT}
   ```
   `ROPA_MADRE = "wearing a plain, clean, light-coloured shirt"` pasa a constante de producción (hoy vive en `lab/hyperframes/f60/etapa0b_secuencia.py`; OK de Omar 17:48). `condition_by_period` NO entra a la madre.
3. **Filtro de edad (nuevo, OK de Omar 20:29)**: la madre es la cara de la persona en su `era`. Año de la foto = primer número de 4 dígitos de `anio` (existe en `image_prompts`, `image_f8` y supps; `_iter_image_items` hoy no lo lleva: agregalo). Una persona NO aporta madre a una foto si ese año cae fuera del tramo de su `era` (`m03_visual._tramo`) **y** dentro de algún tramo de su `condition_by_period` que también esté fuera de su `era`. En cualquier otro caso, sí aporta. `era` o `anio` ilegibles → aporta. Vale para el «≥ 2 fotos», para el people_group de la madre (contado sobre esas mismas fotos) y para la regla única de madres en todos los caminos (secuencia, una foto, caps con clip, QA). La persona sigue en `persona` (es ruteo). Sin números nuevos.
   - Simulación del auditor sobre A3: Daniel 13 fotos → 12 con madre; sin madre solo la de 1991 (cae en su `condition 1991-1992`); el baile de 1961 y Madrid 1966 conservan la madre. Personas con madre (≥ 2): Daniel, María, Víctor Calvo, Milagros, Ramón, Eric Saint, Mercedes, Maitland Parker. Escribí la tabla real en la salida.
4. **Lotes en paralelo**: solo la madre de una persona va antes que sus lotes; lotes de distintas personas y lotes de la misma persona corren a la vez, con tope `FLUX_MAX_WORKERS`.
5. **Fotos por llamada = 6** (DECISIONES 18:34).

## Etapa C — caps con clip (diseño, va en esta misma tanda)
- `persona` ya llega a `image_f8` y a los supps de los caps con clip (A: `CLAVES_F8_PAPEL`). Verificá que m06 la conserve hasta `asset_manager` en esos caps; si m06 la pierde (copia `image_prompt` sin `image_f8`), llevala — es el único cambio permitido en m06 además del registry de B.2.
- Supps de caps con clip: entran al MISMO pre-paso de secuencia que los caps flux. El pre-paso corre UNA vez en `process_script`, antes del bucle de caps (los lotes cruzan caps: Daniel junta `ch01_supp_02` con `ch04_img_10`), y devuelve sus resultados por (cap, idx) a `_process_flux_chapter` **y** a `_generate_supplementals_for_veo_chapter` (si no, la supp ve el archivo hecho y queda `skipped_exists` en vez de `ok_secuencia`).
- Condiciones de entrada a secuencia (todas, sobre la lista CRUDA): `len(persona) == 1`, `persona[0]` con madre que aporta (punto 3), `_norm_foto_madre_refs(item.get("foto_madre_ref")) == []`, sin `text_in_image` o con `present` falso. Ítems como `[Milagros, John Patrick]` van por una foto aunque solo uno tenga madre. **Lote de 1 foto → camino de una foto** (no secuencia).
- Foto inicial del clip (`image_f8`): camino de una foto con la regla única de madres (no secuencia: es una sola).
- Foto final del clip: sin cambio (ya sale por `/edit` desde la inicial y hereda la cara).
- `_process_veo_chapter` lee `chapter["image_prompts"]` como list[str] y `chapter["id"]`: entre m06 y él hay un adaptador (buscalo: grep `video_prompts`); ahí también se puede perder `persona`.
- `process_script`, `_generate_supplementals_for_veo_chapter`, `_process_veo_chapter` y el pre-paso reciben el registry de madres. **PARÁ** si hay que cambiar más que esas funciones, el adaptador y m06: mostrá el porqué.

## Módulos que toca (y para qué)
| módulo | para qué | cambio |
|---|---|---|
| `foto_madre.py` | arma las fotos madre | + madre por persona (Seedream t2i del perfil), prompt del punto 2, filtro del punto 3 para el «≥ 2» |
| `script_engine/m06_assembler.py` | arma lo que va a `asset_manager` | registry `{nombre: foto_madre}`; `persona` en caps con clip si se pierde |
| `asset_manager.py` | pide las fotos y clips | regla única de madres + filtro por era; pre-paso de secuencia por la cola; `_fal_queue_poll`; función que baja N y registra N en el costo; caps con clip |
| `qa_studio_server.py` | arreglos de fotos en QA | fix y nueva semilla con la regla única (base B.4) |
| tests | | los del base B.5 + filtro por era (dentro / fuera / era ilegible / year vacío) + caps con clip + reanudar desde `request_id` guardado |

## Constantes (todas con origen; ninguna nueva salvo las declaradas)
| valor | origen |
|---|---|
| fotos por llamada = 6 | Omar, DECISIONES 18:34 |
| madres por llamada ≤ 2 | existente `_norm_foto_madre_refs` |
| madre si ≥ 2 fotos (dentro de su era) | analista (base) + filtro del punto 3 (Omar 20:29) |
| espera de la cola = `CLIP_POLL_TIMEOUT` (600 s) | existente; 6 fotos midieron 283 s en 0b |
| `ROPA_MADRE` | Omar 17:48 |
| precio por imagen v5 Lite (/edit y t2i) = 0,035 US$ | pricing de fal leído en la Etapa 0, confirmado en 0b (10 × 0,035); si fal devuelve el costo en la respuesta, usá ese |
| timeout del submit a la cola = 60 s | literal existente de `_call_clip_once`; pasalo a constante con nombre y ese origen |
| año de la madre = primer número de 4 dígitos de `era` | base |
Cualquier otro número: PARÁ y preguntá.

## Prueba (copia `lab/hyperframes/f60/base`; NUNCA topics_db ni `_steps` reales)
- Entradas: canon `a3/05_visual_canon_a3.json` inyectado al topic (como en A3) y `a3/03_visual_a3.json` como 03_visual de la copia.
- Rutas: los módulos hacen `from config import OUTPUT_DIR`/`STEPS_DIR` al importar → parcheá `foto_madre.OUTPUT_DIR`, `asset_manager.OUTPUT_DIR`, `m06.STEPS_DIR` y `m06._load_topic` (que devuelva el topic con el canon A3), nunca `config`. `save_db` NO se llama. `video_id` de lab para el costo. Verificá con mtimes que nada fuera de la copia cambió.
- **Prohibido `process_script`** en la prueba (pide clips): el runner llama directo a la madre, al pre-paso y al camino de una foto, ítem por ítem.
- Generar: madres de las personas con ≥ 2 fotos dentro de su era, y SOLO las fotos que tienen `persona` (caps flux + supps y foto inicial de caps con clip). Clips: NO (cero video).
- Salida `SALIDA_BC.md`: por persona, hoja de contacto (madre + sus fotos) y tabla foto → camino (secuencia / una foto / sin madre por era) → lote → tiempo; Daniel 1991 sin madre; fotos que la cola no devolvió y su caída; costo real; dos miradas por foto (CC + subagente que no vio las anteriores): cara 1–10 frente a la madre, contagio, anacronismos.

## Etapa X en paralelo (subagente aparte, lab, ≈ US$ 0,10): anacronismos
- Regenerar 3 fotos de 0b (prompts, madre y semilla de `e0b/`, ids de 0b): `ch03_img_16` (avión: la frase genérica del avión se cambia por el nombre concreto); `ch02_img_05` (reloj) y `ch05_img_05` (buzón/aparato): el prompt no nombra el objeto → se AGREGA una frase con el objeto de época concreto. El nombre sale del research/ficha de Wittenoom; si no lo trae, el subagente lo busca y cita la fuente. 3 `/edit` sueltos.
- Salida en `SALIDA_BC.md` §X: antes/después y si el anacronismo se fue. Nada de producción.

## DECISIONES.md (CRLF, tal cual)
```
- 2026-10-30 20:29 · **F60 B:** una persona no aporta su foto madre a una foto si el año (`anio`) cae fuera de su `era` y dentro de un tramo de su `condition_by_period` fuera de su `era` (p. ej. Daniel enfermo en 1991); en cualquier otro caso sí; ilegible → sí · Omar · F60
- 2026-10-30 20:29 · **F60 B:** la secuencia va por la cola de fal con el `request_id` guardado antes de esperar; `_clip_poll` → `_fal_queue_poll`; `ROPA_MADRE` pasa a producción · Omar · F60
```

## PARADA B+C
Commit, ESTADO, F60_REPORT §Etapas B+C (+ §X) con el veredicto íntegro del `revisor-handoff`. Nada de producción de Wittenoom (voz, fotos reales, clips, render) sin OK de Omar.
