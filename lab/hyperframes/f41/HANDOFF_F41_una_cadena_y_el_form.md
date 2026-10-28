# HANDOFF F41 — Una sola cadena y el form de punta a punta

Analista · 2026-10-27 · rama `f11-guion-v4` (main no se toca) · Modelo CC: Opus medium (cableado y borrado, sin módulos nuevos).

## Por qué (en llano)
El form de QA Studio lanza `run_pipeline.py --research --video-type long --batch`, que es el orquestador que encadena las fases. Ese orquestador quedó del tiempo de antes de F11: no conoce lo que se construyó de F11 a F40. Omar quiere correr un tema nuevo de 0 desde el form. Hoy eso falla en silencio:

| # | qué pasa hoy (verificado en el código y en `data/topics_db.json`) | dónde |
|---|---|---|
| 1 | `fase1_5` elige la cadena por `guion_version` (3/4 = nueva) o por los flags `--v3 --guion v4`. Ningún topic nuevo guarda `guion_version`: `f39-kyshtym`, `f18-kyshtym-mayak` y `f8s1-ycua-bolanos` tienen `None`. Solo `f8s3-vajont` tiene 4, puesto a mano por el script de lab de F26. `run_pipeline` no pasa los flags → **desde el form corre la cadena vieja**: el `m01a` viejo regenera el esqueleto y pisa lo hecho. | `fase1_5.py:173-181`, `:508`, `:522-529`; `run_pipeline.py:124` |
| 2 | La PARADA del papel sale con exit 0 y sin `data/scripts/<id>.json`. `run_pipeline` la reporta como «m06 quedó en [R]/[E]», pero el juez m06 está desconectado desde el chat 119, y ahí corta. No existe compuerta del papel en el form. | `run_pipeline.py:131-137`, `fase1_5.py:573-581` |
| 3 | La fase VIDEO corre `fase2b <id>` sin `--plan-only` y sin `--gfx`: no hay guion de pantalla, ni su compuerta, ni el render con gfx. | `run_pipeline.py:170-184` |
| 4 | Los topics recientes tienen `video_type = None`. | `topics_db.json` |

Decisión de Omar (20:59): no importa perder topics viejos; el único publicado es Orleans. **La cadena vieja se borra.** Queda una sola: la de F39 (research v3 → ficha → escaleta → guion v4 → partición y títulos → papel), seguida de voz, música, m03, foto madre, assemble, imágenes, visor, fondos, guion de pantalla, render con gfx y fase3.

## Constantes
| valor | origen | quién |
|---|---|---|
| Tope de la tanda **US$ 0,00** | Derivado: la tanda no llama a ninguna API (todo es en seco o con stubs) | analista |
| Ritmo de imágenes 7,0 s por imagen (sin cambio) | Ya existe: `m03_visual.SECONDS_PER_IMAGE_TARGET` (línea 1195). El 10,75 de Vajont era un recorte del script de lab de F26/F27 y no entra | voto del analista; Omar lo confirma al pegar el prompt |
| Fondos del `--plan-only` = el `fase2b <id>` sin gfx que ya existe (código cero) | `fase2b.py:2918` lo exige («correr el render una vez o fase2b sin --plan-only») | voto del analista; Omar lo confirma al pegar el prompt |
| Flags del render final: `--reuse-visuals --keep-segments --gfx --gfx-sparse` | Ya existen: `lab/ESTADO_SESION.md:843` («Video completo») | proyecto |

Cualquier otro número que haga falta → PARADA y se le pregunta a Omar.

## Parte A — Una sola cadena (módulos: `fase1_5`, `topic_researcher`, `fase1`)
| módulo | hoy | después |
|---|---|---|
| `fase1_5` | Dos cadenas (vieja y v3), elegidas por `guion_version` o por `--v3/--guion`; también el guionista v3 (F10) junto al v4 | Una sola cadena: la de F39 con guion v4. `is_v3_topic`, `is_v4_guion`, `--v3`, `--guion` y las ramas viejas se borran. Un topic sin `evidence_pool` v3 → PARADA con su motivo, sin gastar |
| `topic_researcher` | No guarda `video_type`; `investigar_semilla` y `research_topics` no marcan nada de cadena | Todo topic que sale de research guarda el `video_type` pedido (el form manda `long`) |
| `fase1` | Auto-chain a `fase1_5.run_one_topic_from_menu` con lo que hubiera | Igual, pero llega a la única cadena (sin flags que olvidar) |

A.1 **Lista previa (sin PARADA):** cada función, rama, flag y módulo que queda sin llamador en producción al borrar la cadena vieja (AST o `lab/tools/mapa_modulos.py`), con sus tests. Lo que tenga otro llamador vivo no se borra y se anota. Se borra, no se apaga. Los tests de lo borrado se borran por nombre.
A.2 `video_type`: research lo guarda en el topic. No se toca la caída a `short` por cap de fase2b (o14): queda en la lista.
A.3 **Salida en texto de A:**
- La tabla de lo borrado (archivo:función · llamadores = 0 · tests borrados).
- `grep` 0 de `is_v3_topic|is_v4_guion|--v3|--guion` en código de producción.
- Una tabla de solo lectura para cada topic de `topics_db.json`: qué haría hoy `fase1_5 --topic <id> --batch` (la única cadena desde qué paso, o PARADA con qué motivo). Sin correr nada.

## Parte B — El orquestador y el form (módulos: `run_pipeline`, `qa_studio_server`, `qa_form.html`; `qa_form_markers` solo si hace falta)
Interfaz fija con A: `python fase1_5.py --topic <id> --batch`, `--from normalizer_gate` y `--aprobar-papel "QUIÉN FECHA"`, más `fase1_5.estado_papel(id)`. Con eso B corre en paralelo con A.

| módulo | hoy | después |
|---|---|---|
| `run_pipeline` | GUION → ASSETS → VISOR → `fase2b` sin gfx → fase3; la PARADA del papel se lee como «m06» | GUION → **PAPEL** → voz e imágenes → VISOR → FONDOS → **GUION DE PANTALLA** → RENDER gfx → fase3; retoma un topic donde quedó |
| `qa_studio_server` | Lanza solo `--research` | Además lanza «retomar topic» (`run_pipeline --topic <id> --batch`) |
| `qa_form.html` | Gates: seed_pick, judge_action, visor_gate, remeasure_pick | Más `papel_gate` y `guion_gate`, que muestran el documento entero, legible dentro del form |

B.1 **GUION:** `fase1_5 --topic X --batch`. Si `estado_papel(X)` no está aprobado → compuerta del papel (B.2). El mensaje «m06 [R]/[E]» se borra (el juez está desconectado desde el chat 119).
B.2 **Compuerta del papel** (`papel_gate`, con `QA_FORM`):
- Muestra `data/scripts/_steps/<id>/01e_pantalla.md` entero. Botones: **A** aprobar / **P** parar.
- A → `fase1_5 --topic X --aprobar-papel "Omar <fecha de hoy>"` → `fase1_5 --topic X --from normalizer_gate --batch`, que es voz, música, m03, foto madre y assemble.
- P → reporte con el comando para retomar.
- Sin `QA_FORM` (terminal): para siempre e imprime el comando. **Nunca se aprueba solo.**
B.3 **ASSETS y VISOR:** sin cambio (`fase2a` y `visor_gate`).
B.4 **FONDOS:** `fase2b X` sin gfx (cuece los visuales base y deja un mp4 de preview).
B.5 **GUION DE PANTALLA:** `fase2b X --plan-only` → `guion_gate`:
- Muestra `output/<id>/GUION_PANTALLA.md` entero. Botones: **A** aprobar / **P** parar.
- P es el camino normal cuando el analista revisa y aplica `--plan-edit`; después se retoma.
- A → `fase2b X --aprobar-guion "Omar <fecha de hoy>"` → `fase2b X --reuse-visuals --keep-segments --gfx --gfx-sparse` → fase3, igual que hoy.
- Sin `QA_FORM`: para siempre e imprime el comando.
B.6 **Retomar:** `etapa_de(id)` es de solo lectura y decide por artefactos en disco (papel aprobado, `data/scripts/<id>.json`, `assets_manifest.json`, visuales base, `GUION_PANTALLA.json` con `aprobado`, mp4 con gfx). `run_pipeline --topic X` arranca en la primera etapa que falta. **Nunca re-corre una etapa pagada que ya está hecha.**
B.7 El orquestador **no cierra ningún programa de Omar** (DECISIONES 00:30). Si el render necesita RAM, avisa en el reporte y no cierra nada.
B.8 **Salida en texto de B:**
- La tabla `etapa_de` para cada topic de `topics_db.json`.
- El recorrido en seco del form con stubs (el smoke ya inyecta `_form_command`): los marcadores emitidos en orden, del research a fase3, con A en ambas compuertas, y el recorrido con P en el papel seguido de «retomar».

## Validación (US$ 0)
Tests nuevos para B.1–B.6 en `test_run_pipeline.py` (stubs, sin API), suite rápida, suite amplia y el candado de ch02 de Orleans (`lab/hyperframes/f40/verificar.sh`). **Prohibido** correr `fase1_5`, `fase2a` o `fase2b` reales, aprobar papel o guion, o tocar `main`.

## Abierto que no entra (lista de 18:30, se arregla solo si se repite)
o14 (`video_type` por cap → short), foto madre fuera de `cost_tracker`, costo de Claude que el form no muestra (solo Gemini), iniciales en el normalizer y el cortador, el cortador parte las citas.

## Después de F41
Omar corre un tema nuevo de 0 desde el form. El analista revisa el papel y el guion de pantalla en sus compuertas (skill `revision-guion-pantalla`).
