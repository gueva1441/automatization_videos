# F8 — Imágenes v3 + cierre de guion + 3 semillas — REPORTE (modo autónomo)

**Rama:** `f8-imagenes-v3` (desde `524573d`, punta de `f7-research-v3`). Sin merge, sin render, sin QA Studio.
**Pedido:** `lab/hyperframes/f8/HANDOFF_F8_imagenes_v3.md` §4. **Decisiones tomadas solo:** `DECISIONES_F8.md` (D1–D23).
**Para mirar primero:** `compara_imagenes_f8.html` (12 pares v2/v3 + la prueba del `/edit`), `humo/hoja_contactos.jpg`, `semillas/SEMILLAS.md`.

## 1. Qué se hizo

### §2 — Cierre de parámetros de guion (commit `a59ab76`)
- Escaleta: **≥ 2 beats por cap de desarrollo** (`video_length`: `min_beats_dev_cap` 2, `max_beats` 12). Como 1 + 2 × 5 + 1 = 12, en verde la escaleta queda en **exactamente 12 beats** (D2: el «10–12» del handoff no cierra). En amarillo sigue 7–8 beats y la regla no aplica (D3).
- **Última frase del video = cita o pregunta, nunca resumen:** blanda al editor (`guion_v3_reglas.closing_soft`, editor `f8-1`, con permiso para tocar solo la última frase sin agregar nada); la regla 8 del guionista y la 17 de la escaleta se reescribieron porque decían lo contrario (D4).
- No se re-corrió Orleans (§2.3). Tests en `test_module_f8.py`; los fixtures de 8 beats de F6 llevan un fixture que deja la regla vieja (D5).

### §1 A–F — Imágenes v3 (commit `73e3613` + arreglos del humo en `c24de5c`)
- **A. Motor:** `PERFIL_SEEDREAM` → `fal-ai/bytedance/seedream/v5/lite/text-to-image`, 2560×1440 fijo, US$ 0.035; el `/edit` de la foto madre sale del mismo id (`…/v5/lite/edit`) y **funciona** (probado en el humo). v5 Lite no acepta `seed`: ya no se manda (D7). Concurrencia `pipeline.fal_concurrency` (20), 3 intentos con backoff exponencial en 429/503 (D9), `ms` por imagen en el meta junto al `endpoint` real (D10). `config.py` (fuera de git) actualizado en local (D8).
- **B. Ancla por beat:** con escaleta, cada imagen hereda el beat del párrafo donde cae su ancla y el prompt de slots recibe «VISUAL SUBJECT PER IMAGE» con la imagen sensorial, la emoción y la intensidad del beat (+ los bullets como contexto). Cada beat ≥ 1 imagen, el pico 2 y una de ellas la más cerrada (se reasigna solo el sujeto; el plan de anclas, `_validate_anchor_substring`, `_reconcile_anchor_timing`, fluidificador, candado, `foto_madre_ref` y `hard_fact_ids` no se tocaron) (D12). Sin escaleta (v2), m03 sale byte-idéntico (test) (D11).
- **C. Estilo:** «Grainy 35mm documentary photograph, <año>, dark-history realism, muted colors, visible film grain, slightly underexposed.» al principio y «35mm film grain, muted documentary colors.» al final; el año sale de las fechas de los datos centrales de los beats (Orleans: 2005).
- **D. Composición (validador determinista + instrucción al director):** motivos racionados por video (máx. 2 salvo que el beat los nombre), manos nunca sujeto ni en plano cerrado, sin macro facial ni los clichés de cara, conteos e izquierda/derecha reescritos en código, ≤ 25 % de humanos en plano medio, ≥ 1 establecimiento por cap (con ≥ 4 imágenes). La doctrina R6 que comparten m03 y m09 enseñaba esos mismos clichés: el camino v3 usa una copia del SI con la R6 reescrita; la constante de m09 no cambió (D13). Orden de arreglo y re-hechuras: D14, D21.
- **E. Sensible:** palabras prohibidas (blood, wound, gore, mutilated, dismembered, soga al cuello), menor en daño, cuerpos ≤ 2 por video y nunca en el cap 1; marca `sensible` por imagen hasta el manifest de asset_manager. Que m09 no elija una imagen sensible como miniatura **no** está cableado (D16).
- **F. Re-encuadre: solo propuesta.** fase2a no arma clips (los arma fase2b, frenado): m03 calcula cuántos planos pide la duración por encima del tope y deja `reencuadres_propuestos` en el cap, inerte (D17). Con caps de 105 s casi nunca se dispara (pide 15–16, tope 16).
- Código nuevo: `script_engine/m03_imagenes_v3.py` (funciones puras). Ganchos en `script_engine/m03_visual.py`; `asset_manager.py`, `engine_profiles.py`, `cost_tracker.py`.

### §1 G — Corrida de humo (commit `c24de5c`)
- 12 imágenes de Orleans f7r3 (8 beats: gancho y pico con 2) → `humo/` (JPG livianos, `humo.json`, `HUMO.md`, hoja de contactos) y `compara_imagenes_f8.html`. PNG completos en `output/ba6c3cac-f7r3/humo_f8/` (fuera de git). Anclas y foto v2 «equivalente»: aproximadas (D20).
- **Medido:** 12/12 OK, 2560×1440, endpoint `…/v5/lite/text-to-image` en las 12; **35–68 s por imagen** en la corrida de 12 (mediana 49 s; el handoff estimaba 33–60; la #1 rehecha sola tardó 87 s) y **68 s de pared con 12 en paralelo**; US$ 0.42 las 12 + 0.035 la rehecha (#1) + 0.035 la prueba del `/edit` (31.7 s). Prompts (Pro + Flash): 56 s; su costo de Gemini **no se midió** (el cost_tracker solo envolvió las imágenes).
- **Auditoría del video (después de la pasada):** 2 pasillos (antes de los arreglos de D21 salían 4), 0 cuerpos, 3 de 12 humanos en plano medio (25 %), ningún cliché de cara en los prompts.
- **A ojo (mío, para que Omar confirme):** las imágenes v3 siguen la imagen sensorial de cada beat (el televisor con el huracán, el fogonazo desde el techo, el paso elevado, la lista con «desconocido», la celda vacía con la marca del agua), donde v2 tenía calendario, generador, una macro de cara y una pareja de turistas. Flojo: varias salen limpias y saturadas (más «película» que foto de archivo: #1, #3, #8); el #8 (pico) parece un videojuego; el #6 muestra un brazo levantado sobre el agua (¿mano como sujeto?); el #10 inventa nombres en la lista («MARIA G.» en una cárcel de hombres).
- El `/edit` conserva la forma del complejo de la foto madre y le agrega la inundación.

### §3 — Tres semillas (commit `c24de5c`)
Corridas en paralelo al principio de la sesión (D18), una vez, sin reintentos. Fichas en `semillas/SEMILLAS.md`; por semilla, `POOL_GATE.md`, fuentes, manifest, perfil, costo y log.

| | S1 Ycuá Bolaños | S2 Cromañón | S3 Vajont |
|---|---|---|---|
| Compuerta | 🟢 verde (214 · 58 · 12 · 49) | 🔴 rojo (67 · 30 · 3 · 22) | 🔴 rojo (0 · 0 · 0 · 0) |
| Costo medido | US$ 1.29 | US$ 0.66 | US$ 0.33 |
| Por qué | — | solo `datos` < 75: un PDF equivocado (el folleto institucional de Perfil en lugar de las pericias), una caída de Pro sin reintento y grounding en 1 de 4 búsquedas | la regla «documento > evento + 20 años» descarta todo lo escrito sobre 1963 después de 1983; además, grounding en 1 de 4 búsquedas |

No elegí ninguna. S2 y S3 quedan en el inbox con la marca `pool_gate` (D23).

## 2. Qué no se hizo / quedó a medias
- Re-encuadre en el render: solo propuesta (fase2b frenado).
- Miniaturas sin sensibles: la marca llega al manifest, m09 no la lee.
- Los caps Veo: la pasada de video no rehace el cuadro 0 del clip (su movimiento ya está escrito).
- La regla de antigüedad del research (Vajont) y el PDF equivocado de R2 (Cromañón): anotados, no tocados (research, fuera de F8).
- La regla de 12 beats exactos no se probó con Pro (§2.3: no se re-corre Orleans): puede subir los reintentos de la escaleta.
- Sin render completo, sin QA Studio, sin merge.

## 3. Costos medidos de la sesión
| tramo | US$ |
|---|---|
| Semillas (research v3 + compuerta, 3) | 2.28 |
| Humo: 12 imágenes + 1 rehecha + 1 `/edit` | 0.49 |
| Gemini de los prompts del humo (4 armadas + 1 rehecha) | no medido (estimado < 0.5) |
| **Total medido** | **2.77** (presupuesto del handoff: < 10) |

## 4. Tests
`test_module_f8.py`: 17 tests (§2: beats por cap, amarillo, cierre; §1: perfil v5, 429/503 con 3 intentos y `ms`, `/edit`, beats y pico, sin escaleta, estilo, composición, auditoría de video, doctrina v3 vs v2 intacta, re-encuadre, render v3 con LLM simulado, cap 1 sin cuerpos, v2 sin cambios, pasada de video). Suites de guion, gfx, m03 y m09: **526 verdes + las 5 fallas previas conocidas** (3 `test_module_01b_pauses`, 2 `test_module_m03_merge_timing`). Fallas previas de otros scripts que no son de F8 (fallan igual en `f7-research-v3`): `test_module_03_plan_anchors.py` (3, el fake no acepta `description`), `test_pr3_calculate_image_count.py` (espera 17–18 fotos y el tope de F7c-2 deja 16), y los que piden topics que ya no están en `topics_db`.

## 5. Dudas para Omar
1. ¿12 beats exactos en verde, o subir `max_beats` a 13–14 para dejar 2 beats en el gancho o en el cierre?
2. Seedream 5.0 Lite: ¿alcanza el estilo «grano y subexpuesto» o hay que endurecerlo? Varias salen limpias y saturadas.
3. ¿Se acepta perder el `seed` determinista por sujeto (v5 Lite no lo tiene)? La consistencia queda en la foto madre.
4. Semillas: S1 está lista para escaleta. ¿Arreglamos el research (regla de antigüedad, PDF enlazado, reintento de R3) y re-corremos S2 y S3?
5. ¿Las reglas C–E también para guiones v2, o solo v3?

## 6. Veredicto del revisor-handoff
(pendiente: se pega íntegro abajo)
