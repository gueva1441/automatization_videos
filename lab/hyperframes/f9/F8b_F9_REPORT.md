# F8b + F9 — Research, imágenes y voz v4 — REPORTE (modo autónomo)

**Rama:** `f9-voz-v4` (desde `cd3f2e5`, punta de `f8-imagenes-v3`). Sin merge, sin render de video, sin QA Studio.
**Pedido:** `lab/hyperframes/f9/HANDOFF_F8b_F9.md` §5. **Decisiones tomadas solo:** `DECISIONES_F9.md` (D1–D21).
**Para mirar/escuchar primero:** `lab/hyperframes/f8/compara_imagenes_f8.html` (tres columnas), `lab/hyperframes/f8/humo/hoja_contactos_f8b.jpg`, `lab/hyperframes/f9/audio/cap2_cap4_v4_msnarrador.mp3` contra `cap2_cap4_v4_bill.mp3` (en disco; los mp3 están en `.gitignore`), `lab/hyperframes/f8/semillas/SEMILLAS.md`.

## 1. Qué se hizo

### §0 — Respuestas del analista
`max_beats` 14 en `video_length` (D2). Las demás respuestas se aplican abajo o no piden código.

### §1 — Research v3 y re-corrida de S2 y S3
- **Antigüedad por ítem** (`contamination`/`doc_contamination`): un documento entra si nombra el evento, sea del año que sea; cada ítem se mide por su fecha ±20 años, con excepciones (después: juicio, sentencia, aniversario, comisión…; antes: construcción, fundación, concesión…) (D3).
- **PDF enlazado** que no nombra el evento en sus primeros 5 k caracteres: descartado y anotado (D4).
- **R3**: 2 reintentos con backoff; si fallan, `extraccion_fallida` y el pool sigue (D5).
- **R1**: 3 reintentos y Flash con búsqueda como alternativa, con conteo de focos con grounding (D6).
- Tests en `test_module_f8b.py` (fixture de 1963 con documentos de 2014–2023, PDF enlazado con y sin el evento, caída de Pro, Flash alternativo).

| | antes (F8) | ahora (F8b) | costo de la re-corrida |
|---|---|---|---|
| S2 Cromañón | 🔴 rojo · 67 datos · 30 citas · 3 elegibles · 22 eventos | 🟡 **amarillo** · 129 · 39 · 5 · 38 | US$ 0.87 |
| S3 Vajont | 🔴 rojo · 0 · 0 · 0 · 0 | 🔴 rojo · 121 · 9 · **0** · 30 | US$ 0.82 |
| S1 Ycuá Bolaños | 🟢 verde (sin tocar) | 🟢 verde; ficha con el riesgo de menores para m03 | — |

- **Vajont** ya entra al pool (documentos de 1971 a 2024, en italiano e inglés; solo 9 ítems descartados por fecha). Sigue en rojo por **0 humanos elegibles** (la compuerta pide 2 para verde y 1 para amarillo): los sobrevivientes aparecen con una cita cada uno, y para ser elegible una persona necesita 3 citas o 3 datos propios. Las fuentes que trajo la búsqueda son institucionales; faltan historia oral o libros de testimonios.
- **Cromañón** queda en amarillo (≈ 10 min). Le faltan 21 datos para el verde.
- **R1:** en las dos semillas, 3 de 4 focos salieron con grounding de Pro. El cuarto no salió ni con Flash.
- No elegí ninguna semilla. Detalle en `SEMILLAS.md` (sección F8b arriba, lo de F8 abajo).

### §2 — Imágenes: reglas nuevas, grade de post y re-humo
- **Armas** (D8):
  - validador determinista y regla para el director;
  - un beat cuya imagen sensorial es un disparo se cuenta desde las víctimas o el testigo;
  - un tirador o un arma como sujeto hace rehacer la imagen.
- **Pico a escala humana** (D9).
- **Texto** (D10): sin texto legible por defecto. Si el beat lo exige, va en el idioma del lugar, con ≤ 3 palabras y la marca `texto_en_imagen`.
- **Escala desde el pool** (D11) y **clichés ampliados** (D12).
- **Grade de post** (`script_engine/image_grade.py`, D13–D14):
  - FFmpeg en `asset_manager` al guardar: escribe `_graded.png`, conserva el original y el manifest apunta al graduado;
  - corre solo en guiones v3 o con `IMAGE_GRADE=1`;
  - en las 12 del humo, la saturación baja 8–27 % en las imágenes de color y el negro puro pasa de hasta 17 % a 0 %;
  - la imagen casi gris (#12) no baja.
- **Re-humo** (D15):
  - #3, #7, #8, #9 y #10 rehechas y las 12 graduadas → `hoja_contactos_f8b.jpg` y la tercera columna en `compara_imagenes_f8.html`;
  - a ojo, para que Omar confirme: el #8 (pico) ahora es un preso de espaldas que mira por la ventana rota hacia el techo lejano (escala humana, cámara con la víctima);
  - el #10 dice «UNKNOWN» y el #3 «CATEGORY 5» (en inglés, ≤ 3 palabras);
  - el #9 pasa de 7 a ~25 figuras en el paso elevado (todavía no «cientos»);
  - **el #7 sigue flojo**: después de tres vueltas son siluetas en un techo lejano, vistas desde la celda y sin fogonazo, pero todavía en postura de tiro.
- Costo de imágenes de esta tanda: US$ 0.245 (7 imágenes, contando las dos vueltas extra del #7).

### §3 — Voz v4 + MS Narrador
- **Perfil** (D16):
  - `MISTERIO_ABISAL` suma `voice_id_v4` (N9Z5MLTIaHFLflaLtbDi), `elevenlabs_model_v4` (eleven_v4), `language_code_v4` es, `voice_settings_v4` y `voice_lufs_v4`;
  - `voice_id` sigue en Bill, para que v2 no cambie.
- **Cuándo va v4:** cuando el cap trae `narration_tts`. `TTS_V2=1` vuelve a v2 + Bill.
- **Settings:** `VOICE_SETTINGS_BY_INTENT_V4` solo con stability (hook 0.45 · setup 0.65 · rising 0.55 · shock 0.45 · consequences 0.6 · resolution 0.65 · outro 0.6) y similarity 0.8 del perfil.
- **Etiquetas desde el guion** (`script_engine/tts_tags.py` vía `m01c_editor.narration_tts`, D18):
  - `[long pause]` después de cada cita y al cerrar el cap;
  - `[short pause]` antes del pico y en «…»;
  - `[quietly]` / `[whispers]` solo en la frase de golpe (máx. 2 por cap, nunca en setup);
  - `[slowly]` en gancho y pico.
- **Texto limpio:** `narration` no cambia. A Eleven va el texto normalizado con las etiquetas trasladadas por oración; el forced alignment, el hash y los subtítulos siguen con el texto limpio.
- **Sonoridad** (hallazgo, D20): MS Narrador salía 8 dB más fuerte que Bill (−15.8 contra −23.9 LUFS) y fase2b no normaliza. La voz v4 se lleva a −24 LUFS para que la música por track, calibrada con Bill, siga valiendo.
- **Prueba de cierre** (caps 2 y 4 de Orleans f7r3, con la música del perfil):

| | MS Narrador v4 | Bill v4 |
|---|---|---|
| palabras/s (con pausas) cap 2 · cap 4 | 2.23 · 2.28 | 2.32 · 2.44 |
| pausas ≥ 0.6 s cap 2 · cap 4 | 17 · 20 | 13 · 6 |
| pausa mediana larga | 0.92 · 0.87 s | 0.66 · 0.64 s |
| residuos de etiqueta en el alineado | 0 | 0 |
| desfase alineado − Whisper: mediana · p95 | 80 · 300 ms | 80–100 · 260 ms |
| sonoridad de la mezcla | −25.3 LUFS | −25.0 LUFS |

- **[slowly] en desarrollo:** no hace falta, MS Narrador queda debajo de 2.4 palabras/s (D19).
- **Monotonía:** MS Narrador hace más pausas largas que Bill (17–20 contra 6–13 por cap). En los caps de desarrollo no hay susurros, salvo uno `[quietly]` en el cap 4 (shock, intensidad 4).
- **Desfase:** la mediana queda debajo de 150 ms. El p95 (300 ms) la pasa, igual que Bill y que v2 en F5e (240–500 ms): es el sesgo de Whisper medido en F5e, no las pausas. Ninguna palabra quedó con residuos.
- **Costo de voz:** US$ 0.29 (2 corridas × 2 voces × 2,436 caracteres). v4 tiene multiplicador 1.0 según la API (D17). El consumo del plan no se pudo leer (la clave no tiene permiso, 401).

## 2. Qué no se hizo / quedó a medias
- El #7 de Orleans (beat del disparo) sigue mostrando tiradores en postura de tiro, aunque lejos y sin fogonazo.
- El #9 no llega a «cientos».
- Vajont sigue en rojo (faltan testimonios, no es un bug). Cromañón queda en amarillo, no en verde.
- La regla blanda de las etiquetas al editor (prompt) no se agregó: la regla es solo determinista (D18).
- El grade no se probó dentro de un render de fase2b (no hubo render). Lo que fase2b indexe por nombre de foto va a ver `_graded` (D14).
- Lo que Omar tiene que hacer a oído: escuchar los dos mp3 (no hay validación automática de la actuación).

## 3. Costos medidos de la tanda
| tramo | US$ |
|---|---|
| Re-corrida de S2 y S3 (research v3 + compuerta) | 1.69 |
| Imágenes F8b (7 generaciones) | 0.245 |
| Voz (2 corridas × 2 voces) | 0.29 |
| Gemini de los prompts de imagen (m03) | no medido (estimado < 0.3) |
| **Total medido** | **2.23** (presupuesto < 5) |

## 4. Tests
- `test_module_f8b.py` (17, research e imágenes) y `test_module_f9.py` (10, etiquetas y audio con Eleven simulado: payload v2 idéntico, v4 con idioma, alineado limpio, TTS_V2, re-generación por cambio de etiquetas, normalización solo en v4).
- Suites de guion, gfx, m03, m09 y audio: **563 verdes + las 5 fallas previas conocidas** (3 `01b_pauses`, 2 `m03_merge_timing`).
- Scripts de m03 (leakage, place, doctrina compartida, telemetría, supplementals, matcher): PASS.

## 5. Dudas para Omar
1. ¿Te gusta MS Narrador frente a Bill en v4 (los dos mp3, misma música y mismas etiquetas)?
2. El #7: ¿alcanza con siluetas lejanas o preferís sacar el beat del disparo de la imagen (un plano de presos agachándose en el agua)?
3. Vajont: ¿bajamos el umbral de elegibles para temas históricos (1 testigo con ≥ 2 citas) o buscamos historia oral como pista de R1?
4. Grade: ¿la fuerza está bien (`saturation` 0.70, `grain` 6) o lo querés más marcado?

## 6. Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí los tests, leí `git diff cd3f2e5 HEAD` y crucé las cifras del reporte contra los artefactos. No ejecuté nada que llame APIs pagas. Las observaciones son menores o ya están declaradas, y no encontré un incumplimiento de FRENOS.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 0.1 | `max_beats` = 14 | OK | `script_engine/video_length.py` (`"max_beats": 14`); `test_module_f8.py` ajustado. |
| 0.2–0.5 | Grade de post en vez de más texto; sin `seed` por sujeto; arreglar research y re-correr; reglas C–E solo v3 | OK | Aplicados en §1 y §2; el grade corre solo en guiones v3 o con `IMAGE_GRADE=1` (`asset_manager._grade_enabled`). |
| 1.1 | Antigüedad por ítem | OK | D3; fixture de 1963 en `test_module_f8b.py`; aserción de `test_module_f7.py` ajustada y declarada. |
| 1.2 | PDF enlazado: debe nombrar el evento en los primeros 5 k caracteres | OK | D4 y test; en S3 descartó un PDF. |
| 1.3 | R3 con 2 reintentos y backoff, `extraccion_fallida` | OK | D5 y test. |
| 1.4 | R1 con 3 intentos, Flash alternativo y conteo de grounding | OK | D6, `_focos_grounding` y test. Quedó 3 de 4 focos con grounding en S2 y S3. |
| 1.5 | Re-correr S2 y S3 y actualizar `SEMILLAS.md` | OK | S2 amarillo (129 · 39 · 5 · 38, $0.872) y S3 rojo (121 · 9 · 0 · 30, $0.820) en `POOL_GATE.md` y `costo.json`; coinciden con el reporte. $1.69 en total, dentro del ~$2. `SEMILLAS.md` tiene 39 líneas nuevas. |
| 1.6 | S1 sin tocar y ficha con el riesgo de menores | OK | Reporte §1 y diff de `SEMILLAS.md`. |
| 2.1 | Armas: validador determinista y regla para Flash | OK | `WEAPONS` y `weapon_subject` en `m03_imagenes_v3.py`; D8 (`F8_NOTE_ARMA`) y regla 5 del SI v3. |
| 2.2 | Pico a escala humana | OK | `human_scale` y `F8_NOTE_CERRADA` en `m03_visual.py`. |
| 2.3 | Texto en el idioma del lugar, ≤ 3 palabras, `texto_en_imagen` | OK | `fix_text_slot`, `place_language` y `NO_TEXT` (D10). |
| 2.4 | Densidad y escala desde el pool | PARCIAL | Implementado (`fix_scale`, `beat_scale`). El #9 pasa de 7 a ~25 figuras y no llega a "cientos"; el reporte lo declara. |
| 2.5 | Clichés ampliados | OK | D12; lista ampliada y ejemplo sacado del SI v3. |
| 2.6 | Grade de post en `asset_manager`, original conservado, histograma antes/después | OK | `image_grade.py` (nuevo); `asset_manager._apply_grade` escribe `_graded.png` y guarda `path_original`; `test_grade_baja_saturacion_y_no_recorta_negros` pasa. Los parámetros están en DEFAULTS del módulo; `misterio.json` no se tocó (D13) y la clave de perfil `image_grade` es opcional. El handoff decía "parámetros en el perfil". |
| 2.7 | Re-humo de #3, #7, #8, #9, #10, hoja `hoja_contactos_f8b.jpg` y HTML con tercera columna | PARCIAL | Los archivos existen (`f8b_01..12.jpg`, hoja, HTML). El #7 sigue con siluetas en postura de tiro tras 3 vueltas y el reporte lo declara. Costo $0.245 = `_costo_imagenes_usd` 0.455 → 0.700 en `humo.json`. |
| 3.1 | Perfil con MS Narrador, `eleven_v4`, `language_code=es`, flag `TTS_V2=1` | PARCIAL | Existe como claves `_v4` (`audio_profiles.py`) y `TTS_V2` funciona (`audio_manager.tts_v4_enabled`). Pero `voice_id` sigue en Bill y `elevenlabs_model` no cambió. Es una desviación del texto del handoff, declarada en D16 para mantener los guiones v2 byte-idénticos. |
| 3.2 | Solo stability + similarity; calibración por intent | OK | `VOICE_SETTINGS_BY_INTENT_V4` con 0.45/0.65/0.55/0.45/0.6/0.65/0.6; similarity 0.8. |
| 3.3 | Etiquetas desde el guion en `narration_tts`; `narration` limpia | PARCIAL | `tts_tags.py` y `m01c_editor.narration_tts` implementan lo determinista (pausas, `[quietly]`/`[whispers]` máx. 2 y nunca en setup, `[slowly]`). El handoff decía "determinista + soft": la parte soft (prompt del editor) no se hizo, declarado en D18. |
| 3.4 | `audio_manager` manda `narration_tts`; alineado con texto limpio; sin residuos ni desfase > 150 ms | PARCIAL | Alineado con texto limpio y 0 residuos (`voz_f9.json`). Mediana 80 ms (Bill 80–100 ms). El p95 es 300 ms, mayor que 150 ms, y el reporte lo atribuye al sesgo de Whisper. Coincide con `sync_f9.json`. |
| 3.5 | Medir palabras/s y pausas; sin susurros en desarrollo | OK | `voz_f9.json`: 2.23 / 2.28 palabras/s, 17 / 20 pausas largas, un solo `[quietly]` en el cap 4. D19 explica por qué no hace falta `[slowly]` en desarrollo. |
| 3.6 | Prueba de cierre (caps 2 y 4) con MS Narrador y con Bill v4 | NO VERIFICABLE | Los mp3 están en `.gitignore` y no los abrí. Los números de `voz_f9.json` y `sync_f9.json` coinciden con la tabla del reporte. |
| 3.7 | Costo de voz anotado | OK (con matiz) | $0.29 = 4 × 0.0731. El consumo del plan no se pudo leer (401). El reporte contradice el "v4 cobra doble" del handoff, citando la API (D17). |
| F | FRENOS | OK | El diff no toca `evidence.py`, escaleta, guionista, `m02_5`, `tts_normalizer`, forced alignment, `foto_madre_ref`, `hard_fact_ids`, candado ni fluidificador. Hay cambios en m03 y asset_manager solo dentro de §2. El payload v2 queda idéntico (test de `test_module_f9.py`). No hay render, QA Studio ni merge. |
| T | Tests | OK | Pedidos: 93 passed. Suite amplia: 563 passed y 5 failed, exactamente las 5 previas (3 de `01b_pauses` y 2 de `m03_merge_timing`). |
| G | No commiteados | OK | `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` y `gfx_profiles/misterio.json` siguen modificados y sin commitear. `git log cd3f2e5..HEAD` sobre esas rutas y sobre `config.py` sale vacío. `lab/hyperframes/f7/topics_db_pre_f7b.json` y `config.py` no aparecen en el diff. |

Observaciones:
1. `lab/hyperframes/f7/f7c_orleans.py` se tocó (2 líneas, para llamar a `narration_tts`). No está en la lista de alcance ni en DECISIONES. Es un runner de lab y el cambio es coherente con §3.3, pero no está declarado.
2. El reporte (§1) dice que Vajont "pide 3" elegibles. El POOL_GATE muestra umbral verde = 2 y mitad = 1. La cifra del reporte está equivocada, aunque el color y los resultados (0 elegibles) son correctos.
3. 3.1 y 3.3 se cumplen con desviación declarada (D16 y D18): `voice_id` y `elevenlabs_model` del perfil no cambian, y la regla blanda del editor no se hizo. Omar tiene que aceptar ambas.
4. Pendientes declarados que dependen de Omar: #7 y #9 de la hoja, S3 en rojo, S2 en amarillo y escuchar los mp3. Los costos "Gemini de prompts: no medido (<0.3)" quedan como estimación, no medición.
5. El reporte §6 sigue con "(pendiente)" para este veredicto. Hay que pegarlo íntegro ahí.

Fuera de alcance: solo `lab/hyperframes/f7/f7c_orleans.py` (observación 1). Las otras modificaciones de tests (`test_module_f7.py`, `test_module_f7d.py`, `test_module_f8.py`) están declaradas en DECISIONES.

Riesgos que el contrato no cubre: (a) `_graded` cambia el nombre de la foto que ve fase2b (`flow_specs`, marcas de QA) y no se probó en un render. (b) Quedó sin validar la actuación de la voz v4 (monotonía, p95 de desfase de 300 ms). (c) El consumo real del plan de ElevenLabs sigue desconocido y el handoff suponía que v4 cobra el doble.

Respuesta del autor a las observaciones (después del veredicto): la 1 quedó declarada como D22 en DECISIONES_F9; la 2 se corrigió en §1 del reporte (la compuerta pide 2 elegibles para verde y 1 para amarillo; las «3» eran las citas o datos que necesita una persona para ser elegible); la 5 se resuelve con este commit final. La 3, la 4 y los riesgos quedan para Omar (§5).
