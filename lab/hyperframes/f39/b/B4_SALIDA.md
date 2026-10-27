# B.4 — Salida en texto por paso · `f39-kyshtym`

Corrida única 16:04:16 → 16:45:42 (`_inicio.txt` / `_fin.txt`), `exit=0`, termina en **PARADA del papel**. Log:
`lab/hyperframes/f39/b/corrida.log`. Archivos: `data/scripts/_steps/f39-kyshtym/` (leídos, no tocados). Cada número
lleva su archivo/clave; lo que es estimación o deducción lo dice.

---

## 1. research

**Perfil** (`_perfil.json`):
- años: `anio_evento` 1957 · `anio_inicio` 1957 · `anio_fin` 1957
- `tipo_evento`: **puntual**
- `idiomas_research`: ruso · inglés · español (`idioma_local` Ruso, `cobertura_ingles` true)
- `lugar_principal`: «Asociación de Producción Mayak»; 6 `nombres_lugar` + 7 `nombres_locales`
- el perfil **no trae día ni mes** del evento (solo años).

**Fuentes de R1** (`fuentes_r1.json`, `prompt_version` f7a-1):
- `fuentes`: **7** → en 4 · ru 3 · es 0
- `_descartadas`: 29 → en 18 · ru 9 · es 2 (las 29 con motivo «ninguna URL del grounding se le parece»)
- `_grounding`: 7 URLs · `_focos_grounding` {pro 0, flash 1, sin 3}

**Bajadas y con aporte** (`fuentes.json` `bajada_ok` / `aporte`, `fuentes/manifest.json`):

| idioma | en R1 | bajadas | con aporte | detalle |
|---|---|---|---|---|
| ru | 3 | 3 | 3 | F01 ru.wikipedia (25 datos · 4 citas · 8 personajes), F03 dic.academic.ru (34 · 6 · 9), F07 veteranrosatom.ru PDF «Маяк – наша гордость и боль», 2007 (142 · 19 · 32) |
| en | 4 | 3 | 2 | F05 Cambridge 2021 (8 · 1 · 0), F06 docs-books «Midnight in Chernobyl» (2 · 0 · 0); F04 Grokipedia «Alyoshenka» bajó (3 211 car., `nombra_evento` false) sin aporte; F02 Facebook **no bajó** (original: «texto de 574 caracteres (< 800: ¿paywall o portada?)»; wayback: «sin copia en la Wayback Machine») |
| es | 0 | 0 | 0 | — |
| **total** | **7** | **6** | **5** | |

Pool (`00_pool_v3.json`): `datos` 203 → ru 193 · en 10 (por `idioma`); por documento F07 139 · F03 29 · F01 25 · F05 8 ·
F06 2. `citas` 27 (F07 19 · F01 4 · F03 3 · F05 1), `personajes` 40, `cronologia` 67, `lugares` 17, `_descartados` 61,
`cifras_canonicas` 0.

**`POOL_GATE.md`** (pegado tal cual):

```
# POOL_GATE — `f39-kyshtym`

**🟢 VERDE** · 2026-10-27

| métrica | valor | umbral (verde) | piso (rojo) |
|---|---|---|---|
| datos | 203 ✔ | 150 | 40 |
| citas_verificadas | 22 ✔ | 8 | — |
| elegibles_humano | 11 ✔ | 2 | — |
| eventos_con_fecha | 42 ✔ | 10 | 3 |
| personas_con_nombre | 40 ✔ | — | 2 |

Tubería normal: 12 min (≈ 1,500 palabras).
```

(El log imprime la misma compuerta dos veces, `[escaleta] compuerta del pool: verde {...}`, antes y después de la ficha.)

**Hilos:** `research_v3.WORKERS = 8` (`researcher_steps/research_v3.py:46`; R2 descargas y R3 un documento por hilo).
**Ni el log ni los archivos dicen cuántos hilos se usaron.** Por diseño: R2 ≤ 7 (7 fuentes); R3 = un hilo por texto
distinto → 5 documentos leídos (F01, F03, F05, F06, F07; F04 no tiene `_r3_cache`) → 5 hilos. Los mtimes de `_r3_cache/`
se superponen (F06 16:18:28, F05 16:18:38, F03 16:19:35, F01 16:19:36, F07 16:24:00 con sus 4 partes en fila), lo que
cuadra con R3 en paralelo.

**US$ y tiempo** (`01_v3_costos.json`, paso «research»): **US$ 1.4829 · 1 358.7 s** (≈ 22 min 39 s; log 16:04:18 →
16:26:57). Incluye 4a–4e. Desglose con la tabla «por módulo» de `corrida.log` (suma exacta 1.4829, 37 llamadas):

| módulo | llamadas | US$ |
|---|---|---|
| R1 descubrimiento (Pro) | 16 | 0.4722 |
| R1 descubrimiento (Flash) | 4 | 0.0821 |
| R1 fichas del grounding | 1 | 0.0036 |
| R2 fichas desde el texto | 1 | 0.0124 |
| R3 F07 (4 partes) | 4 | 0.5155 |
| R3 F01 / F03 / F05 / F06 | 4 | 0.1302 / 0.1133 / 0.0356 / 0.0232 |
| research v3 perfil del seed | 1 | 0.0029 |
| research v3 vocabulario del caso | 1 | 0.0088 |
| motor (sin tag) = 4a–4e | 5 | 0.0831 |

Línea de tiempo **estimada por mtimes** (el log no tiene hora por sub-paso): R1 16:04:18 → 16:17:30 (`_r1_cache.json`)
≈ 13 min · R2 descargas 16:17:46–48, `manifest.json` 16:18:11 · R3 16:18:11 → 16:24:00 ≈ 5 min 50 s · R4/R5 +
compuerta → `00_pool_v3.json` 16:24:49 · 4a–4e 16:24:49 → 16:26:57.

## 2. 4a–4e (Flash)

**No se pueden separar en `01_v3_costos.json`: están dentro de «research».** Estimación:
- US$: la línea `motor (sin tag)  5 calls · in 50,151 · out 4,459 · think 22,757 · $0.0831` del resumen por módulo de
  `corrida.log` (5 llamadas = 4a, 4b, 4c, 4d, 4e) → **≈ US$ 0.0831** (estimación).
- tiempo, por mtimes: `00_pool_v3.json` 16:24:49 → `01_facts_sources.json` 16:25:14 (4a) → `02_canonical.json` 16:25:27
  (4b) → `03_meta.json` 16:25:39 (4c) → `04_summary.json` 16:26:25 (4d) → `05_visual_canon.json` 16:26:57 (4e) →
  **≈ 128 s** (estimación).
- El log dice `✓ f39-kyshtym registrado · ... · fuentes: 5 · datos: 12` (esos 5/12 son de 4a/`research_summary`, no del pool).

## 3. ficha (`ficha_caso.json`)

`modelo` gpt-6.1-sol · `esfuerzo` high · `prompt_version` f23-1 · `titulo` «Desastre nuclear Kyshtym Mayak» ·
`pool_md5` b846eeb1529bb861877fb128c89d7f78. (`meta` no existe; los conteos están en `conteos` y `conteos_crudo`.)

| clave | crudo (`conteos_crudo`) | final (`conteos`) |
|---|---|---|
| hechos | 70 | **70** |
| citas | 17 | **16** |
| escenas | 10 | **9** |
| personas | 54 | **54** |
| personas_descartadas | 2 | 1 |
| cifras | 34 | 30 |
| cronologia | 62 | 62 |
| contradicciones | 8 | 7 |
| decisiones | 12 | 11 |
| versiones | 4 | 4 |
| descartados | 24 | 33 |
| humanos_candidatos / giros / pico / pregunta_final | 4 / 6 / 1 / 1 | 4 / 6 / 1 / 1 |

**Sacados: 10** (`sacados`; `chequeo.sacados` por sección: cifras 4 · escenas 1 · contradicciones 1 · decisiones 1 ·
personas_descartadas 1 · citas 1 · descartados 1).
**US$ 0.3956 · 428.1 s** (paso «ficha»; log 16:26:57 → 16:34:05; resumen por módulo `ficha_caso 1 call $0.3956`).

## 4. escaleta (`01a_escaleta.json`)

`prompt_version` f26-1 · modelo claude-fable-5-1 (resumen por modelo: Fable 4 llamadas = escaleta 1 + guionista 1 +
editar frase 2). No hay `01a_escaleta_rechazada*.json`.

- **Intentos: 1** (`_intentos`). Intento 1: **0 bloqueantes**, 9 reparaciones, 13 no bloqueantes (log: «intento 1: 0
  bloqueante(s) [] · 9 reparación(es) · 13 a métricas»).
- `_reparaciones` (9): «beat 9: apoyo L09 no existe en el pool → fuera»; «a_pantalla D18: cap 6 inválido o lleno → fuera»;
  «a_pantalla D43: cap 6 inválido o lleno → fuera»; y 6 recortes de palabras objetivo por cap (cap 1 220→110, cap 2
  500→250, cap 4 520→250, cap 5 550→250, cap 6 560→250, cap 7 500→140).
- `_avisos`: [] (vacío).
- **Humano:** P43 Anatoly Ivanovich Valevich (fuente F07). En la ficha está en `historia.humanos_candidatos` y también en
  `personas_descartadas`. `_metricas.humano_en_escena_caps` [1, 2, 4, 6, 7], `humano_entra_cap` 1.
- **Antagonista:** `institucion`, D01 «Complejo químico Mayak». `_metricas.antagonista_caps` [].
- **Pico:** **beat 5** (cap 4), id T28; `_metricas.pico_es_el_de_la_ficha` true.
- Beats: 12 (por cap 1, 2, 1, 2, 2, 2, 2); curva de intensidad [4, 1, 2, 3, 5, 2, 4, 4, 3, 4, 3, 3].
- **`a_pantalla`: 5** (D03 cap 1, D17 cap 4, D20 cap 6, D90 cap 6, D83 cap 7). En `caps[].pantalla_ids` hay **12** en
  total (1, 1, 2, 2, 2, 2, 2) con lo que suma el plan del pool; `_pantalla_por_fecha` mueve 2 y saca 5 (cap lleno o
  repetido).
- No bloqueantes (13, `_intentos[0].no_bloqueantes`): cap 3 con menos de 2 beats; falta beat de intensidad 1 después del
  pico; beat 5 con Valevich en escena sin dato suyo verificado; imagen del gancho sin cifras; la última frase no nombra
  al humano; la última frase repite textual Q18; falta la pregunta de pantalla en los 7 caps.
- **US$ 0.8105 · 157.6 s** (paso «escaleta»; log 16:34:05 → 16:36:43).

## 5. guion (`01b_guionista_v4.json`, `01b_narration.json`, `01b_narracion_v3.json`, `06_judge_narrative.json`)

`prompt_version` f25-1 · ficha f23-1 · modelo claude-fable-5-1 · `nota_b` null.

**Bloqueantes:** antes de la reparación **2** → después **2** (`reparacion.bloqueantes_antes` / `bloqueantes_despues`;
`reparacion.parada` true). Pasos: `regenerados` 0, `ediciones` 2 (**las dos rechazadas**, `motivo_rechazo` «tocó otras
frases del párrafo», `despues` == `antes`), `fechas` 0, `editor` 0 (fuera del camino desde F27). Los 2 que quedan, enteros:

```json
{"codigo": "a", "cap": 2, "beat": 2, "frase": "Lo que se decía en esas calles quedó anotado tal cual: «La fábrica es nociva, a los trabajadores los llaman 'chocolateros', mueren como moscas.", "motivo": "entre comillas, pero no es una cita del pool: «La fábrica es nociva, a los trabajadores los llaman 'chocola…»"}
{"codigo": "a", "cap": 5, "beat": 8, "frase": "El Chelyabinsky Rabochy publica que el domingo pasado por la noche «muchos habitantes de Cheliábinsk observaron un resplandor especial en el cielo estrellado…", "motivo": "entre comillas, pero no es una cita del pool: «muchos habitantes de Cheliábinsk observaron un resplandor es…»"}
```

Log: `[v4] quedan 2 bloqueante(s) después de la ronda única: PARADA`. La cadena igual sigue a partición, papel y juez (así
está escrito `fase1_5.run_guion_v4`), y el RESUMEN final solo muestra «PARADA en papel».

**`metricas`** (sobre el texto de la reparación, antes de la partición): `palabras` 1925 · `largo` «1925 palabras ≈ 13.4
min» · **`citas` 11** · `puntaje` 60 · `duras_v3` 39 · `blandas_v3` 38 · `humano_caps` [1, 2, 4, 6, 7] · `cierre`
«pregunta» · `ecos` 1 · `antagonista_tipo` institucion · `antagonista_caps` 0 · `fechas_literales_por_cap` 0 en los 7 ·
`ids_por_parrafo` antes 11.38 / después 1.52.

**Palabras** (`split()` sobre cada texto; el juez cuenta con su tokenizador):

| cap | guion = reparación (`01b_guionista_v4` párrafos) | objetivo (`metricas.palabras_por_cap`) | **final** (`01b_narration.json` = `01b_narracion_v3.json`) | juez m05 |
|---|---|---|---|---|
| 1 | 175 | 110 | **175** | 176 |
| 2 | 323 | 250 | **323** | 324 |
| 3 | 187 | 260 | **187** | 187 |
| 4 | 272 | 250 | **272** | 273 |
| 5 | 333 | 250 | **333** | 333 |
| 6 | 366 | 250 | **356** | 356 |
| 7 | 265 | 140 | **223** | 224 |
| **total** | **1 921** | 1 510 | **1 869** | 1 873 |

La partición (`m01d_particion.rebalance` con `shorten=editor_shorten()`) acortó los caps 6 (−10) y 7 (−42): frases
borradas, p. ej. «Salió por la puerta.» (cap 6) y «Un hombre viejo con carpetas de juicio.» (cap 7).
**≈ minutos a 2,4 palabras/s:** final 1 869 → 778.8 s ≈ **12.98 min**; guion 1 921 → 800.4 s ≈ 13.34 min.
Caps fuera de banda en `duras_v3`: corto el cap 3 (187 < mín. 221); largos los caps 1, 2, 5, 6, 7 (máx. 126 / 288 / 288 /
288 / 161); los caps 6 y 7 siguen por encima del máximo después del acorte.

**Juez m05** (`06_judge_narrative.json`, 16:45:42; sin llamadas a modelo, no tiene línea en el resumen de costos):
`video.densidad` 1.44 (mín 2.0) · `adj_100` 0.59 (mín 2.0) · `trigramas_repetidos` 0.0309 (máx 0.05) · `datos_distintos`
27 · `palabras` 1873 · `problemas_de_fechas` 4 · `pantalla_dichos` 1 («cap 4: [D17] …») · `caps_con_repetidos_en_cap`
[4, 5, 6] · `caps_fuera_de_adjetivos` [1–7] · `antagonista` «Igor Vasilyevich Kurchatov» (la escaleta dice «Complejo
químico Mayak») · cliffhangers ok 2 de 6 (caps 1, 2) · `umbral`: densidad ✗ · repeticion ✓ · adjetivacion ✗ ·
repeticion_en_cap ✗ · nombres ✓ · antagonista ✓ · cliffhanger ✗ · `violaciones_narrador` {}.

**US$:** guionista_v4 **1.0680** (201.8 s) + reparacion_v4 **0.1048** (33.3 s; 2 llamadas «editar frase», ninguna
aceptada) = **1.1728**.

**Fecha del evento:** el perfil (`_perfil.json`) solo da el año: **1957** (`anio_evento`, puntual); día y mes no están en
el perfil. En el pool, T28 = `fecha` 1957-09-29, `hora` 16:22. **La voz sí la dice**, en letras, en la primera oración
del cap 4: «Domingo veintinueve de septiembre de mil novecientos cincuenta y siete.», y la hora: «Son las cuatro y
veintidós.» (en F23 no decía el día). Otras: cap 1 «Cheliábinsk-40, mil novecientos cincuenta y siete.»; cap 5 «Lunes
treinta de septiembre.» y «Seis de octubre de mil novecientos cincuenta y siete.». `fechas_literales_por_cap` da 0
porque mide dígitos.

## 6. partición (`01a_skeleton.json`)

1. Un misterio ardiente
2. Un proyecto oculto
3. Temperatura descontrolada
4. El golpe seco
5. La verdad oculta
6. Verdades contradictorias
7. El largo silencio

**US$ 0.1310 · 120.5 s** (paso «particion»; resumen por módulo `m01d_particion 3 calls $0.1310`; por los totales por
modelo, deducido: 2 Pro + 1 Flash).

## 7. papel (`01e_pantalla.json`; el `.md` lo pega CC)

`prompt_version` m01e-6 · `prompt_md5` 3b98aef1d8595124967ac7a85b75bab7 · `modelo` claude-sonnet-5-5 · `effort` medium ·
`intentos` 5 · resultado: 11 fichas · 8 sellos · 6 relojes · 50 `descartados` (del modelo: 44 voz_lo_dice, 3 otro,
2 spoiler; 1 de validación).

- **Vueltas: 4** (`reintento.vueltas`). Llamadas (`por_intento`): 1) in 48 038 / out 20 545 · US$ 0.3015 · 141.8 s;
  2) 55 105 / 1 312 · 0.1233 · 11.7 s; 3) 54 524 / 218 · 0.1112 · 2.1 s; 4) 54 538 / 1 354 · 0.1226 · 12.0 s;
  5) 54 561 / 209 · 0.1112 · 2.3 s.
- **Cierre: `tope`** (`reintento.cierre`). `tope` = US$ 1.00, «respaldo (el perfil no trae costos.m01e_tope_usd)»;
  `error`: «gastado 0.7699 + esta llamada hasta 0.3032» → sin quinta vuelta.
- **Cortados al cierre: 0** (`cortados_al_cierre`).
- **Picos vacíos: 1** — ch01 beat 1 (`picos_vacios`). (m01e marca 7 beats como pico: ch01 b1, ch02 b3, ch03 b4, ch04 b5,
  ch05 b7, ch06 b10, ch07 b11.)
- **`a_pantalla` vacíos: 1** — ch01 beat 1, D03 (`a_pantalla_vacios`).
- **US$ 0.7699 · 172.6 s** (`usd` 0.76992; paso «pantalla»).

**Motivos por vuelta** (`reintento.vueltas[].motivos`; log: cada vuelta «fichas fuera 1 · preguntas nuevas 0 · picos
vacíos 1»):

| vuelta | beats | motivos que la dispararon | aplicado | US$ |
|---|---|---|---|---|
| 1 | ch01 b1, ch02 b3, ch04 b5, ch06 b10 | **D03** en ch01 b1 fuera (`no_dicho` … «(gancho)»); D31, D09 ×2, D90: preguntas de spoiler/no_dicho (las 3 se mantuvieron: «otro hecho»); D122, T61, D152 «vuelve a ser candidato»; «el beat 1 de ch01 es pico y quedó sin ficha»; «… quedó sin ninguno de los datos que la escaleta dejó para la pantalla …: D03» | ch01 b1: ficha + sello | 0.1233 |
| 2 | ch01 b1 | **D50** en ch01 b1 fuera (`no_dicho` … gancho); D122, T61, D152 (iguales); pico sin ficha; D03 sin pantalla | ch01 b1: ficha | 0.1112 |
| 3 | ch01 b1 | **D03** otra vez («NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7») fuera (`no_dicho` … gancho); D122, T61, D152; pico sin ficha; D03 sin pantalla | ch01 b1: ficha + sello | 0.1226 |
| 4 | ch01 b1 | **D201** en ch01 b1 fuera (`no_dicho` … gancho); D122, T61, D152; pico sin ficha; D03 sin pantalla | ch01 b1: ficha | 0.1112 |

Al cierre, el único `descartado` de validación es D03 en ch01 b1 («NIVEL 6 DE 7», regla `no_dicho`): la salida de la
vuelta 4 volvió a proponer D03.

**c3/g4 de F38e: sí.** Las vueltas 2, 3 y 4 se gastaron solo en ch01 beat 1, con los mismos dos motivos cada vez
(«pico y quedó sin ficha» y «a_pantalla D03 vacío»). Cada propuesta del modelo para ese beat (D03 → D50 → D03 → D201 →
D03) la sacó la misma regla `no_dicho` del gancho. D03 es justo el `a_pantalla` que la escaleta reservó «sin que la voz lo
lea». Además, D122, T61 y D152 («vuelve a ser candidato») salieron iguales en las 4 vueltas y ninguna vuelta los tocó
(`aplicados` siempre ch01 b1; `ignorados` 0). Gasto de las vueltas 2–4: US$ 0.3450.

## 8. Costos y tiempos por paso (`01_v3_costos.json` `_corridas`)

| paso | modelo (resumen por modelo/módulo de `corrida.log`) | llamadas | US$ | s | ventana en el log |
|---|---|---|---|---|---|
| research (incl. 4a–4e) | Gemini 2.5 Pro + Flash | 37 | 1.4829 | 1 358.7 | 16:04:18 → 16:26:57 |
| ficha | gpt-6.1-sol high | 1 | 0.3956 | 428.1 | 16:26:57 → 16:34:05 |
| escaleta | claude-fable-5-1 | 1 | 0.8105 | 157.6 | 16:34:05 → 16:36:43 |
| guionista_v4 | claude-fable-5-1 | 1 | 1.0680 | 201.8 | 16:36:43 → 16:40:04 |
| reparacion_v4 | claude-fable-5-1 | 2 | 0.1048 | 33.3 | 16:40:04 → 16:40:38 |
| particion | Gemini (2 Pro + 1 Flash, deducido) | 3 | 0.1310 | 120.5 | 16:40:46 → 16:42:47 |
| pantalla | claude-sonnet-5-5 medium | 5 | 0.7699 | 172.6 | 16:42:47 → 16:45:39 |
| **total `_corridas`** | | **50** | **4.7627** | **2 472.6** (41 min 12.6 s) | |

- Resumen por modelo al final de `corrida.log`: **TOTAL 50 calls · US$ 4.7626** (Fable 1.9833 · Sonnet 0.7699 · Flash
  0.1993 · Pro 1.4145 · gpt-6.1-sol 0.3956). Las 21 líneas «por módulo» suman 50 llamadas y US$ 4.7627.
- **Diferencia `_corridas` vs resumen: US$ 0.0001 = redondeo** (cada paso se guarda a 4 decimales). No hay gasto fuera de
  `_step_cost`: cada módulo del resumen cae en algún paso (las llamadas también cuadran, 50 = 50), y el juez m05 no hace
  llamadas (no tiene línea).
- Reloj: 16:04:16 → 16:45:42 = 2 486 s; los pasos suman 2 472.6 s; los ≈ 13 s restantes quedan fuera de los pasos
  (arranque, registro, 16:40:38 → 16:40:46 entre reparación y partición, juez m05 16:45:39 → 16:45:42).
- Tope de la tanda US$ 5.00 (`lab/TOPE_TANDA.json`): no se pasó (4.7627).

## 9. Lado a lado con F23 (misma semilla; solo números)

Fuentes F23: `lab/hyperframes/f23/F23_REPORT.md`, `resumen_f23.json`, `fuentes_f23.json`, `manifest_f23.json`,
`ficha_kyshtym_f23.json`, `guion_kyshtym_f23.json`, `run_research.log`, `POOL_GATE.md`; y
`data/scripts/_steps/f18-kyshtym-mayak/00_pool_v3.json` (mtime 2026-10-24 23:05; misma compuerta 154/21/16/56/23 que F23).

| | F23 (`f18-kyshtym-mayak`) | F39 (`f39-kyshtym`) |
|---|---|---|
| perfil | 1948–1967, prolongado; ru · en · es | 1957–1957, puntual; ru · en · es |
| fuentes R1 | 10 (ru 9 · en 1 · es 0) | 7 (en 4 · ru 3 · es 0) |
| descartadas R1 | 42 (en 19 · ru 19 · es 4) | 29 (en 18 · ru 9 · es 2) |
| bajadas | 8 (ru 7 · en 1) | 6 (ru 3 · en 3) |
| con aporte al pool | 8 (ru 7 · en 1) | 5 (ru 3 · en 2) |
| datos del pool por idioma | ru 136 · en 18 | ru 193 · en 10 |
| compuerta | verde | verde |
| · datos | 154 | 203 |
| · citas_verificadas | 21 | 22 |
| · elegibles_humano | 16 | 11 |
| · eventos_con_fecha | 56 | 42 |
| · personas_con_nombre | 23 | 40 |
| research US$ / s | 1.2127 / 1 301 (perfil, R1, R2, R3, R5) | 1.4829 / 1 358.7 (incluye 4a–4e ≈ 0.0831) |
| ficha: hechos / citas / escenas / personas / sacados / US$ | 74 / 16 / 12 / 45 / 14 / 0.3343 | 70 / 16 / 9 / 54 / 10 / 0.3956 |
| escaleta: intentos (bloqueantes) / US$ | 2 (26 → 0) / 0.3222 (gpt-6.1-sol) | 1 (0) / 0.8105 (Fable) |
| guion: bloqueantes al final | 0 | 2 |
| palabras (`split`) | 1 446 | 1 921 guion · **1 869** final |
| ≈ min a 2,4 palabras/s | 10.0 (el reporte F23 dice 11.8, con otra tasa) | 13.34 guion · 12.98 final |
| citas (`metricas.citas`) | 8 | 11 |
| palabras por cap | 111 · 76 · 81 · 134 · 122 · 601 · 319 | 175 · 323 · 187 · 272 · 333 · 356 · 223 (final) |
| caps cortos (bajo el mínimo del cap) | 4: caps 2, 3, 4, 5 (76, 81, 134, 122 vs 204–212) | 1: cap 3 (187 vs 221) |
| duras_v3 / puntaje | 34 / 34 | 39 / 60 |
| ¿dice el día del evento? | no | sí (cap 4, «veintinueve de septiembre», y la hora) |
| partición / papel | no corrieron en F23 | US$ 0.1310 / 0.7699 |
| total de la cadena Kyshtym | 2.7437 (research + ficha + escaleta + guion; la tanda F23 fue 2.7471 con perfiles de otros temas) | 4.7627 |
