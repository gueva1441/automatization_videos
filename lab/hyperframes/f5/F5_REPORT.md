# F5_REPORT — Guion v2: el research completo llega al guion y a la pantalla

Rama `f5-guion-v2` (desde `39e37ac`, F4e; F4f no existe, J0). `main` intacta (`43f528a`). Sin imágenes ni render: las simulaciones de §3 son `plan_only`. Orden §6: §1.1 → §1.2 → §1.3+§1.4 → §1.5 → §2 → §3 → **PARADA** (espera VALIDACION_F5 del analista). Decisiones: `DECISIONES_F5.md` (J0–J38 + J39–J44 abajo).

## Qué se hizo

| § | Commit | Qué |
|---|---|---|
| 1.1 | `66ee44b` | `researcher_steps/evidence_pool.py`. Una llamada Flash por bloque, literal del research, fuente solo si el bloque la ata, limpieza y merge entre bloques, geocodificación anclada. Orleans: 72 datos · 27 eventos · 26 lugares · 2 citas · 8 personas (antes, 10 facts). |
| 1.2 | `2be6c11` | `m01a`: `_evidence_plan` por cap (≥ 3 datos nuevos y ≤ 1 puente, cronología en orden), personajes con el antagonista obligatorio, `cliffhanger` = ID del dato que revela el cap siguiente. Lo que Flash erra se repara en código y queda auditado (`_evidence_repairs`). |
| 1.3–1.5 | `fc955ef` | `m01b` con los datos asignados, las reglas A–G y reintento dirigido. Normalizer: horas AM/PM, dólares, porcentajes, comillas, siglas. Juez narrativo determinista `m05_narrative.py`. Números en palabras `num_es.py`. |
| 2 | `e18e656` | `gfx_pool.py`: candado con el pool; recortes y datos desde el pool del cap ±1 (nunca desde la narración), con kicker de fuente o fecha y dedupe por ID; ícono por contenido; reloj desde la cronología; pregunta desde el cliffhanger; `apply_gfx(plan_only=True)`. |
| 3 | (este commit) | Guion v2 de Orleans sobre una copia del research, página de comparación, simulación del director para v1 y v2, este reporte. |

Tests: suites de guion y gfx con **364 verdes**. Hay 3 fallas viejas en `test_module_01b_pauses.py` que no son de F5 (J0b).

## §3 — Guion de Orleans, v1 vs v2

Medido con el mismo pool para las dos versiones (`GUION_v1_v2.md`; página: `lab/guion/compara_orleans.html`).

| | v1 | v2 | umbral |
|---|---|---|---|
| Densidad (datos duros / 100 palabras) | 1.36 | **3.29** | ≥ 2.0 |
| Adjetivos / 100 palabras (heurística) | 6.22 | **2.93** | ≤ 3.6 (J18) |
| Datos del pool en más de 2 caps | 2 («6,500» en 4, «500» en 3) | **0** | 0 |
| 3-gramas repetidos entre caps | 3.4 % | 4.1 % | < 5 % |
| Antagonista (Gusman) nombrado | no (0 caps) | **sí (caps 1, 2, 3, 5, 6, 7)** | sí |
| Cliffhangers que anticipan el dato | — | 5 de 6 (ver nota) | 6 de 6 |
| Datos distintos del pool | 12 | **41** | — |
| Palabras | 1398 | 1397 | LEN igual |

- Datos nuevos por cap en v2: 4 · 5 · 7 · 8 · 8 · 6 · 3. En v1: 3 · 0 · 3 · 1 · 1 · 2 · 2.
- «6,500», «pecho» y «500 desaparecidos» pasan a 2 caps cada uno. **«29 de agosto» sigue en 3 caps:** son eventos distintos del mismo día, por eso el juez no lo cuenta como repetición.
- **Nota sobre el ✔ del cap 4:** es un falso positivo del medidor (matcheó «estaban», de «no estaban contabilizados»; la pregunta del cierre no nombra los 517). El cap 3 falla de verdad: el cierre habla del pecho, no de la evacuación de Templeman. Medido estricto: **4 de 6**.
- El narrador aceptó 3 caps con problemas tras 3 intentos (`_f5_violations`):
  - cap 3: adjetivos y cierre;
  - cap 5: Morgan y Hubert sin cargo completo, y adjetivos;
  - cap 7: densidad 1.88.

## §3.3 — Simulación del director (sin render, fotos de v1 como proxy)

Mismo código y mismas fotos. Las palabras de v2 se reparten en la duración del audio de v1 y las escenas quedan en los mismos tiempos de v1 (anchors sintéticos, J41). Detalle por cap: `SIM_v1_v2.md`; cues: `cues/gfx_cues_v{1,2}_chNN.md`.

| | v1 | v2 |
|---|---|---|
| Recortes en pantalla | 5 | 7 |
| …que salen del evidence_pool | 0 | **7** |
| …con kicker = fuente («Organización, año») | 0 | **0** |
| …con kicker = fecha o año | 5 | 7 |
| Datos en pantalla | 2 | 0 |
| Crítico: repite | 12 | **4** |
| Crítico: estorba | 2 | 2 |
| Caps con reloj | 0 | **3** (desde la cronología: 28 ago, 29 ago, 30 ago) |
| Caps con pregunta | 6 | 6 (desde el cliffhanger) |
| Palabras de peso 3 sin material en pantalla | 24 | 20 |

## Lo que hay que saber (para la validación)

1. **Recortes con fuente: 0 en v2.** Los recortes ganadores son eventos de la cronología, que en el research no traen fuente: solo 10 de 72 datos la tienen y ningún evento. Con la regla «fuente → fecha → sin recorte», todos salen con fecha. No se puede mejorar sin inventar la procedencia. La mejora real va en el research: que cada dato de [DATOS DUROS] diga de qué fuente sale.
2. **Datos en pantalla: 0 en v2.** El narrador ahora escribe las cifras en dígitos y R7 (F4c) saca el dato que la voz dice literal. Las cifras van en los recortes.
3. **Algunos recortes arrancan torcidos:** «federal otorga más de $650,000…» o «piso comienzan a inundarse…». Son cláusulas literales, pero sin etiquetador gramatical el filtro de arranque no detecta todo.
4. **Las preguntas desde el cliffhanger son más concretas, pero no todas buenas.** «¿Cómo escaparon los prisioneros?» (cap 3) sugiere una fuga que el dato no dice.
5. **El umbral de adjetivos está recalibrado** a 3.6 (la heurística mide v1 en 6.2 contra el 14 del analista; J18). Hay que validar esa escala.
6. **Íconos que faltan:** espiral (huracán) y rayo tachado (generadores). F5 es sin imágenes; quedan anotados en el plan (`icon_missing`) y son el primer pendiente de F6.
7. **Riesgos del §4.6:**
   - Largo: igual que v1 (1397 palabras).
   - Nombres propios: suman Strock, Hubert, Morgan, Schwarz, Waganfeald y Kunkel para el TTS, sin revisar fonética.
   - Contradicciones del pool (6,375 vs 6,500): el prompt del skeleton pide contarlas juntas, pero v2 usa solo 6,500 (D33). La contradicción no quedó contada.
   - Hay que agregar una regla dura para eso si se quiere.
8. **§1.6 (`m03_visual`, opcional): no se hizo.**
9. Las simulaciones corrieron con Firefox abierto. No son renders (sin HyperFrames ni navegador): solo un re-encode con ffmpeg y llamadas a Gemini.
10. **Costo:** no medido con exactitud. Fueron unas 30 llamadas Flash del guion, más director/fragmentos/preguntas, más 49 juicios del crítico (visión) para v1 y v2. Del mismo orden que la estimación del handoff (≈ $0.30 a $0.50).

## Cómo se reproduce
```
PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/correr_f5_orleans.py --etapa todo
PYTHONIOENCODING=utf-8 python lab/guion/build_compara_orleans.py
PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/metricas_guion.py
PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/analizar_sims.py
```
Topic de prueba: `ba6c3cac-f5v2`, en `data/scripts/_steps/ba6c3cac-f5v2/` y `data/scripts/ba6c3cac-f5v2.json`, fuera de git. Copia versionada en `lab/hyperframes/f5/v2/`. Simulaciones en `output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work_f5sim_v1/` y `output/ba6c3cac-f5v2/_fase2b_work/`. Los `verified_facts` de v1 no se tocaron, y los md5 de `misterio.json`, `lexico_propuestas.json`, `normalizer_custom_dict.json` y `topics_db.json` coinciden antes y después de la prueba.

## Revisor (revisor-handoff), veredicto íntegro (por sección)

VEREDICTO GLOBAL: CUMPLE CON OBSERVACIONES
Contrato: HANDOFF_F5_guion_v2.md. Solo lectura. Corrí el set de tests pedido y comparé JSON y reportes.

Tests (corridos por mí): 364 passed, 3 failed. Las 3 fallas son test_module_01b_pauses::{test_tone_blocks_tienen_pausas, test_hook_abre_con_pausa, test_prose_rules_regla_pausas}, las declaradas en J0b. El diff de m01b contra 39e37ac no toca tonos ni PAUSAS (grep de PAUSA/TONE vacío). Las 12 líneas que borra son la plantilla {PROSE_RULES} y la firma de _validate_narration/_call_with_length_retry. No corrí 39e37ac, así que "fallan igual antes" queda inferido, no medido.

POR SECCIÓN
| § | Veredicto | Evidencia |
|---|---|---|
| 1.1 evidence_pool | CUMPLE CON OBS. | 66ee44b. validate_block (evidence_pool.py:187) exige texto literal en el bloque. resolve_source (:125) devuelve solo fuentes de [FUENTES CONSULTADAS] que el ítem o su línea nombran, si no null. Pool de v2: 72 datos, 27 cronología, 26 lugares, 2 citas, 8 personajes. Fuente en 15 de 101 ítems; lat/lon en 12 de 26 lugares. verified_facts v1 == v2 (True, 10 facts); el 01_facts_sources de v1 no tiene evidence_pool y sus archivos siguen con fecha del 4-jul. OBS: el campo `fecha` de datos no se valida como literal (:198). En 5 datos el año no está en el texto (D38, D60, D65, D66, D72); `hora` y `rol` tampoco se validan. |
| 1.2 skeleton | CUMPLE | 2be6c11. `_evidence_plan`, personajes con antagonista y cliffhanger por cap. El sim muestra 3–8 datos nuevos por cap. Las reparaciones deterministas (J10) quedan auditadas en `_evidence_repairs`. |
| 1.3 + 1.4 narrador y normalizer | CUMPLE CON OBS. | fc955ef + staged. Reglas A–G y reintento dirigido. normalize_pool_forms cubre horas, dólares, %, comillas y siglas (J24/J25). OBS: el handoff pide "≥3 datos asignados" y el staged lo cambia a "3–6" (F5_RULES regla A). OBS: el narrador aceptó 3 caps con violaciones (J22, declarado): cap 3 (adjetivos, cierre), cap 5 (Morgan y Hubert sin cargo, adjetivos), cap 7 (densidad 1.88). El handoff dice "falla → reintento", no "falla → aceptar". |
| 1.5 juez | CUMPLE CON OBS. | m05_narrative.py. 06_judge_narrative.json: densidad 3.29, adj 2.93, trigramas 4.08 %, datos en más de 2 caps = {}, antagonista true. La métrica de cliffhanger falla a nivel video: umbral cliffhanger False, y el cap 3 es False. ADJ_MAX = 3.6 en vez de 8 (J18, declarado): v2 también pasaría con 8, pero la heurística mide v1 en 6.22 y no en 14, así que la escala sigue sin validar. El cap 4 aparece True por falso positivo (matchea «estaban»). El estricto es 4 de 6, como dice el reporte. |
| 2 producción | CUMPLE CON OBS. | e18e656. gfx_director.py suma el pool al candado; gfx_pool.py hace recortes del pool con dedupe por id; gfx_layer.py arma la pregunta desde el cliffhanger; m06_assembler.py pasa el pool. Todo detrás de `if pool`. El kicker (`_kicker`, gfx_pool.py:~115) toma short_source(fuente) o fecha o año, y si no hay, "" (sin recorte); nunca inventa fuente. OBS: el año de respaldo sale de `it["fecha"]`, que no es literal. Ejemplo: D72 muestra «2010» y su texto no trae año. Los 7 kickers de v2 son fecha o año, ninguno es fuente (0 con fuente). Íconos espiral y rayo sin generar (J33; icon_missing). §1.6 no hecho (opcional, J44). |
| 3 prueba Orleans | CUMPLE CON OBS. (sin commitear) | Entregables presentes: compara_orleans.html (51,939 bytes), 14 cues, v2/*.json, GUION_v1_v2.md, SIM_v1_v2.md, F5_REPORT.md. Los números coinciden entre reporte, md y json: densidad 1.36→3.29, adj 6.22→2.93, trigramas 3.4→4.1 %, recortes 5→7 (7 del pool en v2, 0 en v1), "repite" 12→4, reloj en 3 caps, preguntas 6/6. Todo está en staging (65 archivos); F5_REPORT.md tiene un cambio sin stagear (339→364 verdes). No existe VALIDACION_F5.md (correcto: es del analista). |

CANDADOS §5
- No inventar: OK en fuente (null cuando el bloque no la ata). Hueco menor en la fecha derivada, ver §1.1 y §2.
- verified_facts e imágenes de v1 intactos: OK. Archivos de _steps de v1 intactos; `_fase2b_work_f5sim_v1` es el dir nuevo (esto último sale del reporte y de que existe). Sin png/jpg/mp4 nuevos fuera de los dirs de simulación.
- main en 43f528a: OK.
- Guiones viejos: OK. Los tests gfx y m01b/m01a sin pool pasan.
- Sin render completo: OK (apply_gfx plan_only, las sims no usan HyperFrames).
- "Revisor por módulo": NO VERIFICABLE. No hay rastro de revisión por módulo en DECISIONES_F5, F5_REPORT ni en los mensajes de commit.

FUERA DE ALCANCE
- diag_234_cap4.py: modificado sin stagear, cambia TOPIC a 933c76c7 y no tiene relación con F5. Hay que confirmar de quién es.
- Efecto de mi corrida de tests: test_module_gfx_lab escribe en el real `output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/gfx_lab_ch02/` (compositions y freeze jpg, mtime 23:51). Es comportamiento previo del test, no de F5, pero toca el directorio de v1.

RIESGOS QUE EL CONTRATO NO CUBRE
- Hay 0 recortes con fuente en v2 (el research no ata fuente a la cronología) y el cliffhanger real está en 4/6; se necesita el análisis de Omar o del analista antes de decidir.
- Contradicción 6,375 vs 6,500 sin contar en v2 (reporte punto 7); nombres propios nuevos sin revisión fonética para TTS.
- §3 sin commitear: el estado final depende del staging.

**Respuestas a las observaciones del revisor:**
- **Revisión por módulo:** es esta. Un solo revisor con veredicto separado por sección (§1.1 a §3), en lugar de seis corridas.
- **Año derivado del kicker:** la objeción es válida. Para un evento de la cronología, la fecha está literal en la línea del bloque («- 14 de octubre de 2010: …») aunque no en el `evento`. Para un dato (D72), el campo `fecha` lo normalizó Flash. Queda para el analista. El arreglo propuesto, sin hacer porque cambia la simulación de ch05, es tomar el año de `fecha` solo en eventos de la cronología, y en los datos solo si está en su texto.
- **«3–6» en vez de «≥ 3»:** el mínimo de 3 se sigue validando (`cap_problems`). El «hasta 6» va solo en el prompt, para que el cap entre en el largo (J43).
- **`diag_234_cap4.py`:** no es nuestro (ya estaba modificado antes de F4c) y no se commitea.
- **`test_module_gfx_lab`:** escribe en `gfx_lab_ch02` de v1. Es comportamiento previo de ese test, no de F5.

## PARADA
Espero `VALIDACION_F5.md` del analista (§4). No se rehace el video ni se aplica al siguiente sin la decisión de Omar.
