# F23_REPORT — el tiempo del caso, umbrales a métrica, intent desde la escaleta, idiomas del caso · Kyshtym desde la semilla

CC · 2026-10-24 · base `2dcc428`, rama `f11-guion-v4`, sin merge. Handoff `HANDOFF_F23_tiempo_umbrales_intents.md`
(md5 `4384909cd470b14188fd533ede87001f`). **Tanda US$ 2.7471 de 6.00.**

**En corto.** Cambios de §1 hechos, con siete desvíos declarados (tabla §1). Tests: **845 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`), con `test_module_f23.py` (34) y dos fixtures de F22/F22b apuntadas a los respaldos de F22 (desvío 8). Kyshtym corrió entero
desde la semilla: perfil nuevo (**1948–1967, prolongado**, idiomas ruso · inglés · español) → research v3 (10 fuentes, 8
descargadas: 7 ru + 1 en, ninguna en español) → compuerta **verde** (154 datos · 21 citas verificadas · 16 elegibles ·
56 eventos con fecha · 23 personas) → ficha v2.2 (74 hechos, 16 citas, 12 escenas) → escaleta f22-2 sin columna (intento 1:
26 bloqueantes → intento 2: 0) → guion v5.3 con Fable: **1,446 palabras ≈ 11.8 min, 0 bloqueantes, 8 citas**. Lo que no
salió: Osetrov/Komarov/Serov **no están** (la R1 nueva no trajo el documento donde estaban); el chequeo de año de R3 sacó dos
ítems del caso (1989 y 2008); el cap 6 se lleva 601 palabras y los caps 2–4 tienen 76–134; el guion nunca dice el día de la
explosión (29 de septiembre). Y `metricas` se cayó en la corrida (un `min()` vacío en `m05.cap_review`, que §1.1 destapó):
arreglado sin API y métricas recalculadas sobre el mismo guion (desvío 7).

## 1. Ítems de §1 → hecho / no / desvío

| § | ítem | estado | dónde / motivo |
|---|---|---|---|
| 1.1 | perfil `anio_inicio/anio_fin/tipo_evento`, `anio_evento = anio_inicio` | hecho | `research_v3.PROFILE_SCHEMA`, `seed_profile`, `tiempo_del_perfil` (sin perfil nuevo: `anio_fin = anio_inicio`). |
| 1.1 | regenerar perfiles Kyshtym / Orleans / Ycuá (Flash), respaldo `_perfil_f22.json` | **desvío** | Kyshtym: perfil entero nuevo (lo hace `run_seed` sin `_perfil.json`). Orleans e Ycuá: de lo que devolvió `seed_profile` se sumaron **solo** los campos nuevos (`anio_inicio`, `anio_fin`, `tipo_evento`, `cobertura_ingles`, `idiomas_research`); nombres, `place_re` y vocabulario quedan los de F20/F21, porque sus pools no se rehacen y un `place_re` distinto los dejaría desalineados. Resultado: Orleans 2005–2005 puntual, [inglés, español]; Ycuá 2004–2004 puntual, [español, inglés]. US$ 0.0034. |
| 1.1 | contaminación solo si año < `anio_inicio − 20`; se borran `LATE_OK`/`EARLY_OK` | hecho | `research_v3` (bloque de contaminación de ítems). |
| 1.1 | sin año en el perfil → error, no año actual | hecho | `run_seed`: `ValueError`. |
| 1.1 | `presente_en_evento` y digest con el rango | hecho | `person_stats(…, anio_fin)`, `build_pool`, `build_digest`. |
| 1.1 | R3: AAAA además de AAAA-MM(-DD); `fechas_presente` tres granularidades; año cita/fecha difiere > 1 | hecho | reglas 5 y 7 del prompt de R3 y la validación. |
| 1.1 | regex de años `1[0-9]{3}\|20\d\d`; año por defecto `anio_inicio`, o el de la entrada anterior | hecho | `evidence.py` (3), `guion_v3_reglas._DATE/_YEAR`, `m05.date_problems` (ya no «2000»). |
| 1.1 | compuerta / `gate_eventos_fecha` cuentan mes o día (año si prolongado) | hecho | `pool_gate.con_fecha`, `measure`. |
| 1.1 | `is_hard` / `used_in` con la granularidad | hecho | `evidence.is_hard` (AAAA, AAAA-MM, AAAA-MM-DD). |
| 1.1 | borrar `guion_v3_reglas.replace_repeated_dates`; `DATE_MAX_PER_CAP` → métrica; paráfrasis + «ese año/invierno/mes», «esa primavera»; «ese domingo» → «ese día» | hecho | `fechas_literales_por_cap`; `date_problems` ya no marca el tope por cap. |
| 1.1 | `guion_v4.replace_repeated_dates`: solo fecha completa, mismo año; nada si prolongado | hecho | `replace_repeated_dates(parrafos, iso, tipo_evento)`; `reparar` le pasa el tipo del caso. |
| 1.1 | `m05._date_paraphrased` solo con puntual | hecho | |
| 1.1 | prompt guion v5.3 (una línea) | hecho | md5 abajo (§4). `PROMPT_VERSION = "f23-1"`; v5.2 queda como `SYSTEM_V5_2` / `f22-1`. |
| 1.1 | prompt ficha v2.2: línea de cronología | hecho | §4. |
| 1.2 | rojo solo por datos < 40 / personas < 2 / eventos < 3; amarillo informativo, no acorta | hecho | `pool_gate.evaluate` (pisos en `video_length`); `target_words` siempre el de la tubería normal, `max_beats` None. |
| 1.2 | `MIN_DOC_CHARS` 800, `EVENT_CHECK_CHARS` 20 000 | hecho | |
| 1.2 | piso de conteo 1 000 → 10 | hecho | `_count_re` (+ `(?<!\d\s)` para que «10 700» no se lea 700: lo destapó el piso nuevo), `COUNT_MIN = 10`. |
| 1.2 | `FOCUS_DENSITY` → métrica | hecho | `FOCUS_SOLO_METRICA`: anota «densidad baja», no corta. |
| 1.2 | oficial por defecto `academico`/`libro` con `oficial_por_defecto` | hecho | `tipos_oficiales(docs)`. |
| 1.2 | ficha v2.2: hechos 40–80 (nivel 1 10–20), citas 10–25, escenas 6–15 | **desvío** | La línea de hechos del handoff se pegó literal; además, para que el prompt no se contradiga, se sacó «entre 12 y 20» de la línea vieja de nivel 1 (quedó en la nueva: «nivel 1 entre 10 y 20»), la segunda mención («entre 60 y 80 hechos útiles») pasó a 40 y la oración arranca «Cada hecho lleva un campo nivel». Y el mensaje de usuario de la ficha (`fc.prompt`, «escenas (8–15), hechos (60–80), citas (15–25)») pasó a los mismos conteos. Diff línea a línea en §4. |
| 1.2 | bandas de caracteres desde `video_length` (palabras × 6); «cap corto» aviso | **desvío** | `video_length.char_band(role)` = palabras del rol × 6 × (0.5, 1.3): los factores 0.5–1.3 los elegí yo (el handoff no los da) para que las bandas viejas queden adentro. `m01b_narrator.LEN_*` y las notas de `m01d` salen de ahí. En el camino viejo `m01b_narrator` un cap corto sigue levantando el reintento que ya tenía (no lo toqué: no mueve párrafos). |
| 1.2 | `m01a_skeleton`: se quita el robo de pantalla | hecho | `assign_screen_ids` sin donantes. |
| 1.3 | intent desde las funciones de los beats; cap 1 hook, cap 7 outro; fallback | **desvío (nombre)** | `m01a_escaleta.INTENT_DE_FUNCION` / `intent_de_cap`; `caps_view` lo usa. «rising» del handoff = `rising_tension`, el nombre que ya usan `DEFAULT_INTENT_BY_CAP`, `tts_tags` y el render. Mezcla: manda la mayor `intensidad`; empate, el primer beat. |
| 1.3 | `tts_tags` / render leen el intent real | hecho | `tts_tags.caps_tts`: `narrative_intent` del cap o `intent_de_cap`. El render lee `narrative_intent` de los caps (ahora el derivado). |
| 1.3 | rango como valor válido en «un hecho, una cifra» | hecho | `evidence.es_rango`; `count_variants` y `canonize_figures` no cuentan un rango como otra cifra. |
| 1.4 | `idiomas_research`; R1 «Buscá … en {idiomas}» | hecho | `idiomas_research(local, cobertura_ingles)` (local, inglés si hay cobertura, español al final). |
| 1.4 | `_doc_rank` gov; `Accept-Language` desde idiomas | hecho | `set_idiomas`, `ACCEPT_LANGUAGE`. |
| 1.4 | `detect_lang` alfabeto + 6 listas; `_TAIL_HEAD` | hecho | |
| 1.4 | FOIA → «archivos desclasificados o solicitudes de acceso a la información»; «prensa local de la época del evento» | hecho | R1 y focos de descubrimiento. |
| — | dorado v3 «si cambia, solo por las líneas de 1.1» | **desvío** | Cambia, pero por **§1.2**: solo las tres notas de largo de `m01d` (bandas de caracteres derivadas). Con esas tres notas vueltas atrás, el hash es el de F22e (`cf2181e4…`): `test_module_f23.test_dorado_v3_solo_cambian_las_bandas`. Nuevo `V3_GOLDEN = aaffb169…`. |
| — | antecedentes viejos | **desvío (efecto)** | Con contaminación `< anio_inicio − 20`, un antecedente de más de 20 años antes del inicio se cae (en Ycuá/Orleans nada; en Kyshtym, con inicio 1948, entra hasta 1928: el sanatorio de 1930 quedó). |
| — | fixtures de `test_module_f22` (autor_en_documento, F13) y `test_module_f22b` (1982) | **desvío 8** | Leían el pool y la ficha de Kyshtym de `_steps` en vivo; con el pool de F23 (que no tiene F13) fallaban 9. Ahora leen `00_pool_v3_f22.json` / `ficha_caso_f22.json` si existen. Los asserts no cambiaron. |
| — | `m05.cap_review`: el orden de fechas se mide con los eventos que el texto dice | **desvío 7 (arreglo)** | En la corrida, `metricas` se cayó con `min() arg is an empty sequence`: con la cronología de mes/año como dato duro (§1.1), un evento asignado al cap puede no tener su anchor literal en el texto. Ahora el orden se mide solo con los que lo tienen. No es un chequeo nuevo (el aviso blando de orden ya existía); se recalcularon las métricas del mismo guion sin API (`nota` en `guion_kyshtym_f23.json`); los bloqueantes son los de la corrida. |

## 2. Compuerta: antes (F22) | después

| | color | datos | citas verificadas | elegibles humano | eventos con fecha | personas con nombre |
|---|---|---|---|---|---|---|
| pool F22, compuerta de F22 (lo guardado) | verde | 208 | 20 | 4 | 22 (solo día) | — |
| pool F22, compuerta de F23 | verde | 208 | 18 | 7 | 35 (mes o día) | 13 |
| **pool F23, compuerta de F23** | **verde** | **154** | **21** | **16** | **56** (prolongado: año, mes o día) | **23** |

Eventos con fecha en la cronología de F23 (56): **18 con día, 8 con mes, 30 con año solo**; los 38 de mes/año entran porque
el perfil dice `prolongado` (con «puntual» contarían 26). En F22 eran 61 (22 día · 13 mes · 26 año), y la compuerta vieja
contaba solo los 22 de día. Orleans e Ycuá con la compuerta nueva: verdes (test).

## 3. Los cinco puntos de §2

**1. Compuerta.** Verde, las cuatro medidas por encima del umbral (tabla de arriba). 38 eventos de mes/año entran ahora.

**2. Osetrov, Komarov, Serov: no.** En F22 los tres salían de un solo documento (F13, cyberleninka 2018) con cita
`verificada_parcial`. La R1 de F23 (sin caché, con el prompt nuevo «Buscá con Google en ruso, inglés y español») trajo 10
fuentes distintas — pravo.ru, juryst.ru, ru.wikipedia, svoboda, meduza, pravosoznanie, ozersk74, en.wikipedia, archive74
y un YouTube — y ninguna es aquel artículo: los nombres no aparecen en ningún texto descargado. Así que no se puede medir lo
de `autor_en_documento` sobre ellos. Sobre lo que sí hay: las 24 citas tienen `autor_en_documento`, en cirílico cuando el
documento es ruso («Анатолий Васильевич Дубровский», «Анна Ильина», «Галина Чанова»…); **21 verificadas, 3 parciales, 0
sin verificar** (en F22: 20 verificadas con la compuerta vieja). Las 3 parciales son por «N palabras seguidas literales:
va sin nombre» (Otdelnov, Dubrovsky Q16, Kuleshov Q20). Tampoco está Kutepova (la humana de F22d): no hay documento suyo.
Nota: la R1 trajo 10 fuentes y no 20 como en F22, y cero en español; 2 no bajaron (YouTube, archive74 PDF).

**3. Rango de años.** Descartados por «contaminación»: **0** (en F22: **36**, todos por «fecha > evento + 20 años»: 1979,
1986, 1989, 1990, 1993, 1996, 1997, 1998, 2000, 2003, 2005, 2007, 2008, 2009, 2015, 2017, 2021). En la cronología de F23
quedan 1976 (Medvedev da a conocer el desastre), 1985, 1989, 1990, 1993 (evacuación de Muslyumovo aprobada), 1994-09-22,
**1997 (Chanova empieza a cobrar)**, **2001 (último año indexado)**, 2007, 2008, 2011 (×3, el expediente de N.N.D.). Lo
que sí se cayó y es del caso: dos eventos por la validación de R3 «el año de la cita = el año de la fecha» (± 1), porque
la cita literal menciona 1957 y el evento es posterior: «La fiscalía … presentó 86 demandas» (2008; la cita dice «después
de la avería … de 1957») y «La URSS reconoce oficialmente … la explosión» (1989; la cita dice «в 89 году», año de dos
cifras, y «29 сентября 1957»). No lo toqué (cero chequeos nuevos; el handoff pedía solo bajar a ± 1). Las 86 demandas
igual llegaron al guion por otro ítem.

**4. Intents.** Escaleta F23 (beats por cap: 1, 1, 1, 1, 1, **6**, 3):

| cap | fijo (`DEFAULT_INTENT_BY_CAP`) | F22d (derivado) | **F23 (derivado)** | beats F23 (función · intensidad) |
|---|---|---|---|---|
| 1 | hook | hook | **hook** | gancho 4 |
| 2 | setup | setup | **setup** | planteo 1 |
| 3 | rising_tension | rising_tension | **rising_tension** | giro 2 |
| 4 | shock | rising_tension | **rising_tension** | escalada 4 |
| 5 | consequences | shock | **shock** | pico 5 |
| 6 | resolution | rising_tension | **consequences** | respiro 2, consecuencia 3, giro 3, revelacion 3 ×3 (empate en 3: el primero) |
| 7 | outro | outro | **outro** | revelacion 3, giro 3, cierre 2 |

Con el fijo, la explosión (cap 5) habría ido como «consequences»; ahora va «shock». Cambian 3 de 7 (caps 4, 5, 6).

**5. El guion (Fable 5.1, v5.3).** 1,446 palabras ≈ 11.8 min · **0 bloqueantes** · 8 citas · 6 personas con nombre
(Dubrovsky — el humano —, Chanova, Lyudmila Smirnova, Slivyak, Medvedev, y el diario Chelyabinsky Rabochy, que el contador
toma por persona).

| cap | intent | palabras F22d → **F23** | personas con nombre (F23) | citas | fechas literales: métrica (dígitos) · leídas (en letras) | bloqueantes |
|---|---|---|---|---|---|---|
| 1 | hook | 215 → **111** | Dubrovsky | 1 | 0 · 0 («septiembre de 1957», mes) | 0 |
| 2 | setup | 109 → **76** | Dubrovsky | 0 | 0 · 0 («enero de 1949», mes) | 0 |
| 3 | rising_tension | 237 → **81** | Dubrovsky | 0 | 0 · 0 | 0 |
| 4 | rising_tension | 186 → **134** | — | 0 | 0 · 0 | 0 |
| 5 | shock | 251 → **122** | Dubrovsky | 0 | 0 · 1 («el treinta de septiembre») | 0 |
| 6 | consequences | 416 → **601** | Dubrovsky, Chelyabinsky Rabochy, L. Smirnova, Slivyak | 6 | 0 · 3 («treinta de septiembre de 1957», «dos de octubre de 1957», «once de octubre») | 0 |
| 7 | outro | 162 → **319** | Dubrovsky, Chanova, Medvedev | 1 | 0 · 0 (años: 1970s, 2001, 1997, 1993, verano de 1958) | 0 |

- **Fechas literales por cap**: la métrica (`fechas_literales_por_cap`, regex de día + mes en dígitos) da 0 en los siete
  caps porque Fable escribe las fechas en letras («treinta de septiembre de mil novecientos cincuenta y siete»); contadas
  a mano (día + mes en letras): 0, 0, 0, 0, 1, 3, 0. En F22d (Fable): una sola («Veintinueve de septiembre», cap 4). La
  métrica no ve fechas en letras: queda dicho, no lo cambié.
- **El día de la explosión no se dice.** Cap 1 da «septiembre de mil novecientos cincuenta y siete»; cap 5 dice «al día
  siguiente, el treinta de septiembre». Ninguna parte dice «29 de septiembre».
- **Tráiler en el gancho: ninguna frase de la lista** («en este video», «vas a ver», «lo que viene», «te voy a contar»,
  «esta es la historia de», …). Leído: el gancho es una escena (la sala a oscuras, el estruendo, la cita); tiene una
  oración que anticipa — «Lo que pasó esa noche se va a poder esconder durante años; lo que no se va a poder borrar es a
  los que lo oyeron» — que no es tráiler de lista pero sí adelanta el tema. Lo marco para que lo juzgue el analista.
- **Métricas duras de v3 (no frenan): 34** (`metricas.duras_v3`, `puntaje` 34). Las principales: caps 2–5 por debajo del
  mínimo de palabras del cap (76, 81, 134 y 122 contra 204–212), «usaste 0 de los datos asignados» en los caps 1, 3 y 4,
  la primera oración del gancho con 15 palabras (máx. 12), dos cierres que no anticipan el dato del cap siguiente y una
  comilla fuera de una cita del pool. En el camino v4 esto es métrica: los bloqueantes son los únicos que frenan, y dieron
  0. Lo pongo acá para que el puntaje del guion se lea con esto a la vista.
- Palabras por cap: la tabla cuenta con `split()` (`compara_f23.html`); `metricas.palabras_por_cap` da 1 más en los caps 1
  y 6 (112, 602), por cómo tokeniza.
- **Reparto**: la escaleta puso 6 de 14 beats en el cap 6 y uno solo en cada cap 2–5; el guion lo siguió (601 palabras en
  el cap 6, 76–134 en los caps 2–4). «Cap corto» ya es aviso (§1.2), así que nada lo frenó.
- Antagonista: Mayak (institución). Humano: Dubrovsky (electricista → liquidador), presente en los 7 caps salvo el 4.

`compara_f23.html`: F22d (Fable, v5.2) | F23 (Fable, v5.3) por cap, con los textos lado a lado.

## 4. Prompts: md5 y diff línea a línea

### md5

| prompt | archivo (md5 del archivo) | bloque SISTEMA | código | igual |
|---|---|---|---|---|
| ficha v2.2 | PROMPT_FICHA_v2_2.md (`00c134a6f593223b69efcb7e7c19af52`) | `070b75dff58aecfa407fac3d62020ce4` | `070b75dff58aecfa407fac3d62020ce4` | sí |
| guion v5.3 | PROMPT_GUIONISTA_v5_3.md (`35b8e7794bffff8985a83ed968d8ab11`) | `8ca9aa494e3a0b9b4a99f60e6006c5f8` | `8ca9aa494e3a0b9b4a99f60e6006c5f8` | sí |

Sin cambio: escaleta `SYSTEM_V2` (f22-2) `22cfd68b7cee4734e95bb3ee27bb96b2`, columna `SYSTEM` `f294cf6b1220983903ce339f5b21cb27`.

### ficha: f22-1 → f23-1

```diff
--- f22-1
+++ f23-1
@@ -5 +5 @@
-- cronologia: los eventos del día en orden, con la fecha y la hora tal como están en el pool, y sus ids.
+- cronologia: los eventos en orden, con la fecha que el pool tenga (año, mes o día) y la hora si la hay, tal como están en el pool, y sus ids.
@@ -11,2 +11,2 @@
-- escenas (8 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
-- hechos (60 a 80) con un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso; entre 12 y 20), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.
+- escenas (6 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
+- hechos: entre 40 y 80 según lo que el pool dé (nivel 1 entre 10 y 20); con un pool chico, menos hechos buenos valen más que relleno. Cada hecho lleva un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.
@@ -27 +27 @@
-- hechos: entre 60 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
+- hechos: entre 40 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
@@ -29 +29 @@
-- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
+- citas: las mejores 10 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
```

### guion: f22-1 (v5.2) → f23-1 (v5.3)

```diff
--- f22-1 (v5.2)
+++ f23-1 (v5.3)
@@ -37 +37 @@
-Las fechas: la fecha completa una vez, en el cap 2. Después: «ese día», «esa noche», «al día siguiente», «el miércoles».
+Las fechas: cada fecha nueva se dice completa la primera vez. Si todo pasa en un día, después alcanza con «ese día», «esa noche», «al día siguiente», «el miércoles»; si el caso dura años, cada salto de tiempo se dice («En 1960…»).
```

## 5. Costo por paso

| paso | modelo | llamadas | tokens in / out | US$ | tope |
|---|---|---|---|---|---|
| perfiles (Orleans, Ycuá) | Gemini Flash | 2 | — | 0.0034 | — |
| research Kyshtym (perfil, R1, R2 fichas, R3, R5) | Gemini Pro 1.1018 + Flash 0.1107 | 31 | — | 1.2127 | 3.50 |
| ficha v2.2 | gpt-6.1-sol high | 1 | 27 398 / 23 340 | 0.3343 | 0.60 |
| escaleta f22-2 sin columna | gpt-6.1-sol high | 2 (intento 1: 26 bloqueantes; intento 2: 0) | 15 650 / 6 860 · 16 342 / 6 672 | 0.3222 | 0.40 |
| guion v5.3 | claude-fable-5-1 high | 1 | 11 631 / 15 163 | 0.8745 | 1.20 |
| **total** | | 37 | | **2.7471** | **6.00** |

Salida acotada por llamada para que el peor caso entre en el tope de cada paso: ficha 50 000, escaleta 16 000, **guion
21 000** (el default de `guion_v4` es 32 000; con 32 000 el peor caso de Fable, US$ 1.72, no entraba en 1.20). Usó 15 163.

## 6. Archivos

`lab/hyperframes/f23/`: `F23_REPORT.md`, `POOL_GATE.md`, `FICHA_kyshtym.md`, `ESCALETA_kyshtym.md`,
`NARRACION_kyshtym_f23.md`, `compara_f23.html`, `resumen_f23.json`, `costos_f23.json`, `PROMPTS_f23_diff.md`,
`PROMPT_FICHA_v2_2.md`, `PROMPT_GUIONISTA_v5_3.md`, `prompt_kyshtym_f23_{ficha,escaleta,guion}.txt` (con md5),
`kyshtym_research_f23.json`, `perfil_kyshtym_f23.json`, `perfiles_f23.json`, `fuentes_f23.json`, `manifest_f23.json`,
`ficha_kyshtym_f23.json`, `ficha_crudo_kyshtym.json`, `escaleta_kyshtym_f23.json`, `escaleta_crudos_kyshtym_f23.json`,
`guion_kyshtym_f23.json`, `f23_corridas.py`, `f23_compara.py`, `f23_diffs.py`, logs. `_transfer_tmp/` borrado.
En `_steps/f18-kyshtym-mayak/` (no versionado): `00_pool_v3.json` y `_perfil.json` nuevos; respaldos `00_pool_v3_f22.json`,
`_perfil_f22.json`, `ficha_caso_f22.json` y `_f22/` (caché R1/R3, `fuentes.json`, `POOL_GATE.md` y manifest de F22).
Orleans/Ycuá: `_perfil.json` con los campos nuevos y `_perfil_f22.json`.

## 7. Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

Tabla (resumen de lo verificado)
# | requisito | estado | evidencia
1 | §1.1 tiempo del caso (perfil, contaminación, fallback, rango, R3, regex, compuerta, is_hard, replace_repeated_dates, _date_paraphrased) | OK | `git diff 2dcc428` (research_v3, evidence, pool_gate, guion_v3_reglas, guion_v4, m05); `m05._date_paraphrased` devuelve False si prolongado; `ValueError` sin año en el perfil
2 | §1.2 umbrales a métrica (rojo 40/2/3, amarillo ya no acorta, MIN_DOC 800, 20.000, piso 10, oficial por defecto, bandas por video_length, sin robo de pantalla) | OK, con 1 desvío declarado | `m01a_escaleta.pool_gate_profile` ya no escribe `_largo`; el factor 0.5–1.3 de `char_band` lo eligió CC (declarado en el reporte)
3 | §1.3 intent desde los beats | OK | `m01a_escaleta.intent_de_cap` e `INTENT_DE_FUNCION`; cap 1 siempre hook y cap 7 siempre outro; «rising» = `rising_tension` (nombre del catálogo, declarado)
4 | §1.4 idiomas del caso | OK | reporte §1 y diff; no lo audité línea por línea
5 | Prompts solo en las líneas dichas | OK, con desvío declarado | La línea de guion v5.3 es literal. En la ficha v2.2 se tocaron además «entre 12 y 20», «60 a 80 hechos útiles» → 40 y el mensaje de usuario `fc.prompt`. Los tres están declarados en el reporte §1 y en el diff §4. Los md5 de los bloques coinciden con el código: `070b75df…` (SYSTEM_F23_1) y `8ca9aa49…` (SYSTEM_V5_3). Los md5 de los archivos coinciden con el reporte: `00c134a6…` y `35b8e777…`. La escaleta (`SYSTEM_V2`) no cambia.
6 | Cero chequeos nuevos | OK | El diff no agrega bloqueantes ni validaciones nuevas. Lo nuevo es un `ValueError` por falta de año (lo pedía el handoff), una línea informativa en la compuerta y `es_rango`, que afloja. El arreglo de `m05.cap_review` filtra los eventos sin anchor antes de medir el orden: afloja y no agrega chequeo. Está declarado como desvío 7.
7 | Tests | OK | Corrí la suite del pedido: 845 passed, 5 failed. Son las 5 previas: 3 de `01b_pauses` y 2 de `m03_merge_timing`. `test_module_f23.py` existe.
8 | Corrida y topes | OK | `costos_f23.json`: 0.0034 + 1.2127 + 0.3343 + 0.3222 + 0.8745 = 2.7471, bajo 6.00. Por paso: research 1.21 (tope 3.50), ficha 0.33 (0.60), escaleta 0.32 (0.40), guion 0.87 (1.20). Coincide con el reporte.
9 | Entregables y limpieza | OK | Existen `POOL_GATE.md` (verde, 154/21/16/56/23 como dice el reporte), `NARRACION` (97 líneas), `compara_f23.html` (24 KB), `PROMPTS_f23_diff.md` y `costos_f23.json`. `_transfer_tmp/` no existe. `.env` y `config.py` no figuran en `git status`. `lab/_gpt_probe_analista/` está sin trackear (`??`) y no hay que añadirlo al commit. `ESTADO_SESION.md` actualizado.
10 | Números del reporte vs archivos | PARCIAL | Total, palabras (1446), citas (8) y minutos (11.8) coinciden. En `palabras_por_cap` el reporte dice 111 para el cap 1 y 601 para el cap 6, y el JSON da 112 y 602 (diferencia de 1).
11 | Reporte §7 | PENDIENTE | Dice REVISOR_PENDIENTE: va este veredicto íntegro.

Observaciones
1. El reporte dice «0 bloqueantes» y no menciona que `metricas.duras_v3` trae 34 problemas duros, y `puntaje` también da 34. Entre ellos: cap 1 con primera oración de 15 palabras (máx 12), caps 2, 3 y 4 con 76, 81 y 134 palabras contra mínimos de ~204–212, y varios «usaste 0 de los datos asignados». Esos duros no bloquearon en la corrida. Solo se menciona el desbalance de caps; el resto no se declara. Omar debería saberlo antes de puntuar el guion.
2. `metricas` se recalculó después de la corrida, por el arreglo de `m05.cap_review`. Está declarado en el JSON y en el reporte, y los bloqueantes y párrafos son los de la corrida. Aun así el JSON conserva `error_metricas_corrida`.
3. Osetrov, Komarov y Serov no aparecen en el pool ni en el guion. El reporte lo declara honestamente: la R1 no trajo el documento. El criterio 2 de §2 queda sin poder medirse.
4. Dos eventos del caso (1989 y 2008) se perdieron por la validación de R3 de ±1 año. Está declarado y es lo que pedía el handoff.
5. La métrica de fechas literales da 0 en los 7 caps porque el guion escribe las fechas en letras. Está declarado. El guion nunca dice el «29 de septiembre».
6. El dorado v3 cambió por §1.2 (bandas de `m01d`) y no por §1.1 como permitía el handoff. Está declarado como desvío, con un test que lo acota.
7. La ficha v2.2 tiene tres cambios más que la línea literal pedida. Es un desvío chico, declarado y razonable, pero es un desvío de «prompts solo en las líneas dichas».
8. Los perfiles de Orleans e Ycuá se actualizaron solo con los campos nuevos y no se regeneraron enteros. Está declarado.

Fuera de alcance: ninguno atribuible a F23. `diag_234_cap4.py` y `gfx_profiles/*` no son de esta tarea, como dijiste. Las ediciones a `test_module_f10/f11/f22/f22b/f22d/f5d/f7/f7d/f8b.py` están justificadas por el reporte.

Riesgos que el contrato no cubre: (a) un guion con 34 duras de v3 y cap 6 de 601 palabras contra 76–134 en los caps 2–4 pasa como «0 bloqueantes» porque la escaleta puso 6 de 14 beats en un cap. (b) Con perfil «prolongado», cualquier año cuenta como evento fechado, así que la compuerta es más laxa (56 eventos, de los cuales 30 son solo año). (c) El research ya no repite el documento clave de F22, así que los resultados no son reproducibles entre corridas.

*(Después del veredicto, CC sumó al §3.5 las 34 duras de v3 y la nota de palabras por cap (observaciones 1 y 10); nada más cambió.)*
