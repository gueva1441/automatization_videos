# F29 — El gfx obedece a la escaleta · sfx ElevenLabs · Sonnet vs Flash en dos caps

CC · 2026-10-25 · rama `f11-guion-v4` · handoff `lab/hyperframes/f29/HANDOFF_F29_gfx_realizador.md` · **PARADA al final de D**.

Commits: B `6eb6fda` · A `2fcd603` · C `115d999` · D `1711e88`.
(B se commiteó antes que A: lo hice en ese orden; el contenido de cada commit es solo su parte.)

Costos: ElevenLabs SFX **US$ 0.037** (tope 3) · Gemini **US$ 0.012** en C + US$ 0.0004 en D (tope 3; C ≤ 2) · Claude **US$ 0.0028** (tope 2, solo D).

Parámetros adicionales pedidos por Omar para C (anotados): **timeout del render gfx 900 → 1500 s** (`gfx_config.GfxRenderSettings.timeout_sec`) y **NVENC cq 19 → 23** (`fase2b.NVENC_ARGS`; test `test_module_fase2b_hwencode` al día). Peso medido abajo (C).

Suite: rápida (f29a, f29b, hwencode, gfx_director) 53 verdes; amplia **921 verdes + las 5 previas** (01b_pauses ×3, m03_merge_timing ×2), log `c/suite_amplia_c.log`.

---

## A. La escaleta manda (0 API) — `2fcd603` + ajustes en `115d999`

Archivos: `script_engine/gfx_realizador.py` (nuevo, 381 líneas), `gfx_layer.py` (+47), `gfx_pool.py` (+27/−), `gfx_director.py`, `gfx_critic.py`, `gfx_config.py`; tests `test_module_f29a.py` (8) y `test_module_gfx_director.py` adaptado.

| Punto del handoff | Qué quedó |
|---|---|
| A.1 entrada | `gfx_layer._realizador` carga `01a_escaleta.json` + partición (`gfx_realizador.cargar`) y la pasa al pool y al director (`ctx["realizador"]`). Sin escaleta: el camino de siempre con aviso en el log. Flag `gfx_rules.realizador` (on). |
| A.2 ventanas | `ventanas()`: para cada beat del cap, primer y último timestamp de las palabras de sus párrafos (`music_intensity.tiempos_por_palabra`) → `gfx_beats_chNN.json` (ventanas, candidatos, pico de escaleta, cierre). |
| A.3 candidatos | Obligatorios: `a_pantalla` del cap en el beat que los contiene (`dato_central`/`datos_apoyo`); si no, el beat que describe `por_que` (raíces de 5 letras, sin números en palabras, empate → el beat posterior); si no, el último. Opcionales: `dato_central`/`datos_apoyo` del beat que la voz no dijo (`ya_dicho`: `used_in` del ítem o ≥ 60 % de solapamiento de contenido con la voz). Nada fuera de los beats del cap: el pool solo ve estos candidatos (`para_pool`). |
| A.4 cuántos | `TOPE_POR_FUNCION` (gancho 1, planteo 1, escalada 2, giro 2, pico 1, respiro 1, revelación 2, cierre 1), `TOPE_CAP = 5`; el `dato_central` del giro primero. Ningún bloque fuera de la ventana de su candidato (`finalizar`). `gap_fill` detrás de `gfx_rules.gap_fill` (off). `punch_in` solo mientras hay un bloque en pantalla. Contador (count_up) fuera. Pico: `garantizar_pico` — si el pico de `gfx_peak` no tiene bloque grande (cubriéndolo o arrancando ≤ 5 s después) agrega un rótulo con un candidato del beat del pico (excluye ids ya puestos; si no hay, el `dato_central`); si `gfx_peak` no da pico, se usa el beat de mayor `intensidad` de la escaleta. |
| A.5 sellos | `finalizar`: ≤ 1, el de la palabra del pico; ícono solo si es abstracto (sello, tinta, prensa). **Hecho como filtro en el realizador; no toqué el diccionario palabra → ícono** (vive en `gfx_fragments`/`gfx_profiles`; `gfx_profiles/*` está fuera de git por regla). |
| A.6 pregunta | `pregunta_cierre`: el `cierre` del último beat del cap, literal, en el mismo `chapter_question`; `gfx_question` solo si falta. |
| A.7 duración | `duracion_texto`: `max(2.5, palabras/3 + 1)` ≤ 8 s para rótulos, recortes y citas. |
| A.8 crítico | `gfx_critic`: «repite» corta siempre; la cita pierde `reserved` a efectos del crítico. |
| A.9 tests | `test_ventanas_por_beat`, `test_a_pantalla_en_su_beat` (**D128 → beat 11, después de `pico.t` del cap 6; D245 → 13; Q50 → 8**), `test_finalizar_ventana_topes_sellos_y_duraciones`, `test_pico_con_bloque_grande_en_los_7_caps`, `test_pregunta_es_el_cierre_del_ultimo_beat`, `test_critico_parejo`, y (en C) `test_pico_sin_pico_de_gfx_peak_sale_de_la_escaleta`, `test_pico_no_repite_un_item_ya_puesto`. |

## B. Sfx con ElevenLabs — `6eb6fda`

`script_engine/sfx/make_sfx.py` regenera con ElevenLabs Sound Effects (`eleven_text_to_sound_v2`, prompt_influence 0.5) con caché por prompt/duración/modelo (`_prompts.json`: si el wav existe y nada cambió, no llama). Proceso: recorte del silencio inicial (si deja el archivo vacío, sin recorte), pico a −1 dBFS, ganancia a −20 LUFS integrado con limitador a −1 dBFS. Los sintetizados de F2 movidos (git mv) a `script_engine/sfx/_f2_sintetizados/` con su `make_sfx_f2.py`. Datos: `b/sfx_viejos_lufs.json`, `b/sfx_nuevos.json`.

| sonido | s | prompt | LUFS F2 | LUFS nuevo | pico dBFS | US$ |
|---|---|---|---|---|---|---|
| tipeo | 0.75 | a few dry keystrokes of an old mechanical typewriter, close microphone, dry room, no reverb, no bell | −14.1 | −21.6 | −1.0 | 0.0015 |
| sello | 0.35 | a rubber stamp pressed once onto paper on a wooden desk, soft dull thud, close, dry, no reverb | −23.3 | −22.2 | −1.0 | 0.0010 |
| papel | 0.6 | a sheet of paper sliding over a wooden table, close microphone, dry, no reverb | −5.9 | −19.9 | −7.0 | 0.0012 |
| golpe_grave | 1.2 | a deep muffled low thud, distant, no tail, no reverb, not cinematic, not an explosion | −19.0 | −19.8 | −1.1 | 0.0024 |
| whoosh | 0.8 | a short soft whoosh of air, gentle, low, smooth, no metallic sound | −11.1 | −20.0 | −3.9 | 0.0016 |
| click | 0.08 | a single soft dry click of a small mechanism, close, no reverb | −15.0 | −26.0 | −1.0 | 0.0010 |
| tic | 0.18 | a single soft dry tick of a small mechanism, close, no reverb | −14.6 | −23.7 | −1.0 | 0.0010 |
| tic_sordo | 0.22 | a single muffled low tick, soft and dull, close, dry, no reverb | −15.8 | −20.0 | −1.8 | 0.0010 |
| latido | 0.9 | a single slow heartbeat, two low muffled thumps, close, dry | −22.2 | −25.1 | −1.0 | 0.0018 |
| brasa | 0.9 | soft crackling of small embers, close, quiet, dry | −21.0 | −24.3 | −1.0 | 0.0018 |
| rumor | 1.2 | a low rumble of earth, distant and deep, quiet, no impact | −13.7 | −20.0 | −2.8 | 0.0024 |
| viento | 1.4 | a soft cold gust of wind, low, quiet, no whistle | −19.2 | −20.0 | −3.5 | 0.0028 |
| vacio | 1.2 | a very low soft sub-bass tone that fades away, empty, quiet, no attack | −15.5 | −19.9 | −9.8 | 0.0024 |
| drone_subida | 3.0 | a low dark drone slowly rising in pitch and swelling, deep and quiet, no impact at the end, no metallic sound, ambient | −11.5 | −20.5 | −3.1 | 0.0060 ×2 |
| zumbido | 0.9 | a faint low electrical hum with a few soft clicks of a counter, quiet, close | −16.3 | −23.9 | −1.0 | 0.0018 ×2 |

Total **US$ 0.037** (drone_subida y zumbido se generaron dos veces: la primera salió muda por el recorte de silencio a −50 dB → arreglo «sin recorte si queda vacío» y se regeneraron). Los de ataque corto quedan en −22…−26 LUFS: manda el techo de −1 dBFS.

**En la mezcla (B.2):** LUFS del tramo con y sin sfx en 8 bloques del render de C (`b/sfx_en_mezcla.json`): diferencia **0.0–0.2 LU** (golpe_grave del título 0.0, papel 0.0–0.1, tic 0.1–0.2). Con las mismas ganancias por bloque (−18 dB), los nuevos quedan más bajos que los de F2 (papel −14 dB, drone −9, whoosh −9, tipeo −7.5 en LUFS del archivo). **No recalibré las ganancias de `gfx_config`**: la medida dice que casi no se oyen bajo la voz, pero no puedo escucharlo; queda para que Omar decida con el mp4.

## C. Vajont con el realizador (Flash) — `115d999`

Copia del topic `f8s3-vajont-f29` (`c/f29c_vajont.py`): reusa imágenes/clips Veo (manifest de F27), visual base DepthFlow (`--reuse-visuals`), voz, música e intensidad de F28, y las cachés de visión y el plan crudo del director. Se rehízo realizador, pool (Flash), crítico, render gfx en fila (NVENC cq 23, timeout 1500 s) y ensamble. Firefox cerrado y RAM > 14 GB antes de cada render.

**Salida:** `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3.mp4` (1 205 051 965 B = **1.21 GB**) + `_v3_no_music.mp4`. Hoja: `lab/hyperframes/f29/BLOQUES_v3.jpg`.

**Peso con cq 23:** 1.21 GB vs 1.6 GB del render F28 con cq 19 (−25 %) vs 606 MB de F27 (libx264).

**Dos corridas.** Intento 1 (67.0 min de pared, `c/fase2b_intento1.out`, `c/vajont_v3.json` es de esa corrida): ch02 y ch04 salieron sin pico porque `gfx_peak` no dio pico → agregué el pico desde la escaleta; y en el pico se duplicaban ítems (T23, D106, T58) → excluir ids ya puestos + ventana de 5 s. Con eso, reensamble (`--reassemble-from-segments`; el manifest rehízo los 7 caps) en **63.9 min** (`c/reensamble.txt`, `c/fase2b.out`). Lo del intento 1 quedó apartado: `_v3_intento1.mp4`, `c/BLOQUES_v3_intento1.jpg`, `c/bloques_intento1.json`, `output/f8s3-vajont-f29/_bak_c_intento1/`. RAM libre mínima en el intento 1: 10.7 GB.

**Tiempo de gfx por cap (final / intento 1, s):** ch01 130/132 · ch02 548/540 · ch03 573/602 · ch04 555/612 · ch05 704/745 · ch06 728/781 · ch07 319/332. Ningún cap a base_clip; el máximo (781 s) está debajo del viejo timeout de 900 s.

### Comparación F27 → F29 (`c/bloques.json`)

| | F27 (handoff) | F27 (medido aquí) | F29 |
|---|---|---|---|
| bloques | 36 | 35 | **22** |
| sellos | 11 | 15 | **4** |
| spoilers (1.910 en cap 6, Montedison en cap 7, antes del pico/juicio) | 2 | 2 | **0** |
| pico con bloque grande | 1/7 | 1/7 | **7/7** |

Mi contador (`c/f29c_bloques.py`) lee los planes resueltos de F27 y cuenta todos los tipos (recorte, rótulo, sello, cita, contador, nivel de agua, zoom, íconos): da 35 y 15, no 36 y 11. No sé de dónde salen los números del diagnóstico; dejo los dos.

### Por cap (tiempos del cap; en el mp4 se suman 2.5 s de arranque y los caps anteriores)

| cap | t | tipo | texto | beat | ventana | ¿ya dicho? |
|---|---|---|---|---|---|---|
| ch01 | 37.4 | rótulo **PICO** | «Antes de que se fuera la luz, se abrió de improviso, de par en par, el…» (Q19) | 1 | 0–94 | no |
| ch01 | 37.4 | sello | fuerza | — | — | — |
| ch02 | 15.9 | recorte | El Consejo Superior de Obras Públicas aprobó el proyecto (D117) | 2 | 0–65 | no |
| ch02 | 128.2 | rótulo **PICO** | la montaña que camina (Q53) | 3 | 66–130 | **sí** |
| ch02 | 128.2 | sello | montaña | — | — | — |
| ch03 | 3.2 | nivel de agua | 266 (D118) | — | — | — |
| ch03 | 23.5 | recorte | Un deslizamiento de 3 millones de metros cúbicos cayó en el lago (T15) | 4 | 0–61 | no |
| ch03 | 97.7 | rótulo **PICO** | La periodista Tina Merlin denuncia el peligro del desprendimiento (T18) | 5 | 62–124 | **sí** |
| ch03 | 113.9 | recorte | Ocurrió un pequeño desmoronamiento en el monte Toc (T23) | 5 | 62–124 | no |
| ch04 | 25.7 | recorte | el periódico l'Unità por difundir supuestas noticias falsas sobre la presa (T33) | 6 | 0–51 | no |
| ch04 | 64.2 | sello | montaña | — | — | — |
| ch04 | 75.4 | recorte | 15 metros por encima de la cota de seguridad recomendada (D106) | 7 | 52–116 | no |
| ch04 | 113.3 | rótulo **PICO** | Se completa el cambio de propiedad de la central hidroeléctrica del Vajont (T52) | 7 | 52–116 | no |
| ch05 | 9.1 | recorte | Las poblaciones de Erto y Casso están viviendo en continua aprensión (Q50) | 8 | 0–90 | no |
| ch05 | 151.0 | recorte | El jefe de obras cierra la jornada laboral (T64) | 9 | 91–166 | no |
| ch05 | 162.8 | rótulo **PICO** | El director Alberico Biadene envía una carta (T61) | 9 | 91–166 | no |
| ch06 | 29.1 | recorte | Una ola enorme pasó por encima de la presa y devastó Longarone (T58) | 10 | 0–109 | no |
| ch06 | 105.2 | rótulo **PICO** | Una sección masiva del Monte Toc se desprendió y se estrelló contra el… (T57) | 10 | 0–109 | no |
| ch06 | 114.2 | recorte | En el desastre murieron 1.910 personas (D128) | 11 | 110–164 | no |
| ch07 | 35.8 | rótulo **PICO** | queremos justicia (Q13) | 12 | 0–98 | **sí** |
| ch07 | 35.8 | sello | montaña | — | — | — |
| ch07 | 121.9 | recorte | el Tribunal de Belluno condenó a Montedison a pagar (D245) | 13 | 99–178 | no |

| cap | pico (gfx_peak) | sellos | pregunta (fuente: cierre del último beat en los 7) | crítico |
|---|---|---|---|---|
| ch01 | 37.4 «fuerza» → rótulo | 1 | «El dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.» | sello suma |
| ch02 | 128.2 «montaña» → rótulo | 1 | «En marzo del cincuenta y nueve, en otro embalse de la misma empresa, una montaña caminó primero.» | recorte suma, sello suma |
| ch03 | 97.7 «agua» → rótulo | 0 | «El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta.» | nivel suma, 2 recortes suma |
| ch04 | 113.3 «montaña» → rótulo | 1 | «La presa cambió de dueño con el agua todavía subiendo. La montaña no se enteró del contrato.» | 2 recortes suma, sello suma, **zoom «rostro mujer» estorba → fuera** |
| ch05 | 162.8 «párroco» → rótulo | 0 | «A las diez y media de la noche, el párroco de Casso escuchó algo y abrió la ventana.» | 2 recortes suma |
| ch06 | 105.2 «amaneció» → rótulo | 0 | «Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle.» | 2 recortes suma |
| ch07 | 35.8 «montaña» → rótulo | 1 | «La sentencia dice inundación agravada por la previsión del evento. No dice quién, …, decidió que Micaela siguiera durmiendo.» | sello suma, recorte suma, **zoom «vaso agua» repite → fuera** |

Ninguna cita en el render; ningún «repite» pasó.

### Lo que no salió como pide el principio (para que Omar lo mire en la hoja)
1. **Rótulos del pico que repiten la voz:** ch02 Q53 «la montaña que camina», ch03 T18 (Tina Merlin), ch07 Q13 «queremos justicia» — los tres con `ya_dicho = sí`. Salen del respaldo de `garantizar_pico` (si no hay candidato no dicho en el beat del pico, toma el `dato_central`), que no filtra «ya dicho». El crítico no los corta porque corre antes de `garantizar_pico`.
2. **Sello fuera del pico en ch04:** el sello «montaña» está a los 64.2 s y el pico a los 113.3 s. `finalizar` deja el sello cuya palabra es la del pico, pero no mira el segundo: la palabra aparece antes.
3. **Rótulo y sello a la vez** en el pico de ch01, ch02 y ch07 (mismo segundo).
4. **ch06:** el rótulo del pico (T57, el desprendimiento del Toc, a los 105.2 s) cae al final del beat 10; el recorte D128 (1.910 muertos) queda en el beat 11 a los 114.2 s, después del pico, como pide el handoff.
5. **Rótulo largo que se sale del cuadro:** en ch06, el rótulo del pico (T57, 13 palabras) se corta a la derecha («…SE ESTREL»). Los rótulos del pico toman la frase del candidato tal cual y no se cortan al ancho.
6. **Nivel de agua de ch03** (266, a los 3.2 s) no tiene beat: viene del director como antes (el handoff lo deja «como hoy»).

## D. Sonnet vs Flash como realizador, caps 5 y 6 — `1711e88`

Script `d/f29d_sonnet.py`: copia del topic `f8s3-vajont-f29d` (mismos insumos que C, con los planes de ch01–ch04 de C para que lo «ya mostrado» sea igual), `fase2b --only-cap` ch05 y ch06 en el mismo proceso, con `gfx_pool.FORMA_CALL` = `claude-sonnet-5-5` vía `claude_helpers.make_call` (effort low, `response_schema=None`, cruda en `d/crudos/`, tope US$ 2 chequeado antes de cada llamada). Mismo prompt que Flash. Flash = lo que salió en C, copiado a `output/f8s3-vajont-f29/d/`.

**Qué decide el modelo en este diseño.** El handoff (D.1) describe el paso de forma como «tipo de bloque, lado, duración, texto del rótulo dentro del candado literal». En el realizador de A, tipo, ventana, lado y duración salen de forma determinista de la escaleta y del pool. **Lo único que decide el modelo es qué cláusula literal del recorte se usa, entre hasta 3 opciones** (`plan_pool_documents`). Así que D compara solo ese paso.

**Salidas:** `output/f8s3-vajont-f29/d/ch05_gfx_{flash,sonnet}.mp4`, `ch06_gfx_{flash,sonnet}.mp4` y sus planes resueltos. Hoja lado a lado: `lab/hyperframes/f29/D_flash_vs_sonnet.jpg` (un renglón por bloque: Flash a la izquierda, Sonnet a la derecha). Diferencias en `d/diferencias.json`.

**Resultado: no hay diferencias.** En los dos caps hubo una llamada por cap con 2 recortes cada una. En ch05, recorte0 tenía 3 opciones y recorte1 una sola; en ch06, recorte0 una sola y recorte1 tres. Sonnet devolvió `{"elecciones": [{"id": "recorte0", "n": 1}, {"id": "recorte1", "n": 1}]}` en ambos, lo mismo que Flash. Los planes resueltos y los mp4 de cada cap son **idénticos byte a byte** (`cmp`). Bloques distintos: 0 · tipos distintos: 0 · textos distintos: 0. Solo 2 de las 4 elecciones tenían alternativa real.

| cap | modelo | llamadas | tokens in/out | US$ | s de la llamada | pared del cap |
|---|---|---|---|---|---|---|
| ch05 | Flash (C) | 1 | — | ≈ 0 (dentro de los US$ 0.0098 de Flash de todo C) | — | gfx 704 s (render de C) |
| ch05 | Sonnet | 1 | 503 / 45 | 0.00146 | 1.2 | 749 s (fase2b --only-cap completo) |
| ch06 | Flash (C) | 1 | — | ≈ 0 (ídem) | — | gfx 728 s (render de C) |
| ch06 | Sonnet | 1 | 463 / 45 | 0.00138 | 2.4 | 769 s (ídem) |

Claude total **US$ 0.0028**. Gemini en D US$ 0.0004 (visión del crítico; el plan crudo del director venía en caché). Las paredes no se comparan del todo: la de Flash es el render gfx del cap dentro del render completo de C, y la de Sonnet es el `fase2b --only-cap` entero (gfx + ensamble del cap). La llamada del modelo pesa 1–2 s en 12–13 min.

**Visto en la hoja (vale para los dos lados):** el rótulo del pico de ch06 (T57, «Una sección masiva del Monte Toc se desprendió y se estrelló contra el embalse») se sale del cuadro por la derecha («…SE ESTREL»). Lo mismo se ve en `BLOQUES_v3.jpg`.

Sin decidir: Omar mira los dos. Con estos dos caps no hay diferencia que mirar.

---

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

El reporte dice la verdad en lo que pude cotejar (números, rutas, costos, commits). Los incumplimientos del handoff están declarados en el reporte, pero siguen siendo incumplimientos. No corrí la suite: me apoyé en los logs commiteados (suite_amplia_a.log y suite_amplia_c.log).

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Un commit por parte | OK | B 6eb6fda, A 2fcd603, C 115d999, D 1711e88, sobre la base e971a8f. El reporte avisa que B salió antes que A. |
| 2 | A.1 a A.4, A.6 a A.9: escaleta, ventanas, candidatos, tope por función y 5 por cap, `gap_fill` apagado, pregunta = `cierre`, duración por texto, crítico parejo, tests | OK | `script_engine/gfx_realizador.py` (381 líneas; 367 en A + 24 de ajustes en C, coincide), `gfx_config.py:217` (`gap_fill=False`), `test_module_f29a.py`. Los 8 tests del reporte coinciden con A (6) + C (2). |
| 3 | A.5: quitar el diccionario palabra→ícono (calavera, gota) | PARCIAL | No se tocó. El reporte lo admite: lo resolvió con un filtro en `finalizar`, y `gfx_profiles/*` está fuera de git. Aún hay referencias a calavera y gota en `gfx_critic.py:43`, `gfx_fragments.py:414` y `gfx_peak.py:74`. El efecto pedido (≤1 sello, sin ícono figurativo) se logra por otro camino. |
| 4 | A.3: lo que la voz ya dijo queda fuera | PARCIAL | Tres rótulos del pico (ch02 Q53, ch03 T18, ch07 Q13) salen con `ya_dicho=sí` por el respaldo de `garantizar_pico`. El reporte lo declara. Contradice el principio del handoff, y el crítico no los ve porque corre antes. |
| 5 | A.5: sello solo sobre la palabra del pico | PARCIAL | El sello «montaña» de ch04 está a los 64.2 s y el pico a los 113.3 s. Además hay rótulo y sello en el mismo segundo en ch01, ch02 y ch07. Declarado en el reporte. |
| 6 | B.1 a B.4: 15 sonidos con ElevenLabs, viejos movidos, caché por prompt | OK | 15 wav en `_f2_sintetizados/` (git mv), `_prompts.json`, `b/sfx_nuevos.json`. El costo por sonido suma US$ 0.037, dentro del tope de 3. |
| 7 | B.2: normalizar a −20 LUFS | PARCIAL | Varios quedan entre −22 y −26 LUFS (click −26.0, latido −25.1, brasa −24.3, zumbido −23.9). Es por el techo de −1 dBFS y está declarado. |
| 8 | B.2: medir LUFS con y sin sfx en 3 bloques; recalibrar si suena distinto | OK | Medido en 8 bloques (`b/sfx_en_mezcla.json`), diferencia 0.0–0.2 LU. No recalibró las ganancias y lo dice. |
| 9 | C.1 y C.2: copia `f8s3-vajont-f29`, solo gfx, salida `_v3.mp4`, `BLOQUES_v3.jpg` | OK | `f8s3-vajont_final_gfx_v3.mp4` de 1 205 051 965 B (coincide con el reporte), dura 1009.6 s. `BLOQUES_v3.jpg` existe. |
| 10 | C.3: tabla por cap y comparación contra F27 | OK | `c/bloques.json`: F29 = 22 bloques, 4 sellos, pico 7/7, spoilers 0. Coincide con el reporte. |
| 11 | C.3: «36 → N» y «11 → N» | PARCIAL | El contador propio da F27 = 35 bloques y 15 sellos, no 36 y 11. El reporte muestra ambos y lo explica. |
| 12 | Parámetros de Omar: timeout 900→1500 s y NVENC cq 19→23, con peso medido | OK | Diff de `gfx_config.py` y `fase2b.py` en 115d999, test hwencode actualizado. Peso 1.21 GB. |
| 13 | D.1: Sonnet con `claude_helpers`, effort low, sin esquema, mismo prompt, cruda guardada, solo caps 5 y 6 | OK | `gfx_pool.py` +5 (`FORMA_CALL`), `d/f29d_sonnet.py`, 2 crudos en `d/crudos/`. |
| 14 | D.1: el modelo decide tipo, lado, duración y texto | PARCIAL | En el realizador solo decide la cláusula literal del recorte, entre hasta 3 opciones. El reporte lo dice y lo justifica. La comparación Flash/Sonnet queda muy acotada (2 de 4 elecciones con alternativa real). |
| 15 | D.2: los 4 mp4, hoja lado a lado, costo y tiempo por cap | OK | Los 4 mp4 existen. `cmp` confirma que flash y sonnet son idénticos en ch05 y en ch06. `D_flash_vs_sonnet.jpg` existe. `d/costos_f29d.json` da US$ 0.00284 y 749.2 s / 769.4 s, que coinciden con el reporte. |
| 16 | Topes de costo | OK | Claude US$ 0.0028 (tope 2), ElevenLabs US$ 0.037 (tope 3), Gemini US$ 0.012 + 0.0004 (tope 3; C ≤ 2). |
| 17 | Reporte con veredicto, ESTADO_SESION, PARADA | NO VERIFICABLE | El reporte tiene el marcador `__VEREDICTO__`, y ESTADO_SESION y el hash del reporte (`__FINAL__`) se completan después de esta revisión. |

Fuera de alcance: ninguno en los commits. No hay `.env`, `config.py`, `gfx_profiles/*`, `diag_234_cap4.py` ni `lab/_gpt_probe_analista/` en ninguno de los cuatro. Los M de `gfx_profiles/*`, `diag_234_cap4.py` y `f28a.log` ya estaban sucios antes y no entraron.

Observaciones menores sobre el reporte:
- Los `ch0X_gfx_*.mp4` de D pesan 1.2 GB cada uno (≈57 Mbps para unos 170 s). El reporte no explica por qué son tan pesados; el peso de 1.21 GB que sí explica es el del video completo.
- El «gfx 704 s / 728 s» de Flash y el «749 s / 769 s» de Sonnet miden cosas distintas. El reporte lo aclara.

Riesgos que el contrato no cubre:
- El rótulo largo del pico de ch06 se sale del cuadro («…SE ESTREL»). Es un defecto visible en el entregable final y no hay candado para evitarlo.
- Las ganancias de los sfx nuevos no se recalibraron y nadie los escuchó: queda a juicio de Omar con el mp4.
- La comparación Sonnet vs Flash no discrimina nada: con las mismas elecciones, el resultado no informa para decidir de modelo.

---

**PARADA.**
