# F72b — la pregunta de cierre es la última oración de la voz; qué sigue leyendo la escaleta; música tardía

Handoff: `lab/hyperframes/f72/HANDOFF_F72b.md` (md5 `2d92f0238a6dc8f336d3afdd3a92fa27`, verificado). Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1` (Wittenoom), rama `f11-guion-v4`. DECISIONES 2026-11-03 20:50 (Omar, «si dale»). Sin tocar prompts ni main. No corrí `--reuse-visuals`, `--gfx`, `--aprobar-guion` ni `--plan-edit`.

## Resultado en una línea

Las 7 preguntas de cierre de Wittenoom son ahora la última oración de la voz aprobada, todas con fuente `voz-final` y las 7 iguales al texto que esperaba el handoff. Las pausas congeladas suman 26,1 s y la mezcla de previsualización bajó de 856,1 s a 824,4 s. `--plan-only`: exit 0, 203 s, US$ 0. Siguen los mismos 5 chequeos en ✗; el de música es un falso positivo de la medición (C).

## A — `gfx_realizador.pregunta_cierre_fuente`

Código (`script_engine/gfx_realizador.py`):
- (i) Si la última oración de la voz del cap termina en «?», queda esa pregunta, fuente `voz-pregunta`. Es igual que antes.
- (ii) Si no, queda la última oración de la voz del cap (`voz_utils.oraciones_de_texto` sobre el texto de todos los beats del cap), fuente `voz-final`.
- **Borrados:** el emparejamiento con el `cierre` del último beat (`voz-alineada`) y el respaldo con el `cierre` literal (`escaleta`). La función ya no lee `cierre`. `FUENTES_CIERRE = ("voz-pregunta", "voz-final")`. Sin voz → `(None, None)`.
- `script_engine/gfx_layer.py`: solo cambian un comentario y el texto del log («sin escaleta o el cap no trae voz»).

Tests:
- **Borrados:** `test_module_f38e_b.py::test_b4_ii_…`, `::test_b4_iii_…` y `::test_b4_vajont_…` (la tabla de Vajont con `voz-alineada`), y también `test_module_f29a.py::test_pregunta_es_el_cierre_del_ultimo_beat`.
- **Ajustados, sin cambiar lo que prueban:** `test_module_f32.py::test_b2_la_pregunta_dura_su_lectura` y `test_module_f38e_a.py::test_r8_closing_question_y_el_plan_fijo_dan_la_misma_pausa`. Pasaban el texto en `cierre` y ahora lo pasan en `texto`. En f32 la frase quedó en una sola oración, para que la lectura siga siendo la del texto entero.
- **Nuevo:** `test_module_f72b.py`, 7 tests sin red: `voz-final` gana aunque el `cierre` diga otra cosa; `voz-pregunta` queda igual; el `cierre` ya no es respaldo; la voz es la de todos los beats del cap; `closing_question` guarda la fuente y dura lo que lleva leerla; los 7 caps de Wittenoom dan los textos del handoff. Las entradas de Wittenoom quedan congeladas en `lab/hyperframes/f72/b_fase1_wittenoom/` (copias de `01a_escaleta.json` md5 `b37cb3c7…` y `01b_narracion_v3.json` md5 `29c3a4f3…`).
- Mapa: los stickers de `gfx_layer.py` y `gfx_realizador.py` llevan el md5 nuevo y la frase F72b, en `lab/mapa/stickers/fase2b_gfx.json`. `mapa --check`: 161 archivos · 0 fallas.

Simulación con los 7 caps de Wittenoom (la escaleta y la narración por beat reales). La primera tabla es antes del cambio, la segunda después:

| cap | antes: texto · fuente · lectura |
|---|---|
| ch01 | «Esa foto se tomó en un pueblo que hoy no figura en ningún mapa. Pero antes de que lo borraran, alguien tuvo que llevar a ese hombre hasta allí.» · voz-alineada · 9,53 s |
| ch02 | «Del barco, a un avión pequeño. Del avión, a la tierra más roja que Víctor había visto en su vida.» · voz-alineada · 6,47 s |
| ch03 | «Un año después de que McNulty escribiera ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.» · escaleta · 9,00 s |
| ch04 | «Habían estado unos diez meses. Creyeron que se llevaban de Wittenoom un hijo y nada más.» · voz-alineada · 5,87 s |
| ch05 | «Fueron nueve meses. El mismo tiempo que un embarazo. Daniel había estado en Wittenoom diez.» · voz-alineada · 6,07 s |
| ch06 | «No porque fuera técnicamente imposible. En esa tierra vivía un hombre que no podía irse.» · voz-alineada · 5,87 s |
| ch07 | «Daniel Écija vivió diez meses en Wittenoom. Lo que respiró allí, en diez meses, tardó casi treinta años en matarlo. Wittenoom ya no está en el mapa.» · voz-alineada · 9,87 s |

| cap | después: texto · fuente · lectura | = esperado |
|---|---|---|
| ch01 | «Dos años antes de la foto, en Madrid, hubo un baile.» · voz-final · 3,47 s | sí |
| ch02 | «Del avión, a la tierra más roja que Víctor había visto en su vida.» · voz-final · 4,40 s | sí |
| ch03 | «Ese mismo año, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.» · voz-final · 6,13 s | sí |
| ch04 | «Creyeron que se llevaban de Wittenoom un hijo y nada más.» · voz-final · 3,80 s | sí |
| ch05 | «Y no fue el único que se llevó Wittenoom adentro.» · voz-final · 3,27 s | sí |
| ch06 | «En esa tierra vivía un hombre que no podía irse.» · voz-final · 3,20 s | sí |
| ch07 | «Lo que sobró de la mina, sí.» · voz-final · 1,87 s | sí |

Control cruzado: la última oración de `narration` de cada capítulo en `data/scripts/<tid>.json` (la narración aprobada) es la misma que en las 7 filas de arriba.

Nota: la tabla de «antes» es mi simulación con la escaleta y la narración de hoy. El handoff cita 14,1 s para ch03 en el guion anterior y mi simulación da 9,00 s, así que el guion viejo no salía exactamente de estas entradas. No lo investigué.

## B — qué lee todavía `01a_escaleta.json` (SOLO LECTURA, sin arreglar)

Hecho base: **nada vuelve a escribir `01a_escaleta.json` cuando se edita o se aprueba la narración.** Solo la escribe `m01a_escaleta._persist` (`script_engine/m01a_escaleta.py:760-765`), que se llama al generarla (:1336) y en el camino congelado (:1390), los dos desde `fase1_5.run_escaleta_v3` (`fase1_5.py:543-563`).

Al aprobar en QA, el camino es: `qa_studio_server.py:2319` → `m01f_critico.guardar_y_aprobar` (`m01f_critico.py:474`) → `_aplicar` (:284-290) → `m01d_particion.reconstruir` (`m01d_particion.py:276-295`). Ese camino lee la escaleta y re-escribe solo `01a_skeleton`, `01b_narration` y `01b_narracion_v3`.

La escaleta no tiene md5 propio ni sello. `papel_falta` (`fase1_5.py:448-458`) mira solo `narracion_md5`: el papel se rehace con la escaleta vieja. `_aplicar_deberia` cambia `parrafos[].ids_usados` (`m01f_critico.py:386-388`), pero no toca `dato_central` ni `datos_apoyo`. Un beat puede quedar sin texto (`beats_sin_texto`, `m01f_critico.py:456-461`) y la escaleta lo sigue listando.

| campo | archivo:línea | para qué | ¿desfasa tras editar la narración? |
|---|---|---|---|
| `beats[].cierre` | `gfx_realizador.py:83` (ventanas) → `pregunta_cierre_fuente` | pregunta de cierre | **se borró en F72b A**; `ventanas` todavía lo copia a `real.beats` |
| `beats[].cierre` (texto a emparejar) | `gfx_realizador.py:85-86` → `beat_de_pantalla` :105 | en qué beat cae un `a_pantalla` sin id → `candidatos` (solo log y `gfx_beats`) | sí, con impacto solo de diagnóstico |
| `beats[].cierre` | `m01e_pantalla.py:249` → `_para_modelo` :303 | Opus (autor del papel) lo ve como «qué cuenta el beat» | sí: papel nuevo con `cierre` viejo |
| `beats[].cierre` | `m01e_pantalla.py:266` → `beat_de_pantalla` :268 | beat de cada `a_pantalla` → `archivo[].a_pantalla.beat` :283 → `a_pantalla_vacios` :580-586 y ⚠ del .md :1158-1160 | sí |
| `beats[].cierre` | `pantalla_entrada.py:153` (copiado a `ent.beats`) | ningún filtro ni `pantalla_colocar` lo lee | sí, sin efecto |
| `beats[]` `n`/`cap` (estructura) | `gfx_realizador.py:63`; `m01e_pantalla.py:241-253`, `validar` :521-523 | ventanas por beat (t0/t1 salen de los párrafos); slots del papel | en parte: un beat sin texto se saltea en las ventanas (`gfx_realizador.py:77`), pero en m01e sigue como slot y puede ser `pico` → «pico sin ficha» sin solución (:577, :610-613) |
| `beats[].funcion` | `gfx_realizador.py:79` → `pantalla_entrada.py:152-153` → `pantalla_filtros.py:273, 290`; `gfx_guion.py:235, 422`; chequeo «gancho no vacío» `gfx_guion.py:549` | función de cada bloque, eventos del guion, chequeo 9 | sí: la etiqueta es fija |
| `funcion == "gancho"` | `pantalla_entrada.py:121, 126` → `_item` :90 → `pantalla_filtros.py:121-122, 163-164`; `m01e_pantalla.py:247` → :727-729 | candado y `no_dicho` contra la voz de todo el video | sí (casi siempre sigue siendo el beat 1) |
| `funcion == "giro"` | `gfx_realizador.py:147-148` | orden de los candidatos (log) | sí, diagnóstico |
| `funcion == "pico"` | `music_intensity.py:91, 97` (vía `fase2b.py:1559-1563`) | «golpe» de música +5 dB | sí |
| `beats[].intensidad` | `gfx_realizador.py:79`; `music_intensity.py:60, 90-94` | pico de respaldo del cap → zoom_punch y silencio de música; «sube» +3 dB con ≥ 4 | sí: es la intensidad planeada |
| `beats[].dato_central` | `gfx_realizador.py:81` → :100, :147-148 | beat del `a_pantalla`; candidatos | sí |
| `beats[].dato_central` | `voz_datos.py:38-40` (`pico_cap`) | elige la **oración pico** (`voz_datos.py:113`) → zoom_punch (`gfx_style.py:121-127`) | sí: si la voz ya no dice el dato, elige por raíces de un dato ausente |
| `beats[].dato_central` | `m01e_pantalla.py:248`, :255-258 → `beats_que_lo_cuentan` :277 → `voz_lo_dice` (`validar` :545-547); :263 | prioridad del autor; en qué caps se busca si la voz dice el ítem | sí: busca en caps equivocados |
| `beats[].datos_apoyo` | `gfx_realizador.py:82`; `m01e_pantalla.py:249, 256, 264`; `pantalla_entrada.py:153` | igual que `dato_central` | sí |
| `emocion`, `imagen_sensorial`, `pregunta_abierta` | `gfx_realizador.py:85`; `m01e_pantalla.py:250-251, 266` | emparejar el `por_que` de un `a_pantalla`; contexto del autor | sí |
| `beats[].paga` | `m01e_pantalla.py:251` | contexto del autor | sí |
| `beats[].flash_forward` | `m01e_pantalla.py:252` → `momentos_detalle` :342-348 → `fecha_relato` :714-721 | año del relato por oración, para el verificador | sí |
| `beats[].texto` | ninguno: el texto por beat sale de `01b_narracion_v3.parrafos` (`gfx_realizador.py:84`; `m01e_pantalla.py:236-239, 265`) | voz por beat | no |
| `a_pantalla[]` | `gfx_realizador.py:135-145` | candidatos obligatorios (log y `gfx_beats`) | sí: la premisa «la voz no lo dice» puede romperse |
| `a_pantalla[]` | `pantalla_entrada.py:87-90` → `pantalla_filtros.py:292, 297` → `pantalla_colocar` :190, 199, 225, `repartir.prio` :317 | `a_pantalla` faltantes; se colocan primero | sí |
| `a_pantalla[]` | `m01e_pantalla.py:262-269, 283, 293`; `estilo_de` :681; :729; `a_pantalla_vacios` :580-586 | lo ve el autor; estilo «papel»; aviso en el .md | sí |
| `a_pantalla[]` por cap | `fase2b.py:3207-3211, 3221` → `gfx_guion.py:498-512` | **chequeo 6 «a_pantalla»** del guion | sí: exige ids de la escaleta vieja aunque la voz ya los diga |
| `pico` (`beat`, `id`) | `voz_datos.py:33-42` (desde `pantalla_entrada.py:107`) → `gfx_layer.py:709` → `plan["pico"]` → `transiciones_por_relato` (`gfx_layer.py:786`; `gfx_style.py:121-127, 139-140`) | zoom_punch del pico | sí: cae en el beat y la oración de la escaleta vieja |
| `pico.beat` | `gfx_realizador.py:169` (`pico_escaleta`) | nadie lo lee | sí, sin efecto |
| `pico.beat` | `m01e_pantalla.py:245, 248, 577, 610-613, 1156, 1162` | beat pico del autor, motivo «pico sin ficha», etiqueta PICO | sí |
| `pico.beat` | `music_intensity.py:186` → :105 | silencio de música 1,5 s antes del pico | sí |
| `promesa_gancho`, `loops`, `recuerda_loop`, `pico`, `humano`, `antagonista`, `cierre_humano` | `m01e_pantalla.py:287-288` → `_para_modelo` :305 | contexto del autor del papel | sí |
| `beats[].cap` | `gfx_realizador.py:63`; `m01e_pantalla.py:243-247, 267`; `music_intensity.py:70` | beats por cap | bajo riesgo: la compuerta no mueve párrafos de cap |

No los lee nadie de estos módulos: `pregunta_pantalla`, `humano_en_escena`, `escena_idx`, `contador`, `palabras_objetivo`, `pregunta_valida` ni `_pantalla_por_fecha`.

Notas:
- Con el guion aprobado, el plan congelado no relee la escaleta (`gfx_layer.py:608-613, 633`). Solo `fase2b.py:3207-3211` vuelve a leer `a_pantalla` para el chequeo 6.
- Fuera de los módulos pedidos: `m01d_particion.build_contract`, que usa `reconstruir`, lee `pico`, `antagonista`, `_pool_plan` y `narration_tts(esc, …)` (`m01d_particion.py:229-237`).

## C — la música de ch03 y ch07 «tarde» (SOLO LECTURA, sin arreglar)

**Conclusión: el ✗ es un falso positivo de la medición. La música arranca con el title card en los dos caps; no hay hueco al arrancar.**

- El chequeo se arma en `script_engine/gfx_guion.py:556-566`, con `mezcla["musica"]`. El valor sale de `_medir_inicio_musica`, en `fase2b.py:3067-3109`, llamado en `fase2b.py:3046` sobre `_preview_music_ducked.wav`.
- `fase2b.py:3090-3091` toma la ventana de 4 s más fuerte de los primeros 20 s de la pieza del cap y la busca en la pista ±20 s. `fase2b.py:3094-3099`: `c = irfft(rfft(tr)*conj(rfft(w)))`, `norma = sqrt(max(cs[len(w):]-cs[:-len(w)],0)) + 1e-9`, `lag = argmax(c/norma)`.
- En un tramo de la pista que está todo en ceros, la norma vale 1e-9. `c` no da 0: da ruido de redondeo de la FFT, en float32/complex64 porque `_pcm` (`gfx_guion.py:82-87`) devuelve float32. Ruido ÷ 1e-9 da puntajes de 10³. El máximo legítimo ronda 2–5, así que el `argmax` cae dentro del silencio.
- Ese silencio es dato correcto: la regla «silencio durante una cita de testigo» (`script_engine/music_intensity.py:113-121`, fade de 1,5 s en :145-151), aplicada en `fase2b.py:1674-1676`, con +3 s de pre-roll en `_correr_tramos` (`fase2b.py:1681-1687`). En `output/audio/<tid>/intensity_map.json` (escrito por `fase2b.py:1567`):
  - ch03: silencio 9,6–20,96 s, «cita de testigo (beat 4)» → en el mp4, 200,73–212,09 s.
  - ch07: silencio 12,82–20,26 s, «cita de testigo (beat 13)» → en el mp4, 768,62–776,06 s.
  - ch04 da ✓ porque su silencio, a 34,74 s, cae fuera de la ventana de búsqueda.
- Prueba del mecanismo: misma fórmula sobre la música separada (mezcla − voz). Es una aproximación, porque la pieza original ya no está en disco.
  - ch03: puntaje en el lugar real 3,95; máximo 2,8·10³ en 202,46 s, en ceros; desvío +6,83 s.
  - ch07: 2,42 contra 1,05·10³ en 770,64 s; desvío +15,85 s.
  - ch04 (control): desvío 0.
  - Se reproduce el patrón de +5,06 s y +14,01 s del guion.
- La línea «mapa de intensidad: … ch03 silencio,silencio · ch07 silencio» del log enumera los tramos que no son fondo; no dice que estén al principio.

Inicio de los caps (de GUION_PANTALLA): ch03 en 03:08.1 (188,133 s), ch07 en 12:32.8 (752,800 s). Los dos con title card de 3,0 s; la voz entra a los 3,08 s y a los 3,10 s.

Mediciones en `_fase2b_work/mezcla_preview.wav`, la de la corrida F72, antes del `--plan-only` de D (ffmpeg volumedetect):

| tramo | qué es | mean | max |
|---|---|---|---|
| 03:08–03:15 | arranque de ch03 | −26,4 dB | −12,7 dB |
| 03:20–03:27 | tramo vecino (cae dentro del silencio de la cita) | −27,4 dB | −13,3 dB |
| 12:33–12:48 | arranque de ch07 | −27,4 dB | −12,8 dB |
| 12:50–12:57 | tramo vecino (dentro del silencio de la cita) | −30,6 dB | −15,2 dB |

RMS de la música separada (mezcla − voz), por medio segundo:

| tramo | música |
|---|---|
| 03:08–03:09 | −24 / −25 dB |
| 03:09,5–03:10,5 (crossfade ch02→ch03, sin voz) | −36 a −42 dB |
| 03:11–03:20 (bajo la voz) | −32 a −42 dB |
| 03:21–03:31,5 | **−120 dB (ceros: silencio de la cita)** |
| 03:32–03:35 | vuelve de −53 a −35 dB |
| 12:32,5–12:35 (title card, sin voz) | −27 a −38 dB |
| 12:35,5–12:48 (bajo la voz) | −37 a −42 dB |
| 12:48,5–12:55,5 | **−120 dB (ceros: silencio de la cita)** |
| 12:56–12:59 | vuelve de −54 a −39 dB |

Lo que se oye: al arrancar no hay hueco. Sí hay voz sola, sin música, en 03:21–03:32 y en 12:48,5–12:56: es el silencio buscado de la cita de testigo. Los scripts de lectura (`rms.py`, `ncc.py`) quedaron en el scratchpad de la sesión, fuera del repo.

## D — `fase2b.py 123bbb64-… --plan-only`

Comando: `python fase2b.py 123bbb64-9fca-4395-8bf4-57d60e219ef1 --plan-only`, con la venv. 20:55:32 → 20:58:57, **exit 0**, sin exit 2: `fondos.json` sigue en `68e57663…`, con el papel `39c99927…`. Log en `lab/hyperframes/f72/f72b_plan_only.log`, sin commitear.

```
  🎞  base -g30 de 7 caps en paralelo: 84s
  🔊 mezcla de previsualización: …\_fase2b_work\mezcla_preview.wav (824.4s, 13s)
  ⏱  --plan-only 203s · costos {}
[20:58:57] INFO | viral_pipeline | [cost_tracker] Video 123bbb64-9fca-4395-8bf4-57d60e219ef1 — Costo total: $0.0000
```

**Tiempo: 203 s. Costo: US$ 0** (costos vacíos; el tracker da $0.0000). La línea «♻ reuse-visuals» la imprime `--plan-only` solo; yo no pasé ese flag.

Las 7 preguntas de cierre, tal como quedaron en `GUION_PANTALLA.md`:

| cap | t | texto | dura | fuente |
|---|---|---|---|---|
| ch01 | 01:08.3 | «Dos años antes de la foto, en Madrid, hubo un baile.» | 3,5 s | voz-final |
| ch02 | 02:54.6 | «Del avión, a la tierra más roja que Víctor había visto en su vida.» | 4,4 s | voz-final |
| ch03 | 05:51.7 | «Ese mismo año, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.» | 6,1 s | voz-final |
| ch04 | 07:37.5 | «Creyeron que se llevaban de Wittenoom un hijo y nada más.» | 3,8 s | voz-final |
| ch05 | 09:53.2 | «Y no fue el único que se llevó Wittenoom adentro.» | 3,3 s | voz-final |
| ch06 | 12:04.9 | «En esa tierra vivía un hombre que no podía irse.» | 3,2 s | voz-final |
| ch07 | 13:41.5 | «Lo que sobró de la mina, sí.» | 1,9 s | voz-final |

Las 7 tienen «filtro: pasó». La de ch07 dura 1,9 s: es su lectura a 15 cps y no hay mínimo que la alargue.

Chequeos:

```
     ✓ dos bloques al mismo tiempo
     ✓ bloque que cruza un corte
     ✗ texto sin lectura
     ✓ pregunta de cierre sin lectura
     ✓ cifra que contradice la voz
     ✗ a_pantalla
     ✓ costuras con cuadro no negro
     ✗ inicio de voz por cap
     ✓ gancho no vacío
     ✗ inicio de música por cap
     ✗ papel sin colocar
     ✓ papel sin alinear
     ✓ relojes del papel (informativo)
```

Son los mismos 5 ✗ que en F72. «inicio de música por cap» es el falso positivo de C. «a_pantalla» lee la escaleta vieja (fila de `fase2b.py:3221` en B). Los otros tres no los abrí.

| archivo | antes (F72) | después (F72b) |
|---|---|---|
| `output/<tid>/GUION_PANTALLA.md` | `27c0d8c13291c6558b211cfd5c6a9595` | `6b2b9944d70efa89796bb0516172ebde` |
| `output/<tid>/GUION_PANTALLA.json` | `45c296f2a6a89b369307f0020548431e` | `4f6ba64ce1ec3376cfb9beab37298352` |

El guion sigue sin aprobar (`etapa_de` = `aprobar_guion`).

## Suite amplia (como en F71b)

Sin red, con `-n auto`: `test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, `concat_windowed`, `transition_timeout` y `test_constantes_con_origen`. Quedan fuera `fase2b_*`, `gfx_lab` y `f58`, porque escriben en disco real. Log: `lab/hyperframes/f72/suite_b/amplia.log`.

- Primera corrida: `4 failed, 1411 passed, 29 skipped, 2 xfailed`. La falla nueva era `test_module_f42_mapa::test_check_da_0`: sticker viejo de `gfx_layer.py` y `gfx_realizador.py`. Actualicé los stickers; `test_module_f42_mapa.py`: 4 passed.
- Las otras 3 son las de F71/F71b: `test_module_f51c.py::test_f51c_corte_veo_real_de_wittenoom[1-start-paredes de chapa.]` (lee una narración congelada) y `test_module_m03_merge_timing.py::test_c_guarda_de_minimo` y `::test_c_veo_path_y_veo_anchor_intacto`.
- Tests tocados (`f72b`, `f38e_b`, `f38e_a`, `f32`, `f29a`): 40 passed, 2 skipped.
- `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt`: md5 `489cb2a0…` antes y después.
- No hay 1492 como en F71b porque esta vez quedaron fuera `fase2b_reassemble` y `fase2b_hwencode`. Además, se borraron 4 tests y se sumaron 7.

## Qué entra al commit

- Código: `script_engine/gfx_realizador.py`, `script_engine/gfx_layer.py`.
- Tests: `test_module_f72b.py`, `test_module_f38e_b.py`, `test_module_f38e_a.py`, `test_module_f32.py`, `test_module_f29a.py`.
- Lab: `lab/hyperframes/f72/b_fase1_wittenoom/` (entradas congeladas), `lab/mapa/stickers/fase2b_gfx.json`.
- `lab/hyperframes/f72/F72b_REPORT.md`, `lab/ESTADO_SESION.md` y `DECISIONES.md`, que solo trae las dos líneas de Omar del 3-nov (F72 y F72b).
- Quedan fuera: los logs de la corrida y de la suite, el handoff, `diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt` y las ENTRADA.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | Handoff leído es el pedido (md5 2d92f023…) | OK | md5sum del handoff = 2d92f0238a6dc8f336d3afdd3a92fa27 |
| A1 | Pregunta de cierre = última oración de la voz del cap, fuente "voz-final"; si termina en «?», queda esa pregunta | OK | script_engine/gfx_realizador.py:175-196 (diff). `FUENTES_CIERRE=("voz-pregunta","voz-final")`; usa `voz_utils.oraciones_de_texto` |
| A2 | Borrar el emparejamiento con el cierre de la escaleta y el respaldo del cierre literal, con sus tests | OK | El diff borra ambas ramas. `grep voz-alineada` solo queda en docstrings de tests. El report dice que se borraron 3 tests de f38e_b y 1 de f29a. Los tests tocados corren: 44 passed, 2 skipped (f72b, f38e_b, f38e_a, f32, f29a, f42_mapa) |
| A3 | Simular los 7 caps de Wittenoom con texto, fuente y lectura; textos iguales a los del handoff | OK | Tabla en el report, líneas 35-43. GUION_PANTALLA.md tiene 7 "voz-final" (grep -c) y md5 6b2b9944… (confirmado). `test_module_f72b.py` pasa con las entradas congeladas: md5 b37cb3c7… y 29c3a4f3… |
| B | Inventario solo lectura (campo, archivo:línea, para qué, ¿desfasa?) | OK | Report líneas 57-87. Verifiqué por muestreo: `fase2b.py:3221` (a_pantalla de esc_full), `gfx_realizador.py:83-86` (cierre/texto/campos), `music_intensity.py:113-121`, `gfx_guion.py:498-500` (chequeo 6). Coinciden. No hay edición de código del inventario |
| C1 | Causa de la música "tarde" con archivo:línea | OK | `fase2b.py:3090-3099` (correlación cruzada normalizada con norma+1e-9 sobre tramo en ceros) y silencio de cita en `music_intensity.py:113-121`. Coincide con el código |
| C2 | dB de mezcla_preview.wav en 03:08–03:15 y 12:33–12:48 | PARCIAL | El report da mean −26,4 / −27,4 dB. Re-medí el wav actual (ya regenerado por D, 824 s): −25,9 y −26,5 dB. La diferencia es de ~1 dB y es esperable, porque el wav cambió y los offsets se movieron. El report lo aclara ("la de la corrida F72, antes del plan-only"). No puedo reproducir el valor exacto, porque el wav anterior ya no existe |
| D | `--plan-only` sin flags prohibidos; 7 preguntas con duración, chequeos, md5 nuevo, tiempo y costo | OK (con una limitación) | Report 142-192: exit 0, 203 s, US$ 0, 13 chequeos, md5 verificado. Existe `f72b_plan_only.log`. No corrí fase2b, así que no pude confirmar los flags de la línea de comando. Por el md5 y el log, coincide |
| R1 | Reglas: sin prompts ni main; solo archivos del alcance | OK | `git diff --stat` solo muestra gfx_realizador, gfx_layer, 4 tests, stickers y DECISIONES |
| R2 | Suite amplia "como en F71b" | PARCIAL | `suite_b/amplia.log` es la primera corrida: 4 failed, 1411 passed. Las 3 fallas heredadas de F71/F71b son reales. La cuarta (f42_mapa) se arregló con los stickers y se re-corrió solo ese archivo (4 passed). No hay una segunda corrida completa que deje 3 fallas. Además, la suite quedó más chica que la de F71b (sin fase2b_reassemble ni fase2b_hwencode), cosa que el report admite |
| R3 | Veredicto del revisor íntegro en el report | NO VERIFICABLE | Este veredicto es el que debe pegarse. Todavía no está en el report |
| R4 | PARADA: report, ESTADO_SESION, commit | PARCIAL | El report existe y no está vacío. ESTADO_SESION y el commit no están hechos, como se anticipó. Los pendientes son del orquestador |

Fuera de alcance: ninguno entre los archivos versionados tocados. `diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt`, `test_module_f29a.py` y otros ya venían modificados por trabajo previo, así que no los atribuyo a F72b. El report los excluye del commit. Cuidado al hacer `git add`: hay que agregar solo la lista del report (gfx_realizador.py, gfx_layer.py, los 5 tests, la carpeta b_fase1_wittenoom/, el sticker JSON, F72b_REPORT.md, ESTADO_SESION y DECISIONES).

Observaciones:
1. La suite completa no se re-corrió tras arreglar los stickers. Falta evidencia de "solo 3 fallas heredadas" en una corrida única.
2. Los 5 chequeos en ✗ siguen iguales. El de música es falso positivo, según el report y según el código leído en C. Los otros tres (texto sin lectura, inicio de voz, papel sin colocar) no se investigaron.
3. El report admite que la tabla "antes" no reproduce los 14,1 s del handoff para ch03 (su simulación da 9,00 s). Es una discrepancia sin investigar, pero no afecta el resultado de A.

Riesgos que el contrato no cubre: (a) el chequeo 6 "a_pantalla" y varios campos de la escaleta vieja (dato_central, pico) siguen leyéndose sin sello de versión, así que cualquier edición de narración los desfasa. (b) El falso positivo de música puede ocultar una regresión real. (c) Una última oración muy corta, como ch07 con 1,9 s, queda como pausa corta; no hay mínimo.

## Adenda de CC

- **Obs. 1 / R2:** después del veredicto volví a correr la suite completa, con los mismos archivos: `3 failed, 1412 passed, 29 skipped, 2 xfailed` en 66,7 s. Las 3 fallas son las heredadas: `f51c[1-start-paredes de chapa.]`, `m03_merge_timing::test_c_guarda_de_minimo` y `::test_c_veo_path_y_veo_anchor_intacto`. Log: `lab/hyperframes/f72/suite_b/amplia_2.log`. `pedido_paquetes_wittenoom.txt` sigue en `489cb2a0…`.
- **«Fuera de alcance»:** el revisor dice que `test_module_f29a.py` ya venía modificado. No es así: su diff contra HEAD es solo el test borrado en F72b y la línea del docstring (16 líneas), y no figuraba en el `git status` del arranque. Lo mismo vale para f32, f38e_a y f38e_b. Entran al commit como parte de F72b.
- **R3 y R4:** el veredicto queda pegado acá. ESTADO_SESION y el commit van a continuación.
- **Riesgo (c):** el handoff no fija un mínimo para la pausa y DECISIONES tampoco trae uno; no agregué ninguno. La pregunta de ch07 queda en 1,9 s.

PARADA.

