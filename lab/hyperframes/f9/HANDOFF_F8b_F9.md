# HANDOFF F8b (arreglos de research e imágenes) + F9 (Voz v4) — tanda autónoma

**Fecha:** 2026-10-22 10:10 · **Analista:** chat proyecto · **Ejecuta:** CC, sesión nueva, **modo autónomo** (Omar fuera ~8 h) · **Gate:** Omar al volver
**Rama:** `f9-voz-v4` desde `f8-imagenes-v3` (cd3f2e5). Sin merge a `main`.
**Leer antes:** este archivo; `lab/hyperframes/f8/F8_REPORT.md` §5 (dudas) y `semillas/SEMILLAS.md`; `claude/DECISION_F9_voz_2026-10-22.md` (está en el proyecto; su contenido operativo está en §3 de abajo).
**Reglas del modo autónomo:** las mismas de F8: no preguntar, decidir y anotar en `lab/hyperframes/f9/DECISIONES_F9.md`, commit wip antes de compactar, `ESTADO_SESION.md`, sin render completo, sin QA Studio, sin merge; si el contexto pasa de ~80 %, abrir sesión nueva con el prompt de §6.

---

## 0. Respuestas del analista a las dudas de F8 §5
1. `max_beats` → **14** (12 mínimos; 2 en gancho o cierre opcionales).
2. Estilo "grano y subexpuesto": **no** más texto; **grade de post** (§2.6).
3. Perder `seed` por sujeto: **aceptado**.
4. Semillas: **sí**, arreglar research (§1) y re-correr S2 y S3. Omar elige al volver.
5. Reglas C–E: **solo v3**.

---

## 1. F8b-R — Research v3: tres bugs y un hallazgo
1. **Antigüedad por ítem, no por documento (bug que rompe todo tema anterior a 2005).** `doc_contamination` descarta documentos con año > evento + 20. Cambiar a: el documento entra si nombra el lugar/evento (ya existe el chequeo); la antigüedad se mide **por ítem** (`fecha` del dato/evento/cita contra el año del evento, ±20, con excepción para `tipo` consecuencia/juicio/aniversario). Test con fixture 1963 → documentos de 2014–2023 entran.
2. **PDF enlazado equivocado (S2 F05):** antes de aceptar un PDF enlazado desde una portada corta, exigir que el PDF nombre el evento/lugar en sus primeros 5 k caracteres; si no, descartar y anotar. Test.
3. **R3 sin reintento ante caída de Pro (S2 F08):** 2 reintentos con backoff; si falla, documento marcado `extraccion_fallida` y el pool sigue. Test.
4. **R1 sin grounding (3 de 4 focos en S2 y S3):** ya hay reintento; subir a 3 intentos con temperatura 0.7 y, si sigue sin grounding, **una query Flash+search alternativa** por foco con las palabras clave del seed en el idioma local. Registrar cuántos focos salieron con grounding.
5. **Re-correr S2 Cromañón y S3 Vajont** (research v3 + compuerta, sin escaleta). Actualizar `semillas/SEMILLAS.md` con el color nuevo y las fichas. Presupuesto ≈ $2.
6. S1 Ycuá Bolaños: no tocar (verde). Anotar en su ficha el riesgo de menores para m03 §2.3/E.

## 2. F8b-I — Imágenes: reglas de encuadre que salieron del humo
Ver `lab/hyperframes/f8/humo/hoja_contactos.jpg`: 8/12 buenas (#1, #2, #6, #12 excelentes), #7–#8 "videojuego", #3 y #10 texto mal.
1. **Armas y disparos:** nunca fogonazo, nunca arma en primera persona, nunca encuadre desde el tirador. Armas solo en reposo, a distancia, de espaldas. La cámara está **con las víctimas o con el testigo** (para Orleans beat 5: Brady Richard en la terraza del CCC mirando hacia el HOD; presos agachándose en el agua; siluetas quietas en un techo lejano). Validador determinista sobre el prompt (lista: muzzle flash, firing, discharging, barrel, first-person, POV, aiming at camera) + instrucción a Flash.
2. **Pico:** escala humana; nunca objeto ni arma en detalle. (Se suma a "la más cerrada del cap" sin contradecirla: cerrada sobre un humano o un rastro humano.)
3. **Texto en imagen:** por defecto **sin texto legible** ("no readable text, no signage, no labels"). Si el beat exige texto (un letrero, una lista), va en el **idioma del lugar del evento** (inglés para Orleans), ≤ 3 palabras, y se marca `texto_en_imagen: true` para QA. Nunca español en documentos de otro país.
4. **Densidad y escala desde el pool:** si el dato dice cientos/miles, el prompt dice "hundreds of…, filling the frame"; nunca 5–7 figuras para "una fila interminable".
5. **Clichés:** ampliar la lista con sinónimos (hollowed eyes, cracked lips, facial muscles tensed, eyes squeezed shut, grimace, veins).
6. **Grade de post (lo que arregla "limpias y saturadas" para cualquier motor):** paso FFmpeg sobre cada imagen generada antes de DepthFlow/Ken Burns: desaturación 15–25 %, negros levantados (lift), leve viñeta, grano de película fino (noise fijo por imagen), temperatura ligeramente fría. Parámetros en el perfil del canal (`gfx_profiles/misterio.json` o `art_profiles`), aplicados por `asset_manager` al guardar (`_graded.png`, original conservado). Test: histograma antes/después (saturación media baja, negros no recortados).
7. **Re-humo:** regenerar solo #3, #7, #8, #9, #10 con las reglas nuevas + aplicar el grade a las 12 → `humo/hoja_contactos_f8b.jpg` y `compara_imagenes_f8.html` con tercera columna "F8b".

## 3. F9 — Voz: ElevenLabs v4 + MS Narrador v1
Decisión de Omar (prueba en `lab/hyperframes/f9/audio/`): **`eleven_v4` + voz propia `N9Z5MLTIaHFLflaLtbDi`** ("MS Narrador v1", Voice Design). v2 descartado ("robot"); Gemini TTS descartado (bloqueo de seguridad).
1. `audio_profiles.MISTERIO_ABISAL.voice_id` → `N9Z5MLTIaHFLflaLtbDi`; `elevenlabs_model` → `eleven_v4` (en `video_length.py`/perfil, no solo en `config.py` que está fuera de git); `language_code="es"`. Fallback a v2+Bill por flag `TTS_V2=1`.
2. v4 no acepta `style`, `speed` ni SSML: `VOICE_SETTINGS_BY_INTENT` pasa a `stability` + `similarity_boost` solamente. Calibración inicial: hook 0.45 · setup 0.65 · rising 0.55 · shock 0.45 · consequences 0.6 · resolution 0.65 · outro 0.6; similarity 0.8.
3. **Etiquetas desde el guion** (m01c editor, regla determinista + soft): `[long pause]` después de cada cita y al cerrar cap; `[short pause]` antes del pico y donde hay "…"; `[quietly]`/`[whispers]` solo en la frase de golpe, máx. 2 por cap, nunca en caps `setup`; `[slowly]` al abrir gancho y pico y al inicio de cada párrafo de desarrollo si la medición de palabras/segundo de v4 supera 2.4. Salen en un campo nuevo `narration_tts` por cap. **`narration` queda limpia**: subtítulos, candado literal, m03, m05 y forced alignment siguen leyendo `narration`.
4. `audio_manager`: manda `narration_tts` a Eleven; `text_for_tts` para el forced alignment = `narration` (sin etiquetas). Verificar que el alineado no tenga residuos ni desfase > 150 ms por las pausas (medir en los 2 caps de prueba).
5. **Monotonía (riesgo propio de esta voz):** medir palabras/segundo y rango de pausas por cap; caps de desarrollo sin susurros; gancho y pico con las etiquetas fuertes.
6. **Prueba de cierre (sin render de video):** caps 2 y 4 de Orleans F7c-3 con `narration_tts`, mezclados con la música del perfil → `lab/hyperframes/f9/audio/cap2_cap4_v4_msnarrador.mp3`, más el mismo par con Bill v4 para comparar. Costo ≈ 6 k caracteres ≈ $0.5.
7. Costo por video ≈ $4 (v4 cobra doble). Anotar consumo del plan.

## 4. FRENOS
- Research: solo §1; no tocar `evidence.py`, escaleta, guionista.
- m03/asset_manager: solo §2; no tocar plan de anclas, fluidificador, candado, foto_madre_ref, hard_fact_ids. DepthFlow recibe la imagen `_graded`; si algo del flujo lee el original por nombre, mantener ambos.
- Audio: solo §3; `m02_5`, `tts_normalizer` y forced alignment no cambian de contrato. Guiones v2 siguen en v2+Bill byte-idénticos.
- Sin render completo, sin QA Studio, sin merge, sin validador de visión.

## 5. Orden y entregas
1. (0:00–0:20) rama, leer, commit wip.
2. (0:20–2:30) §1 research + re-correr S2 y S3 (en paralelo mientras sigue). `SEMILLAS.md` actualizado.
3. (2:30–5:00) §2 imágenes + grade + re-humo + HTML.
4. (5:00–7:30) §3 voz + prueba de cierre.
5. (7:30–8:00) `F8b_F9_REPORT.md` (hecho / no hecho / costos / decisiones / dudas), revisor, commit final, `ESTADO_SESION.md`.
Tests por regla en `test_module_f8b.py` y `test_module_f9.py`. Presupuesto de la tanda < $5.

## 6. Prompt de continuación (sesión nueva si se satura)
```
Continuación F8b+F9 (modo autónomo, Omar fuera). Leé lab/hyperframes/f9/HANDOFF_F8b_F9.md completo y lab/ESTADO_SESION.md. Rama f9-voz-v4. Retomá desde el último punto del §5 pendiente, mismas reglas: no preguntar, decidir y anotar en DECISIONES_F9.md, commit wip antes de compactar, sin render completo, sin QA Studio, sin merge. Si volvés a pasar de ~80 % de contexto, repetí este procedimiento. Al terminar: F8b_F9_REPORT.md, revisor, commit final.
```
