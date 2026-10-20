# F4_REPORT — De la identidad del lab a producción

Rama `f3-lab-identidad` · `main` = `43f528a` intacta · modo nocturno (decisiones en `DECISIONES_F4.md`).

---

## §1 Pendientes de F3 + identidad en el perfil — commit `4f05f66`

**Qué hay:**
- `gfx_profiles/misterio.json` = la identidad que guardó Omar a las 01:20 (acento `#c2302f`, golpe suave 1.015, cifras con sello, sello rojo S 84 px, mood 2.5 s, clave `identity`). `chapter_question.enabled` sigue en `false` para el director (la pregunta la hace `gfx_question`, D1).
- Pregunta de cierre: máx 8 palabras, rechaza abstractas, few-shot con «¿Quién fue el culpable?», «¿Qué pasó con los presos del tercer piso?», «¿Por qué nadie abrió las celdas?».
  - ch02 generada: «¿Cómo sucumbieron los generadores de respaldo?» (la de F3 era «¿Cómo el encierro transformó la oscuridad moral de los prisioneros?»). **Activa en ch02: la de Omar, «¿Quién fue el culpable?»** (D7).
  - ch05 generada: «¿Qué justicia lograron Robie y Paul?» → rechazada después por abstracta (revisor) → «¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?».
- 1.1 mood agua ya estaba hecho en F3 (`d4ed4e5`); 1.3 video completo con pausas va en el render de §4 (D8).

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | misterio.json con valores de Omar: acento #c2302f, punch 1.015, anim_figure stamp, emphasis_stamp_px 84, mood_dur 2.5, clave identity | OK | git diff gfx_profiles/misterio.json: los seis valores están. identity trae lab_tokens con los mismos valores. |
| 2 | chapter_question.enabled false | OK | Lectura del JSON: {'enabled': False, 'max_per_cap': 1, ...}. Decisión D1. |
| 3 | gfx_question con few-shot de las 3 preguntas del handoff | OK | FEW_SHOT en script_engine/gfx_question.py, inyectado en build_prompt. Test test_f4_prompt_lleva_few_shot_y_tope_8. |
| 4 | Tope de 8 palabras | OK | MAX_WORDS = 8, token question_max_words_auto: 8 en el perfil, validate() lo aplica. El test rechaza una pregunta de 9 palabras. |
| 5 | Rechazo de abstractas | OK | abstract_words y _ABSTRACT en validate(). Los tests rechazan "transformó... moral" y aceptan "¿Quién apagó los generadores?". |
| 6 | Tests verdes con el comando indicado | OK | Lo corrí: 247 passed in 16.78s. |
| 7 | diag_234_cap4.py NO es parte de esto | OK | Su único cambio es el UUID de TOPIC, no relacionado con F4. Sigue sin commitear: excluirlo del commit. |
| 8 | main = 43f528a | OK | git rev-parse --short main da 43f528a. La rama actual es f3-lab-identidad. |
| 9 | 1.1 (agua sin cáusticas) ya hecho (D5) | OK | Commit d4ed4e5. El test test_moods_sin_patrones_repetidos (test_module_gfx_lab.py:429-436) cubre agua, veneno, muerte y oscuridad con assert "repeating-" not in html. Comentario en gfx_project.py:141. El argumento es cierto. |
| 10 | 1.3 (video completo con pausas) diferido a §4 (D8) | PARCIAL | Coherente con la regla nocturna de un solo render completo, pero no hay evidencia de que se haya hecho: sigue pendiente de verdad. |
| 11 | 1.2: regenerar ch02 y ch05 y pegar en el reporte | PARCIAL | preguntas_f4.json tiene ambas, con 1 intento y sin rechazos. Pero costo es null, así que el gasto de Gemini no está registrado. |

Observaciones:
- La pregunta generada para ch05, "¿Qué justicia lograron Robie y Paul?", se acepta. "Justicia" es abstracta y la raíz "justi" no está en _ABSTRACT: el filtro no cubre todos los casos.
- La pregunta generada para ch02, "¿Cómo sucumbieron los generadores de respaldo?", cumple las reglas. La activa de ch02 sigue siendo la manual de Omar (D7).
- gfx_identity.py se tocó fuera de §1 (sacó chapter_question de ENGINE_BLOCK y agregó la conversión int a float), pero está declarado en D1 y D2.
- Los 8 tests de calibración F2 se ajustaron a los valores nuevos (D4), coherente.
- El respaldo .bak_f3_* del perfil anterior no lo verifiqué.

Fuera de alcance: C:\CLAUDE_PROJECTS\automatization_videos\diag_234_cap4.py (modificado, no relacionado, no debe entrar al commit). Los otros archivos sin trackear son previos y no son de F4.

Riesgos que el contrato no cubre:
- El gasto de Gemini de las preguntas regeneradas no está contabilizado (costo: null) y el tope de F4 es $2.
- El filtro de abstractas por raíces de 5 letras da falsos negativos (ejemplo: "justicia").
- Todo está sin commitear: sin commit no hay punto de retorno antes de §2.
```

**Respuesta de CC:** «justicia» y «libertad» sumadas a las abstractas y ch05 regenerada (D9). Gasto estimado por tokens ≈ US$ 0.002 (D9). Commit hecho.

---

## §2 El director aplica la identidad + PARADA 1 (ch05)

**Qué hay** (`script_engine/gfx_style.py`, token `identity_rules`, decisiones D10–D19):
- El plan dorado de ch02 va como ejemplo en el prompt del director («así se arma un capítulo de este canal»); el director solo elige dónde y qué dato. Las formas las pone el sistema.
- Movimiento por foto, transiciones por tramo, golpes de zoom (máx 4, uno por frase, lejos del pico), reloj solo con 2 horas verificadas, sello del ícono en M.
- Bug arreglado: el render disperso (el del video completo) perdía el nivel de agua, el reloj, el corte a negro y el latido (D17).

**ch05 desde cero, sin tocar nada a mano** (`--only-cap ch05 --gfx --gfx-sparse`, looks; 385 s de capa; segmento 115.0 s = voz + 3 s pregunta + 1 s negro):
- Movimiento: alejar ×2 (apertura y cierre), acercar ×10, 3D ×4 (paisajes), quieta 0.
- Transiciones (15): fundido cruzado ×6, corte ×6, flash ×2, fundido a negro ×1. Violaciones de la identidad: ninguna.
- Bloques: título · dato ×2 («Human Rights Watch», «Templeman III») · contador «500 prisioneros» · mood ×4 (oscuridad, muerte con calavera…) · golpes de zoom ×4 · zoom de detalle + latido en «cuerpos» · pregunta + negro.
- **Pico:** «Cuerpos sin vida a la deriva en la misma agua pútrida…» (76.9 s) → zoom de detalle con latido; salió el recorte de «Templeman III» por la regla de ±5 s.
- **Pregunta generada:** «¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?»
- Sin nivel de agua (no hay cifra de agua dicha en ch05) ni reloj (no hay 2 horas).
- Página de revisión: `output/ba6c3cac…/_fase2b_work/gfx_review_ch05.html` · cues y plan: `lab/hyperframes/f4/ch05/` · hoja de cuadros: `capturas/hoja_ch05_f4.png`.
- **PARADA 1 para Omar:** «¿se parece a lo que armé en ch02?» (modo nocturno: se sigue con §3 y §4 sin esperar).
- Candado sin `--gfx`: md5 de ch02 `--only-cap` = `38e5ba14…` ✔ (`onlycap_ch02_nogfx_f4.log`).

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

Tests corridos por mí: 258 passed (el comando completo del pedido). No corrí fase2b.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 2.1 | Director lee perfil y golden como few-shot en el prompt | OK | gfx_director.py `system_prompt()` + `golden_fewshot()` (gfx_style.py:223). `select_gfx_plan` usa `system_prompt()`. Test `test_few_shot_del_plan_dorado`. |
| 2.1b | El LLM no elige formas | OK | El prompt dice "las formas las pone el sistema". Movimiento, transiciones y golpes salen deterministas de gfx_style. gfx_layer.py:505-517 sobrescribe `punch_in` y `transitions`. |
| 2.2 | Golpes ≤4, 1 por frase, fuera de ±5 s del pico | OK | `select_punches` (gfx_style.py:170). ch05: [19.02, 34.74, 55.4, 71.08], pico 76.94 (el más cercano a 5.86 s). Violaciones [] en el log. |
| 2.2b | Flash ≤2; ≥1 corte cada 3; 1 fundido a negro | OK | Transiciones de ch05: 2 flash, 1 dip (14.4 s), máximo 2 no-corte seguidos, `violaciones []` (log gfx_ch05.log:20). |
| 2.3 | Transiciones solo con --gfx | OK | Solo se escriben en `apply_gfx` (gfx_layer.py:505), detrás de `identity_rules`. `transitions_of` cae a `plan_transitions` si no hay plan. md5 ch02 sin gfx = 38e5ba14… (onlycap_ch02_nogfx_f4.log:39). |
| 2.3b | Reloj solo con ≥2 horas | OK | gfx_peak.py `ticker_min_times`=2 en misterio. Test `test_f4_reloj_solo_con_dos_horas_verificadas`. ch05 sin reloj. |
| 2.3c | Sello del ícono en M | PARCIAL | `icon_stamp_px`=112 en gfx_project.py:216 y gfx_config.py. Los tests solo afirman el valor del token (test_module_gfx_style.py:19), no el HTML. La hoja muestra "CADÁVERES" con calavera, tamaño razonable. |
| 2.4 | ch05 desde cero con identidad: render, página de revisión, cues | OK | gfx_review_ch05.html, gfx_cues_ch05.md/json, plan resolved y hoja_ch05_f4.png existen y no están vacíos. Render "[gfx] ch05 OK en 385s (disperso)", `--only-cap`. Hoja vista: título "CAPÍTULO 5", sello, contador, recorte, ícono, zoom de detalle y pregunta concreta. |
| 2.4b | Pregunta concreta, 8 palabras o menos | OK | «¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?» tiene 6 palabras. Corte a negro de 1 s a continuación. |
| 2.4c | Sin violaciones en ch05 | OK | `identidad: … violaciones []`. |
| Dec. | D10–D19 documentadas | OK | DECISIONES_F4.md, diff de 12 líneas. |

Observaciones (no bloquean):
- En las cues de ch05 todo corte se rotula "corte seco (post-zoom)" (8 de 15 transiciones, `cue_events` en gfx_project.py), aunque solo uno sigue al zoom. Es solo la etiqueta; el plan tiene el `why` correcto.
- El nivel de agua y el reloj no salen en ch05 (sin cifra de agua ni 2 horas). Es coherente con las reglas, pero el pico de ch05 queda sin esos bloques.
- D14: en ch02 el reloj de fecha que Omar aprobó ya no sale. Está declarado y justificado con el handoff §1.1.
- Pasos de §3, §4 y §5 del handoff: no los evalué porque el pedido era solo §2.

Fuera de alcance:
- `diag_234_cap4.py` (cambia TOPIC): no es nuestro, como indicaste; no lo toques en el commit.
- `gfx_lab_server.py` (importa `suggest_movement` de gfx_style) y `gfx_identity.py` (comentario/ruta): son coherentes con D18 y con "una sola fuente".
- Untracked no pedidos: `lab/hyperframes/f4/F4_REPORT.md` y `onlycap_ch02_nogfx_f4.log`.
- No toqué nada fuera de lectura y ejecución de tests.

Riesgos no cubiertos por el contrato:
- Un solo cap (ch05) validó las reglas con render real. El disperso con bloques de pico (D17) solo tiene test unitario; agua y reloj no se vieron en pantalla en F4.
- `DIRECTOR_VERSION` pasó a v1.6 y los 7 caps vuelven a llamar a Flash (costo bajo, dentro del tope de $2).
- El gate de "se parece a ch02" es juicio visual de Omar; ningún test lo cubre.
```

**Respuesta de CC:** la etiqueta de los cortes en las cues ahora muestra el motivo de la identidad («corte (ritmo rápido)», etc.). El nivel de agua en disperso se ve en pantalla en el render completo de §4 (ch02). Gemini §2: 1 llamada del director (ch05) + 0 de visión nuevas (cache) ≈ US$ 0.003.

---

## §3 Golpe de zoom / empuje / corte+golpe sobre clips de video

**Qué se encontró:** la premisa (C64 de F3: «HyperFrames no escala el `<video>`») no se sostiene en el render. Cinco pruebas y dos mediciones sobre renders reales (`lab/hyperframes/f4/s3/README.md`) muestran que el contenedor `#vw` escala el clip: el golpe suave lleva ch01 (Veo) y la escena 3D de ch04 de escala 1.000 a 1.015, y hasta el render de F3 anterior al arreglo ya tenía el zoom acercado. El golpe, el empuje de muerte y el corte + golpe ya escalaban el video.

**Qué cambió:** el zoom de evidencia deja de usar el cuadro congelado en producción (token `zoom_freeze_frame`, false): el clip 3D/Veo sigue moviéndose durante el zoom. El preview del lab lo conserva (no se pudo verificar su player). Test nuevo; 259 verdes.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Que zoom, empuje y corte+golpe escalen también el clip (DepthFlow/Veo) | OK (ya escalaban) | README.md:7-11 y la imagen zoom_sin_congelado_render_snapshot_base.png: el render y el snapshot muestran el clip acercado frente a la base. La medición de ch01 y ch04 lo confirma (fila 3). |
| 2 | Sin congelar el movimiento: scale en el contenedor, no freeze | OK | script_engine/gfx_project.py:575: el cuadro congelado solo se crea si `zoom_freeze_frame`. El default es False (gfx_config.py:243). El preview del lab lo fuerza a True (gfx_lab_server.py:475). |
| 3 | Verificar en ch01 (Veo) y ch04 (3D) | OK | Re-corrí measure_punch_ch01_ch04.py. ch01 pasa de 1.000 a 1.015 y ch04 de 1.000 a 1.015 tras el golpe, igual que el README:21-22. Los logs de render están staged. |
| 4 | Tests | OK | Mi corrida de la suite pedida: 259 passed. Test nuevo `test_f4_zoom_y_golpes_escalan_el_contenedor_del_video` (test_module_gfx_peak.py:173). El test viejo del congelado quedó ajustado a `zoom_freeze_frame=True`. |
| 5 | Decisiones documentadas | OK | DECISIONES_F4.md D20-D22 |

Observaciones:
- **La premisa del handoff se contradice, y la evidencia es sólida pero indirecta.** Las 5 pruebas son de HyperFrames sintético, un clip real de ch05 y un render viejo de ch02. Solo la imagen de ch05 la vi directamente; las otras no las abrí. El cambio real de §3 es sacar el congelado en producción.
- **No hay medición de empuje de muerte ni de corte+golpe sobre un clip real.** El README:24 admite que ch01 y ch04 no los tienen. Se cubren por analogía (mismo `tl.to("#vw…")`) y por el test de HTML. Eso es PARCIAL respecto de "verificar los tres".
- **Zoom de evidencia en ch01/ch04: sin medición.** Solo se midió el golpe suave (1.015), no el zoom 2.2 con el clip en movimiento sobre un clip real de esos caps. La única imagen de zoom sin congelado es de ch05.
- **Diferencia en ch04.** La dif de 17.5 se atribuye a texto encima, sin comprobarlo.
- **No pude verificar la imagen ch02 prefix.** Quedó fuera de mi lectura.

Fuera de alcance: ninguno de los staged. `diag_234_cap4.py` aparece modificado sin staged y no es de este trabajo. Los logs y los probe_vscale*.py staged son evidencia coherente con §3.

Riesgos que el contrato no cubre: el preview del lab sigue con cuadro congelado, así que lo que Omar ve en el lab difiere del render de producción. Falta un render de producción con zoom de evidencia sobre un clip Veo/3D que se vea en movimiento. El diagnóstico C64 de F3 queda desmentido solo para el render, no para el player del navegador.
```

**Respuesta de CC:** el render completo de §4 rehace ch05 sin el congelado: su zoom de evidencia cae en una escena 3D (escena 11), así queda la prueba en producción de un zoom sobre clip en movimiento (se mide en §4). El empuje de muerte y el corte + golpe se buscan en los caps del render completo que los tengan.

---

## §4 Render completo de Orleans con identidad (PARADA 2)

Comando: `python fase2b.py ba6c3cac-a091-41c0-8dad-afd2f4364747 --reuse-visuals --keep-segments --gfx --gfx-sparse` (looks, disperso, sin `--hw-encode`: D19). Log `full_run_f4.log`. Antes: RAM libre 15.4 GB (19.4 GB con Firefox cerrado). Respaldos de F2b/F3 en `_fase2b_work/_bak_f4_pre/` y `_bak_f4_pre_full/`. ch01 y ch04 se reusaron de los renders de §3 (mismo código); los otros 5 caps se rehicieron.

**Entregables** (`output/ba6c3cac…/`):
- `…_final_gfx.mp4`: B-F4, **712.2 s** (video y audio arrancan en 0; audio 712.23).
- `AB_ba6c3cac…_f4.mp4`: A sin gfx | B-F4, 1920×540, 712.2 s, audio de B. A es más corto (sin pausas): se congela al final y se desfasa ~4 s por cap.
- Cues y páginas de revisión de los 7 caps: `lab/hyperframes/f4/corrida_final/` (las `gfx_review_chNN.html` apuntan a los segmentos en `_fase2b_work/`).

### Bloques y formas por cap

| cap | bloques visibles* | datos (+contador) | recortes | mood / bloque de ícono | golpes | zoom | agua | movimiento | transiciones | violaciones | capa gfx s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ch01 | 11 | 2 (+1) | 1 | 1 / 1 | 4 | — | — | (Veo/híbrido: no aplica) | fundido 2 · negro 1 · corte 1 | ninguna | 134.4 |
| ch02 | 14 | 1 | 2 | 3 / 1 | 4 | sí | sí | acercar 9 · 3D 4 · paneo 1 · quieta 1 | fundido 7 · corte 5 · negro 1 · flash 1 | ninguna | 336.3 |
| ch03 | 14 | 3 | 1 | 3 / 0 | 4 | sí | — | acercar 12 · 3D 5 · alejar 1 | fundido 10 · corte 4 · negro 1 · flash 2 | ninguna | 517.6 |
| ch04 | 16 | 3 | 1 | 5 / 3 | 4 | sí | — | acercar 12 · 3D 4 · paneo 1 | fundido 8 · corte 5 · negro 1 · flash 2 | ninguna | 413.2 |
| ch05 | 14 | 3 (+1) | 0 | 3 / 1 | 4 | sí | — | acercar 10 · 3D 4 · alejar 2 | fundido 7 · corte 5 · negro 1 · flash 2 | ninguna | 386.4 |
| ch06 | 13 | 3 (+1) | 1 | 1 / 1 | 4 | sí | — | acercar 9 · 3D 3 · alejar 1 · paneo 1 · quieta 1 | fundido 8 · corte 4 · negro 1 · flash 1 | ninguna | 348.8 |
| ch07 | 11 | 2 | 1 | 3 / 1 | 4 | — | — | (Veo/híbrido: no aplica) | fundido 5 · corte 4 · negro 1 | ninguna | 189.3 |

- Totales de forma: movimiento acercar 52 · 3D 20 · alejar 4 · paneo 3 · quieta 2 (solo fotos con texto); transiciones fundido cruzado 47 · corte 28 · flash 8 · fundido a negro 7.
- \*Bloques visibles = título + datos + contador + recortes + zoom + moods + golpes + agua/reloj/matriz + pregunta (las transiciones no cuentan). «Bloque de ícono» = moods con `icon_callout` (tope 3 por cap); el resto lleva solo sello. Fallbacks: 0. Lint: 0 errores en los 7 caps. Candado literal: 0 rechazados.
- Los 7 caps llegan al tope de 4 golpes de zoom: siempre hay candidatos (el léxico de Orleans es denso).
- ch02 sin alejar: su primera foto es un documento (quieta) y la última, un paisaje (3D); la regla prioriza esas dos.

### Picos y preguntas
- **Picos:** ch02 «sumergidos» (33.7 s) → nivel de agua 4.6 m; ch05 «cuerpos» (76.9 s) → zoom de detalle + latido. En los otros 5 caps ninguna frase tiene palabras de peso 3: sin pico (regla F3).
- **Preguntas de cierre:**
  - ch01 «¿Qué ocultó el huracán Katrina?»
  - ch02 «¿Quién fue el culpable?» (la de Omar)
  - ch03 «¿Cuánto duró el calvario de los prisioneros?»
  - ch04 «¿Qué vieron esos ojos en la oscuridad?»
  - ch05 «¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?»
  - ch06 «¿Cómo la indiferencia sepultó a esos prisioneros?» ← abstracta: «indiferencia» no está en la lista de abstractas (ver deuda)
  - ch07 sin pregunta (último cap).

### §1.3 Video completo con pausas
- Cada cap con pregunta = voz + 3 s de pausa + 1 s de negro (ch02: 97.63 → 101.63). Final B − final A = 23.75 s ≈ 6 caps × 4 s (los segmentos sin gfx traen ~0.04 s de cola de audio que la pausa absorbe). Contra la suma: audios de los caps 687.6 s + 24 s = 711.6 s; segmentos con gfx suman 711.4 s; final 712.2 s (+0.8 s de la unión inicial con el padding del gancho, igual que en A: 688.5 contra 687.6).
- `blackdetect` sobre el final: 6 negros, uno por frontera, de 0.67–0.87 s: el negro visible dura ~0.8 s y no 1 s (el umbral de detección y el fundido de 4 cuadros de cada unión del concat se comen ~0.2 s; queda dentro de los 0.75–1 s del handoff), sin negros fuera de las fronteras (`blackdetect_final_gfx.txt`). Frontera ch02→ch03 vista de cerca: pregunta → negro → título en persiana (`capturas/frontera_ch02_ch03.png`).
- El nivel de agua sale en el final disperso (`capturas/agua_ch02_final.png`): el arreglo D17 funciona.

### §3 en producción
- Zoom de ch05 sobre la escena 3D: con el congelado (render de la PARADA 1) el cuadro quedaba quieto después de acercar (cambio entre cuadros 0.16); ahora el clip sigue moviéndose (1.91).
- Empuje de muerte sobre clip Veo (ch07 «cadáveres», 45.8 s): escala 1.000 → 1.0125 → 1.015.

### Tiempos
| medida | F2b | F4 |
|---|---|---|
| corrida completa | 2272 s (37.9 min) | **2299 s (38.3 min)**, con 5 de 7 capas rehechas |
| capa gfx (5 caps rehechos) | — | 1778 s |
| concat + música | 85 s | **84 s** (66 + 18) |
| incremental | 7.5 min | no medido (regla nocturna: un render completo) |

Las capas tardan más que en F2b (ch03 518 s contra 345 s): con la identidad, 13–15 fotos por cap llevan movimiento sobre el PNG, y el disperso tiene que renderizar esas escenas enteras en HyperFrames.

### Gemini F4
cost_tracker: corrida completa $0.0753 + ch05 $0.0093 + ch01 $0.0080 + ch04 $0.0215 + ch02 sin gfx $0 + preguntas §1 ≈ $0.002 → **≈ US$ 0.12** (tope $2).

- `IDENTIDAD_misterio.md` versionado en `gfx_profiles/` (commit de §2).
- **PARADA 2:** Omar mira `AB_…_f4.mp4` / `…_final_gfx.mp4` y decide el merge (§5). No se mergea sin su OK.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Un solo render completo, looks + disperso | OK | full_run_f4.log: "gfx ON (HyperFrames, looks)", cada cap "(disperso)". full_run_f4.time 02:12:15 a 02:50:34 = 2299 s, coincide con el reporte. |
| 2 | `--hw-encode` solo si PSNR OK | OK | No se usó. DECISIONES_F4 D19: NVENC midió 48.7 dB, menos de 50. Es la lectura conservadora del handoff. |
| 3 | AB_{id}_f4.mp4 (sin gfx / con gfx) | OK | ffprobe: 1920x540, 712.23 s, con audio. El archivo existe (76 MB). A dura 688.49 s y B 712.23 s, así que se desfasan ~4 s por cap. El reporte lo declara. |
| 4 | Cues de los 7 caps + página de revisión | OK | corrida_final/ tiene gfx_cues_ch01..07 (.json y .md) y gfx_review_ch01..07.html. Hay además 2 sobrantes de ch02 (.0b_draft, .pre_calib). |
| 5 | Tabla de formas por cap contra los resolved.json | PARCIAL | Coinciden: movimientos, transiciones, recortes, golpes (4 en todos), zoom, agua, pico, violaciones y rejected = 0. Dos discrepancias abajo. |
| 6 | Picos, preguntas, tiempos, Gemini | OK | Picos ch02 33.7 s y ch05 76.94 s coinciden con los resolved. Capas 336+518+386+349+189 = 1778 s, coincide con los logs. Concat+música 66+18 = 84 s. Gemini ~$0.12 contra tope $2 (suma tomada del reporte, no recalculada). |
| 7 | Veredictos íntegros | OK | F4_REPORT.md líneas 16, 72 y 121 (§1, §2, §3). El veredicto de §4 es este. |
| 8 | IDENTIDAD_misterio.md en gfx_profiles/ versionado | OK | `git ls-files gfx_profiles` lo lista. |
| 9 | §1.3: duración = suma de caps + pausas, sin saltos | PARCIAL | Suma de audios del log 687.6 s + 6×4 = 711.6 s; B = 712.23 s (+0.6 s). El reporte da B−A = 23.75 s ≈ 24, pero no compara contra la suma. blackdetect_final_gfx.txt: 6 negros de 0.67–0.87 s, uno por frontera. La captura frontera_ch02_ch03.png muestra pregunta, negro y título sin salto. |
| 10 | Reglas nocturnas: RAM > 14 GB, Firefox cerrado | NO VERIFICABLE | Solo consta en el reporte (15.4 y 19.4 GB). Faltaría un log de RAM previo. |
| 11 | Gemini tope $2 | OK | ≈$0.12 (cost_tracker del log: $0.0753 en la corrida completa). |

Discrepancias de la tabla (punto 5):
- "Datos": la nota dice "dato + contador", pero ch01, ch05 y ch06 tienen count_up=True además de callouts. Con el contador serían 3, 4 y 4; la tabla pone 2, 3 y 3, que son solo los callouts.
- ch04 "mood / con ícono" dice 5 / 3. En el resolved los 5 énfasis tienen icono; solo 3 tienen icon_callout=True. La cifra 3 es defendible, pero la columna no lo aclara.
- "Bloques" (11, 14, 14, 16, 14, 13, 11) no se pudo reproducir. transitions da 4, 14, 17, 16, 15, 14, 10, y ch03, ch05, ch06 y ch07 no coinciden con la tabla.

Observaciones menores:
- En agua_ch02_final.png el subtítulo dice "4.6 METROS, 0" (parece un artefacto del remap de "o quince pies").
- El reporte no dice que el negro visible es ~0.8 s y no 1 s.

Fuera de alcance: ninguno. Hay `diag_234_cap4.py` modificado, pero ya estaba así en el estado inicial.
Sin commit todavía: F4_REPORT.md modificado, más full_run_f4.log, .time, blackdetect, capturas/ y corrida_final/ (untracked).

Riesgos que el contrato no cubre: el AB tiene A y B desfasados, así que la comparación lado a lado pierde sentido a medida que avanza el video. La pregunta de ch06 usa "indiferencia", abstracta y fuera de la lista (el reporte ya lo anota como deuda). El incremental no se midió, y el handoff lo pide en tiempos.
```

**Respuesta de CC:**
- Tabla: «datos» ahora muestra el contador aparte (ch01, ch05, ch06 +1); «bloques visibles» y «bloque de ícono» quedan definidos debajo de la tabla (las transiciones no cuentan como bloque). Sobrantes de ch02 quitados de `corrida_final/`.
- §1.3: agregada la comparación contra la suma (711.6 s esperado, 712.2 s real: +0.8 s de la unión inicial con el padding del gancho, la misma diferencia que tiene A). Agregado que el negro visible es ~0.8 s.
- RAM/Firefox: medido con PowerShell antes del render (15.4 GB libres; 23 procesos de Firefox cerrados con cierre normal → 19.4 GB); no quedó en un archivo de log.
- «4.6 METROS, 0»: es el subtítulo de la voz («…4.6 metros, o quince pies»), no un texto de gfx; corte de karaoke por palabra.
- Incremental: no medido por la regla nocturna de un solo render completo (el incremental re-ensambla el video). Queda como deuda; el último medido es 7.5 min (F2b).
- AB desfasado: inevitable mientras A no tenga pausas; para comparar un cap, conviene la página de revisión de ese cap.
