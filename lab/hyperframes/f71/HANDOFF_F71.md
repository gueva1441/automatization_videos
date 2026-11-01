# HANDOFF F71 — las fotos siguen a la voz (anclas) + chascada: falso «nsfw»

## Por qué (Omar, 2026-11-01 16:19, «si dale»)
`compute_anchor_starts` devuelve None en ch02, 03, 05, 06, 07 de Wittenoom → fase2b reparte las fotos parejo, sin seguir la voz. Frena el render.

## Causa raíz (simulada por el analista con los archivos reales)
Dos traductores distintos:
- La voz lee `01b_narration_normalized.json` (gate LLM m02_5: spans aplicados + `normalize_pool_forms`), vía `audio_manager._resolve_text_for_tts`.
- La aguja de `anchor_timing._needle_normalized` usa `tts_normalizer.normalize_for_tts` (abreviaturas, unidades, siglas del custom_dict). No convierte años y deletrea siglas que la voz no deletreó.

| Cap | Ancla que falla | Aguja vieja | Audio |
|---|---|---|---|
| ch02 #6 | «y CSR, la compañía…» | `y ce ese` | `y csr la` |
| ch03 #5 | «En 1944, el inspector…» | `en 1944 el` | `en mil novecientos…` |
| ch05 #5 | «En 1978 el gobierno…» | `en 1978 el` | `en mil novecientos…` |
| ch06 #14 | «En 2016, un documento…» | `en 2016 un` | `en dos mil dieciséis…` |
| ch07 #1 | «En 2023, Marcos…» | `en 2023 marcos` | `en dos mil veintitrés…` |

## Arreglo (simulado: 7/7 caps, 97/97 anclas por trigrama)
La aguja sale del MISMO texto que leyó la voz, con la misma decisión que `_resolve_text_for_tts`:
1. Si el cap tiene entrada en `01b_narration_normalized.json`: ubicar el ancla en `narration_original` (find desde el cursor, en orden), re-aplicar los `spans_applied` con `decision=="applied"` igual que `_apply_spans_to_narration` (más largo primero, primera aparición, `str.find`), corriendo el offset del ancla (si el offset cae dentro de un span → inicio del reemplazo); aguja = primeros 3 tokens de `normalize_pool_forms(texto_reemplazado[offset:offset+200])`.
   - Primera aparición importa: «Maitland»→«Méitland» se aplicó solo a la 1.ª; aplicar el span sobre el ancla suelta falla en ch07 #4 (simulado).
2. Si el ancla no está literal en `narration_original` (narración editada después de m03; hoy ch06 #8 y ch07 #11): aplicar los mismos spans al texto del ancla + `normalize_pool_forms`.
3. Si el cap no tiene normalizado (SHORT o LONG sin gate): `normalize_for_tts` como hoy (es lo que leyó la voz en ese caso).
El resto del matcher (escalera 3→2→1, cursor, crecientes) no cambia.

Simulación: `lab/hyperframes/f71/sim_analista_replay.py` (+ `sim_analista_spans.py`, la variante descartada). Resultado:
```
ch01 OK 8 · ch02 OK 15 · ch03 OK 16 · ch04 OK 14 · ch05 OK 16 · ch06 OK 16 (1 por paso 2) · ch07 OK 12 (1 por paso 2)
```

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Aguja 3 tokens, escalera 3→2→1(≥4) | ya existe en `anchor_timing.py` | proyecto (135e) |
| Ventana 200 caracteres para la aguja | derivado: 3 tokens caben de sobra; solo acota `normalize_pool_forms` | analista |
| `no_media_generated` como rechazo | tipo de error real de fal (`lab/_nb_tol6/REPORTE.md`, caso nb2_P3); F68 revisor obs. 6 | derivado |

## Módulos
- `anchor_timing.py`: hoy la aguja usa `normalize_for_tts` → recibe el normalizado del cap (`narr_norm=`, entrada de `01b_narration_normalized.json` o None) y arma la aguja como arriba. Helper `cargar_normalizado(topic_id) -> {cap_n: entrada}` ({} si no existe).
- Llamadores (una línea cada uno, pasan `narr_norm`): `fase2b.py:796`, `qa_studio_server.py:325/399/465`, `script_engine/gfx_layer.py:143`.
- `asset_manager.py` (chascada): `_is_content_rejection` busca palabras en TODO el cuerpo, que repite el input (fotos en base64 → «nsfw» por azar; `"safety_tolerance":6` → «safety»). Después: si el cuerpo es JSON, quitar recursivamente las claves `input` y todo string que empiece con `data:` antes de buscar; si no es JSON, quitar `data:[^"\s]+` y corridas base64 de ≥200 caracteres. Agregar `no_media_generated` a `CONTENT_REJECTION_KEYWORDS` (sin el eco del input, hoy solo entra por «safety»). Guardar el cuerpo completo de cada error de fal en `output/<topic>/assets/_errores_fal/<ts>_<nombre>.json` (hoy se trunca a 300/600 y no se puede diagnosticar).
- No se toca: prompts, esquemas, m02_5, audio_manager, la voz.

## Etapas
A. Anclas: código + tests (los 5 casos de la tabla como fixtures reales, «Maitland» primera aparición, ancla no literal, cap sin normalizado = comportamiento viejo). Salida: tabla por cap de Wittenoom: anclas, OK/None, por trigrama/fallback, y por cada ancla de ch02/03/05/06/07: start (s) + las 3 palabras del audio en ese start. Además `/cap/N` de QA con `sync_approx` False en los 7 (o por qué no). Correr también contra Orleans `ba6c3cac-…` y decir si cambia algo (no debe romper lo que ya emparejaba).
B. Chascada nsfw: código + tests con cuerpos sintéticos: (1) input con base64 que contiene «nsfw» + `invalid_request` → NO rechazo; (2) `content_policy_violation` → rechazo; (3) `no_media_generated` → rechazo; (4) solo `safety_tolerance` en el input → NO rechazo. Decir qué camino toma hoy un error de clip que NO es rechazo (¿reintenta?, ¿va a Kling?, ¿falla?) sin cambiarlo.

## Reglas fijas
Cero llamadas pagas, cero prompts; no correr fase2b, run_pipeline ni la voz. Lo viejo se borra: si `_needle_normalized` queda sin uso fuera del paso 3, se borra (y el `diag_235_matcher_ba6c.py` que lo importa se actualiza o se borra, decir cuál). Suite amplia (`lab/hyperframes/f41/verificar.sh`) verde salvo las previas. Revisor-handoff íntegro. Una línea en ESTADO_SESION y en DECISIONES (Omar 16:19). PARADA: `lab/hyperframes/f71/F71_REPORT.md`.
