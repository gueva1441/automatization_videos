# F10 — hasta la PARADA (§4.3): integración v3 + guion de Ycuá Bolaños

**Rama:** `f10-integracion-v3` (desde `790bec9`). Sin merge, sin producción: **PARADA** hasta el OK de Omar.
**Pedido:** `lab/hyperframes/f10/HANDOFF_F10_integracion_v3.md` §4.1–§4.3. **Decisiones:** `DECISIONES_F10.md` (D1–D18).
**Para leer:** `lab/hyperframes/f10/NARRACION_ycua.md` (por beat, con `narration_tts`), `ESCALETA_ycua.md`, `06_judge_ycua.json`, `costo_guion_ycua.json`.

## 1. §4.1 — Integración (hecho)
- **`fase1_5 --v3`** (o `topic["guion_version"] == 3`, siempre que el topic traiga `evidence_pool`):
  - `m01a` = compuerta del pool + escaleta;
  - `m01b` = guionista → editor → **`m01d_particion`** → juez m05;
  - lo demás (normalizer_gate, audio, m07, m03, assemble) sin cambios;
  - sin el flag, el camino viejo queda igual (test).
- **Nuevo `--from <paso>`:** reanuda la cadena hasta `assemble` (lo va a usar §4.4).
- **`script_engine/m01d_particion.py`:** escribe `01a_skeleton.json` y `01b_narration.json` con el contrato de siempre.
  - Agrega solo `narration_tts` e `ids_usados`.
  - Los títulos de cap salen de una llamada Flash corta, con respaldo determinista.
  - Los campos `bullets`, `pantalla_ids`, `cliffhanger` y `personajes` se derivan de la escaleta.
  - Los largos se miden contra `_len_range(role)` ±15 %: si un cap se pasa, se mueve un párrafo o el editor lo acorta; si queda corto, es aviso.
  - `regenerate_cap` (editor + escaleta + caps vecinos) queda como función.
- **Corrida en seco de Orleans f7r3** (topic de copia; se simula solo lo que cuesta plata o escribe fuera): `seco/seco_chequeos.json`, todo verde.
  - pasaron los 7 pasos hasta `assemble`;
  - skeleton y narración tienen el contrato completo;
  - `narration_tts` llega al audio y el texto de alineado va limpio;
  - m03 v3 queda activo;
  - `assemble` arma 7 caps y `fase2a.normalize_script` los acepta;
  - m02_5 corrió de verdad, en batch.
- **Bug de F7d encontrado y arreglado:** `topic_researcher` perdía el `evidence_pool` al guardar el topic, así que ningún topic de semilla v3 podía correr el guion v3 sin carga a mano (D15).
- **Decisión 2 de Omar (beats de disparo):** aplicada en `m03_imagenes_v3`; el tirador no aparece nunca. Queda una nota de re-hechura en `m03_visual` que el freno no me dejó cambiar (D2).
- **Decisión 3 (temas históricos):** no aplicada todavía (D3).
- **Tests:** `test_module_f10.py` (10). Suite amplia: 572 verdes + las 5 fallas previas.

## 2. §4.2 — Guion de Ycuá Bolaños (hecho; para leer)
- **El topic no existía en `topics_db`:** en F8 solo había corrido `run_seed`. Lo completé con el camino LONG v3 de `topic_researcher` (4a–4e), reusando la carpeta de F8 (US$ 0.99, D14).
  - El pool se rearmó con los arreglos de F8b: 227 datos · 52 citas verificadas · 15 elegibles · 62 eventos, verde.
  - Los ids cambiaron; las notas del analista van con los ids nuevos (D16).
- **Cifra canónica de muertos:** **327 oficiales, además de los desaparecidos** (D192, nota sobre el fallo de la Corte de 2025). La de 400 no se usa (D17). El título que armó 4c dice «400 vidas»: lo decide Omar.
- **Escaleta** (12 beats, 2.º intento; el 1.º lote se rechazó 3 veces, ver D18):
  - humano: **Liz Torres** (sobreviviente, con citas verificadas);
  - antagonista: Juan Pío Paiva;
  - pico: **T21, 11:25, la explosión**;
  - la orden de cerrar las puertas, en el cap 4;
  - la pericia de las 3 puertas, en el cap 6;
  - cierre: las velas y el «Que nunca más».
- **Narración:** 1,235 palabras (82 % de las 1,500). Por cap: 121 · 214 · 214 · 181 · 195 · 214 · 96. Títulos: Lluvia de Cenizas · El Carrito Repleto · La Nube Negra · Manos en el Vidrio · Bola de Fuego · El Mazo del Juez · Velas en las Ruinas.
- **Quedan 20 reglas duras** después del editor (Orleans F7c-3: 21). Lo que más pesa, a mi lectura:
  1. **Largo:** los caps 4, 5 y 7 quedan debajo del mínimo.
  2. **El cierre termina en un resumen** («busca que la memoria no se apague…»), no en la contradicción pericia–testimonios que pidió la nota 4 ni en una cita o pregunta (regla de F8 §2, que es blanda).
  3. **El pico no dice la hora (11:25)** y cierra con un juicio («Fue una masacre»).
  4. **327 suena en la voz (cap 5)**, aunque el plan de pantalla la reservó para verse y no decirse: cuenta como dura.
  5. **Hay párrafos sin dato** en los beats 3, 5 y 9, ids declarados que no suenan literales y una cita del gancho que adelanta un cap.
- **Etiquetas de voz (`narration_tts`):** pausas largas después de cada cita; `[slowly]` en el gancho y el pico; `[whispers]` solo en el golpe del pico (cap 5); `[quietly]` en los caps 4 y 6.
- **Costo del guion:** US$ 0.88 (escaleta 0.51 con el primer lote rechazado, guionista 0.17, editor 0.21, títulos 0.003). Con el research del topic, **US$ 1.87**.

## 3. PARADA
No sigo a producción hasta el OK de Omar. Según §4.3:
- si la nota del analista es menor que 8: una sola corrida de ajuste con sus notas;
- si es 8 o más: producción completa (§4.4).

## 4. Dudas para Omar / el analista
1. ¿El cierre se rehace con nota explícita («terminar en la pericia contra los testimonios, con una pregunta») en la corrida de ajuste?
2. ¿Aceptamos 327 dicho en la voz (es la canónica oficial) o va solo en pantalla?
3. Título del video: dice «400 vidas»; el guion dice 327 oficiales.

## 5. Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Contrato §2: chapters[7], solo se agregan narration_tts e ids_usados; sin flag byte-idéntico | OK | 01a_skeleton.json (Ycuá) trae 7 caps con bullets, chapter_number, cliffhanger, duration_seconds, evidence_ids, narrative_intent, pantalla_ids, render_engine, role y title. 01b_narration.json trae 7 caps con chapter_number, datos_usados, ids_usados, narration, narration_tts (los 7 con tts e ids). El diff de fase1_5.py en `_build_audio_script` y `process_topic` solo agrega ramas `use_v3`, y el `else` viejo queda igual. Tests `test_audio_script_v2_igual_y_v3_con_narration_tts` y `test_sin_flag_corre_el_camino_viejo`. Los tests prueban "igual" y no comparan bytes de una corrida real. |
| 2 | FRENOS §3 | OK | `git diff 790bec9 HEAD --stat`: no hay m02_5, tts_normalizer, m07, fase2a, fase2b, gfx_*, m03_visual, evidence.py, foto madre, candado ni anclas. m03_imagenes_v3 sí está tocado, y es lo permitido (14 líneas, decisión 2 de Omar). Sin merge (rama f10-integracion-v3). Sin validador de visión. |
| 3 | §4.1 tests y corrida en seco | OK | `test_module_f10.py` tiene 10 tests: frontera de párrafo y pico intacto, acortar con el editor, cap corto como aviso, contrato de 7 caps, v2 sin flag. `seco/seco_chequeos.json` da status PASS en m01a, m01b, normalizer_gate, audio, m07, m03 y assemble, con `normalizado: true` y `fase2a_normaliza: true`. El check del m02_5 en batch queda registrado en D13 (corrió real) y en el reporte. |
| 4 | §4.2 cadena y 4 entregas | OK | 01_v3_costos.json y costo_guion_ycua.json: escaleta (2 corridas), guionista, editor y partición. El juez está en 06_judge_ycua.json. Están ESCALETA_ycua.md, NARRACION_ycua.md, el juez y el costo. Las notas del analista están en escaleta_notas.md. El pool está verde (POOL_GATE.md y topics_db): 227 datos, 52 citas verificadas, 15 elegibles, 62 eventos. |
| 4b | Cifras del reporte vs archivos | OK, con una diferencia de 1 palabra | Palabras por cap: yo conté 121·214·214·181·194·214·96 (1,234); el reporte dice cap 5 = 195 y total 1,235. NARRACION_ycua.md también dice 195, así que es una diferencia de conteo de tokens. Las 20 duras coinciden (`revision_despues.hard` = 20; NARRACION línea 5). Costos: 0.297 + 0.2095 + 0.1701 + 0.2052 + 0.003 = 0.8848 (reporte: 0.88; "0.51 escaleta" = 0.5065). Los títulos de cap coinciden. |
| 5 | §4.3 PARADA: no se siguió a producción | OK | `output/audio/f8s1-ycua-bolanos` no existe. En `_steps/f8s1-ycua-bolanos/` no hay 03_visual.json, m07 ni assemble. El último commit es el wip antes del revisor. |
| 6 | Tests | OK | Lote del pedido: 138 passed. Suite amplia: 573 passed y 5 failed, que son justo las 5 previas (3 de 01b_pauses y 2 de m03_merge_timing). No corrí nada que llame APIs. |
| 7 | No commiteados | OK | diag_234_cap4.py, gfx_profiles/lexico_propuestas.json y gfx_profiles/misterio.json siguen modificados sin commitear. config.py y topics_db_pre_f7b.json no aparecen en el diff 790bec9..HEAD. |

Fuera de alcance
- topic_researcher.py (+3 líneas, aditivas): lo veo dentro de alcance. Sin ese arreglo el contrato §2 ("topic con pool v3 pasa por producción sin pasos a mano") no se cumple, y no está en la lista de frenos. Está documentado en D15, tiene test y es condicional.
- script_engine/m01a_escaleta.py (solo el texto del mensaje de rechazo): dentro de alcance. No cambia reglas ni el contrato de F6b, lo justifica D18 y está probado en la práctica con la escaleta que pasó en el 2.º intento.
- Archivos de lab/hyperframes/f10/ y data/topics_db.json (entrada de Ycuá): el handoff los pide, así que están bien.

Observaciones
1. El guion todavía NO es producible tal cual. Quedan 20 duras, entre ellas: caps 4, 5 y 7 bajo el mínimo, el cierre sin la contradicción pericia vs. testimonios que pedía la nota del analista, el pico sin "11:25", y "327" dicho en voz aunque está reservado para pantalla. El reporte las declara con honestidad. No es incumplimiento, porque la PARADA es para que Omar las lea. Pero la nota de cierre del analista (§4.2) no se cumplió, y el reporte lo dice.
2. El humano de la escaleta es Liz Torres. La nota decía "Blas Cristaldo o Liz Torres", así que cumple. Tatiana Gabaglio no es la voz principal.
3. D2: F8_NOTE_ARMA en m03_visual sigue diciendo "silhouettes on a far rooftop", y contradice la regla 2 de Omar. Se dejó por el freno y está declarado. Un beat de disparo en un video futuro la va a reactivar.
4. D3 (temas históricos) no se aplicó, y el handoff dice "re-correr Vajont cuando toque". Está bien.
5. `regenerate_cap` v3 (§2) quedó como función y no está enganchado a ningún CLI. Está declarado en D10.
6. El reporte tiene la sección 5 (veredicto del revisor) vacía a propósito, para pegar este texto.
7. La dependencia del titular "400 vidas" contra los 327 oficiales queda para Omar (duda 3 del reporte).

Riesgos que el contrato no cubre
- Esos 20 hards llegan tal cual a audio y m03 si Omar da OK sin pedir la corrida de ajuste.
- topics_db.json y los pasos de Ycuá están fuera de git. Hay respaldos solo en el scratchpad, que es temporal.
- Falta la prueba end-to-end con audio y m03 reales de un topic v3 (es §4.4). El seco simuló TTS, LLM de m03 y m07.

Respuesta del autor (después del veredicto): la observación 6 se resuelve con este commit. Para el riesgo de los datos fuera de git, dejo una copia de la entrada de Ycuá en topics_db en `lab/hyperframes/f10/ycua_topic_entry.json`. Lo demás queda para Omar en la PARADA.
