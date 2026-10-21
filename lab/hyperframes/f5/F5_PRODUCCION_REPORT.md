# F5 — Producción de Orleans v2 · PARADA: Omar ve el video

Rama `f5-guion-v2`, desde `19cf5d9` (F5d). `main` intacta. Decisiones: `DECISIONES_F5.md` P1–P9.

## El video
**`output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4`** — 571.2 s (9 min 31 s), 243 MB, con gfx (looks, disperso), identidad y crítico activos. También está la versión sin música: `…_final_gfx_no_music.mp4`.
- La voz dura 542.6 s; el resto son las pausas de la pregunta de cierre y los cortes a negro.
- v1 duraba ~11.5 min: la narración nueva es más corta.

## Lo que se hizo, en orden
1. **Retoque de los caps 5 y 6** (mejor de 3 solo en esos dos; el resto, byte-idéntico).
   - Cap 5: la frase del research («El sheriff de la cárcel declaró… 14 órdenes») va sin comillas; las comillas quedan solo para la cita de Gusman. Hay una regla dura nueva, «comillas solo para citas del pool».
   - Cap 6: «dos turistas de Ohio, Robie Waganfeald y Paul Kunkel Jr.».
   - Re-validación del guion completo: 0 reglas duras en los 7 caps, densidad por id 2.02, 3-gramas 5.3 % (antes 8.7 %), cliffhangers 6/6.
   - Costo: US$ 0.25 de Pro.
2. **Bloque G.**
   - **G1:** el crítico juzga un snapshot de HyperFrames del bloque YA dibujado en t + 1 s (`hyperframes snapshot --at`, uno por cap, ~12 s). Token `critic_snapshot`. En el render, los 27 bloques se juzgaron sobre el snapshot.
   - **G2:** el titular del recorte tiene como máximo 8 palabras. Si no entra en la tarjeta, baja un cuerpo (hasta 2); nunca se corta.
   - **G3:** la caja final del zoom pasa por `verify_crop`. En el render sacó 2 zooms que no se veían: ch01 «abandonados» y ch06 «intoxicación».
   - **G4:** espiral (huracán) y rayo tachado (generadores), con el pipeline de los 12 (Flux.2 Pro, mismas 3 semillas, potrace). Los elegí yo, sin PARADA: espiral «a», rayo «b». Los 12 aprobados no cambiaron (comparados byte a byte).
3. **Producción en su topic propio, `ba6c3cac-f5v2`.**
   - Topic en `topics_db.json`: copia de v1 con el `evidence_pool` y la foto madre de v1.
   - Las simulaciones viejas se movieron a `output/_bak_ba6c3cac-f5v2_simulaciones/`.
   - Cadena: TTS → música → prompts (m03 con timestamps reales) → assemble → fase2a (imágenes + Veo) → **un solo render** con `--keep-segments --gfx --gfx-sparse --gfx-quality looks`.
   - Firefox cerrado y RAM libre 19.5 GB antes del render (el script lo verifica y no arranca si no se cumple).
   - Hoja de contactos por cap: `lab/hyperframes/f5/produccion/hojas/`.

## Tiempos
| etapa | tiempo |
|---|---|
| retoque caps 5–6 (Pro, mejor de 3) | 3.5 min |
| guion de producción: TTS + música + m03 + assemble | 4.0 min |
| imágenes + Veo (fase2a) | 10.2 min |
| reintento del Veo del ch07 (ver abajo) | ~1.5 min |
| render fase2b con gfx (un solo render) | **77.8 min** |
| capa gfx por cap (dentro del render) | ch01 135 s · ch02 634 s · ch03 466 s · ch04 519 s · ch05 353 s · ch06 483 s · ch07 363 s |

## Costos
| rubro | US$ | cómo se midió |
|---|---|---|
| imágenes Seedream 4.5: 81 (79 escenas + 2 bases de Veo) | 3.24 | 81 × 0.04 (tarifa de `config.py`; 81 imágenes generadas en el log) |
| Veo 3.1: 2 clips buenos (ch01, ch07) | 0.48 | 2 × 0.24. El 1.er intento del ch07 dio 422 en fal; no verifiqué si fal lo cobra |
| TTS ElevenLabs: 7,157 caracteres | 0.21 | estimado: caracteres × 0.00003 (`config.py`); el tracker no lo guardó |
| Gemini Pro, narración (F5d 0.74 + retoque 0.25) | 0.99 | medido (`01b_costo*.json`) |
| Gemini, prompts de imagen (m03) | ≈ 0.84 | **no medido**: `process_topic` no guarda el tracker. Estimado con el último m03 de Orleans v1 (`cost_history`, índice 43) |
| Gemini, gfx del render (director, crítico, visión) | 0.19 | medido (fase2b) |
| íconos nuevos G4: 6 imágenes Flux.2 Pro | 0.27 | 6 × 0.045 |
| **total de esta tanda** | **≈ 6.2** | sin contar las corridas F5–F5d anteriores |

## Bloques por cap (veredicto del crítico sobre el bloque dibujado)
18 de 27 bloques pasan. «Quedan» = lo que sale en el video.

| cap | quedan | el crítico sacó | además |
|---|---|---|---|
| ch01 | sellos «estrella», «suerte» | sello «subiera» (repite: el tinte de agua sobre agua) | zoom «abandonados» fuera por `verify_crop`; sin reloj (el cap no avanza de fecha) |
| ch02 | **recorte «los prisioneros no serán evacuados» (2005, T05)**; zoom «mano bolígrafo»; reloj 28 AGO | sellos «abandono» y «inundación» (repite) | pregunta «¿Cómo se quedaron sin energía?» |
| ch03 | sello «estruendo»; ícono «tumba» (cruz); ícono «celdas» (candado); zoom «desagüe»; **recorte «el sheriff Marlin Gusman solicita ayuda» (2005, T12)**; reloj 29 AGO | ícono «inundación» (repite) | pregunta «¿Qué nivel alcanzó el agua?» |
| ch04 | sellos «horror», «agujero»; reloj 30 AGO | sello «atrapados» (estorba: tapa las manos en las rejas); zoom «agujero» (repite) | |
| ch05 | sellos «escalofriantes», «murió» | sello «desvanecido» (repite) | |
| ch06 | contador «650,000 dólares»; sellos «intoxicación», «horrores» | — | zoom del pico fuera por `verify_crop` |
| ch07 | sellos «perdieron», «cuerpos» | zoom «espalda prisionero» (estorba); contador «500» (repite) | sin pregunta (es el outro) |

## Lo que no salió bien
1. **G1 confunde el bloque dibujado con la foto.** En ch02 («ABANDONO») y ch05 («DESVANECIDO») el crítico dice que el sello «ya está visible en la imagen» y lo saca como «repite». Es su propio bloque. El prompt de G1 lo aclara («el bloque YA DIBUJADO encima»), pero no alcanza. Arreglo propuesto, no hecho: mandarle dos cuadros, la foto sola y el bloque dibujado. Al menos 2 de los 9 «no pasa» son este error.
2. **G2 dejó solo 2 recortes en todo el video** (la simulación de F5d tenía 6, con el tope de 10 palabras). Con 8 palabras, 23 candidatos no tienen cláusula completa y ninguno se corta, como pediste. Los 5 datos reservados para pantalla tampoco salieron:
   - T04, cap 1 y T22, cap 7: no entran sin pisar otro bloque;
   - T16, cap 4 y T23, cap 6: su cláusula pasa de 8 palabras;
   - T19, cap 6: la voz no habla de eso.

   Los caps 6 y 7 vuelven a quedar sin recorte (P5).
3. **El Veo del ch07 falló** en fase2a con un 422 de fal y quedó como imagen fija. Lo reintenté una vez a mano, con el mismo prompt e imagen, salió bien, y actualicé el manifest antes del render. El manifest previo está en `produccion/assets_manifest_pre_veo07.json`.
4. **TTS:** ElevenLabs avisó «Forced Alignment loss alto» (0.53–0.65) en los 7 caps. Los timestamps cubren todo el audio, sin huecos de más de 1 s, pero no verifiqué el sync a ojo. Las corridas de junio no tenían ese aviso.
5. **Imágenes:** fueron 81 prompts, no 97: la voz es más corta y el número de imágenes sale de la duración del audio. El canon de menores se respetó en los prompts con niños (ch05 imágenes 6 y 7, en el centro juvenil). Queda un borde: ch01 suplementaria 4 es «un hombre joven de fines de la adolescencia» en una celda, y no sé si la imagen lo muestra como menor.
6. **La hoja del ch03** muestra el ícono «tumba» sobre un cuadro gris con franjas negras (tinte del mood muerte, el «lavado» que ya estaba pendiente desde F3).
7. **No medido:** el costo de Gemini de m03 (estimado) y el del TTS (estimado).
8. **G3 en el ch05:** no hay línea de `verify_crop` porque ese cap no terminó con zoom (el director lo descartó antes: «foto-primero»). No había caja que verificar.
9. **Léxico:** la corrida, por ser un video real, sumó propuestas de palabras a `gfx_profiles/lexico_propuestas.json` (`record_proposals`, como en cualquier producción). Lo dejé sin commitear: decide Omar si entra.

## Dónde está
- Video: `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4`.
- Hojas de contactos: `lab/hyperframes/f5/produccion/hojas/hoja_contactos_ch01…07.jpg` (originales en `output/ba6c3cac-f5v2/_fase2b_work/`).
- Cues por cap: `lab/hyperframes/f5/produccion/gfx_cues_ch0N.md`. Logs: `produccion/*.out` y `produccion.log`.
- Prompts con personas (los de producción): `PROMPTS_PERSONAS_v2.md`.
- Script: `lab/hyperframes/f5/produccion_orleans_v2.py --etapa preparar|guion|imagenes|render`.
- Código G: `gfx_critic.py` (`snapshots`, prompt dibujado), `gfx_layer.py` (G1 + G3), `gfx_project.py` (`archive_head_px`), `gfx_pool.py` (8 palabras), `gfx_icons/` + `gfx_profiles/icons/espiral.svg`, `rayo_tachado.svg`. Retoque: `m01b_narrator.regenerate_caps`, `m05_narrative.false_quotes`.
- Tests: 397 verdes (393 + 4 nuevos en `test_module_f5_prod.py`) + 3 fallas viejas de `01b_pauses`. G3 no tiene test propio (lo cubre la corrida: 2 zooms sacados).

## Veredicto del revisor (revisor-handoff, íntegro; dado antes del commit: las notas de G3/ch05 y del léxico ya están arriba, puntos 8 y 9; `main` = `43f528a`, intacta)

VEREDICTO: CUMPLE CON OBSERVACIONES

Tests: corrí el comando pedido y dio 397 passed y 3 failed. Las 3 fallas son las viejas de test_module_01b_pauses.py. No hay bytes 0x08 en ningún .py. No corrí renders ni APIs.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1a | Caps 1–4 y 7 del 01b idénticos al pre_retoque | OK | Comparé 01b_narration.json con pruebas/01b_narration_f5d_pre_retoque.json: iguales en 1,2,3,4,7 y distintos solo en 5 y 6. |
| 1b | Cap 5 sin comillas en la frase del sheriff; comillas solo para Q02 | OK | En el texto del cap 5 la frase «el sheriff de la cárcel declaró que ningún preso murió o escapó… 14 órdenes» va sin comillas. La cita de Gusman sigue entre comillas. `_retoque` guarda la instrucción. |
| 1c | Cap 6 con «dos turistas de Ohio, Robie Waganfeald y Paul Kunkel Jr.» | OK | La frase está en el cap 6, una sola vez. |
| 1d | Re-validar | OK | Existe 06_judge_narrative.json. El costo del retoque está en 01b_costo_retoque.json. Los números de validación del reporte (0 reglas duras, 5.3 % de 3-gramas) no los recalculé. |
| 2-G1 | El crítico juzga el snapshot del bloque dibujado | OK | Los 7 gfx_chNN.log dicen «juzgados sobre el bloque dibujado (snapshot)». Suman 3+4+6+4+3+3+4 = 27 bloques. |
| 2-G2 | Titular del recorte de 8 palabras como máximo, sin cortar | OK | Los logs de fragmentos dicen «≤ 8 palabras». Quedan 2 recortes en todo el video (ch02 y ch03). El reporte lo admite. |
| 2-G3 | La caja final del zoom pasa por verify_crop | PARCIAL | Aparece «zoom final: verify_crop» en los logs de ch01, 02, 03, 04, 06 y 07. En ch01 y ch06 la caja dio «NO se ve: zoom fuera». ch05 no tiene la línea, porque ahí el zoom del director se descartó («foto-primero») y evidence_zoom es null. No hay caja final que verificar, pero el reporte no lo explica. El reporte dice que G3 no tiene test propio. |
| 2-G4 | SVG espiral y rayo tachado con el pipeline de los 12, sumados al set | OK | Existen espiral.svg, rayo_tachado.svg y 3 candidatos de cada uno. El manifest y gfx_config se modificaron. Los tests de iconos pasan. No reconstruí la comparación byte a byte de los 12 antiguos. |
| 3a | Un solo render, topic propio, gfx sparse looks, Firefox cerrado, RAM > 14 GB | OK | produccion/render.out: «RAM libre 19.5 GB · Firefox cerrado» y «fase2b rc=0 en 77.8 min (… --keep-segments --gfx --gfx-sparse --gfx-quality looks)». El topic es ba6c3cac-f5v2. |
| 3b | El mp4 existe | OK | output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4 pesa 255 MB. ffprobe da 571.17 s, que coincide con los 571.2 s del reporte. |
| 3c | Siete hojas de contactos | OK | Las 7 hojas están en `_fase2b_work/` y en `lab/hyperframes/f5/produccion/hojas/`. No abrí ninguna imagen. |
| 3d | 97 imágenes nuevas | PARCIAL | Salieron 81, no 97. El reporte lo declara y lo explica por la duración del audio. |
| 4 | F5_PRODUCCION_REPORT.md con tiempos, costos, bloques por cap, ruta del mp4, y parada | OK | El archivo existe. Bloques por cap: 18 de 27 pasan, y coincide con los logs (2+2+5+2+2+3+2). Los vetos citados (subiera, abandono, inundación, atrapados, desvanecido, espalda prisionero, 500) coinciden con los logs. La suma de tiempos gfx por cap da 2953 s, coherente con los 77.8 min. 81 × 0.04 = 3.24. |
| 4b | Honestidad sobre lo que no salió | OK | El reporte declara las 81 imágenes, el Veo ch07 reintentado a mano, que G1 confunde el sello, los 2 recortes, y los costos estimados de m03 (≈0.84) y TTS (0.21). |

Observaciones:
- La línea «Veredicto del revisor (se pega abajo)» queda vacía hasta que se pegue este veredicto.
- El costo total (≈6.2) incluye ≈1.05 estimado (m03 y TTS), no medido.
- El 1er intento de Veo ch07 dio 422 y no se verificó si fal lo cobró.

Fuera de alcance:
- `diag_234_cap4.py` aparece modificado (1 línea). Omar ya avisó que no es nuestro, no debe entrar al commit.
- `gfx_profiles/lexico_propuestas.json` cambió (+168 líneas). Es un efecto de la corrida (promoción de léxico con "ba6c3cac-f5v2") y no está en la lista del pedido. Hay que decidir si va al commit.
- `lab/hyperframes/f5/corrida/correr_f5_orleans.log` cambió (+2 líneas). Es de la etapa retoque y es plausible.
- `topics_db_pre.json` está en `produccion/` sin trackear. Omar pidió no commitearlo.
- La rama es f5-guion-v2. No verifiqué que main esté intacta con un comando directo.

Riesgos que el contrato no cubre:
- Con G1, el crítico saca como «repite» sellos propios (ch02 «abandono» y ch05 «desvanecido»), así que el resultado visual del video depende de ese sesgo conocido.
- No verifiqué el sync de la voz. ElevenLabs avisó «Forced Alignment loss alto» (0.53–0.65) en los 7 caps, y el reporte confirma que nadie lo miró a ojo.
- Quedan sin recorte los caps 6 y 7, y el borde del canon de menores en la ch01 suplementaria 4 sigue sin confirmarse.
