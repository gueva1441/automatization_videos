# F13 — Largo abierto: ¿qué escribe Sol cuando no le exigimos 1,500 palabras? — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (desde `b204868`). Handoff: `HANDOFF_F13_largo_abierto.md`. Solo narración.

**En una línea:** sin cifras de largo, Sol escribe **Orleans en 777 palabras (≈ 6.3 min)**, contra 1,456 (≈ 11.8 min) con el largo objetivo, e **Ycuá en 1,153 (≈ 9.4 min)**, contra 1,425 (≈ 11.6 min). Los bloqueantes no cambian: 1 en Orleans (el Nagin de siempre) y 0 en Ycuá. Costo de la tanda: **US$ 0.109** de 0.50.

Para leer: `compara_f13.html` (objetivo | abierto por cap; se lee en el teléfono), `NARRACION_orleans_f13_abierto.md` y `NARRACION_ycua_f13_abierto.md`.

## 0. Qué se hizo

1. **`script_engine/guion_v4.py`: parámetro `largo`** (`LARGOS = ("objetivo", "abierto")`) en `prompt()`, `escaleta_section()`, `write()` y `bloqueantes()`. Por defecto vale `objetivo`.
   - **`abierto`:**
     - los caps dicen solo «CAP n», sin «≈ N palabras»;
     - en `<tarea>`, la línea del largo se reemplaza por «Cada cap dura lo que su historia necesita: ni relleno ni resumen.»;
     - el bloqueante (c) de cap fuera de ±25 % no se evalúa (siguen beat faltante, cap vacío y el tope `max_words`);
     - `prompt_version("abierto") = "f13-1"`.
     - El sistema y el resto del usuario quedan idénticos.
   - **`objetivo`:** byte-idéntico a `f11c-1`.
     - Verificado con los md5 del prompt real de Orleans (`24c1ce6e…`, el mismo que usó el analista) y de Ycuá (`e7062b6c…`, el de F11c), y con el sistema (`8edea05e…`).
     - En los tests, contra los md5 que da el `guion_v4.py` de `b204868` sobre los fixtures.
   - No se agregó ninguna regla: solo se sacó la línea del largo y el ±25 % cuando el largo es abierto.
2. **Tests** (`test_module_f13.py`, 4, sin red): `objetivo` byte-idéntico a f11c-1; `abierto` sin cifras de largo y con el resto del prompt igual; `write(largo="abierto")` manda el prompt abierto; el (c) de largo se apaga solo con `abierto` (cap vacío y beat faltante siguen). **Suite amplia: 595 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico`, verde.
3. **Corridas** (`f13_corridas.py`): Sol high, una llamada cada una, sin notas, sin reparación ni editor. El tope de salida se calculó por corrida para no pasar los US$ 0.50, y no hay reintento.
   - Orleans `ba6c3cac-f7r3`, `01a_escaleta.json` (md5 2f794418…).
   - Ycuá `f8s1-ycua-bolanos`, `01a_escaleta_v1.json` (md5 e1ba1a48…).
   - Salidas en esta carpeta: `prompt_<tema>_f13.txt` (sistema + usuario, con md5), `guion_<tema>_f13_abierto.json` y `NARRACION_<tema>_f13_abierto.md`.
   - No se escribió en `_steps` ni en `topics_db`.
4. **Referencias con largo objetivo, sin volver a correrlas:**
   - Orleans: `lab/_gpt_probe_analista/orleans/orleans_v4c_sol.json` (corrida del analista; solo lectura, no se commitea).
   - Ycuá: el crudo de `lab/hyperframes/f11c/guion_ycua_v4c_sol.json`.
5. **`compara_f13.html`** (`f13_compara.py`, misma forma que `compara_f11c.html`): por tema, una tabla resumen y, por cap, dos columnas lado a lado (objetivo | abierto) con palabras, segundos, repetición, preguntas, bloqueantes y las frases marcadas en color. Todo se re-midió con el código de hoy; cada versión se midió con su propio largo.

## 1. Tabla resumen

| tema | versión | palabras | **min** (2.05 p/s) | palabras por cap (1–7) | repetición interna | bloq. | duras v3 | citas | preguntas | frases de analista | cierre | US$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Orleans | objetivo (f11c-1) | 1,456 | **11.8** | 98 · 238 · 230 · 245 · 249 · 249 · 147 | 0.6 % | 1 | 35 | 9 | 5 | 0 | cita | 0.061 |
| Orleans | **abierto (f13-1)** | **777** | **6.3** | 96 · 111 · 85 · 93 · 121 · 88 · 183 | 1.1 % | 1 | 33 | 9 | 2 | 0 | cita | 0.045 |
| Ycuá | objetivo (f11c-1) | 1,425 | **11.6** | 102 · 236 · 233 · 238 · 241 · 243 · 132 | 0.3 % | 0 | 17 | 11 | 6 | 0 | cita | 0.114 |
| Ycuá | **abierto (f13-1)** | **1,153** | **9.4** | 110 · 197 · 180 · 183 · 184 · 202 · 97 | 0.0 % | 0 | 22 | 10 | 6 | 0 | cita | 0.064 |

Objetivos de la escaleta (el abierto no los recibió): 110 · 250 × 5 · 140 en los dos temas.

**Lectura de los números** (la nota la da el analista):
- **Orleans se acorta mucho:** los caps de desarrollo bajan de 230–249 a 85–121 palabras. El cap 7 es el único que crece (147 → 183).
- **Ycuá se acorta poco:** los caps de desarrollo quedan en 180–202 palabras, porque la escaleta de Ycuá tiene más datos por beat.
- **Bloqueantes:** iguales en las dos versiones. En Orleans, el único es el (d) de C. Ray Nagin (descartado por el pool y usado por la escaleta), el mismo bloqueante falso de la corrida del analista. Ycuá no tiene ninguno.
- **Humano:** en Orleans, Reed aparece por nombre en los caps 1, 2, 3, 5 y 7 con objetivo, y en los caps 2, 5 y 7 con abierto. En Ycuá, Liz Torres aparece en los caps 1, 2, 5, 6 y 7 en las dos versiones.
- **Duras v3:** son métricas del v3, no bloqueantes del v4, y vienen con dos sesgos contra el abierto:
  - 6 duras de cada abierto son de largo de cap, que mide justamente el largo que se soltó (el objetivo no tiene ninguna). En Orleans son 5 por debajo del mínimo (caps 2–6, «N palabras: el mínimo del cap es 212») y 1 por encima del máximo (cap 7: 183 palabras, máximo 161). En Ycuá, las 6 son de mínimo (caps 2–7);
  - las de «usaste N de los datos asignados (mínimo 3)» quedan casi iguales (3 → 3 en Orleans; 3 → 4 en Ycuá).

  Sin esas 6 duras de largo, el abierto queda en 27 en Orleans (35 en el objetivo) y en 16 en Ycuá (17 en el objetivo).

**Límite de la métrica «repetición interna»:** casi no separa las versiones (0–1 % en promedio; el cap que más da es el 5 de Orleans: 4.2 % con objetivo y 6.7 % con abierto). Mide 3-gramas de contenido que se repiten *literalmente* en dos o más oraciones del mismo cap, y el relleno de Sol es **paráfrasis**, no frases repetidas. Por ejemplo, el cap 3 de Orleans objetivo, el que el analista señaló («repite cuatro veces lo mismo»), da 0 %:
- **Objetivo, cap 3 (230 palabras):** «generadores», «oscuridad», «viento», «gritos», «siguen» y «también» aparecen 3 veces cada una, en cuatro párrafos que cuentan lo mismo (se cortó la luz, gritos entre pabellones, viento, celdas cerradas).
- **Abierto, cap 3 (85 palabras):** ninguna palabra de contenido se repite 3 veces. Son dos párrafos: la falla de los generadores, la oscuridad, el viento, los gritos y el agua que empieza a subir.

Este conteo de palabras es solo una ilustración para el reporte; no lo agregué como métrica. La métrica de 3-gramas quedó tal como pide el handoff.

## 2. Costo y tokens

| corrida | entrada | salida | razonamiento | US$ | segundos |
|---|---|---|---|---|---|
| Orleans abierto | 2,973 | 1,385 | 2,559 | 0.0454 | 108 |
| Ycuá abierto | 3,474 | 1,861 | 3,827 | 0.0638 | 134 |
| **tanda F13** | | | | **0.1092** (tope 0.50) | |

Referencias (no se volvieron a correr):
- Orleans objetivo: US$ 0.061, con 3,027 / 5,476 tokens (entrada / salida, que incluye 3,027 de razonamiento). Que entrada y razonamiento coincidan exactamente es lo que trae el `usage` del JSON del analista, tal como lo devolvió la API: no lo recalculé.
- Ycuá objetivo (guionista F11c): US$ 0.114, con 3,537 / 2,281 / 8,412.

Prompts:
- Sistema: el mismo de F11c (md5 `8edea05e…`).
- Usuario abierto: Orleans `61d3196e…` e Ycuá `6cad43be…`.
- `max_completion_tokens` de cada corrida: 32,000. El peor caso de las dos juntas cabía en el tope.

## 3. Frenos

- No se tocaron `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, el pool ni las escaletas (md5 verificados antes de cada corrida).
- Cero reglas nuevas. Sin merge.
- `.env` y `lab/_gpt_probe_analista/` no se commitean: la referencia de Orleans se lee de ahí, pero no se copia.
- No hubo escaleta nueva, ficha, imágenes, voz ni producción.

## 4. Veredicto del revisor-handoff (íntegro)

Nota de CC, después del veredicto:
- **#12:** lo verifiqué contra `resumen_f13.json`. Orleans abierto tiene **6** duras de largo: 5 de mínimo (caps 2–6) y 1 de máximo (cap 7: «183 palabras: el máximo del cap es 161»). El revisor contó solo las de mínimo, así que el 27 del reporte es correcto. Aclaré el texto de §1 para que lo diga explícito.
- **#13:** los tokens 3,027 / 3,027 están así en el `usage` del JSON del analista; lo aclaré en §2.
- **#11:** agregué lo del cap 5.

VEREDICTO: CUMPLE CON OBSERVACIONES

Todos los frenos del handoff se cumplen. Encontré un error numérico en el reporte (§1, duras de largo) y una incoherencia menor en los tokens de la referencia Orleans. Ninguno afecta el código ni la conclusión.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Parámetro `largo` (objetivo/abierto) en prompt, escaleta_section, write y bloqueantes | OK | `git diff script_engine/guion_v4.py`: `LARGOS`, defaults "objetivo", ValueError si el valor es inválido. |
| 2 | `objetivo` byte-idéntico a f11c-1 | OK | Cargué el `guion_v4.py` de b204868 y el actual con los temas reales. Orleans 24c1ce6e = 24c1ce6e (iguales), Ycuá e7062b6c = e7062b6c, sistema 8edea05e = 8edea05e. Los md5 del reporte coinciden. |
| 3 | `abierto` sin cifras de largo; una frase en `<tarea>` | OK | `prompt_*_f13.txt` tienen 0 «≈». El prompt abierto no contiene «palabras». La frase exacta está en `_largo_line`. Md5 abiertos 61d3196e (Orleans) y 6cad43be (Ycuá), como dice el reporte. |
| 4 | Bloqueante (c) de largo apagado solo con `abierto` | OK | Diff: `elif largo == "abierto": pass`. Cap vacío y beat faltante siguen. Lo cubre `test_bloqueante_de_largo_apagado_solo_con_abierto`. |
| 5 | `PROMPT_VERSION` "f13-1" solo con abierto | OK | `prompt_version()`. |
| 6 | Tests sin red | OK | pytest de f13, f11, f11b, f11c y f12: 49 passed. No re-corrí la suite amplia de 595; el número está en el reporte y en ESTADO_SESION (NO VERIFICABLE por mí, el resto sí). |
| 7 | Corridas Sol high, una llamada, sin notas ni reparación | OK | `corridas.out` y `costos_f13.json`: 2 corridas, sin error, sin reintento. |
| 8 | Tope US$ 0.50 | OK | Total 0.1092 (0.0454 + 0.0638) en `costos_f13.json`, coincide con el reporte. |
| 9 | Tabla (palabras, minutos, palabras por cap, bloqueantes, duras, citas, preguntas, cierre, US$) | OK | `resumen_f13.json` coincide con las 4 filas: 1456/777/1425/1153; 11.8/6.3/11.6/9.4; caps; bloq. 1/1/0/0; duras 35/33/17/22; citas 9/9/11/10; US$ 0.061/0.045/0.114/0.064. Re-corrí `f13_compara.py -I`, que regeneró html y resumen sin llamar a ninguna API. |
| 10 | Costo y tokens de las corridas nuevas | OK | Orleans 2,973 / 1,385 / 2,559 y Ycuá 3,474 / 1,861 / 3,827: coinciden con el resumen. Referencia Ycuá 3,537 / 2,281 / 8,412 también coincide. |
| 11 | Métrica «repetición interna» con `m05._trigrams`, más el límite explicado | OK | Valores 0.6/1.1/0.3/0.0 coinciden con el resumen. El límite es correcto: el cap 3 de Orleans objetivo da 0.0 %, y el relleno es paráfrasis, no 3-gramas literales. Falta decir que por cap el Orleans abierto sube: cap 5 pasa de 4.2 % a 6.7 %. |
| 12 | Texto del reporte sobre duras de largo | FALLA (menor) | El reporte dice «6 duras de cada abierto» son de largo y que sin ellas Orleans queda en 27. En `resumen_f13.json` Orleans abierto tiene 5 (caps 2–6; los caps 1 y 7 no tienen), no 6. Por eso Orleans sin ellas queda en 28, no 27. Ycuá sí tiene 6 (22 → 16, correcto). |
| 13 | Referencia Orleans, tokens | PARCIAL | Reporte y resumen dan 3,027 de entrada y 3,027 de razonamiento. La coincidencia exacta es sospechosa, probablemente un artefacto de cómo se leyó el json del analista. El costo y los demás datos están bien. |
| 14 | No tocar m05, evidence.py, guion_v3_reglas.py, config.py, pool ni escaletas | OK | `git diff` sin cambios en esos archivos. Los md5 de las escaletas se verifican en `f13_corridas.py` (líneas 28–29). Los tracked modificados son `guion_v4.py` y `lab/ESTADO_SESION.md` (más los ajenos). |
| 15 | Sin merge; sin .env ni `lab/_gpt_probe_analista/` en commit | OK (pendiente) | Todavía no hay commit. `lab/_gpt_probe_analista/` figura como `??`: al commitear, no incluirlo con `git add -A`. |
| 16 | `lab/ESTADO_SESION.md` actualizado | OK | Modificado, con la sección F13 y la cifra de 595 + 5. |
| 17 | Entregables en la carpeta, con nombres del contrato | OK | NARRACION_*, guion_*.json, prompt_*, compara_f13.html y F13_REPORT.md existen y no están vacíos. |
| 18 | §4 del reporte: veredicto íntegro | PENDIENTE | Dice «(pendiente)»; se llena con este texto. |

Fuera de alcance: ninguno propio. `diag_234_cap4.py` y `gfx_profiles/*` aparecen modificados, pero el pedido los marca como ajenos a F13 y no deben entrar al commit.

Riesgos que el contrato no cubre:
- La comparación es de una sola muestra por tema y la nota de calidad queda para el analista. Las duras v3 sesgan contra el abierto (mide el mínimo de largo que se soltó).
- La métrica de repetición no detecta paráfrasis, así que no mide el relleno que el handoff quería medir.
- El bloqueante falso de Nagin sigue en las dos versiones de Orleans.
