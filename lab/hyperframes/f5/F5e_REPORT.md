# F5e — Arreglos de capa gfx después de ver Orleans v2 · PARADA

Rama `f5-guion-v2`. Se rehízo solo la capa gfx: el guion y las imágenes no se tocaron. `main` intacta. Decisiones: `DECISIONES_F5.md` Q1–Q7.

## El video
- **Nuevo final:** `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4` (571.2 s). Re-render de la capa gfx con `--reuse-visuals`: 41.0 min, con RAM libre 18.7 GB y Firefox cerrado.
- **El anterior:** `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx_f5d.mp4`.
- Las capas y los planes previos quedaron en `_fase2b_work/_bak_f5e_pre/`.
- **Hojas de contactos:** `lab/hyperframes/f5/produccion/hojas_f5e/hoja_contactos_ch01…07.jpg`.

## Qué cambió en pantalla
| | antes (F5d) | ahora (F5e) |
|---|---|---|
| recortes | 2 | **5**: ch01 ×2, ch02, ch03, ch07 |
| datos reservados para pantalla que salieron | 0 de 5 | **2 de 5**: T04 «Los reclusos reciben su última comida…» (ch01) y T22 «La ACLU publica el informe…» (ch07, kicker «American Civil Liberties Union (ACLU), 2006») |
| sellos neutros o verbos | estrella, suerte, subiera, estruendo, agujero, murió, perdieron | **ninguno** |
| crítico: pasan | 18 / 27 | **24 / 27** |
| «repite» por su propio sello | 2 (abandono, desvanecido) | **0** |
| contador | 650,000 (ch06) y 500 (ch07, vetado) | **517 en ch05** (el 500 del ch07 sale: mismo hecho); 650,000 en ch06 |

- **Los 3 bloques que el crítico sacó ahora:**
  - zoom «Rostro del joven» (ch01): la foto ya lo muestra;
  - ícono «inundación» (ch03): la foto ya muestra la inundación;
  - zoom «espalda prisionero» (ch07): no aporta.

  Los tres juzgan contra la foto, no contra el bloque.
- **Titulares de 9 a 12 palabras con cuerpo menor:** «Los reclusos reciben su última comida antes de que el huracán azote» (12, con ícono espiral, G4), «los prisioneros no serán evacuados de la Prisión de Orleans Parish» (11), «la Prisión de Orleans Parish (OPP) albergaba a 6,375 reclusos» (10), «el sheriff Marlin Gusman solicita ayuda para la evacuación» (9).
- **No entraron:** T16 (ch04), T19 y T23 (ch06). Su oración choca con otros bloques en toda la escena, aun corriéndose.
- **El contador 6,375 del ch01 se planeó pero no salió:** el pico de la frase de al lado limpia ±5 s. La cifra sí sale en el recorte de D57.

## Sincronía voz ↔ subtítulo (punto 5)
- **Cómo se midió:** los subtítulos salen de los timestamps de ElevenLabs. Los comparé con faster-whisper (modelo small) palabra por palabra en los 7 caps (`produccion/SYNC_v2.md`) e hice lo mismo con v1, que no tenía el aviso, como referencia (`SYNC_ba6c3cac_v1.md`).
- **Mediana:** el subtítulo va +100 ms detrás de Whisper en los 7 caps de v2. En v1 da +80 a +140 ms en 6 caps (la medición de ch02 de v1 salió rota: Whisper alineó 7 de 409 palabras), así que el corrimiento aparece igual sin el aviso. Lo atribuyo al sesgo de Whisper, no a un desfase del alineado.
- **Palabras con más de 150 ms:** entre el 20 y el 34 % por cap en v2, y entre el 17 y el 35 % en v1. Son picos sueltos: p95 de 240 a 500 ms y máximo 1.04 s («inició», ch06 46.8 s).
- **ASS:** el primer Dialogue de cada `chNN_subs.ass` arranca exactamente en el timestamp.
- **Conclusión:** no hay un desfase sistemático mayor a 150 ms atribuible al aviso de alineación; v2 sincroniza como v1. **No lo vi a ojo:** es una medición, con el ruido propio de Whisper (±100–200 ms).

## QA Studio (punto 6)
- **Abierto:** http://127.0.0.1:8000 (topic `ba6c3cac-f5v2`, lanzado con el venv de `viral-video-pipeline`).
- Cada foto tiene una casilla **«↻ regenerar»**. Las marcas se guardan en `output/ba6c3cac-f5v2/assets/_qa_marks.json`.
- `lab/hyperframes/f5/regen_marcadas.py` regenera solo las marcadas con el mismo prompt, otra semilla y sin validador de visión. Deja backup en `_qa_backups` e invalida el clip del cap. Después hace falta un re-render con `--reuse-visuals`.
- **Pendiente:** que Omar marque las fotos. Todavía no hay ninguna marcada.

## Research (punto 7)
`topic_researcher.MAGNITUDE_SECTION`: el prompt del ángulo técnico suma `[DATOS DE MAGNITUD]`, sin tope: categoría, vientos, marea, altura del agua, muertos y desaparecidos, área. Cada dato con cifra, unidad y fuente. Los ángulos humano y misterio quedan idénticos (test). Orleans no se re-investigó.

## Código
- `gfx_pool`: 12 palabras, reservados, `_free_slot`, `count_groups`, `pool_count_up`.
- `gfx_project.archive_head_px`.
- `gfx_critic`: dos cuadros, `g1-snap-2`.
- `gfx_intensity`: `clase`, `neutra`, `is_verb_form`, `stamp_lexicon`; token `stamp_nouns_only`.
- `qa_studio_server` + `qa_studio.html`: marcas y `_reseed_core`.
- `topic_researcher`.
- Scripts del lab: `sync_check.py`, `regen_marcadas.py`, `produccion_orleans_v2.py --etapa render_gfx`.
- Tests: `test_module_f5e.py` (6). Suites: 403 verdes + 3 fallas viejas de `01b_pauses`.
- `gfx_profiles/misterio.json` sumó «negrura»: 3 durante el render; es una promoción automática del léxico y no se commitea (lo decide Omar, como `lexico_propuestas.json`).
- Costo del re-render: US$ 0.02 de Gemini (lo que reporta fase2b: director de intensidad con prompt nuevo y crítico con dos cuadros). Imágenes y Veo: US$ 0.

## Veredicto del revisor
(íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Tests corridos por mí: 403 verdes y 3 fallas viejas de `test_module_01b_pauses`, como se esperaba. No hay bytes 0x08 en los .py tocados. Nadie tocó el guion ni las imágenes: `data/scripts/_steps/ba6c3cac-f5v2/01b_narration.json` es de las 06:01 y ningún PNG de `assets/` es posterior a las 08:00. No vi el MP4 ni las hojas de contactos, así que no verifiqué a ojo la legibilidad del cuerpo menor ni los solapes.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | G2: titular hasta 12 palabras con cuerpo menor, 8 solo si cabe | OK | `gfx_pool.py` usa `archive_head_max_words_pool`=12; `gfx_project.archive_head_px` baja el cuerpo desde 9 palabras. Titular de 12 palabras en `gfx_cues_ch01.md` (14.7 s). |
| 1b | Reservados para pantalla con prioridad | PARCIAL | Salen 2 de 5: T04 en ch01 y T22 en ch07. T16 (ch04) y T19/T23 (ch06) siguen fuera con «no entra sin pisar otro bloque» (`gfx_ch04.log`, `gfx_ch06.log`). Ganan los sellos, punch-ins y ticker, no otro recorte: ch04 y ch06 no tienen ningún recorte. La prioridad pedida vale entre recortes, pero el resultado deja 3 de 5 sin salir. |
| 1c | Titular T22 con comilla sin cerrar | OBSERVACIÓN | El titular de ch07 es `La ACLU publica el informe "Abandoned & Abused`. El título del informe queda cortado y la comilla abierta, y eso va en pantalla. |
| 2 | G1: el crítico recibe foto sola y bloque dibujado, y nunca repite por su propio sello | OK | `gfx_critic.py` manda dos imágenes y el prompt lo prohíbe; la caché pasó a `g1-snap-2`. En los 7 planes resueltos todo veredicto dice `mira: bloque dibujado`. Ningún sello recibió «repite»: solo 3 zooms/íconos lo recibieron, y es por la foto. |
| 3 | Sellos solo en léxico o sustantivos/adjetivos de peso ≥ 2; sin verbos ni neutras | OK | `gfx_intensity.py` descarta `clase` que no sea sustantivo/adjetivo, `neutra` y formas verbales. Los sellos del render nuevo son todos de peso 2 o 3 y no hay verbos ni neutras. `faltaban` quedó descartado en el log. |
| 3b | Palabras genéricas de peso 3 | OBSERVACIÓN | «reclusos» (ch01) y «prisioneros» (ch03) son sellos de peso 3 propuestos por el director. Cumplen la regla, pero son palabras del tema que se repiten en todo el relato. |
| 4 | 517 y 500 son un hecho: un contador, con 517 en el cap que lo dice | OK | `count_up` 517 en ch05 (14.0 s); el 500 de ch07 ya no sale. La narración dice 517 solo en ch05. `pool_count_up` y `count_groups` hacen el dedupe por hecho, y el 650,000 sigue en ch06. |
| 5 | Sincronía voz-subtítulo en los 7 caps y reporte de desfase > 150 ms | PARCIAL | El reporte no lo hizo a ojo: lo midió con Whisper `small` contra los timestamps de ElevenLabs y lo declara (`F5e_REPORT.md`, `DECISIONES_F5.md` Q5). La mediana es +100 ms en los 7 caps, pero entre el 20 y el 34 % de las palabras pasan de 150 ms, con p95 de hasta 500 ms y máximo de 1.04 s. «Sesgo de Whisper» es una hipótesis, no está demostrada. |
| 5b | Alcance de la medición de sincronía | PARCIAL | `sync_check.py` solo compara timestamps con el mp3 y mira el primer Dialogue del ASS. No mide el desfase real en el MP4 final, que es lo que Omar iba a ver. La referencia v1 de ch02 está rota (7 de 409 palabras, p95 de 60 s) y el reporte igual cita v1 como «+80 a +140 ms». La conclusión «no hay desfase sistemático > 150 ms» se sostiene solo para la mediana. |
| 5c | Re-render, nuevo final, hoja de contactos y reporte | OK | `ba6c3cac-f5v2_final_gfx.mp4` (571.2 s) y el `_f5d` anterior conservado. Hay 7 hojas en `hojas_f5e/`. `render_gfx.out` dice rc=0 con `--reuse-visuals`; el costo es US$ 0.0225. |
| 6 | Galería del QA Studio y regenerador, sin validador de visión | OK | `:8000` responde, `/marks` devuelve `{"marks":{},"done":{}}` y `qa_studio.html` tiene la casilla «regenerar». `regen_marcadas.py --dry-run` corre sin pagar. `_reseed_core` usa el mismo prompt con otra semilla, hace backup y no usa validador. Falta que Omar marque; la regeneración real no se probó (cuesta). |
| 7 | `[DATOS DE MAGNITUD]` solo en el prompt del ángulo técnico, sin tope | OK | `topic_researcher.py`: `MAGNITUDE_SECTION` se inserta solo si `angle.key=="tecnico"`; incluye categoría, vientos, marea, altura, muertos y área. Orleans no se re-investigó. |

Fuera de alcance:
- `diag_234_cap4.py` y `gfx_profiles/lexico_propuestas.json` los declaraste ajenos al trabajo.
- `gfx_profiles/misterio.json` tiene un cambio sin commitear que no está en esa lista: agrega «negrura»:3 al léxico `oscuridad_encierro`, y «negrura» salió como sello en ch02. Parece una promoción automática de léxico durante el render, no un cambio a mano.
- Los `gfx_cues_ch0N.md`, `DECISIONES_F5.md` y `produccion.log` sin commitear son productos del trabajo.
- Los archivos tocados en el commit 7c0b2e5 están dentro del alcance.

Riesgos que el contrato no cubre:
- Sin validador de visión, la regeneración con otra semilla puede traer fallas que antes se filtraban. Después hace falta otro re-render con `--reuse-visuals`.
- Los reservados que no entran no tienen otra vía de aparecer, y el desfase real de subtítulos en el MP4 final sigue sin medirse.
