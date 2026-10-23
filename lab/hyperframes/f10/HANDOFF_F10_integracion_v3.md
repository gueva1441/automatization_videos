# HANDOFF F10 — Integración v3 de punta a punta + primer video: Ycuá Bolaños

**Fecha:** 2026-10-22 22:20 · **Analista:** chat proyecto · **Ejecuta:** CC, sesión nueva, **modo autónomo** con **una PARADA** (§4.3) · **Gate:** Omar
**Rama:** `f10-integracion-v3` desde `f9-voz-v4` (790bec9). Sin merge a `main` (la decisión de merge se toma con el video terminado).
**Leer antes:** este archivo; `lab/ESTADO_SESION.md`; `lab/hyperframes/f9/F8b_F9_REPORT.md` §5; `lab/hyperframes/f8/semillas/SEMILLAS.md` (S1).
**Reglas del modo autónomo:** como F8/F9 (no preguntar, `DECISIONES_F10.md`, commit wip antes de compactar, `ESTADO_SESION.md`, sesión nueva con §7 si pasa de ~80 %). **Excepción:** la PARADA de §4.3 es obligatoria: ahí se detiene y espera a Omar.

---

## 0. Decisiones de Omar sobre F8b/F9 §5 (cerradas 2026-10-22 22:14)
1. **Voz: MS Narrador v1 en v4** (`N9Z5MLTIaHFLflaLtbDi`). Confirmado.
2. **Beats de disparo:** la imagen es siempre **la reacción de las víctimas o el testigo** (presos agachándose en el agua, caras hacia arriba, Brady Richard mirando); el tirador **no aparece nunca**, ni lejano. Regla dura en m03 v3; el #7 no se rehace más.
3. **Temas históricos (> 40 años):** elegible = 1 testigo con ≥ 2 citas; R1 agrega `historia_oral|testimonianze|entrevistas` como tipo de fuente prioritario. Re-correr Vajont por la compuerta cuando toque (no ahora).
4. **Grade:** `saturation 0.70`, `grain 6` se queda.
5. **Alucinaciones de imagen** (manos, caras, objetos raros): **no se atacan con más reglas**. Omar las regenera en QA Studio. Lo que sí se ataca: que el pipeline corra entero sin manos.

---

## 1. Por qué F10
La tubería v3 de guion (compuerta → escaleta → guionista → editor → `narration_tts`) existe solo en runners de `lab/`. `fase1_5.py` sigue llamando a `m01a_skeleton` + `m01b_narrator`. Imágenes v3 (`m03_imagenes_v3`, grade) y voz v4 están enganchadas por flag, pero nunca corrieron en una producción real de principio a fin. **F10 = que un topic con pool v3 pase por producción sin pasos a mano, y el resultado sea el primer video completo: Ycuá Bolaños.**

## 2. Contrato de integración (lo que tiene que quedar)
```
topic (pool v3, gate verde/amarillo)
  └─ fase1_5 --v3
       m00  (ya hecho para S1; para seeds nuevos: topic_researcher con RESEARCH_V3=1)
       gate (pool_gate) → verde: 1,500 pal / amarillo: 1,200 / rojo: STOP con motivo
       m01a_escaleta  → escaleta.json (frozen)
       m01b_guionista → párrafos por beat (best_of_2)
       m01c_editor    → texto final + cambios[] + validadores duros
       m01d_particion → chapters[7] con el CONTRATO ACTUAL (chapter_number, role, render_engine,
                        duration_seconds, title, narrative_intent, bullets, narration, ids_usados,
                        narration_tts, humanizer_phrases)   ← lo único nuevo que se escribe en F10
       m05 juez (v3)  → 06_judge_narrative.json
       m02_5 normalizer (sin cambios; lee `narration`)
       audio_manager  → v4 + MS Narrador, lee `narration_tts`; alineación con `narration`
       m07 música (sin cambios)
       m03 v3         → prompts por beat + grade (`_f8` activo porque hay escaleta)
       assemble
  └─ fase2a (DepthFlow/Ken Burns sobre `_graded.png`)   (sin cambios de contrato)
  └─ fase2b --gfx (director + identidad; gfx_question solo respaldo; cita/contador desde pool)
  └─ QA Studio (Omar marca) → regen_marcadas → re-render afectado → final
```
Reglas:
- `fase1_5 --v3` (o `topic["guion_version"]==3`) elige el camino nuevo; sin flag, byte-idéntico a hoy.
- `m01d_particion`: corta en frontera de párrafo por `beat→cap` de la escaleta; respeta `_len_range(role)` ±15 %; si un cap se pasa, mueve el último párrafo del beat al cap siguiente solo si no es el pico y la frase de cierre se mantiene; si no, pide al editor acortar (una llamada corta, misma regla de no agregar). `bullets` = `imagen_sensorial` + `dato_central` del beat.
- `regenerate_caps` v3: regenera un cap con el editor + escaleta + texto vecino, no con el guionista entero.
- Veo en caps 1 y 7 como hoy; `EXPECTED_CHAPTER_COUNT = 7` intacto.
- `pantalla_ids` (reservados) viajan en el skeleton-equivalente para `gfx_pool`.
- Todo lo que hoy lee `skeleton` río abajo (fase2b, gfx_*, audio por intent) debe encontrar los mismos campos: `title`, `narrative_intent`, `cliffhanger`, `pantalla_ids`, `personajes`. Si falta uno, se deriva de la escaleta, no se cambia el consumidor.

## 3. FRENOS
- No tocar: `m02_5`, `tts_normalizer`, `m07`, `fase2a` (salvo leer `_graded.png` si no lo hace ya), `fase2b`, `gfx_*`, `m03_visual` fuera de `m03_imagenes_v3`, `evidence.py`, foto madre, candado, anclas.
- No cambiar el contrato de `chapters`; solo **agregar** `narration_tts` e `ids_usados`.
- Sin merge a `main`. Sin validador de visión.
- Presupuesto del video completo ≈ $12 (research hecho; guion ~$1.5, voz ~$2.5, fotos ~$3.2, Veo ~$0.8, Pro de m03 ~$1). Si algo repite por error, tope $20 y parar.

## 4. Fases y entregas

### 4.1 Integración (3–4 h, Sonnet)
- `fase1_5 --v3` con el contrato de §2; `m01d_particion` + tests (frontera de párrafo, rangos, pico intacto, contrato completo, v2 byte-idéntico sin flag).
- Corrida en seco con **Orleans f7r3** hasta `assemble` sin audio ni imágenes reales (mocks) para validar el contrato; luego `m02_5` real sobre la narración v3 (gate en modo batch).
- Commit.

### 4.2 Ycuá Bolaños — guion (1 h, Opus para leer el resultado, no para programar)
- Topic `f8s1-ycua-bolanos` (pool verde). Correr compuerta → escaleta → guionista → editor → partición → juez. Parámetros vigentes (1,500 palabras, 105 s, 12–14 beats).
- **Notas del analista para la escaleta de S1** (van como indicaciones, no como reglas):
  - Humano: **Blas Cristaldo** (su mañana hora por hora desde las 07:00) o **Liz Torres**; **Tatiana Gabaglio solo como la adulta que recuerda**, nunca descrita como niña en imagen.
  - Antagonista: Juan Pío Paiva y sus hijos; el guardia Daniel Areco como la mano que cerró.
  - Pico: 11:25, la explosión con los portones cerrados (D88, D91, D94).
  - Cierre: la contradicción pericia (3 puertas) vs. testimonios (portones cerrados por los guardias): la pregunta humana que queda.
  - Cifra de muertos: fijar una canónica con fuente ("más de 300" / "396" / "400" según el documento oficial); decirla una vez.
  - Menores: cero imágenes de niños; objetos (zapatos, carritos, la chimenea, el patio de comidas).
- Entregar `lab/hyperframes/f10/ESCALETA_ycua.md`, `NARRACION_ycua.md` (por beat, con `narration_tts` visible), `06_judge`, costo.

### 4.3 **PARADA** — lectura
Commit + `ESTADO_SESION` + mensaje a Omar: "guion de Ycuá Bolaños listo para leer". **No seguir a producción hasta el OK de Omar.** El analista lee del disco y da nota; si < 8, una sola corrida de ajuste con notas; si ≥ 8, OK.

### 4.4 Producción completa (tras el OK; 2–3 h de máquina)
- `fase1_5 --v3` desde `normalizer_gate` en adelante (audio v4 MS Narrador, m07, m03 v3 + grade, assemble) → `fase2a` → `fase2b --gfx` con identidad `misterio` (sparse, Firefox cerrado, RAM libre ≥ 18 GB).
- **B1 del backlog** se aplica antes del render: cortar siempre en `cuts/` aunque la ventana sea 100 % + validador post-render de cuadro congelado (es el bug que arruinó ch05 de Orleans). Son 2 h; entra acá porque el render completo lo necesita.
- Salidas: `output/<video_id>/<video_id>_final_gfx.mp4`, hojas de contactos por cap, `DIRECTOR_TRACE`, `F10_REPORT.md` con: tiempos por fase, costos por fase, sincronía medida (alineación vs. Whisper), palabras/segundo de la voz, nº de imágenes `sensible`, lista de fotos candidatas a regenerar (las que el validador marcó) para QA.
- Abrir **QA Studio** y dejarlo listo para que Omar marque; **no regenerar nada** hasta que marque.

### 4.5 Cierre
Revisor, commit final, `ESTADO_SESION`. Dudas para Omar en el reporte.

## 5. Criterio de éxito
1. Un comando (`fase1_5 --v3 <topic>` + `fase2a` + `fase2b --gfx`) produce el video sin pasos a mano.
2. Guion de Ycuá Bolaños ≥ 8 por lectura del analista y de Omar.
3. Video completo de 11–13 min, voz MS Narrador con pausas del guion, fotos con grade, gfx con identidad, sin cuadro congelado.
4. Omar lo ve entero y decide: publicar (con sus regeneraciones en QA) o qué falta.

## 6. Riesgos
1. Campos del skeleton que gfx/fase2b esperan y la escaleta no trae → derivarlos (§2), no tocar consumidores.
2. Partición que rompa un beat → regla de párrafo + editor acorta.
3. Audio v4 con 7 caps: variación de tono entre caps → stability por intent ya calibrada; medir palabras/s por cap.
4. Render largo (90 fotos + gfx): ~1.5–2 h; Firefox cerrado; B1 antes.
5. Contenido sensible en S1 (menores): reglas de m03 E + notas de §4.2; miniatura sin imágenes `sensible` (H6: cablear si cabe, si no, anotar).

## 7. Prompt de continuación
```
Continuación F10 (modo autónomo con PARADA en §4.3). Leé lab/hyperframes/f10/HANDOFF_F10_integracion_v3.md completo y lab/ESTADO_SESION.md. Rama f10-integracion-v3. Retomá desde el último punto pendiente de §4. Si estás antes de §4.3: seguí hasta la PARADA y esperá a Omar. Si Omar ya dio OK (ESTADO lo dice): producción completa §4.4 y cierre §4.5. Mismas reglas: no preguntar fuera de la PARADA, DECISIONES_F10.md, commit wip antes de compactar, sin merge, sin validador de visión.
```
