# F49 — Fotos: S5 de F48 (Opus 5.5 + entrada nueva) contra C2 (Pro), caps 2 y 7 de Wittenoom (lab)

CC, 2026-10-28. Handoff `lab/hyperframes/f49/HANDOFF_F49_fotos_opus_vs_pro.md` (md5 `8bc4a5dd510dfff4650570f6cebd6093` ✓). Rama `f11-guion-v4`.

## Commits
- Paso 0 `c5893e1`: handoff + las dos líneas de DECISIONES 2026-10-28 10:34, tal cual.
- Parte 1 (producción, chascada) `e76d8ed`: `fix_counts_lr` + `test_module_f49.py` + sticker y mapa.
- Parte 2 (lab): commit de este reporte.

## Lecturas declaradas
`CLAUDE.md`, `DECISIONES.md` (hasta las líneas 10:34), `lab/ESTADO_SESION.md` (cabecera, F48 y F47b), el handoff entero, `script_engine/m03_imagenes_v3.py` (`COUNT_RE`, `problems`, `fix_counts_lr`), `test_module_f8.py`, `f46b_corridas.py` (`f8`, `generar_2`, `parte2`, freno), `f46b_hoja.py`, `f47_corridas.py` (`cargar`, `armar_c2`), `f48_corridas.py` (`armar_etapa`, `prompts`), `PROMPTS_F48.json`, `PROMPTS_F47.json`, `f46b/C2.json`, `image_grade.grade`.

## Módulos (paso 2 de /tanda)
| módulo | sticker hoy | después de F49 |
|---|---|---|
| `script_engine/m03_imagenes_v3.py` (producción) | Reglas deterministas de las imágenes v3; `fix_counts_lr` cambia «three inmates» → «a few inmates» y saca izquierda/derecha. | Igual, y el artículo delante de la cifra se va con ella. Solo cambia el md5 del sticker (el texto sigue valiendo). |
| `lab/hyperframes/f49/f49_corridas.py` (nuevo, lab) | — | Re-pasa los prompts por F8, genera las 40 fotos, hojas y costos. Importa `f47_corridas` (y por él `f46b_corridas`). No reusa `f46b_hoja.py` porque esa tiene las columnas fijas del cap 2 de F46b. |

## Parte 1 — chascada (`e76d8ed`)
- `ART_COUNT_RE = \b(?:(the|a|an)\s+)?` + el patrón de `COUNT_RE`. `fix_counts_lr` lo usa para reemplazar; si el artículo iba en mayúscula, la cantidad vaga empieza en mayúscula.
- `COUNT_RE` y `problems()` no cambian.
- Salida:
```
'The two men sit' -> 'A couple of men sit'
'two men sit' -> 'a couple of men sit'
'The three inmates' -> 'A few inmates'
'Three inmates stand on the left of the frame near 6,375 cots.' -> 'a few inmates stand to one side near 6,375 cots.'
'the two of them' -> 'the two of them'
'The exactly three workers rest.' -> 'A few workers rest.'
'Behind them, the two men wait. Five miners talk.' -> 'Behind them, a couple of men wait. Five miners talk.'
'An eleven workers line' -> 'Several workers line'
```
- `test_module_f49.py`: «The two men sit», «two men sit», «The three inmates», «the two men» a mitad de frase, y «The two of them» (no es conteo).
- Suites (`verif_p1/`): rápida + f49 = 56 passed, 3 skipped; amplia = 922 passed, 4 failed (las previas: `m03_merge_timing` ×2 y `gfx_lab` ×2). `mapa --check` 0.

## Parte 2 — fotos

### 1. Prompts re-pasados por F8 (`PROMPTS_F49.json`, `CAMBIOS_F8.md`)
- Para cada prompt de S5 caps 2 y 7 y de C2 cap 7: armado = `" ".join(partes)`. Se vuelve a pasar por `f46b.f8` con la escala del beat y `documented_people` de su canon (`canon_S5.json` / `canon_C.json`).
- Control: con la `fix_counts_lr` previa (copiada de 50c3c42 en el script) el re-pase da los 40 prompts guardados **byte a byte** (assert). Así, lo único que cambia es por la chascada.
- Cambiaron **1 de 40**:

| variante | cap | foto | antes | después |
|---|---|---|---|---|
| S5 | 7 | 7 | «…in a plain shirt. **The a couple of men** sit side by side on Banjima country…» | «…in a plain shirt. **A couple of men** sit side by side on Banjima country…» |

- C2 cap 2 no se re-pasa: son las fotos `_a` ya generadas de F46b, con su prompt de `f46b/C2.json`.

### 2. Fotos
- 40 llamadas a `seedream/v5/lite` con el payload de producción y `num_images` 1, todas encoladas a la vez en un pool de `FLUX_MAX_WORKERS` = 20 (el de producción, como dice el handoff). En vuelo hubo hasta 20 a la vez.
- Freno antes de cada llamada, contando lo que ya está en vuelo. `cost_tracker` con `f49-lab`.
- Cada PNG pasa por `image_grade.grade` de producción → `_graded`. Salen en `f49/S5/` y `f49/C2/` como `chNN_img_MM.png` + `_graded.png` (fuera de git).
- Resultado (`fotos_resultado.json`): **40/40 ok**. **Rechazos del filtro: 0**. `has_nsfw_concepts`: null en las 40. No hubo reintentos.

### 3. Hojas (3840 px de ancho, una cada 4 fotos)
- Cap 2: `hoja_ch02_01-04.jpg`, `hoja_ch02_05-08.jpg`, `hoja_ch02_09-12.jpg`, `hoja_ch02_13-16.jpg`. Columnas **C2 (F46b `_a`) | S5**.
- Cap 7: `hoja_ch07_01-04.jpg`, `hoja_ch07_05-08.jpg`, `hoja_ch07_09-12.jpg`. Columnas **C2 | S5**.
- Rótulo: cap y n.º, año de C2, año de S5, y las primeras 8 palabras del ancla (`narration_anchor` de `03_visual.json`).
- Las 56 celdas tienen foto: no hay ninguna marcada «falta» ni «rechazada».

Año por variante (el mismo que va en la hoja):

| cap | foto | C2 | S5 | ancla (8 palabras) |
|---|---|---|---|---|
| 2 | 1 | 1961 | 1961 | Dieciséis de septiembre de mil novecientos sesenta y |
| 2 | 2–16 | 1962 | 1962 | (las 15 iguales) |
| 7 | 1 | 2023 | 2021 | Los relaves del vertedero de Colonial se van |
| 7 | 2 | 2023 | 2021 | Un informe técnico lo marcó como la fuente |
| 7 | 3 | 2023 | 2021 | la erosión, los lechos de arroyo, las pozas, |
| 7 | 4 | 2023 | 2021 | Fibras azules que el agua deja donde se |
| 7 | 5 | 2021 | 2021 | En dos mil veintiuno, una nota ambiental registró |
| 7 | 6 | 2021 | 2021 | El mismo informe advirtió que, sin intervención, el |
| 7 | 7 | 2023 | 2023 | Es tierra Banjima. En dos mil veintitrés, Marcos |
| 7 | 8 | 2023 | 2023 | «Todavía lloro por mi territorio, pero eso está |
| 7 | 9 | 2024 | 2024 | Maitland Parker murió de mesotelioma en dos mil |
| 7 | 10 | 2024 | 2026 | Dos años después, Gordon Legal presentó en nombre |
| 7 | 11 | 2024 | 2026 | Nadie ha empezado a limpiar. En los accesos |
| 7 | 12 | 2024 | 2026 | El gobierno de Australia Occidental habla de un |

En el cap 2 los años coinciden en las 16 fotos; en el cap 7 difieren en 7 de 12.

### 4. Costos (`COSTOS_F49.md`, cost_history `f49-lab`)
- 1 registro, 40 entradas de Seedream 5.0 Lite a US$ 0,035: **US$ 1,4000** (tope 2,50).
- Llamadas a LLM: 0. Llamadas a fal que no sean las 40 de Seedream: 0.

## Verificación (paso 8 de /tanda)
- Parte 1: suites de arriba y `mapa --check` 0. El hook `suite_rapida` pasó en el commit.
- Parte 2: no toca producción. Las suites de la parte 1 siguen valiendo (`e76d8ed` es el último cambio de producción).
- El candado `fase2b ba6c3cac… --only-cap ch02 --reuse-visuals --sw-encode` no se corrió, porque escribe en `output/`. `fix_counts_lr` corre en m03 (Fase 1.5), y `--reuse-visuals` no pasa por ahí. Es un argumento de código, no una medición.
- `data/`: solo cost_history (`f49-lab`). Nada en `output/` ni en `topics_db`.

## Lo que queda abierto (entero)
- **m1.** Elegir entre C2 y S5 (y pasar S2–S5 a producción) es de Omar y del analista. Esta tanda no elige.
- **m2.** Una foto por prompt y una sola corrida: lo que se vea entre C2 y S5 de una foto puede ser azar del generador. F46b midió que las 2 fotos de un mismo prompt salían casi iguales, pero eso no mide la varianza entre corridas.
- **m3.** En el cap 2, C2 son las fotos `_a` de F46b. Se generaron en otra fecha, con el mismo motor, payload y grade, y con la F8 previa a la chascada. Los 16 prompts C2 del cap 2 (`f46b/C2.json`) no tienen ningún «a couple of», «a few» ni «several», así que la chascada no los cambiaría (medido con grep). En `PROMPTS_F49.json` la única aparición de «The a couple of» es el campo `prompt_f48_f47` (el «antes») de S5 cap 7 foto 7.
- **m4.** Son dos cambios juntos (modelo + entrada), a propósito, como dice el handoff. Si S5 gana o pierde, la foto no dice cuál de los dos lo explica (en texto se midieron por separado en F47b y F48).
- **m5.** El estilo es el fijo de hoy (`style_head` + `STYLE_TAIL`) para todas las épocas, por decisión de Omar del 10:34. El estilo por época queda para otra prueba.
- **m6.** Cap 7: S5 pone 2026 en las fotos 10–12 (C2 2024) y 2021 en las 1–4 (C2 2023). Es la regla de año de S4 (F48); esta tanda no evalúa si está bien.
- **m7.** Abiertos de F48 que siguen: l2, cómo se regenera el canon de S5 (solo `people_groups`, por confirmar); S5 deja 5 fotos con gente sin grupo; candado de ch02 sin correr.
- **m8.** La chascada solo arregla el artículo delante de la cifra. Una cifra al inicio de una oración sin artículo («Three inmates stand») sigue quedando en minúscula («a few inmates stand»). Ya pasaba antes de F49 y no se tocó.
- **m9.** `FLUX_MAX_WORKERS` = 20 limita a 20 las llamadas en vuelo. Las 40 se encolaron juntas, pero no corrieron las 40 a la vez. Es el límite de producción que pide el handoff.
- **m10.** Las hojas JPG (22 MB en total) van al commit, como las de F46b. Las PNG no.

## Procesos y subagentes
- Shells en segundo plano de la tanda: suite amplia y generación de fotos. Las dos terminaron (exit 0); no queda ninguna viva.
- Subagente: `revisor-handoff`, que terminó al devolver el veredicto.
- No se cerró ningún proceso de Omar.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff | OK | `md5sum` da 8bc4a5dd510dfff4650570f6cebd6093 |
| 2 | Paso 0: dos líneas de DECISIONES tal cual, con el handoff en el commit | OK | c5893e1 agrega 2 líneas a `DECISIONES.md` y el handoff. Texto idéntico al handoff, líneas 133-134. |
| 3 | Chascada: `fix_counts_lr` se lleva el artículo | OK | e76d8ed, `script_engine/m03_imagenes_v3.py`: `ART_COUNT_RE`. `COUNT_RE` y `problems` no cambian en el diff. |
| 4 | Test nuevo con «The two men sit», «two men sit» y «The three inmates» | OK | `test_module_f49.py` tiene los tres casos más dos extras. |
| 5 | Suite rápida verde, commit | NO VERIFICABLE por mí | Solo hay logs: `lab/hyperframes/f49/verif_p1/suite_rapida.log` y `suite_amplia.log`. No corrí pytest, por la regla. Dicen 56 pass y 922 pass + 4 previas. |
| 6 | Prompts ya escritos, re-pasados, con tabla de los que cambiaron | OK | `CAMBIOS_F8.md` y `PROMPTS_F49.json` (5 claves). 1 de 40 cambió, S5 cap 7 foto 7, «The a couple of men» → «A couple of men». Coincide con el reporte. |
| 7 | 40 fotos nuevas, 1 por prompt, en paralelo | OK | `S5/` tiene 56 archivos (28 fotos × 2) y `C2/` tiene 24 (12 × 2). `fotos.log` dice «40/40 ok». |
| 8 | Freno antes de cada llamada | OK | `f49_corridas.py:151-152`, `f46b.freno` dentro del lock. |
| 9 | `cost_tracker` con `f49-lab` y tope 2,50 | OK | `data/cost_history.json` tiene 1 registro `f49-lab`, total_cost 1.4 (40 × 0,035). `COSTOS_F49.md` y `fotos.log` coinciden. Es 56 % del tope. |
| 10 | Grade de producción | OK | Hay un `_graded.png` por cada foto. El reporte afirma `image_grade.grade`. |
| 11 | Hojas C2 \| S5, cap 2 con `_a` de F46b | OK | 4 hojas del cap 2 y 3 del cap 7 (28 pares, 4 por hoja). Vi `hoja_ch07_05-08.jpg`: 3840 px, columnas C2 \| S5, rótulo con n.º, años y 8 palabras del ancla. Las `_a` de F46b existen en `lab/hyperframes/f46/f46b/C2/`. |
| 12 | Ninguna llamada a LLM | OK | `grep` en `f49_corridas.py` no muestra clientes LLM. El costo son solo las 40 entradas de Seedream. |
| 13 | Nada en `data/` salvo cost_history, `output/` ni `topics_db` | OK | `git status` no muestra cambios en esas rutas. |
| 14 | PNG fuera de git | PARCIAL | Ninguna PNG está commiteada ni en stage, pero `git check-ignore` da rc=1: no hay regla en `.gitignore`. Si el commit usa `git add lab/hyperframes/f49`, entran ~56 PNG. |
| 15 | `F49_REPORT.md` con lo abierto entero y veredicto íntegro | PARCIAL | Los números del reporte coinciden con los archivos, incluida la tabla de años. «Lo que queda abierto» está (m1–m10). El veredicto es el marcador `{{VEREDICTO}}`, como se esperaba. |
| 16 | `ESTADO_SESION.md` y commit | PENDIENTE | Lo declara el pedido. Va después del veredicto. |
| 17 | PARADA, no elegir variante | OK | El reporte no elige (m1). |

Observaciones:
1. **Marca de tiempo del tope.** `lab/TOPE_TANDA.json` dice `desde 10:45`. El gasto se registró a las 10:39:56 y las fotos a las 10:42. El tope quedó con una hora posterior al gasto, así que un freno que cuente «desde» esa hora no vería esos US$ 1,40. No cambia el resultado (1,40 < 2,50), pero la cifra del tope no es auditable por ese archivo. El archivo está modificado y sin commitear, y se escribió sin salto de línea final, sin formato.
2. **PNG sin ignore.** Ver requisito 14. El riesgo es operativo, al hacer `git add`.
3. **Candado de ch02.** El candado `fase2b … --only-cap ch02` no se corrió. El reporte lo declara (m8) y lo sostiene solo con un argumento de código.
4. **Alcance de la chascada.** La chascada no cubre cifras al inicio de oración sin artículo. Ya está declarado.

Fuera de alcance: ninguno en lo ya commiteado (c5893e1 y e76d8ed tocan solo handoff, DECISIONES, `m03_imagenes_v3.py`, test, sticker/mapa y logs de verificación). Sin commitear, y esperados: `lab/TOPE_TANDA.json` y los artefactos de `lab/hyperframes/f49/`. `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log` figuraban modificados ya en el `git status` inicial; no son de esta tanda y no deben entrar en el commit.

Riesgos que el contrato no cubre: con 1 foto por prompt y una sola corrida, la diferencia C2 vs S5 puede ser azar del generador (m2 del reporte). C2 del cap 2 viene de otra fecha y de otra corrida de F46b. Falta una regla de ignore para las PNG de `lab/hyperframes/f49/`.

### Adenda de CC (después del veredicto)
- **Obs. 1 (tope):**
  - el «desde 10:45» lo escribí mal: el archivo se escribió justo antes de lanzar las fotos, y el registro de `cost_tracker` empezó a las 10:39:56;
  - lo corregí a `{"usd": 2.5, "desde": "2026-10-28T10:39:00"}`, con salto de línea final;
  - el freno de esta tanda no lee ese archivo. Usa `TOPE_USD` = 2,50 en `f49_corridas.py` contra todo el `cost_history` de `f49-lab`, así que no hubo gasto fuera del freno;
  - el archivo sigue fuera de git, como siempre.
- **Obs. 2 / req. 14 (PNG):** el commit va por rutas explícitas. Entran el script, los JSON y MD, los logs y las hojas JPG; ninguna PNG. No agregué una regla en `.gitignore` porque la tanda no la pide.
- **Obs. 3 (candado):** está declarado en «Verificación», no en m8, y sigue abierto.
- **Req. 7:** las 40 se encolaron juntas; el pool de 20 (`FLUX_MAX_WORKERS`, el de producción que pide el handoff) dejó 20 en vuelo a la vez (m9).
