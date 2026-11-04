# HANDOFF F76 — master −14 LUFS con pico real controlado (cierra C2 de F75)
Rama `f11-guion-v4`, base `ff368d4` (F75). Aprobado por Omar 2026-11-04 15:32 («aprobado hace lo del audio»).

## Por qué
Wittenoom salió a −24 LUFS: en YouTube se oye ~10 dB más bajo que el resto y YouTube no lo sube. F75 C1 probó la receta del analista (limitador a −2 dBFS de muestra + loudnorm lineal) y dejó el pico real en −0,9 dBTP, sobre el techo de −1,5. **La falla fue del analista:** un limitador a la frecuencia normal no ve los picos entre muestras, y loudnorm tomó el pico de muestra como si fuera real. Esta tanda cambia la receta por una que mide el pico real y se corrige sola, y la cablea.

## Constantes (todas con origen; ninguna nueva sin él)
| valor | qué es | origen | quién |
|---|---|---|---|
| −14 LUFS | sonoridad integrada del master | DECISIONES 2026-11-04 l.237 | Omar |
| −1,5 dBTP | techo de pico real del archivo final (AAC) | ya existe: `audio_manager.py:463` | proyecto |
| ×4 (44 100 → 176 400 Hz) | sobremuestreo del limitador para que limite el pico real | estándar: ITU-R BS.1770-4, anexo 2 (el pico real se define con sobremuestreo ×4) | estándar |
| ±0,5 LU | tolerancia de la sonoridad | estándar: EBU R128 (desvío permitido ±0,5 LU donde la normalización exacta es posible) | estándar |
| techo del limitador | arranca en −1,5; si el AAC final pasa el techo, baja exactamente lo que pasó | derivado, medido en cada pasada | material |
| G (ganancia) | arranca en −14 − I medido; cada pasada suma lo que faltó (−14 − I de esa pasada) | derivado, medido | material |
| 44 100 Hz | frecuencia del audio | ya existe: `fase2b.py` (`aresample=44100` en la mezcla) | proyecto |
| 192k | bitrate AAC | ya existe: literal en `fase2b.py` (1343, 1350, 2041, 2083, 2171) y `transition_applier.py:431` | proyecto |
| fin del bucle | para cuando cumple las dos cosas, o cuando una pasada no reduce la falla frente a la anterior | regla, **sin número de vueltas** | analista |

Se borran del plan de F75: el −2 dBFS de muestra (analista, sin respaldo), la 2.ª pasada de loudnorm y `-ar 48000`.

## Simulación del analista (hecha antes de mandar, sobre el audio real de Wittenoom)
Audio: `output/123bbb64-…/<tid>_final_gfx.mp4` (I −24,0 · LRA 6,6 · pico real −6,6). Ojo: ffmpeg **4.4** en la VM del analista; CC tiene 8.1, donde el AAC casi no suma pico (F75: −0,9 → −0,9). Por eso la receta mide y no supone.

| pasada | G | techo limitador | I | LRA | pico real (AAC) |
|---|---|---|---|---|---|
| receta F75 (sin ×4), ffmpeg 4.4 | +10,0 | −2,0 muestra | −14,5 | 5,9 | **+1,4** ✗ |
| 1 (×4) | +10,00 | −1,50 | −14,3 | 6,0 | −0,3 ✗ |
| 2 | +10,30 | −2,70 | −14,5 | 5,5 | −1,0 ✗ |
| 3 | +10,80 | −3,20 | −14,4 | 5,1 | **−1,5 ✓** |
En la etapa del wav (antes del AAC) el ×4 deja el pico real en −1,5 exacto en la 1.ª pasada: lo que sobra lo pone el AAC de ffmpeg 4.4. En 8.1 se espera que cierre en 1–2 pasadas.

## Módulos que toca
1. `script_engine/audio_master.py` (**nuevo**): hoy no existe. Después: una función `master_mp4(path)` que extrae el audio, corre el bucle, re-encoda el audio y remuxa con `-c:v copy` sobre el mismo archivo (vía temporal + reemplazo atómico). Devuelve la tabla de pasadas (G, techo, I, LRA, pico real) y la escribe en el log del paso.
2. `fase2b.py`: hoy no hay master. Después: una llamada a `master_mp4(final_path)` en el lugar común de F75 C0 (`:3656/3657`, justo antes de `final_dur = _get_duration(final_path)`), para los 3 caminos (a)/(b)/(c). Chascada: los 5 literales `"192k"` de fase2b y el de `transition_applier.py:431` pasan a la constante del perfil (sin cambio de salida).
3. `audio_profiles.py`: constantes nuevas junto a `voice_lufs_v4`, cada una con su comentario de origen (tabla de arriba): `master_lufs`, `master_tp_dbtp`, `master_oversample`, `master_lufs_tol_lu`, `aac_bitrate`. `audio_manager.py:463` pasa a leer `master_tp_dbtp` en lugar del literal −1.5 (mismo valor).
4. `DECISIONES.md`: la línea 241 (F75 C) se **reemplaza** por la receta nueva (no se agrega otra al lado).

## Receta (una sola lógica, la vieja no se cablea)
Cada pasada: `volume=<G>dB, aresample=<44100×4>, alimiter=level=disabled:latency=1:limit=<10^(techo/20)>, aresample=44100` → AAC `<aac_bitrate>` → medir el **AAC** con `ebur128=peak=true` (I, LRA, pico real).
- falla = max(0, pico − (−1,5)) + max(0, |I − (−14)| − 0,5).
- falla = 0 → listo.
- si no: techo −= max(0, pico − (−1,5)); G += (−14 − I); otra pasada.
- si la falla no baja frente a la pasada anterior → para, se queda con la pasada de menor falla **que cumpla el techo de pico**, (si ninguna cumple el pico, la de menor pico) y deja un ⚠ en el log y en el reporte (no frena el pipeline: Omar no quiere preguntas chicas).
- `latency=1`: hallazgo de CC en F75 (sin él el audio se atrasa ~5 ms frente al video).
- `_final_gfx_no_music.mp4` y `mezcla_preview.wav` siguen a −24 (no se publican; aceptado en F75).

## Etapas
**E1 (código + tests, subagente A)** módulos 1–3. Tests: el bucle con mediciones simuladas (cierra en 1 pasada; cierra en 3 como la tabla; caso sin progreso → se queda con la mejor que cumple pico, con ⚠); la llamada de fase2b existe una sola vez en el lugar común; el video sale con `-c:v copy` (md5 del stream de video igual). **Salida en texto:** el diff de fase2b alrededor de :3657 y la lista de tests.

**E2 (lab sobre Wittenoom, subagente B, en paralelo con E1 una vez exista la función)** copiar `<tid>_final_gfx.mp4` a `lab/hyperframes/f76/`, correr `master_mp4` sobre la **copia**. **Salida en texto:** tabla de pasadas como la de arriba (ffmpeg 8.1); duración audio vs video antes/después (diferencia ≤ 1 cuadro, 33 ms); md5 del stream de video de la copia antes/después (iguales). 4 extractos nuevos de 60 s, mismos tramos que F75 (0:00–1:00 y 10:44–11:44), original y master, en `lab/hyperframes/f76/`. Los wav/mp4 no van a git.

## Reglas fijas
- US$ 0, ninguna llamada a API. No se toca el mp4 publicado de Wittenoom (md5 `1fb47948e43951d4c009e13c0131d184` antes y después). Nada en `output/`.
- Subagentes en paralelo (E1 y E2 como arriba). Lo viejo no se cablea; el −2 dBFS no aparece en código.
- Suite rápida verde + las 3 heredadas; `mapa_modulos --check` 0 fallas (sticker para `audio_master.py`).
- Reporte `lab/hyperframes/f76/F76_REPORT.md` con la salida de E1 y E2, «abierto» completo y veredicto íntegro del `revisor-handoff`. `ESTADO_SESION.md` actualizado. Commit y push en la rama.
- **PARADA al final. Omar escucha los 4 extractos nuevos de F76 (no los de F75) antes del render de Palomares.**
