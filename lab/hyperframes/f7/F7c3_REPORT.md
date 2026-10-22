# F7c-3 (reglas de oficio) + F7d (compuerta del pool)

Rama `f7-research-v3` · pedido: HANDOFF_F7 §9 (A: F7c-3, B: F7d). **PARADA: Omar lee la columna F7c-3** de [compara_orleans_v3r.html](compara_orleans_v3r.html) (5 columnas: v2 · F6c · F7c · F7c-2 · F7c-3). Texto: [NARRACION_orleans_v3r3.md](NARRACION_orleans_v3r3.md) · escaleta: [ESCALETA_orleans_v3r3.md](ESCALETA_orleans_v3r3.md).

## A. F7c-3

### Las 7 reglas (`script_engine/guion_v3_reglas.py`, desde `m01b_guionista.review`; prompt del guionista, reglas 16–22)

| # | regla | tipo | cómo |
|---|---|---|---|
| 1 | rol de quien habla = su rol del pool | dura | «la reclusa X» / «X, un preso,» / «un guardia lo describió: «cita»» → clase preso/guardia contra `personajes.rol` y `citas.rol` (`role_problems`) |
| 2 | párrafo sin id = relleno | dura | párrafo con `ids_usados` vacío y más de 2 frases (`empty_paragraph_problems`) |
| 3 | antagonista con nombre | dura | si un beat del cap trae un dato VERIFICADO que lo nombra, la voz dice su apellido; nunca «según alguien» / «una voz oficial» (`antagonist_problems`). Su cita `verificada_parcial` puede ir con nombre si un dato verificado lo nombra (`m01b._verified_antagonist`) |
| 4 | sin fotos en ningún cap | dura | foto/fotografía/fotógrafa/imagen(es)/cámara/retrato en cualquier cap (`photo_problems`) |
| 5 | sin voz de tráiler | dura | 14 patrones («es la historia de», «lo que sigue», «se niegan/negaron a olvidar», «en este video»…) (`trailer_problems`) |
| 6 | ancla de lugar y fecha en el gancho | dura | una frase de ≤ 10 palabras con año y un lugar del pool, antes de la segunda cita; es la única fecha permitida en el cap 1 (`hook_anchor_problems`) |
| 7 | cita fuerte, silencio después | blanda → editor | frase de ≤ 6 palabras justo después de una cita (`echo_soft`); va en el prompt del editor como «cortá estas frases-eco» |

Largo: `video_length` (y el config local) a **110 + 250 × 5 + 140 = 1,500**. Tests: un test por regla en `test_module_f7.py` (41 en total) con los casos de F7c-2 (Ducre, Big Whappy, «Es la historia de… se negaron a olvidar», «las imágenes dieron la vuelta al mundo», «Era la única opción»). Corridas sobre la narración F7c-2: las 7 reglas atrapan todos los errores que nombró el analista.

### La corrida

Notas del analista: las de F7c-2 + «T39 como dato del cap 2» (`NOTAS_F7C3`). Escaleta al 2.º intento (US$ 0.18): humano Reed, pico Q14 (francotiradores, cap 5), gancho Q184 (agua del inodoro). **T39 otra vez no entró** en la escaleta (el cap 2 usa Q08, T55 y Q24), pero la regla 3 en el prompt alcanzó: «El sheriff Gusman rechazó la oferta del Departamento de Correccionales… «Vamos a mantener a nuestros prisioneros donde pertenecen»».

**Dos corridas del guionista.** En la 1.ª (`f7c3_corrida1/`: 1,065 palabras, 26 duras) la regla 6 tenía un bug mío: los nombres de lugar del pool se partían con la puntuación («orleans,») y el ancla «Nueva Orleans, agosto de 2005.» salía como faltante (2 duras falsas en los dos intentos y en el editor). Arreglado junto con dos huecos (rol en aposición «Brady Richard, un preso», que es oficial; «se niegan a olvidar») y re-corrí guionista + editor con la misma escaleta. La que vale es la 2.ª.

| métrica | v2 F5d | F6c | F7c | F7c-2 | **F7c-3** |
|---|---|---|---|---|---|
| palabras | 1,165 | 1,070 | 940 | 1,252 | **1,143** |
| densidad (ids / 100 pal.) | 1.97 | 2.15 | 1.81 | 1.44 | 1.66 |
| datos distintos | 21 | 23 | 17 | 18 | 19 |
| adjetivos / 100 | 2.58 | 2.43 | 1.81 | 1.52 | 1.49 |
| trigramas repetidos | 0.087 | 0.007 | 0.020 | 0.016 | 0.012 |
| cliffhangers | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| citas usadas | 2 | 4 | 9 | 12 | 9 |
| duras de su corrida | — | 4 | 16 | 11 | **21** |
| duras con las reglas de hoy (re-medido) | — | 12 | 29 | 23 | **21** |

Con las mismas reglas (última fila), F7c-3 queda algo mejor que F7c-2 (21 contra 23) y peor que F6c (12).

**Lo que arregló** (contra F7c-2): ningún rol cambiado; sin voz de tráiler; ancla «Nueva Orleans, agosto de 2005.» en el gancho; Gusman con nombre en el cap 2; sin «según alguien»; sin fotos. Ecos: quedan 2 blandas («No habría escape.» después de la cita de Gusman, y una falsa: «El oficial Renard Reed lo resumió.», que presenta la cita siguiente).

**Las 21 duras que quedan:**
- **Largo (5):** los caps 3–7 bajo el mínimo (169–184 palabras contra 212; el cap 7, 108 contra 119). Con 8 beats para 1,500 palabras, el guionista escribe 3 párrafos por cap de desarrollo; pasó lo mismo en F7c-2 con 240 por cap (1,252). El largo de 1,500 no sale solo: propuesta, más beats (10–12) o 4 párrafos mínimos por beat de desarrollo.
- **Párrafo sin dato (5):** los párrafos de atmósfera siguen (cap 1: «la sed se convirtió en una tortura lenta y metódica»).
- **Candado literal (8):** ids declarados que no suenan literales (D545, D550…) y «1» / «2» / «hasta el pecho» repetidos en el cap 4.
- 2 citas en el párrafo del cierre (Reyes y Reed); 2 repeticiones entre caps.

A la lectura, juicios que la lista no ve: «tortura lenta y metódica», «Estaban sellando su destino». Sigue valiendo la propuesta de un juez semántico.

**Costo F7c-3:** escaleta 0.18 + guionista 0.15 + 0.17 + editor 0.18 + 0.15 = **US$ 0.84** (las dos corridas).

## B. F7d — compuerta del pool

- **`researcher_steps/pool_gate.py`:** puntaje determinista (datos, citas verificadas, humanos elegibles, eventos con fecha completa). **Verde** si todo llega al umbral (150 / 8 / 2 / 10); **amarillo** si todo llega a la mitad → `target_words` 1,200 y escaleta de 7–8 beats; **rojo** si algo queda por debajo de la mitad → `PoolGateRed` con los motivos («sin testigos», «sin cronología», «pocas fuentes bajadas», «sin humano que seguir»). Umbrales en `script_engine/video_length.py` (`gate_*`; el config local los puede pisar). `POOL_GATE.md` por topic en sus pasos.
- **Antes de la escaleta:** `m01a_escaleta.generate_escaleta` corre `pool_gate_profile` para pools de research v3 (`_research_v3`); los pools viejos no pasan por la compuerta. Rojo → no llama al LLM. Amarillo → `topic["_largo"]`: palabras por cap escaladas a 1,200 y máximo 8 beats (las reglas de la escaleta pasaron a `rules_text(...)`; `RULES` sigue igual para quien lo importe). **Desvío:** el handoff dice 6–8 beats; el contrato de 7 caps con ≥ 1 beat cada uno pone el piso en 7.
- **RESEARCH_V3=1 por defecto** (`research_v3_enabled`): `topic_researcher._research_seed_deep` corre `research_v3.run_seed` (perfil del seed con 1 Flash: año y nombres del lugar → R1 → R2 + fichas → R3 → R4/R5 → compuerta). 4a–4e siguen igual, alimentados con bloques angulares armados desde el pool (`pool_to_blocks`), sin las 4 búsquedas de resumen; el evidence_pool es el de v3 y el topic lleva `research_version: 3`. **Rojo** → `research_topics` deja el seed en el inbox con `pool_gate` (color, métricas, motivos, fecha). `RESEARCH_V3=0` → el camino viejo, sin cambios.
- **Orleans:** 🟢 verde (558 / 162 / 12 / 127): [POOL_GATE_orleans.md](POOL_GATE_orleans.md).
- **Tests** (`test_module_f7d.py`, 8): tres pools sintéticos (uno por color), el de Orleans (verde), POOL_GATE.md y `PoolGateRed`, umbrales desde `video_length`, escaleta (rojo no llama al LLM, amarillo acorta y pide 7–8 beats, pool viejo sin compuerta), `RESEARCH_V3` por defecto y `=0` al camino viejo, seed rojo que vuelve al inbox con motivo, `pool_to_blocks`.
- **Sin probar de punta a punta:** `run_seed` con un seed nuevo real (red y LLM): los tests usan dobles. Un seed nuevo cuesta ≈ US$ 2.6–2.8 de research (F7b) + la compuerta.

**Tests totales:** 466 verdes en las suites de guion, gfx, research, m01 y m03; siguen las 5 fallas previas fuera de esa lista (3 de `01b_pauses`, 2 de `m03_merge_timing`).

## Archivos

Código: `script_engine/guion_v3_reglas.py`, `m01b_guionista.py` (prompt f7c3-1, `_verified_antagonist`), `m01c_editor.py` (ecos al prompt), `m01a_escaleta.py` (`rules_text`, `_profile`, `pool_gate_profile`), `script_engine/video_length.py` (250/140 y `gate_*`), `researcher_steps/pool_gate.py` (nuevo), `researcher_steps/research_v3.py` (`seed_profile`, `pool_to_blocks`, `run_seed`, default on), `topic_researcher.py` (rama v3, `_flag_seed_in_inbox`). Tests: `test_module_f7.py`, `test_module_f7d.py`. Runner: `f7c_orleans.py --f7c3`; comparación: `build_compara_v3r.py`. Salidas: `compara_orleans_v3r.html`, `f7c_metricas_compara.json`, `NARRACION_orleans_v3r3.md`, `ESCALETA_orleans_v3r3.md`, `escaleta_orleans_v3r3.json`, `f7c3_costos.json`, `f7c3_run.out`, `f7c3_corrida1/`, `f7c2_v1/`, `POOL_GATE_orleans.md`.
