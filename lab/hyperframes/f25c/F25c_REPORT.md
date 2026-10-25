# F25c_REPORT — escaleta con Fable por defecto (f25-1), guion v5.4, largo 2,200 · Kyshtym y Vajont

CC · 2026-10-25 · base `187166a`, rama `f11-guion-v4`, sin merge. **Claude US$ 11.4310 de 14.00** (Kyshtym 4.5875 ·
Vajont 6.8435) · **tiempo de pared 1,388 s (23 min)**: la tanda en paralelo tardó 640 s; además, rehacer vE2 llevó 391 s
y el guion de Vajont 357 s (§3).

**En corto.**
- **Los tres cambios de producción están hechos.** Escaleta con Fable por defecto (Sol con `modelo=` /
  `--modelo-escaleta`); prompts f25-1 y v5.4, con un solo cambio cada uno y literales contra su archivo; el tope de
  palabras pasa a métrica, con `max_words` en 2,200. Tests: **868 verdes + las 5 previas**.
- **En la corrida pasó 1 escaleta de 2 en cada tema.**
- **Kyshtym:** kE2 pasó (1·2·2·2·2·2·2) y su guion dio 2,006 palabras, con 1 bloqueante («Q20 está SIN VERIFICAR y va
  con el nombre de Mikhail Kuleshov»).
- **Vajont:** vE2 pasó, pero en la segunda vuelta. La primera la frenó mi reparto del tope en 7 por tema, no el tope de
  14. Su guion dio 2,355 palabras, 0 bloqueantes y 18 citas.
- **El guion copia la promesa de la escaleta tal cual** en la segunda frase (v5.4).
- **Las promesas siguen adelantando:** «durante diecinueve años nadie en el mundo va a saber por qué»; «la presa que
  todos creyeron caída sigue en pie».

## 1. Cambios

| | dónde | qué |
|---|---|---|
| 1 | `m01a_escaleta.py` | `DEFAULT_MODELO_ESCALETA = "claude-fable-5-1"`; `call_escaleta(modelo)`: un claude-* va por `claude_helpers.make_call(modelo, ESFUERZO_POR_ETAPA["escaleta"])` (medium, streaming, 100k), otro modelo por `guion_v4.call_for` (Sol high). `generate_escaleta(…, modelo=None)` y `generate_escaleta_v2(…, modelo=None)`: sin `call`, `call_escaleta(modelo)`. `fase1_5.py --modelo-escaleta {claude-fable-5-1, claude-opus-5-5, gpt-6.1-sol}` → `run_escaleta_v3(modelo=)`. El camino v1 (sin ficha) sigue con Gemini Pro. |
| 1 | prompt escaleta **f24-1 → f25-1** | `PROMPT_ESCALETA_f25_1.md` (archivo md5 `20c72366a258665a1ffcf8f5518e7627`). Bloque SISTEMA md5 **`9325ad3890ebfe241953d86759e20296`** = `SYSTEM_V2` (test byte a byte). La f24-1 queda como `SYSTEM_V2_F24_1` (`006a195f…`). `PROMPT_VERSION_COLUMNA` también pasa a f25-1. |
| 2 | prompt guion **v5.3 → v5.4** | `PROMPT_GUIONISTA_v5_4.md` (archivo md5 `66d828bac271f954bc93b0fa5af1d949`). Bloque md5 **`2f66c1e07e4d6c31178091371821c0c9`** = `SYSTEM_V5_4` = `system()`. `PROMPT_VERSION = "f25-1"`; el v5.3 queda como `system("f23-1")` (`8ca9aa49…`). |
| 3 | `video_length.py` | `max_words` 1700 → **2200**. |
| 3 | `guion_v4.bloqueantes` | Se borró el bloqueante (c) «el video tiene N palabras: el tope es M». Pasa a `metricas["largo"]` = `largo_txt(N)` («largo: N palabras ≈ M min», y «(más que el tope de 2200)» si lo pasa). Los demás bloqueantes, igual. |

Diff de la escaleta (f24-1 → f25-1), la única línea que cambia (`<oficio>` §2, en el medio de la línea):

```diff
- … La promesa es una frase que dice qué va a entender el espectador si se queda. Es una imagen o una pregunta, nunca un resumen de lo que va a pasar ni una lista de lo que viene.
+ … La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede responder todavía. No cuenta lo que va a pasar, no enumera lo que viene, no nombra juicios, comisiones ni consecuencias.
```

Diff del guion (v5.3 → v5.4), `<estructura>` 1:

```diff
- … Primera frase: lo que se ve, sin año, sin cifra, sin institución. Segunda: la promesa. Antes de terminar el cap, …
+ … Primera frase: lo que se ve, sin año, sin cifra, sin institución. Segunda: la promesa, como viene en la escaleta, sin agregarle lo que va a pasar después. Antes de terminar el cap, …
```

**Desvíos:**
- **(a) El tope de 2,200 vive también en `config.py`.** `config.long_video.max_words` pisa al default de
  `video_length`. Lo cambié también ahí, en la copia local (1700 → 2200), y **no se commitea** (regla). En otra máquina,
  hasta que se cambie su `config.py`, sigue en 1700. El tope ya no frena el guion v4, solo cambia el texto de la
  métrica.
- **(b) El camino v3 viejo** (`m01b_guionista.review`) sigue tratando el tope como duro. Ese camino no se usa en v4 y no
  lo toqué.

Tests: `test_module_f25c.py` (5): los dos prompts literales con un solo cambio, Fable por defecto y Sol con `modelo`,
`generate_escaleta` sin `call`, y el largo como métrica. Se adaptaron `f7` (2,200), `f16` (Sol con `modelo=`), `f17`
(columna f25-1), `f22` (`VERSIONES_V5`), `f23` (el v5.3 con su versión) y `f24` (la f24-1 con su versión). **Suite
amplia: 868 verdes + 5 previas.**

## 2. Corrida

- **Entradas:** Kyshtym usa la ficha fS2 de F25a y el pool de F23. Vajont usa la ficha de F24 y el pool de F24.
- **Escaleta:** f25-1 con Fable 5.1, effort medium, `max_tokens` 100 000 en streaming, con esquema (como siempre en la
  escaleta).
- **Guion:** v5.4 con Fable, effort high, 100 000.
- **Paralelo:** un proceso por tema, porque el perfil del caso es un global del proceso. Cada uno con 2 workers, así
  que quedan 4 escaletas a la vez y después 4 guiones a la vez.
- **Ninguna llamada se cortó** (todas `end_turn`).

### Escaletas

| | pasada 1: beats por cap | bloqueantes 1.ª → 2.ª | final | ids · apoyos/beat | humano · antagonista | US$ | s |
|---|---|---|---|---|---|---|---|
| kE1 | — | 1 (antagonista «Mayak (complejo nuclear de Cheliábinsk-40)» no está en la ficha) → 5 (`a_pantalla` D37, D43, D45, D39, D09 repetidos en beats) → **rechazada** | — | — | — | 1.8651 | 351 |
| **kE2** | 1·2·2·2·2·2·2 | 5 → **0** | **1·2·2·2·2·2·2** (14) | 69 · 4.31 | Dubrovsky · Gobierno de la URSS | 1.4066 | 234 |
| vE1 | — | 2 (dato central «P49 (MICAELA COLETTI…)»; antagonista «Società Adriatica di Elettricità (SADE)») → 2 (`a_pantalla` T92, D106) → **rechazada** | — | — | — | 1.9662 | 358 |
| vE2 (1.ª) | — | 6 → **la 2.ª no corrió: freno de mi runner** (gastado 2.824 + reservado 2.215 + peor caso 2.216 > 7.00 de Vajont) | — | — | — | 1.5446 | 326 |
| **vE2** (rehecha) | 1·1·2·2·2·2·2 | 4 → **0** | **1·2·2·2·2·2·2** (14) | 76 · 4.85 | Micaela Coletti · Alberico Biadene | 1.9877 | 387 |

- **El tope de 14 se respetó.** Lo partí en 7 por tema para que cada proceso tuviera su freno, y eso cortó la
  regeneración de vE2 con plata de sobra en el total. Rehice vE2 entera (nueva llamada) con el tope de Vajont = 14 −
  Kyshtym (9.41). La 1.ª vE2 quedó en `_vE2_tope/`.
- **Rechazos repetidos:** los dos son de Fable con los mismos patrones. Antagonistas con paréntesis («… (SADE)», «…
  (complejo…)») que no casan con la ficha, e ids de `a_pantalla` que repite en los beats.

### Guiones

| | escaleta | largo (métrica) | bloqueantes | citas | personas con nombre por cap | US$ | s |
|---|---|---|---|---|---|---|---|
| **gkE2** | kE2 | 2,006 palabras ≈ 16.3 min | 1: (e) «Q20 está SIN VERIFICAR y va con el nombre de Mikhail Kuleshov» (cap 5, beat 9) | 12 | 1 — · 2 Lidia Popova · 3 Dubrovsky, Slavsky · 4 Dubrovsky, Kuleshov · 5 Dubrovsky, Kuleshov · 6 Chelyabinsky Rabochy, L. Smirnova, Demyanovich, Slavsky · 7 Dubrovsky, Chanova, Buldakov, Sociedad Civil, Soviet Supremo, Medvedev | 1.3158 | 271 |
| **gvE2** | vE2 | 2,355 palabras ≈ 19.1 min (más que el tope de 2,200) | **0** | 18 | 1 Trevisano, Coletti · 2 C. Semenza, E. Semenza, Fundación Vajont, Leopold Müller · 3 E. Semenza, Dal Piaz, Volpi, Il Gazzettino, L'Unità, Tina Merlin, Fundación · 4 L'Unità, Lab. Univ. de Padua, Merlin · 5 Biadene, Pancini · 6 Castellano, Onorini, Accamillesi, Celso, Coletti · 7 Biadene, Coppola, Buzzati, Sensidoni, Bocca, Pancini, Coletti, Fundación | 1.3450 | 325 |

- **Palabras por cap:**
  - gkE2: 130 · 296 · 280 · 253 · 282 · 339 · 418.
  - gvE2: 253 · 327 · 281 · 282 · 391 · 406 · 411.
- **Duras de v3 (métrica):** 41 y 42.
- **Personas:** el contador cuenta medios e instituciones como personas.

### Promesa y gancho, textuales

| | promesa de la escaleta | primera frase del gancho | segunda frase del gancho |
|---|---|---|---|
| Kyshtym (kE2 → gkE2) | «Un edificio tiembla en medio de una película, y durante diecinueve años nadie en el mundo va a saber por qué.» | «Una sala a oscuras, una película en la pantalla, filas de sillas de madera.» | «Un edificio tiembla en medio de una película, y durante diecinueve años nadie en el mundo va a saber por qué.» |
| Vajont (vE2 → gvE2) | «Una niña siente que su cama empieza a correr en la oscuridad; a dos kilómetros de ahí, la presa que todos creyeron caída sigue en pie.» | «Hay una casa a oscuras y, dentro de la casa, una cama que ya no está quieta.» | «Una niña siente que su cama empieza a correr en la oscuridad; a dos kilómetros de ahí, la presa que todos creyeron caída sigue en pie.» |

**Lectura:**
- **v5.4 funciona.** El guion copia la promesa palabra por palabra como segunda frase, sin agregarle nada.
- **Las dos promesas siguen siendo una oración con dos mitades.** La de Kyshtym cuenta algo que va a pasar («durante
  diecinueve años nadie en el mundo va a saber por qué»), justo lo que f25-1 dice que no. La de Vajont deja una imagen
  sin cerrar («la presa … sigue en pie»), dentro de la regla.
- **Antes, con f24-1:** en F25a, Fable había dado «Un hombre pide que apaguen una manguera… Lo que le estaban sacando
  del cuerpo, el mundo tardó casi veinte años en saber que existía.» Ahora es una sola oración, pero el adelanto sigue.

## 3. Costo y tiempo

| | llamadas | US$ | pared |
|---|---|---|---|
| escaletas en paralelo (kE1, kE2, vE1, vE2 1.ª) | 7 | 6.7825 | 358 s (4 a la vez) |
| guiones en paralelo (gkE2; el de Vajont no corrió por el choque de nombres de abajo) | 1 | 1.3158 | 278 s |
| **subtotal de la tanda en paralelo** | | | **640 s** |
| vE2 rehecha | 2 | 1.9877 | 391 s |
| gvE2 | 1 | 1.3450 | 357 s |
| **total** | **11** | **11.4310 de 14.00** | **1,388 s** |

- **Error de mi runner:** el primer guion de Vajont no corrió porque el tag `gE2` chocaba con el de Kyshtym (los dos
  salían de «*E2*»). Ya está arreglado: ahora es `g<tag>` (`gkE2`, `gvE2`), y el de Kyshtym se renombró de `gE2` a
  `gkE2`. Adentro, `NARRACION_gkE2.md` todavía dice «gE2» en el encabezado.
- **Respuestas guardadas:** cada respuesta de la API, tal cual, está en `<tag>/respuesta_*.json`.

## 4. Archivos

`lab/hyperframes/f25c/`:
- **Prompts:** `PROMPT_ESCALETA_f25_1.md`, `PROMPT_GUIONISTA_v5_4.md`.
- **Salidas:** `ESCALETA_kE2.md`, `ESCALETA_vE2.md` (kE1 y vE1 rechazadas, sin md), `NARRACION_gkE2.md`,
  `NARRACION_gvE2.md`.
- **Por tag:** `<tag>/resultado.json`, `escaleta.json`, `escaleta_crudos.json`, `respuesta_*.json` y
  `prompt_*.txt` con md5.
- **La vE2 frenada:** `_vE2_tope/`.
- **Costos, tiempos y runner:** `costos_kyshtym.json`, `costos_vajont.json`, `pared.txt`, `f25c_corridas.py`,
  `run_*.log`.

## 5. Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Escaleta v2 con Fable por defecto, Sol con `--modelo` | OK | `m01a_escaleta.py`: `DEFAULT_MODELO_ESCALETA="claude-fable-5-1"` y `call_escaleta(modelo)` (claude-* por `claude_helpers`, otro modelo por `call_for`). `fase1_5.py` tiene `--modelo-escaleta` con gpt-6.1-sol. `test_module_f16/f24/f25c` pasan: 37 verdes. |
| 2 | Prompt escaleta f24-1 → f25-1, un solo cambio, md5 | OK | Diff de `SYSTEM_V2_F24_1` contra `SYSTEM_V2`: una sola línea (`<oficio>` §2), con el texto literal pedido. `SYSTEM_V2_F24_1` es idéntico al `SYSTEM_V2` de HEAD. Bloque md5 9325ad38…; archivo .md md5 20c72366…; el bloque está contenido en el .md. |
| 3 | Prompt guion v5.3 → v5.4, un solo cambio, md5 | OK | Diff `system("f23-1")` contra `system()`: solo `<estructura>` 1, con la frase pedida. Bloque md5 2f66c1e0…; .md 66d828ba…. El reporte coincide. |
| 4 | `max_words` 1700 → 2200 | OK | `video_length.py` (diff de una línea). |
| 5 | Bloqueante (c) pasa a métrica «largo: N palabras ≈ M min», los demás igual | OK | `guion_v4.py`: se borra solo el bloqueante (c). `metricas["largo"]` usa `largo_txt`. Cuentas: 2355 palabras ≈ 19.1 min y 2006 ≈ 16.3 min (a 2.05 palabras/seg). |
| 6 | Corrida: costos, topes y pared | OK | `costos_*.json` suman 4.5875 + 6.8435 = 11.4310, menos que el tope de 14. 11 llamadas, todas `end_turn`, Fable con effort medium (escaleta) y high (guion). Pared: 640 + 391 + 357 = 1388 s (`pared.txt`). Las cifras por tag del reporte coinciden con `resultado.json`. |
| 7 | Por guion: palabras, bloqueantes, citas, personas por cap, promesa y gancho | OK | `resultado.json` coincide con el reporte. gkE2: 2006 palabras, 1 bloqueante, 12 citas. gvE2: 2355 palabras, 0 bloqueantes, 18 citas. La promesa se copia literal como 2.ª frase en los dos. |
| 8 | Entregables en `lab/hyperframes/f25c/` y reporte | PARCIAL | Todo existe. `NARRACION_gkE2.md` todavía dice «gE2» en el encabezado (declarado). La §5 queda en REVISOR_PENDIENTE, lo esperado antes de este veredicto. |
| 9 | No commitear `.env`, `config.py` ni `lab/_gpt_probe_analista/` | OK | `config.py` y `.env` están en .gitignore. `lab/_gpt_probe_analista/` figura sin trackear. |
| 10 | Cero reglas nuevas | OK con matiz | Añadidos fuera de lo pedido: la constante `PALABRAS_POR_SEG` en `guion_v4.py`, la opción `opus-5-5` en `--modelo-escaleta`, y `PROMPT_VERSION_COLUMNA` pasa a f25-1. Ninguno es una regla de generación. |

Desvíos declarados, contrastados:
- **Reparto 7/7:** cierto. `_vE2_tope/resultado.json` muestra la parada «gastado 2.824 + reservado 2.215 + peor caso 2.216 > 7.00». Es un freno de mi runner, no del tope de 14.
- **vE2 rehecha:** cierto, 1.9877 US$ y 387 s. En `resultado.json` figura 3.5323, que suma la primera vE2 más la rehecha.
- **Choque de nombres gE2:** cierto. Hoy los tags son `gkE2` y `gvE2`.
- **`config.py` local:** cierto, ignorado por git. Otra máquina seguiría con 1700 hasta cambiarlo.
- **1 de 2 escaletas por tema:** cierto. kE1 y vE1 fueron rechazadas por `a_pantalla` repetido en beats (más un antagonista con paréntesis en la primera pasada). Por eso hay 2 guiones y no 4. Es una desviación del pedido, y el reporte la dice de frente.

Observaciones:
1. El pedido era «escaleta ×2 → guion de cada una» y solo corrieron 2 guiones. Está declarado y no se corrigió.
2. Por tema, solo pasó 1 de 2 escaletas a la segunda vuelta.
3. gkE2 sale con 1 bloqueante (Q20 sin verificar con nombre propio). El reporte lo muestra.
4. La promesa de Kyshtym sigue adelantando («durante diecinueve años nadie…»), contra lo que dice f25-1. El reporte lo reconoce.
5. El camino v3 viejo (`m01b_guionista`) sigue con el tope duro; está declarado.

Fuera de alcance: `diag_234_cap4.py` y `gfx_profiles/*` aparecen modificados y se anunciaron como ajenos a la tarea. El resto de lo tocado (`m01a_escaleta.py`, `guion_v4.py`, `video_length.py`, `fase1_5.py`, tests `f7/f16/f17/f22/f23/f24`, `test_module_f25c.py`, `lab/hyperframes/f25c/`) está dentro del alcance. Los 5 fallos previos de la suite no los reproduje.

Riesgos que el contrato no cubre:
- El tope de 2200 vive en `config.py`, que no se commitea, así que el default y la máquina de Omar pueden divergir.
- Con el tope convertido en métrica, nada frena un guion que pase de 2200 palabras: gvE2 salió con 2355 y 0 bloqueantes.
- Con n=1 escaleta por tema no se puede concluir que f25-1 mejore la promesa.
