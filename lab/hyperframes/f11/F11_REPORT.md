# F11 — Guion v4: reporte (PARADA)

Rama **`f11-guion-v4`** desde `b8ff4ef` · handoff `lab/hyperframes/f11/HANDOFF_F11_guion_v4.md` · sin merge, sin producción.

**Resultado en una línea:** el v4 baja el prompt a menos de la mitad, cuesta 3 centavos por guionista y no se saltea beats, pero **no cumple el criterio**. Quedan 6, 7, 6 y 7 bloqueantes finales (el tope era 0–2), porque el guionista v4 escribe **450–790 palabras** contra ≈ 1,500. Casi todos los bloqueantes son «cap corto», y la ronda única no los repara: `regenerate_cap_v3` rechaza la prosa nueva con la guardia léxica.

Leer: `compara_v3_v4.html` (teléfono OK), `NARRACION_orleans_v4A.md` / `_v4B.md`, `NARRACION_ycua_v4A.md` / `_v4B.md`.

## Qué se hizo
- `script_engine/guion_v4.py`:
  - `prompt` (encabezado, escaleta por cap con palabras del cap, cada dato con su marca, oficio de 8 líneas exactas, sin `instrucciones_guionista`, sin `ids_usados`);
  - `write` (una llamada a Pro con el `SYSTEM` de m01b; ids calculados con `m05.used_items(…, hard=False)`);
  - `bloqueantes` (a–e, solo con funciones existentes);
  - `reparar` (una ronda: `regenerate_cap_v3` con 1 intento → edición de oración → fechas → editor m01c con criterio «no suben los bloqueantes + guardia léxica»);
  - `replace_repeated_dates` generalizado (día/año de la fecha del evento central, «ese <día de la semana>» por `datetime`);
  - `metricas` (todo `review` + `review_v3` + `cap_review`, tal cual).
- `fase1_5.py`: `--guion v4` (o `guion_version == 4`) → `run_guion_v4` (v4 → reparación → `m01d.particionar` → juez). El camino v3 queda byte-idéntico: un test con `call` falso compara el sha256 de los 6 artefactos medido en `b8ff4ef`.
- `m01d_particion.regenerate_cap_v3`:
  - parámetro `attempts` (por defecto 3, como antes; v4 usa 1);
  - arreglo: si el cap estaba vacío, los párrafos regenerados se perdían; ahora se insertan antes del cap siguiente.
  - El camino v3 no usa esta función.
- Runner `lab/hyperframes/f11/f11_convergencia.py` y html `f11_compara.py`. Salidas:
  - en `_steps/<topic>/`: `01b_guionista_v4{A,B}.json`, `01a_skeleton_v4{A,B}.json`, `01b_narration_v4{A,B}.json`, `01b_narracion_v3_v4{A,B}.json` y `06_judge_narrative_v4{A,B}.json`;
  - en `lab/hyperframes/f11/`: `guion_<tema>_v4{A,B}.json`, `NARRACION_*`, `v3_remedido.json`, `tokens_prompt.json`, `costos_f11.json` y `prompt_<tema>_v4.txt`.
  - No se pisó `_v1`, `_ajuste`, los vigentes de F7c-3 ni `topics_db`.
- Escaletas verificadas por md5 antes de cada corrida: Orleans `2f794418…` (F7c-3) e Ycuá `e1ba1a48…` (v1). Sin notas en ninguna corrida.
- Tests: `test_module_f11.py` (10: bloqueantes a–e, estructura como el ajuste de Ycuá, corridas guardadas, prompt, fechas, cap vacío, una sola ronda, v3 byte-idéntico, ruteo v3/v4). Suite amplia: **564 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`).

## 1. Tokens del prompt y costo

| | prompt v3 (con sistema) | prompt v4 | chars v3 → v4 |
|---|---:|---:|---|
| Orleans | 6,717 | **2,840** (−58 %) | 22,347 → 9,201 |
| Ycuá | 7,938 | **3,387** (−57 %) | 26,743 → 10,608 |

| corrida | US$ | guionista (in / out / thinking) | llamadas | duración |
|---|---:|---|---|---:|
| Orleans A | 0.486 | 2,840 / 886 / 1,526 = US$ 0.028 | 1 guionista, 6 regen, 1 edición, 1 editor, 1 títulos | 441 s |
| Ycuá A | 0.481 | 3,387 / 1,275 / 2,257 = US$ 0.040 | 1, 7 regen, 4 ediciones, 1 editor, 1 títulos | 424 s |
| Orleans B | 0.432 | 2,840 / 872 / 1,872 = US$ 0.031 | 1, 6 regen, 1 edición, 1 editor, 1 títulos | 414 s |
| Ycuá B | 0.594 | 3,387 / 1,274 / 2,631 = US$ 0.043 | 1, 7 regen, 4 ediciones, 1 editor, 1 títulos | 512 s |
| **Tanda** | **1.992** | | | |

El guionista es lo barato: la plata se va en las regeneraciones (6–7 por corrida, US$ 0.025–0.06 cada una, casi todo *thinking*) y en el editor (≈ US$ 0.16). La tanda entró justo en el tope de US$ 2.00. El runner frena antes de una corrida si lo gastado + 0.50 lo pasa; la 4.ª corrida entró con US$ 1.398 gastados.

## 2. Tabla resumen

| tema · versión | bloqueantes | duras v3 re-medidas | palabras | citas («» o "") | humano en N caps | cierre | US$ |
|---|---:|---:|---:|---:|---|---|---:|
| Orleans v3 (F7c-3) | 4 | 22 | 1,143 | 9 | 3 (2, 5, 7) | resumen | — |
| Orleans v4 A | **6** | 36 | 486 | 11 | 3 (2, 5, 7) | resumen | 0.486 |
| Orleans v4 B | **7** | 27 | 450 | 0 (*) | 3 (2, 5, 7) | resumen | 0.432 |
| Ycuá v3 (v1) | 3 | 23 | 1,235 | 12 | 3 (1, 2, 7) | resumen | — |
| Ycuá v4 A | **6** | 33 | 619 | 12 | 3 (1, 2, 7) | resumen | 0.481 |
| Ycuá v4 B | **7** | 43 | 790 | 10 | 3 (1, 2, 7) | resumen | 0.594 |

(*) Orleans B cita con comillas simples ('…'): ni el contador de citas ni `false_quotes` las ven (ver §4).

Criterio del handoff:
- bloqueantes finales 0–2 en las 4 → ❌ (6, 7, 6, 7);
- ningún cap vacío → ✅ (los 4 tienen los 7 caps y todos los beats);
- A y B sin diferencia de bloqueantes > 2 → ✅ (6 vs 7 en los dos temas).

Bloqueantes finales por código:
- Orleans A: 5 c + 1 d.
- Orleans B: 6 c + 1 d.
- Ycuá A: 6 c.
- Ycuá B: 4 c + 2 e + 1 a.

Palabras por cap (final / objetivo):
- Orleans A: 90/110 · 74 · 53 · 38 · 65 · 55 /250 · 111/140.
- Orleans B: 60 · 76 · 43 · 45 · 62 · 50 · 114.
- Ycuá A: 84 · 118 · 99 · 73 · 97 · 103 · 45.
- Ycuá B: 87 · 119 · 85 · 82 · 196 · 100 · 121.

Las «duras v3 re-medidas» de v4 no se comparan 1 a 1 con las de v3. Con ids calculados desaparecen las de «ids declarados no literales», pero suben «el cierre tiene que anticipar el dato del cap siguiente» (4–6 por corrida) y «cada dato una vez por cap».

## 3. Qué reparó la ronda única
- **(a)(e) por edición de oración: funciona.**
  - Ycuá A: las 3 citas SIN VERIFICAR con nombre (e) y las 2 cifras o comillas (a) quedaron en 0, con 4 ediciones aceptadas.
  - Ycuá B: 2 de 4 aceptadas. Una se rechazó por la guardia léxica («nombres nuevos: felicia»: el modelo escribió el nombre completo de Digna Felicia Cáceres para corregir). La otra no bajó los bloqueantes (4 → 4). Quedan 2 e + 1 a en el beat 7–8.
- **(d) Nagin en Orleans: no se reparó en ninguna corrida.**
  - «C. Ray Nagin» está en los descartados del pool como personaje sin acción (`m05.silent_names`), pero la escaleta le da el beat 2 (la evacuación del 28 de agosto) y el v4 lo nombra.
  - La edición se rechazó en A y en B por «tocó otras frases del párrafo»: la guarda que mira que el resto del párrafo quede idéntico.
- **(c) caps cortos: casi no se reparan.**
  - De 26 regeneraciones, pasaron 5 (cap 1 en Orleans A e Ycuá A; caps 1, 5 y 7 en Ycuá B).
  - El resto se rechazó por la guardia léxica de `regenerate_cap_v3`: «adjetivos nuevos» (incluye falsos positivos de la heurística por sufijo: «ante», «perspectiva», «operativo», «siguiente»), «citas nuevas» (el modelo cita literal una cita del pool que el cap no tenía) o «cifras nuevas» («diez»), y en algunos casos por quedar bajo el mínimo (171–186 de 188).
  - Con 1 intento y sin segunda ronda, el cap queda como estaba.
- **Fechas repetidas:** 0 cambios en las 4 (el v4 ya dice la fecha completa una vez).
- **Editor m01c (criterio nuevo):** aceptó 3/8, 6/7, 12/12 y 9/12 párrafos. No subió bloqueantes en ninguna corrida y no los bajó (los cortos no se arreglan acortando).
- Antes → después: Orleans A 7 → 6 · Orleans B 7 → 7 · Ycuá A 12 → 6 · Ycuá B 11 → 7. Ninguna terminó en 0–2: **PARADA** (no hay segunda ronda, tal como pide §1.3).

## 4. Lo que el v4 no ve y v3 sí (honesto), y el caso Q20 / Liz Torres
- **Largo.** El prompt v4 da «N palabras» por cap y nada más (sin objetivo por beat ni por párrafo, como pide §1.1). Pro lo trata como orientativo: un párrafo por beat, 450–790 palabras. Es el problema número uno de la tanda.
  - v3 lo empujaba con «MÍNIMO», «k párrafos de 55–80» y el rechazo. Ninguno de los dos llegaba al objetivo (v3: 1,143 y 1,235), pero v3 quedaba al 76–82 % y v4 al 30–53 %.
  - **No se programó nada** (cero reglas nuevas). Queda para el analista: el largo como dato más visible (total del video, párrafos por beat) o una regeneración de cap sin la guardia de adjetivos.
- **La guardia léxica de `regenerate_cap_v3` no sirve para alargar.** Mide adjetivos, citas y cifras nuevas contra el cap original + los permitidos. Para un cap de 50 palabras que tiene que llegar a 188, casi toda prosa nueva trae «adjetivos nuevos» según la heurística por sufijo.
- **Comillas simples.** Orleans B cita con '…'. Las funciones existentes (`false_quotes`, `quotes_in`, `role_problems` para citas) solo miran «» “” "". Una cita inventada entre comillas simples pasaría el bloqueante (a).
- **Lo que deja de frenar** (antes eran duras y ahora son métricas): cierre que anticipa el cap siguiente, dato asignado usado (mínimo 3), una vez por cap y no en > 2 caps, relleno prohibido («Imaginen», «Imaginá» en el gancho de Orleans A y B), voz de tráiler («Esta es la historia de la orden…», Orleans B), gancho con fecha o cita adelantada, ancla de lugar y fecha, nombre completo una vez por cap, juicios de la lista, fotos, ritmo (frase corta por beat, > 30 palabras, antes del pico), humano en ≥ 3 caps, dato de pantalla dicho en la voz, cifra canónica. Se ven en el html y en `metricas`, pero nada los corrige.
- **El cierre no cambió:** «resumen» en las 4 corridas (y en las dos v3). La línea 8 del oficio no alcanza, y el `cierre` de la escaleta lo empuja al revés: el beat final de Orleans dice «Una verdad que, como el oficial Renard Reed, algunos testigos se niegan a olvidar», y el v4 la copia.
- **Ids calculados.** `ids_usados` = `used_items(texto, pool, hard=False)` por regex sobre todo el pool. Desaparece la contabilidad de ids declarados, pero puede contar choques (un «10» que no es el dato). m03/gfx leen esos ids.
- **Bloqueantes por párrafo.** (a) y (d) se miden por párrafo. Eso evita el falso positivo de v3 en Ycuá v1 cap 3 («de una chimenea…», comillas cruzadas entre dos párrafos), pero no ve problemas que cruzan párrafos.
- **(b) rol: solo distingue preso/guardia** (`role_class`): en Ycuá (sobreviviente, dueño, perito) casi no aplica. Lo declara el handoff.
- **(e) y el humano.** Interpreté «el bloque de `review` (sin la excepción del humano: §1.1)» como: el mismo bloque, salvo cuando el autor de la cita es el humano de la escaleta, porque si no, prompt y bloqueante se contradicen. Se mantiene la excepción vieja del antagonista verificado_parcial.
- **Caso Q20 / Liz Torres.** Q20 («Era como estar dentro de un horno…») es `verificada_parcial` porque en F08 no hay «torres» a ≤ 400 caracteres. La v1 de la escaleta le pedía decirla sin nombre, y Liz Torres es la humana.
  - En v4 la línea dice «— Liz Torres · SIN VERIFICAR», sin «(sin nombre)».
  - Ycuá A: «El ambiente era muy caliente, «como estar dentro de un horno». Escuchó «muchos gritos que luego se fueron apagando».», con Liz nombrada en la oración anterior. Ycuá B no usa Q20.
  - No es bloqueante (excepción §1.1). Igual es una cita de verificación parcial atribuida por nombre: lo decide Omar con el analista (verificar a mano en F08, o sacarle la marca).
- **Lo que queda por decidir** (no se tocó): el largo del v4 y la guardia de la regeneración; Nagin descartado como «sin acción» pero usado por la escaleta (choque pool ↔ escaleta); las comillas simples.

## 5. Veredicto del revisor-handoff

(íntegro; lo dio antes del commit, por eso la fila 13 figura como pendiente: el commit, ESTADO_SESION y este §5 se hicieron después)

VEREDICTO: CUMPLE CON OBSERVACIONES. La implementación y el reporte cumplen el contrato. El criterio de convergencia (§2) NO se cumple, pero el reporte lo dice con honestidad: es la PARADA que el handoff prevé.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Rama f11-guion-v4 desde b8ff4ef | OK | `git log` muestra b8ff4ef como tip. Hay cambios sin commitear. |
| 2 | Guion v4 según §1.1: una llamada, sin best-of ni feedback, 8 líneas de oficio, sin `instrucciones_guionista`, sin `ids_usados`, marcas como dato | OK | `script_engine/guion_v4.py:37-46` (oficio), `:79-106` (marcas), `:165-174` (write: una llamada, ids con `used_items(hard=False)`). |
| 3 | Bloqueantes a–e salen de funciones existentes; ninguna regex ni lista nueva que rechace | OK | `guion_v4.py:222-263` usa `invented_numbers`, `false_quotes`, `role_problems`, `contamination`, y el bloque de `review` copiado en `unverified_named` (`:195-219`). La única regex nueva es la de `replace_repeated_dates` (`:335`), que sustituye y no rechaza. El `re.search` del apellido en (e) replica el bloque de `review`. Tolerancias ±25 %: 0.75/1.25 como en `review`. |
| 4 | Reparación de una ronda (§1.3), con criterio «no sube bloqueantes + guardia léxica» | OK | `reparar` (`:394-444`) y `editor_pass` (`:354-391`). El test `test_reparacion_una_sola_ronda…` pasa. |
| 5 | v3 byte-idéntico (test con `call` falso) | OK | `test_module_f11.py:113`. Corrí `PYTHONIOENCODING=utf-8 python -m pytest test_module_f11.py test_module_f10.py -q`: 23 passed. |
| 6 | Archivos prohibidos de §3 sin tocar | OK | `git diff b8ff4ef --name-only` solo lista `diag_234_cap4.py`, `fase1_5.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json`, `script_engine/m01d_particion.py`. Ningún prohibido aparece. `m01d` no está en la lista prohibida; su cambio (`attempts` y cap vacío) es acotado y el reporte lo declara. |
| 7 | 4 corridas A/B sin notas, con las escaletas fijas | OK | md5 verificados ahora: Orleans `2f794418…` y Ycuá `e1ba1a48…` (`_v1`). El runner los chequea en `f11_convergencia.py:50`. `notas: None`. |
| 8 | No pisar `_v1`, `_ajuste`, F7c-3 ni `topics_db` | OK | Los mtimes de esos archivos son anteriores a F11 (22-oct o 00:09 del 23). Solo hay archivos nuevos `_v4A/_v4B` en `_steps`. `topics_db` no aparece en el diff. |
| 9 | Tope de costo US$ 2.00 | OK, justo | `costos_f11.json`: 0.4856 + 0.4813 + 0.4315 + 0.5939 = 1.9923. No puedo verificar gastos previos fuera de las 4 corridas (pruebas de prompt, etc.). |
| 10 | Entregables: html, NARRACION ×4, guion json ×4, reporte | OK | Todos existen y no están vacíos en `lab/hyperframes/f11/` (`compara_v3_v4.html` 48 KB). No abrí el html para revisar el formato de teléfono ni el color de los marcados. |
| 11 | Números del reporte contra los json | OK | Reconté desde `guion_*_v4*.json`. Palabras, citas, humano en caps, cierre y duras coinciden. Bloqueantes antes → después: 7→6, 7→7, 12→6, 11→7, con los desgloses por código iguales a los del reporte. Regeneraciones: 5 de 26 cambiaron. Ediciones: 4/4 y 2/4. Editor: 3/8, 6/7, 12/12, 9/12. Tokens y costos coinciden con `tokens_prompt.json`. Orleans B con 0 citas lo explica la nota de comillas simples. |
| 12 | Criterio de convergencia (§2): 0–2 bloqueantes, sin cap vacío, A y B con diferencia ≤ 2 | FALLA (reportada) | Bloqueantes finales 6/7/6/7. Sin cap vacío: OK. Diferencia A–B ≤ 2: OK. El reporte lo declara «no cumple» y marca PARADA. |
| 13 | Commit, `ESTADO_SESION` (corregir encabezado `f6-guion-v3`), §5 del reporte | PENDIENTE | Nada está commiteado; los archivos nuevos están sin trackear. `lab/ESTADO_SESION.md` sin diff: el encabezado sigue diciendo `f6-guion-v3`. El §5 del reporte dice «(pendiente)». Son pasos posteriores a este veredicto, pero faltan. |

Fuera de alcance: ninguno. Los modificados de siempre (`diag_234_cap4.py`, `gfx_profiles/*.json`) figuran sin commitear y no deben entrar al commit (§3).

Observaciones:
- El problema de fondo es el largo. v4 escribe 450–790 palabras contra ≈1,500 de objetivo (v3 queda en 1,143–1,235). Los bloqueantes finales son casi todos «cap corto», y la regeneración no los repara por la guardia léxica. El reporte lo documenta; no se programó nada, como exige §3.
- El bloqueante (d) de Nagin (Orleans) queda sin reparar en A y B. El pool lo descarta como personaje sin acción y la escaleta le da el beat 2. Ese choque pool/escaleta no lo cubre el handoff.
- La excepción del humano en (e) (Q20 / Liz Torres) es una interpretación de §1.1 que el reporte declara. La cita sigue siendo `verificada_parcial` y va atribuida por nombre. Lo decide Omar con el analista.

Riesgos que el contrato no cubre:
- Las comillas simples evitan `false_quotes` y `quotes_in`: una cita inventada con ' ' pasaría el bloqueante (a). El reporte lo anota.
- Los `ids_usados` calculados por regex sobre todo el pool alimentan m03/gfx y pueden dar falsos choques numéricos.
- El tope de US$ 2.00 se cumplió con 0.008 de margen; no hay holgura para repetir ninguna corrida.

Nota de CC sobre la fila 9: fuera de las 4 corridas no hubo gasto. Las pruebas del prompt usaron `count_tokens` (gratis) y los tests usan `call` falso.
