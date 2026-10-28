# F50 — El prompt nuevo de foto y de video pasa a producción; Wittenoom en papel

CC, 2026-10-28. Handoff `lab/hyperframes/f50/HANDOFF_F50_prompt_nuevo_a_produccion.md` (md5 `5586254139ed4ddb25ee7504e0d63cfc` ✓). Rama `f11-guion-v4`. Omar al pegar: tope US$ 5,00 y el `negative_prompt` de §C.2 tal cual.

## Commits
| parte | commit | qué |
|---|---|---|
| paso 0 | `3751124` | handoff, DECISIONES 11:15 / 11:22 / 11:50 tal cual, copia de `03_visual.json` y `05_visual_canon.json` en `f50/antes/` |
| A | `5b071d0` | canon desde la ficha (`step_4e.canon_desde_ficha`, `fase1_5.asegurar_canon`), 4e del research borrado |
| B + C | `dcea932` | casilleros con Opus + expediente + armado por código + F8 backstop; movimiento del clip con Opus; `negative_prompt` y `duration` en Veo |
| D | `ab1fd00` | Wittenoom en papel (`PAPEL_FOTOS_WITTENOOM.md/.json`); los caps Veo guardan año, grupo, plano y notas F8 de cada foto |
| cierre | este commit | reporte, ESTADO |

B y C van en un solo commit porque tocan el mismo archivo (`m03_visual.py`) y el mismo archivo de tests (`test_module_f50b.py`); el handoff pedía un commit por parte. Lo de D (claves de los caps Veo) también es de `m03_visual.py`.

`lab/TOPE_TANDA.json` = `{"usd": 5.0, "desde": "2026-10-28T11:35:49"}` (fuera de git).

## Lecturas declaradas
`CLAUDE.md`, `DECISIONES.md` (hasta 11:50), `lab/ESTADO_SESION.md` (cabecera, F49, F48), el handoff entero; `researcher_steps/step_4e_visual_canon.py`, `topic_researcher.py` (4e y su guardado), `fase1_5.py` (`asegurar_ficha`, `process_topic`, `_step_cost`), `script_engine/m03_visual.py` (camino de fotos, re-hechuras, Veo, `_call_with_validation_retry`), `script_engine/m03_imagenes_v3.py`, `asset_manager.py` (`_call_veo_once`, `_generate_veo_clip`), `claude_helpers.py` (`call_json`, `make_call`, `ClaudeError`), y del lab `f46b_corridas.py`, `f47_corridas.py`, `f48_corridas.py`, `f48/pedidos/pedido_S5_ch02.txt`, `f48/slots_S5_ch0{2,7}.json`, `f48/canon_S5.json`, `f49/PROMPTS_F49.json`. Tres subagentes Explore mapearon el canon, el camino de m03 y Veo; uno general adaptó los tests viejos de m03.

## Módulos (paso 2 de /tanda)
| módulo | hoy | después |
|---|---|---|
| `researcher_steps/step_4e_visual_canon.py` | canon desde los `verified_facts` del research, sin grupos | + `canon_desde_ficha`, `adaptador_facts`, `bloque_people_groups`, `TEXTO_1_PEOPLE_GROUPS`, `TEXTO_S5`, `VISUAL_CANON_SCHEMA_FICHA`; `extract_visual_canon` acepta `extra` y `schema` y devuelve `people_groups` |
| `fase1_5.py` | ficha → escaleta; m03 sin canon propio | `asegurar_canon` después de la ficha y antes de m03 en todo camino (marca `canon_ficha_md5`); m03 corre con su costo como paso `m03` en `01_v3_costos.json` |
| `topic_researcher.py` | sub-paso 4e | sin 4e (borrado con su guardado y sus tests) |
| `script_engine/m03_expediente.py` (nuevo) | — | expediente por foto y su bloque S5 |
| `script_engine/m03_visual.py` | slots con Pro → tejido de Flash, Guarda 1, re-tejido | casilleros con Opus → armado → F8 backstop; `_seedream_video_prompt` con Opus y el texto §C.1 |
| `script_engine/m03_imagenes_v3.py` | `wrap_style`, `fix_counts_lr` | + `armar`, `frase_cartel`, `f8_backstop`, `anio_final`, `oracion`; chascadas; `wrap_style` borrada |
| `asset_manager.py` | Veo con `prompt`, `image_url`, `generate_audio`, `resolution` | + `negative_prompt` (`VEO_NEGATIVE_PROMPT`) y `duration` (`_veo_duration`) |
| `cost_tracker.py` | — | solo dos comentarios (`m03:fluidificador` → `m03:casilleros`) |

Solo lectura, sin cambios: `m09_packaging.py` importa las `DOCTRINE_*` (siguen; `test_module_138a` pasa); `qa_studio_server.py` usa `am._generate_veo_clip` (hereda C); `foto_madre.py` lee el canon del topic (ahora el de la ficha).

## Paso 0
Las tres líneas de DECISIONES tal cual; `TOPE_TANDA` 5,00 desde 11:35:49; copia de `03_visual.json` (md5 `912eda12…`) y `05_visual_canon.json` (`42dc7886…`) en `f50/antes/`. Además `f50/antes/topic_wittenoom.json`: la entrada de topics_db antes de A (la verificación de B la necesita con el canon viejo).

## Parte A — canon desde la ficha
- `canon_desde_ficha(topic, ficha)` = `extract_visual_canon(seed={"seed_title": video_title}, angle_blocks={}, verified_facts=adaptador_facts(ficha), canonical=…, extra=texto 1 + TEXTO_S5 + personajes, schema=… + people_groups)`: una sola llamada a Flash, todas las claves de esa respuesta.
- `asegurar_canon`: si `canon_ficha_md5` = md5 de `ficha_caso.json`, no llama; si no, arma, guarda en el topic de topics_db (6 claves + la marca) y en `05_visual_canon.json`; sin ficha o sin `people_groups` → Parada.
- **Verificación automática** (`verificar_a.py`, en seco, pedido de `f48.canon_s5` atrapado):
```
  system  lab d41d8cd98f00b204e9800998ecf8427e  producción d41d8cd98f00b204e9800998ecf8427e  =
  user    lab 7c7fbef58983bef8f97f1683cb89aea7  producción 7c7fbef58983bef8f97f1683cb89aea7  =
  schema  lab 62735601b82ec515d12b843e20110d8b  producción 62735601b82ec515d12b843e20110d8b  =
  pedido entero: lab 46ff0c7bbb606792acb9fe1286680389 · producción 46ff0c7bbb606792acb9fe1286680389 → IGUAL
```
- Llamada real en Wittenoom: `[canon] desde la ficha (b02aa6f8): 7 people_groups, 16 personas, 2 props`, US$ 0,0306. Salida en `A_CANON.md`: los 7 grupos (id · who · appearance · clothing), el diff contra `canon_S5.json` (S5 tenía 15 grupos; `spans` 1937-2007 → 1937-2026) y la tabla personaje → grupo (quedan sin grupo los dos prospectores de 1937–1943 y la CEO de la sociedad de enfermos; el grupo de policía de aeropuerto no cubre a ningún personaje).
- Tests: `test_module_f50a.py` (5: adaptador, pedido con grupos, marca md5 misma ficha/ficha nueva, Parada sin grupos, research sin 4e); `test_module_f39_research.py` y `test_module_f7d.py` sin el 4e; fixtures de `test_module_f17.py`, `test_module_f39_fase1.py` y `test_module_f41_cadena.py` con el paso canon falso (orden esperado: … ficha → canon → escaleta …).

## Parte B — prompt de foto en producción
- Pedido a Opus = `_build_seedream_prompt_step2` + `beats_block` + bloque del expediente S5; SI = v3 + `TEXTO_2_PEOPLE_GROUP` + `TEXTO_S4_YEAR` después de `- foto_madre_ref:`; esquema = slots + `year` + `people_group`. `mood`, `style`, `hard_fact_ids` se siguen pidiendo. Modelo `claude-opus-5-5`, effort `guion_v4.ESFUERZO` (high).
- Armado por código y F8 = los del lab (orden medido; sin `, año` si el setting ya trae año o década); después nombres documentados, `fix_counts_lr`, escala y, si queda un problema, se saca la frase. La pasada 1 de `_validate_no_text_leakage` saca la frase que la dispara (`_sacar_frases_con_texto`; el cartel exento). Marcas `sensible` y `motivos` sobre el prompt final.
- Re-hechuras (`_f8_fix_cap`, `_f8_fix_video`): mismo camino; una negativa de Opus → `CasillerosParada` con la foto, sin volver a Pro.
- Año de cada foto: 1) ancla 2) casillero `year` 3) último año dicho en la narración de los caps anteriores (antes: anclas) 4) fecha del dato_central 5) `topic_year`.
- Chascadas: cartel con sujeto y sin el «lettering» pegado; cifra al inicio de oración en mayúscula.
- **Verificación automática** (`verificar_b.py`, `B_VERIFICACION.md`):
```
  pedido cap 2: sistema+usuario = byte a byte (md5 lab 278e1fe2eba1aa1dee0d3fe1c177875c · producción 278e1fe2eba1aa1dee0d3fe1c177875c); esquema = (md5 lab fa1ebfd1a34c53b070f2879ebd1f4181 · producción fa1ebfd1a34c53b070f2879ebd1f4181)
  armado: 28 prompts · iguales 26 · distintos 2 (por chascada 2) · años distintos 0
  → PASA
```
| cap | foto | antes (F49) | después (F50) |
|---|---|---|---|
| 2 | 13 | On the wooden sign board beside the shed reads "WITTENOOM" in hand-painted block letters lettering, in clear crisp lettering. | The words "WITTENOOM" are written on the wooden sign board beside the shed in hand-painted block letters, in clear crisp lettering. |
| 7 | 11 | On the warning sign fixed to the barricade reads "DANGER ASBESTOS" in faded block stencil lettering, in clear crisp lettering. | The words "DANGER ASBESTOS" are written on the warning sign fixed to the barricade in faded block stencil, in clear crisp lettering. |
- Lo borrado con sus tests: tabla en `B_VERIFICACION.md` §3 (fluidificador, Guarda 1 / candado de cifras, re-tejido, `SEEDREAM_SLOTS_USE_PRO`, `_f8_finish_item`, el camino sin escaleta, `wrap_style`; `test_m03_guarda1_degrade.py` borrado; f27 11 → 8; 134b y 03_leakage_retry recortados; f8 17 → 19; f8b 17). Grep final en producción: ningún uso vivo.

## Parte C — prompt del clip Veo
- `_seedream_video_prompt(image_prompt, ancla, label)`: Opus, sistema §C.1 entero, usuario `FIRST FRAME (final):\n…\n\nNARRATOR OVER THIS CLIP (Spanish, context only): «…»\n\nCLIP LENGTH: 8 seconds.`, esquema `{video_prompt}`, validación de largo 120–700 con su reintento. Borrados `_VEO_VIDEO_PROMPT_STRUCT` y `_SEEDREAM_MOTION_SYSTEM`.
- `asset_manager.VEO_NEGATIVE_PROMPT` = el texto de §C.2 tal cual; `_call_veo_once` manda `negative_prompt` y `duration` (`_veo_duration`: 8 s de `VEO_CLIP_DURATION_SEC`, o el pedido; si no es 4/6/8 → error).
- **Llamada de prueba (1, 4 s)** (`veo_prueba.py`, `veo_prueba.json`, `C_VEO.md`): HTTP 200 en el envío, `IN_QUEUE` → resultado con `video.url`; **ok** en 157 s; ffprobe **4,000 s**, h264 1920×1080. fal aceptó `negative_prompt` y `duration`. Costo en cost_tracker US$ 0,24 (la tarifa fija por clip de config).
- Tests: `test_module_f50b.py` (18: chascadas, armado, año, F8, backstop de texto, expediente, año previo, pedido, sin escaleta, negativa → Parada, armado y marcas, movimiento, payload Veo, lo viejo no está).

## Parte D — Wittenoom en papel
`python -u fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --only m03` (`d_m03.log`): canon ya armado (marca), 7 caps en paralelo, PASS.
```
    Anthropic claude-opus-5-5   10 calls  in  188,508  out   61,242  think        0  $1.9789
    Gemini 2.5 Flash          7 calls  in    4,855  out    2,732  think   53,340  $0.1416
    m03:casilleros          7 calls  …  $1.9510
    motor (sin tag)         7 calls  …  $0.1416   (anclas, Flash)
    m03:motion              3 calls  …  $0.0279
    TOTAL: 17 calls · $2.1205 USD
```
- `PAPEL_FOTOS_WITTENOOM.md` (96 fichas: n.º, ancla, beat, año y fuente, people_group, plano, prompt entero, notas F8, rehecha) y `.json`; caps 1 y 7 con `video_prompt` (635 y 583 caracteres), `negative_prompt` y `duration` `8s`.
- Fotos por cap 5 · 16 · 16 · 14 · 16 · 16 · 13 = **96** (antes 96).
- Años por fuente: 1) ancla 28 · 2) casillero `year` 68 · 3)–5) 0.
- Re-hechuras: 0 de cap y 0 de video.
- Carteles: 10 (lista al final del papel).
- Antes de esta corrida hubo otra que corté a mano a los ~66 s (12:06:41 → 12:07:49): los caps Veo no guardaban año, grupo, plano ni notas F8 de cada foto y el papel los pide. Agregué `CLAVES_F8_PAPEL` / `image_f8` y la corrí de nuevo. La cortada no escribió nada en `03_visual.json` y su salida estaba en búfer (`d_m03_cortada.log`); su gasto no quedó registrado (ver abierto n2).

## Costos de la tanda (cost_history desde 11:35:49)
| qué | video_id | US$ |
|---|---|---:|
| canon desde la ficha (Flash) | 123bbb64… | 0,0306 |
| prueba Veo 4 s | f50-veo-prueba | 0,2400 |
| m03 en papel (Opus 1,9789 + Flash 0,1416) | 123bbb64… | 2,1205 |
| **registrado** | | **2,3911** |
| corrida de m03 cortada a los ~66 s | — | sin registrar (≤ ~2,1) |

Tope 5,00: lo registrado queda en 2,39; con lo no registrado, como mucho ~4,5.

## Verificación (paso 8 de /tanda)
| commit | ch02 (md5) | rápida | amplia |
|---|---|---|---|
| antes (F49) | — | 56 | 922 + 4 previas |
| A `5b071d0` (`f41/f50_A/`) | `f792f3d4…` ✓ | 55 | 926 + 5 (m03_merge_timing ×2, gfx_lab ×3) |
| B+C `dcea932` (`f41/f50_BC/`) | `f792f3d4…` ✓ | 55 | 944 + 4 (m03_merge_timing ×2, gfx_lab ×2) |
| D `ab1fd00` (`f41/f50_D/`) | `f792f3d4…` ✓ | 55 | 944 + 4 (ídem) |

La rápida da 55 y no 56 porque en F49 le sumé `test_module_f49.py`; el conjunto de la rápida es el mismo. `mapa --check` 0 en los tres commits (157 archivos de producción, uno nuevo).

## Lo que queda abierto (entero)
- **n1. Cartel con mayúsculas del modelo.** En cap 7 foto 10 y foto 13 la ubicación y la letra vienen con mayúscula y la regla las deja así: «The words "Federal Court" are written Over the entrance in Metal block letters», «… written On the warning sign on the barricade in Bold block stencil». También quedan letras raras como «in typewritten» (cap 5 foto 10) e «in typewriter» (cap 3 foto 5). Arreglo propuesto, sin aplicar: la preposición inicial en minúscula (es gramática); la mayúscula de la letra queda para el analista. No toqué el papel ya generado.
- **n2. Gasto sin registrar** de la corrida de m03 cortada (~66 s; Opus en vuelo). No sé cuántas llamadas a Opus llegaron a cobrarse: como mucho, el costo de una corrida entera (~US$ 2,1).
- **n3. Canon de A con 7 grupos** (S5 de F48 tenía 15) y `spans` 1937-2026. Flash no es determinista: el diff de `A_CANON.md` es informativo. Tres personajes del pool quedan sin grupo (cruce a ojo, sin corte).
- **n4. `central_subject.foto_madre` quedó vacío** en topics_db (el canon nuevo lo trae vacío; antes apuntaba a `output/<id>/foto_madre/subject.png`, que sigue en disco). La foto madre se rehace en la tanda de fotos. `documented_props` también se reemplazó (2 props).
- **n5. `05_visual_canon.json`** ahora es la copia del canon de la ficha (con `people_groups` y la marca); el viejo está en `f50/antes/`.
- **n6. Casilleros que el armado no usa** (`mood`, `style`, `hard_fact_ids`): se siguen pidiendo, como se midió; sacarlos es otra prueba en texto.
- **n7. Sin escaleta v3 no hay camino de fotos:** `_render_prompts_seedream` corta con `VisualValidationError` (el camino v2 con tejido se borró). Ningún topic en producción quedó sin escaleta, pero no lo verifiqué tema por tema.
- **n8. Cap Veo en producción:** el pedido de casilleros lleva el primer cuadro del clip más los extras (cap 7: 13 fotos). En el lab se midieron solo los 12 extras; la verificación byte a byte es del cap 2 (flux).
- **n9. Regla 3 del año cambiada** (narración en lugar de anclas): en el papel no la usó ninguna foto (0 de 96).
- **n10. Costo de Veo:** `track_fal` cobra US$ 0,24 fijos por clip, sin mirar la duración ni la resolución. El precio real de la prueba de 4 s no está medido.
- **n11. fal apaga Veo 3.1 el 2026-11-17** (hallazgo del handoff): Wittenoom llega a tiempo; el reemplazo del motor de clips es otra prueba.
- **n12. Nuevas claves en `03_visual.json`:** `anio`, `anio_fuente`, `_f8_texto_fuera` en las fotos, e `image_f8` y las claves del papel en los caps Veo. fase2a lee `prompt`/`narration_anchor`; no verifiqué que m06 (ensamblado) las ignore sin problema.
- **n13. `test_module_m03_reglas_133.py`** (guion, no pytest) falla por un topic que no está en topics_db (`ec3d7c7f…`): depende del contenido de topics_db, no del código de m03 (sus chequeos del SI pasan); no verifiqué si ya fallaba antes de F50. No entra en la amplia porque pytest no le junta tests.
- **n14. Nombres que quedaron viejos:** `test_module_134b_fluidificador_flash.py` y `test_module_03_leakage_retry.py` se recortaron a lo vivo, pero conservan el nombre.
- **n15. B y C en un solo commit** (mismo archivo); el handoff pedía uno por parte.
- **n16. `gfx_lab`** falló ×3 en el commit A y ×2 en B+C y D: el mismo conjunto inestable de antes.
- **n17. Revisión del papel:** el analista con formato DEBERÍA, después el OK de Omar; recién ahí la tanda de fotos y clips.

## Procesos y subagentes
- Subagentes: 3 Explore (mapas) y 1 general (tests de m03) terminaron; `revisor-handoff` termina con su veredicto.
- Shells en segundo plano: las verificaciones y la corrida de m03 terminaron; la primera corrida de m03 la corté yo (TaskStop) y comprobé que no quedó proceso vivo.
- No se cerró ningún proceso de Omar.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

Revisé en solo lectura. No corrí pytest ni APIs. El `--check` del mapa no lo reejecuté: me apoyo en los logs.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff con el md5 esperado | OK | `md5sum` = 5586254139ed4ddb25ee7504e0d63cfc |
| 2 | Paso 0: 3 líneas de DECISIONES, `TOPE_TANDA` y copia en `antes/` | OK | DECISIONES.md:136-138 (commit 3751124). `TOPE_TANDA.json` = `{"usd": 5.0, "desde": "2026-10-28T11:35:49"}`. `f50/antes/` existe. |
| 3 | Textos del lab tal cual (TEXTO_1, TEXTO_2, TEXTO_3, TEXTO_S4_YEAR, TEXTO_S5) | OK | Comparé con `ast.literal_eval` lab contra producción: los 5 son IGUAL (804, 168, 129, 288 y 122 caracteres). Están en `step_4e:843/851`, `m03_visual:277/279` y `m03_expediente`. |
| 4 | Sistema §C.1 del handoff | OK | `_VEO_MOTION_SYSTEM` en `m03_visual.py:1832` == bloque del handoff (1393 caracteres, igual). |
| 5 | `negative_prompt` §C.2 | OK | `asset_manager.VEO_NEGATIVE_PROMPT` == texto del handoff. `veo_prueba.json` y `PAPEL.json` lo llevan igual. |
| 6 | A: pedido de canon igual al de F48 S5, canon armado, marca md5 | OK | `verificar_a.py` da md5 `46ff0c7b…` igual. La marca `canon_ficha_md5=b02aa6f8…` coincide con `md5(ficha_caso.json)`, en `topics_db` y en `05_visual_canon.json` (7 people_groups). |
| 7 | B: pedido del cap 2 byte a byte y armado contra PROMPTS_F49 | OK | `B_VERIFICACION.md`: md5 `278e1fe2…` y esquema `fa1ebfd1…` iguales. 26 de 28 iguales, y los 2 distintos son carteles (chascada). |
| 8 | Chascadas con test | OK por lectura | Los 2 carteles del antes/después coinciden con la tabla del handoff. `test_module_f50b.py` existe (18 tests). No lo corrí. |
| 9 | C: Opus, `duration`, `negative_prompt` en `_call_veo_once` | OK | `asset_manager` `_veo_duration`. `veo_prueba.json` muestra el payload con ambos campos. |
| 10 | Prueba Veo de 4 s, 1 sola | OK | `veo_prueba.mp4` existe (10 MB). `C_VEO.md`: ok, 4,000 s, 1920×1080. Un solo registro `f50-veo-prueba` por 0,24 en cost_history. |
| 11 | Lo viejo borrado sin usos vivos | OK | Grep sobre `*.py` fuera de `lab/`, `_*` y `diag_`. Fluidificador, `_VEO_VIDEO_PROMPT_STRUCT`, `_SEEDREAM_MOTION_SYSTEM`, `SEEDREAM_SLOTS_USE_PRO`, `wrap_style` y `_f8_finish_item` solo aparecen en comentarios y docstrings (`gemini_helpers:174`, `m03_imagenes_v3:353`, `m03_visual:122`) y en tests que dicen que se borraron. `topic_researcher` ya no llama al 4e (líneas 11 y 596 son comentarios). `test_m03_guarda1_degrade.py` fue borrado. |
| 12 | D: 96 fotos, caps 1 y 7 con `video_prompt`, `negative_prompt` y `duration` | OK | `PAPEL.json`: 96 fotos (5+16+16+14+16+16+13). Años 28 del ancla y 68 del casillero. `video_prompt` de 635 y 583 caracteres, dentro de 120-700. `duration` = 8s. |
| 13 | Costos del reporte contra archivos | OK | `d_m03.log`: total 2,1205 (Opus 1,9789 + Flash 0,1416). `cost_history`: 123bbb64 = 2,120509. Prueba Veo = 0,24. Canon 0,0306 en `01_v3_costos`. Registrado 2,3911, bajo el tope de 5,00. |
| 14 | Cero fotos y cero clips salvo la prueba | OK | No hay PNG ni MP4 nuevos en `f50/` salvo `veo_prueba.mp4`. Los jpg/mp4 nuevos en `output/ba6c3cac…/_fase2b_work/gfx_lab_*` son de `gfx_lab`, de un tema distinto, y no los generó F50. |
| 15 | Stickers y MAPA al día, suites antes/después | OK por logs | Existen `f41/f50_A`, `f50_BC` y `f50_D`. Rápida 55, amplia 944 con 4 fallas. Los commits tocan `MAPA_PROYECTO` y los stickers. `--check` no lo reejecuté. |
| 16 | Commits por parte | PARCIAL | B y C van en un solo commit (dcea932), declarado en el reporte. El handoff pedía uno por parte. |
| 17 | `F50_REPORT` con lo abierto entero y el veredicto íntegro | PARCIAL | "Lo abierto" tiene n1 a n17. El marcador `{{VEREDICTO}}` sigue vacío, como corresponde. |

Observaciones:
- **Gasto sin registrar.** La corrida de m03 que CC cortó a mano a los ~66 s dejó Opus en vuelo sin registrar (reporte n2). El cálculo "como mucho ~4,5" parece correcto contra el tope de 5,00, pero no se puede verificar. La parte registrada es 2,39.
- **Carteles con mayúsculas raras en el papel** (reporte n1). Dos casos con "written Over the entrance in Metal…" y "written On the warning sign… in Bold block stencil". También hay "in typewritten" y "in typewriter". El papel que verá Omar ya los trae así. El arreglo propuesto no se aplicó.
- **Cobertura del canon.** El canon quedó con 7 grupos (S5 de F48 tenía 15) y 3 personajes del pool sin grupo (n3). Es lo que el handoff dejó como informativo, no como corte.
- **Cap Veo sin medir.** La verificación byte a byte es solo del cap 2. El cap con Veo (cap 7, 13 fotos) no se midió contra el lab (n8).
- **Costo de Veo.** `track_fal` cobra 0,24 fijo y el precio real de 4 s no está medido (n10).
- **Fallas previas.** El reporte atribuye las 4 fallas de la amplia a conjuntos "previos" (`gfx_lab` ×2 y `m03_merge_timing` ×2). `m03_merge_timing` toca la ruta de Veo (`test_c_veo_path_y_veo_anchor_intacto`). No pude comprobar en solo lectura que ya fallaban antes de F50.
- **Claves nuevas en `03_visual.json`.** `anio`, `anio_fuente`, `_f8_texto_fuera` y `image_f8`. No se verificó que m06 las ignore (n12).

Fuera de alcance:
- Ninguno atribuible a F50. El árbol sin commitear tiene `lab/ESTADO_SESION.md` y `F50_REPORT.md`, previstos para el commit de cierre.
- `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log` figuraban modificados antes de F50. `TOPE_TANDA.json` es el cambio pedido por Omar.

Riesgos que el contrato no cubre:
- Si el papel pasa al visto bueno con los carteles en mayúscula, esos prompts salen así en la tanda de fotos.
- Veo 3.1 se apaga el 2026-11-17: la tanda de clips tiene fecha límite.
- Con una sola llamada de canon y 7 grupos, las fotos con gente sin grupo (F49 m7) pueden reaparecer en la tanda real.

### Adenda de CC (después del veredicto)
- **Fallas previas:** las mismas 4 fallas (`m03_merge_timing::test_c_veo_path_y_veo_anchor_intacto`, `m03_merge_timing::test_c_guarda_de_minimo`, `gfx_lab::test_cues_sin_escribir_el_proyecto`, `gfx_lab::test_preview_usa_las_plantillas_reales`) ya están en `lab/hyperframes/f49/verif_p1/suite_amplia.log`, del commit `e76d8ed` de F49: son anteriores a F50.
- **#16 (B y C en un commit):** los dos tocan `m03_visual.py` y `test_module_f50b.py`. Separarlos dejaba un commit con un test que fallaba. Queda declarado (n15).
- **Carteles (n1):** no los arreglé. Toca una regla nueva del armado y el papel ya está generado, así que lo dejo para la revisión DEBERÍA del analista.
