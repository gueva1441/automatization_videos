# F36 — Estructura de la capa de texto: partir, arreglar, alimentar, borrar

CC · 2026-10-26 · Handoff `lab/hyperframes/f36/HANDOFF_F36_estructura.md`. Base `1973ba1`. Rama `f11-guion-v4`. Procedimiento
`/tanda` (pasos 1–12). Sin render, sin `--aprobar-guion`, sin merge. Topic de prueba `f8s3-vajont-f30`.

## Paso 0
- `DECISIONES.md` commiteado tal cual lo dejó el analista (16:49), sin editar: commit `74a309f`.
- Leídos enteros: `CLAUDE.md`, `DECISIONES.md`, `lab/ESTADO_SESION.md` (cabecera, F34, F33), el handoff,
  `lab/hyperframes/f34/REVISION_GUION.md` (su tabla DEBERÍA es el contrato), `lab/hyperframes/f34/F34_REPORT.md` (§B),
  `.claude/commands/tanda.md`, el rotulista entero (1.911 líneas), `gfx_peak`, `gfx_critic`, `gfx_realizador.finalizar`,
  `gfx_layer.apply_gfx` (tramo del plan), `gfx_guion.chequeos`, `lab/tools/mapa_*.py`.
- **Base medida antes de tocar nada:** `fase2b f8s3-vajont-f30 --plan-only --rotulista` sobre `1973ba1` (todo en caché,
  US$ 0) da un guion igual al de F34 B salvo cuatro claves de la corrida: `generado`, `tiempos_s`, `costos` (lo que
  gastó esa corrida) y `mezcla.segundos` (tiempo de pared). El comparador `lab/hyperframes/f36/diff_guion.py` saca esas
  cuatro; el handoff nombra las dos primeras, las otras dos son de la misma clase (anotado). `a/plan_only_base.log`,
  `a/GUION_base.json`.

## Módulos que toca la tanda (paso 2; sticker de `lab/MAPA_MODULOS.md`)
| módulo | qué hace hoy (sticker) | qué hace después |
|---|---|---|
| `gfx_rotulista` | escribe los textos de pantalla, los filtra, los coloca, pone sellos de clima, reloj, agua y tarjeta (1.911 líneas) | A: fachada (`preparar_cap`, `prefetch`, re-exports) |
| `rotulista_llm` / `rotulista_filtros` / `rotulista_colocar` / `clima` / `voz_datos` / `voz_utils` | — (nuevos) | A: el código del rotulista, movido; B–C: los arreglos |
| `gfx_peak` | el pico del cap y la palabra de más peso | A: `peak_word` pasa a `clima` (re-export); D: se borra lo muerto |
| `gfx_realizador` | ventanas por beat, topes, borra todo `count_up` | B.1: no borra el contador del rotulista |
| `gfx_critic` | saca lo que repite o estorba, después del reparto | B.2: corre antes del reparto; a sello de clima y agua solo «¿estorba?» |
| `gfx_guion` | escribe el guion y sus chequeos | B.5: chequeo de cifras con la vecindad; B.9: la tarjeta en la intro |
| `gfx_sparse` / `fase2b` | intro de 2.5 s con el primer cuadro congelado | B.9: con tarjeta, 3 s de negro con la tarjeta |
| `gfx_fragments`, `gfx_question`, `gfx_identity`, plantillas `data_callout`/`grade_css` | muertos o respaldo | D: se borran |
| `gfx_layer` | el director de orquesta | B.2: el orden crítico → reparto; D: solo imports |
| `lab/MAPA_MODULOS.*` | el mapa | se regenera en cada parte; al final 0 muertos |

---

## Parte A — partir `gfx_rotulista.py` sin cambiar comportamiento (commit A)

### Qué se hizo
- El código se **movió con un script** que corta el archivo de `1973ba1` por rangos de líneas (no se retipeó):
  | módulo | líneas | qué tiene |
  |---|---|---|
  | `rotulista_llm.py` | 407 | prompts (`ROTULISTA_SYSTEM/USER`, `PROMPT_VERSION`, los de F29c/F32), `entrada`, `items_cap`, `items_gancho`, `ya_mostrado`, `voz_del_video`, `voz_previa`, `prompt_user`, `llamar`, caché, ledger, tope, reintento |
  | `rotulista_filtros.py` | 333 | `validar` como `ORDEN` de filtros nombrados, `finalizar` (= `cantidad`), `contradicciones`, `pide_documento`, `lo_que_pide` |
  | `rotulista_colocar.py` | 539 | `tiempos`, `despues_del_corte`, `caracteres`, `LECTURA_CPS`, `colocar`, `animacion_de_cifra`, ediciones (`aplicar_ediciones`, `guardar_ediciones`, `mover_a_escena`), `lupa_de_detalles`, `unidades`, `escena_final` |
  | `clima.py` | 245 | `sellos_por_tema`, `elegir_clima`, `palabra_clima`, `vocabulario_clima`, `SELLO_CLIMA_PROMPT`, `TEMA_DE_MOOD`, `_gemini_clima`, `peak_word` (traído de `gfx_peak`) |
  | `voz_datos.py` | 231 | `pico_cap`, `pico_plan`, `reloj_de_voz`, `fechas_completas`, `agua_de_voz`, `tarjeta_inicial` |
  | `voz_utils.py` | 244 | los parsers de español (`numeros`, `numero_en`, `nombres`, `nombre_inicial`, `munon`, `palabras_de_contenido`, `_analiza` y sus tablas) y `oraciones`/`beat_de_oracion` |
  | `gfx_rotulista.py` | 117 | fachada: `preparar_cap`, `prefetch` y el re-export de **todos** los nombres que tenía (test que lo controla contra el código de F34) |
- **Decisión anotada (el handoff la deja a CC):** los parsers de español van a `voz_utils.py` porque los usan cuatro
  de los cinco módulos (llm, colocar, clima, voz_datos) además de filtros. `oraciones` y `beat_de_oracion` también van ahí
  (los usan `entrada` y `validar`; si quedaban en `rotulista_llm`, filtros y llm se importaban en círculo).
  `contradicciones` y `finalizar` quedan en filtros, como pide el handoff. `rotulista_colocar.colocar` importa
  `validar`/`FICHA` adentro de la función (filtros importa colocar arriba por `tiempos`).
- Únicos cambios a mano sobre lo movido: esos imports; `clima.peak_word` importa `lexicon_hits`/`prefer_icon_nouns` de
  `gfx_peak` adentro (para no importarse en círculo); `gfx_peak` re-exporta `peak_word` desde `clima` (lo usan su
  `add_peak_word` y `test_module_f5f`).
- **`validar` como lista ordenada y nombrada:** `ORDEN = [anclaje, gancho_dicho, forma, candado, no_dicho, spoiler,
  lectura, coherencia, cantidad]`; cada filtro es `(bloque, ent, ctx) -> motivo|None`, sale con su `regla` (el nombre;
  `gancho_dicho` sale como `no_dicho`, que es como salía), `cantidad` corre sobre el lote. **Discrepancia con el
  handoff, anotada:** el handoff escribe `[anclaje, forma, candado, no_dicho, spoiler, coherencia, lectura, cantidad]`,
  pero el código de F34 corre **lectura antes que coherencia** y el no-dicho del gancho **antes que la forma**; como A no
  cambia comportamiento, `ORDEN` es el de F34 (leído del código, no de memoria) y el test lo fija contra `1973ba1`.
  Si se quiere coherencia antes que lectura, es un cambio de comportamiento para otra parte.
- Un test viejo cambia de blanco de `monkeypatch` (no de import): `test_module_f34.py` parcheaba
  `gro.vocabulario_clima`; `sellos_por_tema` ahora vive en `clima`, así que parchea `clima.vocabulario_clima`.
- `guard_mapa` (hook) avisa también por `rotulista_*.py`, `clima.py`, `voz_datos.py`, `voz_utils.py`; `mapa_hechos`
  los incluye; `mapa_modulos` tiene sus seis stickers.
- Tests nuevos `test_module_f36.py` (4): el `ORDEN` es exactamente la secuencia de reglas de `validar` + `finalizar` de
  `1973ba1` (leída del código con `git show`), la fachada tiene todos los nombres de nivel de módulo de F34, cada
  nombre vive en su módulo (y el md5 del prompt sigue `d90ae69a…`), `guard_mapa` avisa por los módulos nuevos.
- Para chequear nombres sin definir se instaló `pyflakes` en el Python global (`pip install pyflakes`).

### Verificación (la que exige el handoff)
- `fase2b f8s3-vajont-f30 --plan-only --rotulista --rotulista-tope 0.97` (ledger US$ 0.9637 + 0.01: solo caché) →
  184 s, Claude US$ 0, costo total US$ 0 (`a/plan_only.log`). Guion copiado a `a/GUION_PANTALLA.md/.json`.
- **Diff contra `lab/hyperframes/f34/GUION_PANTALLA.json`: vacío** (`a/diff_guion.txt`, pegado entero):
  ```
  --- 0 líneas distintas
  ```
- md5 `fase2b ba6c3cac… --only-cap ch02 --reuse-visuals --sw-encode` = `38e5ba14e3d24fd20f9297c9e1dfee24`.
- Suite rápida 58 · suite amplia **1025 pasan + las 5 previas** (01b_pauses ×3, m03_merge_timing ×2) = 1021 de F34 +
  4 de `test_module_f36.py` (`a/suite_*.log`).
- Firefox cerrado (cierre normal, 12 procesos → 0) y RAM 16.9 GB libres antes de la primera corrida; 15.4 GB antes del md5.
- Mapa regenerado: 43 módulos · 146 aristas · 14 muertos (los mismos de F33; se borran en D).

### Salida de A: el guion (igual al de F34 B)
`lab/hyperframes/f36/a/GUION_PANTALLA.md` (338 líneas) es el mismo guion de F34 B; lo que queda en pantalla:
- ch01: tarjeta «9 OCT 1963 · 22:39» 0:00 · sello PÁNICO 39.9 · reloj 9 OCT · 1963 76.0. Sin texto.
- ch02: recorte D117 «CONSEJO SUPERIOR DE OBRAS PÚBLICAS, 1943 · Aprobó la presa con 13 de 34 representantes presentes» 128.7 · punch 183.7.
- ch03: agua OLA 20 m 250.7 · punch 250.7 · sello AMENAZA 266.7 · ficha D71 «L'UNITÀ · Diario del Partido Comunista Italiano» 316.2.
- ch04: reloj 4 NOV · 1960 390.6 · ficha T39 «ROCA EN RIESGO DE DERRUMBE SOBRE ERTO · 50 millones de m³» 423.5 · sello AMENAZA 447.2 · punch 458.3 · agua COTA AUTORIZADA 715 m 464.1.
- ch05: punch 527.1 · sello AMENAZA 531.9 · reloj 9 OCT · 1963 596.5 · sello INMINENTE 660.1.
- ch06: punch 707.5 · sello SILENCIO 799.0 · ficha D192 «TÉCNICOS MUERTOS EN EL CENTRO DE CONTROL · 20 técnicos en el estribo izquierdo» 822.2.
- ch07: punch 877.1 · sello AMENAZA 897.6 · reloj 20 FEB · 1968 943.6 · ficha D245 «CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras al municipio de Longarone» 994.2.

### A — simulador contra DEBERÍA
#### Guion de Vajont de F36-A contra el contrato (tabla «DEBERÍA por línea» de F34) — agente `simulador`, íntegro

**Cumple 0 de 15 líneas. Ninguna se resolvió antes de lo previsto.** Es lo esperado: después de A no se esperaba ninguna.

**El guion de A es idéntico al de F34 B.**
- Los 210 eventos son iguales campo por campo.
- También son iguales todos los metadatos de cada cap y los `chequeos`.
- Lo único que cambia es `generado`, `tiempos_s`, `mezcla.segundos` (13.3 contra 11.3) y `costos.claude_rotulista_usd` (0.0 contra 0.4633). Esto último sale de la caché del modelo.
- La comparación también da igual contra `lab/hyperframes/f36/a/GUION_base.json`. `diff_guion.txt` dice «0 líneas distintas».
- Los datos brutos (`rotulista_chNN.raw.json`, `sellos_clima_chNN.json`, `gfx_critic_*.json`) son de F34 B, de las 15:39–15:45. Solo los `gfx_plan_chNN.resolved.json` son de la corrida de A, de las 17:07–17:08.

#### 1. Totales

Conté como texto solo los de tipo ficha, recorte, cita, lupa, persona y contador con `queda: true`. Como sello conté solo los sellos con `queda: true`.

| Concepto | Esperado (DEBERÍA) | Salió con la lista | ¿Sí/No? |
|---|---|---|---|
| Textos | 9: D195 o D118, D117, D49, T39, Q50, D128, D192, T85, D245 | 5: D117, **D71** (sobra), T39, D192, D245. Coinciden 4 de 9; faltan D195/D118, D49, Q50, D128 y T85. | **No** (5 de 9) |
| Sellos | 9: PÁNICO · CALMA + AMENAZA · AVISO · AMENAZA · INMINENTE · COLAPSO + SILENCIO · MEMORIA | 7: PÁNICO (ch01), AMENAZA (ch03, 266.7), AMENAZA (ch04, 447.2), AMENAZA (ch05, 531.9), INMINENTE (ch05), SILENCIO (ch06), AMENAZA (ch07, 897.6) | **No** (7 de 9) |
| Relojes | 4 | 4: ch01 8.3 s, ch04 4.4 s, ch05 12 s, ch07 12 s | Sí (cantidad) |
| Tarjeta | 1 | 1 en el plan (0:00, 3.0 s), pero no se dibuja: `intro_s` sigue en 2.5 | Sí en el plan, **no** en pantalla |
| Aguas | 2 | 2: ch03 «OLA 20 m» y ch04 «COTA AUTORIZADA 715 m» | Sí |
| Punches | 6 | 6: ch02, ch03, ch04, ch05, ch06 y ch07 | Sí |

- **Sellos que coinciden:** 4 de 9, que son PÁNICO, AMENAZA de ch04, INMINENTE y SILENCIO.
- **Sellos con otra palabra o sobrantes:** AMENAZA de ch03 (debería ser AVISO), AMENAZA de ch05 y AMENAZA de ch07.
- **Sellos que faltan:** CALMA, AMENAZA de ch02, AVISO, COLAPSO y MEMORIA.

#### 2. Las 15 líneas

Siempre «salió» quiere decir que el guion cumple la columna DEBERÍA. En todas las filas salió **No**. En «qué salió», los números de caracteres, escenas y duraciones salen de los eventos del guion y de los datos brutos.

| # | cap · t_mp4 | DEBERÍA (resumido) | Salió | Qué salió y por qué (regla y motivo de la data bruta) | Parte que lo arregla (§0.3) |
|---|---|---|---|---|---|
| 1 | ch01 · 18.8 | Ficha D195 «LONGARONE · 1.269 de 1.328 habitantes murieron», sin año | No | La ficha existe, pero con la etiqueta «LONGARONE, 1963» y cortada. Regla: rotulista (candado). Motivo: «no están en el texto fuente de D195: ['1963']». En `rotulista_ch01.raw.json` D195 es el único bloque, tras 2 intentos. | B.7 |
| 2 | ch02 · 162.3 | CALMA queda | No | Sello CALMA cortado por el crítico: «El tinte de 'muerte' contradice la escena de vida… y repite lo que ya se ve». Gemini sí devolvió CALMA en `sellos_clima_ch02.json`. | B.2 |
| 3 | ch02 · 211.1 | AMENAZA en la escena 10 | No | El sello «deslizamiento» (AMENAZA) en 211.1 está cortado por catálogo: «un sello por beat: el beat 3 ya tiene el sello AVISO». Pero AVISO (175.8) ya había caído por el crítico: «El tinte de 'agua'… no tiene relación con el contenido visual». O sea, un sello ya cortado ocupó el beat. Hay otros 4 «deslizamiento»/«montaña»/«cicatriz» cortados por la misma razón. | B.2 (crítico antes del reparto) |
| 4 | ch03 · 266.7 | Sello AVISO | No | Sale AMENAZA, con el crítico en «suma». En `sellos_clima_ch03.json` Gemini devuelve AMENAZA ×2, INMINENTE, ALARMA ×2 y NINGUNA; nunca AVISO. | C.3 |
| 5 | ch03 · 316.2 | Ficha D71 fuera | No | D71 «L'UNITÀ · Diario del Partido Comunista Italiano» sigue en 316.2, 4.9 s, con el crítico en sí/sí/no estorba. Ganó el desempate por orden de oración (sentence 13). | B.6 |
| 6 | ch03 · 348.9 | Lupa D49 «ANCHO DE LA FISURA · Más de 1 metro» | No | La lupa D49 está en 348.9, escena 11, lectura 2.7 s, pero cortada. Regla: rotulista (cantidad). Motivo: «un texto por beat: el beat 5 ya tiene D71». En el raw, D71 y D49 son los dos rank 1 del beat 5. | B.6 (D49 tiene cifra) |
| 7 | ch04 · 464.1 | Agua COTA AUTORIZADA, dur 3.9 | No | La agua 715 m sale con dur 4.5. El corte de la escena 7 es en 468.03 s y 464.06 + 4.5 = 468.56, así que lo cruza 0.53 s. Pasó el filtro sin mirar el corte. | B.4 |
| 8 | ch05 · 527.2 | Recorte Q50 literal, ~75 caracteres, 5.0 s | No | El recorte salió largo, con 147 caracteres que piden 9.8 s cuando hay 5.0 s hasta el corte de la escena (30.8 s). Regla: rotulista (lectura). En el raw, la etiqueta y el texto de Q50 miden 43 y 105 caracteres. | B.8 + C.2 |
| 9 | ch05 · 531.95 | Sello AMENAZA fuera | No | El sello AMENAZA queda en 531.9 s (dur 2.5, «crítico: suma») en la misma escena 2 que el recorte Q50 de la línea 8. Q50 está cortado, así que la regla «nunca sobre un texto» no lo saca. | B.2 (orden), una vez que Q50 viva |
| 10 | ch06 · 710.1 | Sello COLAPSO en la escena 2 | No | El sello de 710.1 es INMINENTE y está cortado por el crítico: «contradice la imagen… desplome ya ocurrido». Los otros 9 sellos del beat 10 están cortados por catálogo: «el beat 10 ya tiene el sello INMINENTE». En `sellos_clima_ch06.json` Gemini devolvió COLAPSO ×4. | B.2 |
| 11 | ch06 · 812.7 | Ficha «MUERTOS, RECUENTO OFICIAL · 1.910 personas» (D128) | No | Hay un `contador` de D128 con `texto` «Guglielmo» (la palabra del ancla, no el 1.910), cortado por el realizador: «contador de una cifra que dice la voz». El raw sí traía D128 como cifra «1.910 personas». D192 queda en 822.2, pero en la escena 14, no en la 13. | B.1 |
| 12 | ch07 · 897.6 | Sello AMENAZA fuera | No | El sello AMENAZA queda en 897.6 (dur 2.5, «crítico: suma»). Es el cuarto del video, junto con ch03, ch04 y ch05. | B.3 + C.3 |
| 13 | ch07 · 943.6 | Reloj con dur 4; ficha T85 en 949.9 | No | El reloj «20 FEB · 1968» sale con dur 12.0: 84.7 + 12 = 96.7 contra el corte de la escena 7 en 93.77 s, o sea que cruza el corte. La ficha T85 está cortada en 943.6, el mismo instante del reloj. Regla: rotulista (cantidad). Motivo: «beat pico (12): solo a_pantalla». | **Ninguna** (regla de Omar 14:22). Queda cortada hasta `--plan-edit`. El reloj de 12 s es B.4. |
| 14 | ch07 · 1025.7 | Sello MEMORIA | No | No hay ningún sello en 1025.7. Los de 1013 y 1023 («ola», «inundación») caen por «la escena 13 ya tiene ficha». En `sellos_clima_ch07.json` Gemini no devuelve MEMORIA, solo NINGUNA, AMENAZA, ALARMA, RABIA y SILENCIO. | B.3 + C.3 |
| 15 | 0:00 | Tarjeta que reemplaza la intro (3 s de negro con fecha-hora, todo +0.5 s) | No | La tarjeta «9 OCT 1963 · 22:39» está a 0.0 s con 3.0 s de dur, pero `intro_s` sigue en 2.5 y el title card del ch01 arranca a 2.5 s. La costura dice «intro 2.5 s (primer cuadro congelado) → title card». | B.9 |

**Sobre el reloj de ch05:** el reloj de 596.5 (dur 12.0, en la escena 9 que termina en 89.43 s del cap) también pasa el corte siguiente. Lo calculé a mano con las mismas cifras; no está en tu contrato. Entra en B.4.

#### 3. Resumen

**El guion cumple 0 de las 15 líneas, y ninguna se resolvió antes de lo previsto.** Los totales que coinciden (4 relojes, 2 aguas, 6 punches, tarjeta en el plan) ya coincidían en F34 y no dependen de estas líneas. Por parte, B debería cerrar 1, 2, 3, 5, 6, 7, 9, 10, 11 y 15. Las líneas 4, 8, 12 y 14 quedan para C. La 13 no la arregla ninguna parte.

**PARADA A:** diff vacío → se sigue a B (autorizado: «Seguir a la parte siguiente solo si la verificación de la anterior cierra»).

---

## Parte B — los bugs, con el caso real de cada uno como test (commit B)

### Qué se hizo, por punto
| punto | dónde | qué cambia | test (caso real) |
|---|---|---|---|
| B.1 | `gfx_realizador.finalizar` | el `count_up` del rotulista (`rotulista: True`) queda; solo sale el del director (cifra que dice la voz); la fila de un contador quitado dice su valor (`value_text`), no la palabra del ancla | D128 «1.910 personas» / «Guglielmo» |
| B.2 | `gfx_layer` (`_escena`, `_criticar_antes`, `_juez_sello`), `clima.sellos_por_tema(juez=)`, `gfx_critic.estorba` | orden nuevo con rotulista: crítico de los textos del rotulista y del agua de la voz → `escena_final` (una por escena) → agua y reloj contra el corte → sellos: vocabulario, corte, palabra, no repetir, **crítico**, y recién ahí «un sello por beat» y «nunca sobre otra cosa» → realizador → el crítico de siempre para lo que queda (hoy nada en el camino con rotulista). Lo que el crítico saca no ocupa beat ni escena | ch02 beat 3 (AVISO que ocupaba el beat), ch02 CALMA (tinte) |
| B.2 | `gfx_critic.estorba` | al sello de clima y al agua de la voz el crítico solo les pregunta si estorban. **Sin prompt nuevo**: es el pedido del crítico del rotulista (`build_prompt_rot`, `aporta` vacío) y de sus tres respuestas solo cuenta la (3) «¿El bloque estorba: tapa un rostro o un texto que está en la imagen?». Lectura declarada: el handoff dice «tapa un rostro o zona clara»; la pregunta existente dice «un rostro o un texto»; escribir «zona clara» sería un prompt nuevo, y el pedido de Omar solo permite los literales de C.2 y C.3 | CALMA: (1) y (2) en «no» por el tinte → pasa; (3) «sí» → sale |
| B.3 | `clima.sellos_por_tema(usadas_video=)`, `clima.usadas_antes` | una palabra que ya salió en el video (los planes de los caps anteriores, que corren en fila) **o en el cap** se pide otra vez a Gemini, una vez, con la lista sin las usadas (mismo prompt literal de F34 A.4, otra lista); si tampoco hay, ese momento queda sin sello | AMENAZA ×4 |
| B.4 | `rotulista_colocar.hasta_el_corte` (después de `escena_final`) | agua y reloj: duración = min(la que traen, corte − inicio − 1 cuadro) | agua ch04 4.50 → 3.94 s; reloj ch07 12 → 9.03 s |
| B.5 | `rotulista_filtros.contradicciones(cerca=)` (filtro `coherencia` y chequeo del guion) | una cota, un nivel o una altura solo contradice a **otra de la misma palabra** (cota con cota, nivel con nivel) en la oración ancla o una vecina; los muertos se siguen comparando con todo el video. Lectura declarada: el 700 m de Vajont está en la oración **vecina** («no pasar de los setecientos metros sobre el nivel del mar»); con «misma magnitud» = nivel/cota juntos seguía dando ✗; el handoff dice «una cota/altura solo contradice a otra» → la palabra | 715 vs 650/700 → sin ✗ |
| B.6 | `rotulista_filtros.finalizar` | desempate: `a_pantalla` → `rank` → dato con cifra o fecha (`numeros` del dato, en dígitos o en letras) → oración | D49 gana a D71 |
| B.7 | `rotulista_filtros.candado` y `finalizar` | en el gancho el candado acepta números y nombres que la voz dice en cualquier cap. **Además** el beat pico del gancho no corta los textos que no son `a_pantalla`: DECISIONES 14:28 («el gancho no es pico a efectos del texto») no estaba aplicado en `finalizar` (lo tapaba el candado: con B.7 D195 pasaba el candado y caía por «beat pico (1): solo a_pantalla») | D195 con «1963» |
| B.8 | `rotulista_colocar.caben`, `rotulista_filtros.lectura`, `rotulista_llm.pasados_de_largo` | cada bloque validado lleva `max_chars` (segundos hasta el corte × 15; en caps de una escena, hasta el fin de la oración siguiente) y, si la entrada trae `caben`, el reintento dice «etiqueta + dato tienen N caracteres y en esa oración caben M». Lectura declarada: «el JSON de salida lleva `max_chars`» se lee como la salida validada del rotulista, no como un campo nuevo del formato del prompt (eso sería un cambio de prompt fuera de C.2/C.3). En B no cambia nada en Vajont: la entrada todavía no trae `caben` (llega en C.2) y el rotulista sale de caché | Q50 147 contra 75 |
| B.9 | `fase2b` (`_intro_de`, `_filtro_tarjeta`, `_pad_tarjeta`, las dos mezclas finales, `_grafo_musica`, `_mezcla_preview`, el guion), `gfx_guion` | con `tarjeta_inicial` completa en el plan de ch01 (y `--gfx`), la intro es `title_dur` (3 s, identidad F3) de negro con la tarjeta dibujada como el título del title card sin kicker (Anton al `title_px`, color y raya de acento del CSS común, todo de `tc_metrics`/identidad); sin tarjeta, los 2.5 s de siempre. `intro_s` = 3.0, todo +0.5 s; la música de ch01 se mide en la mezcla | con y sin tarjeta, tarjeta incompleta, sin `--gfx`, clip de 90 cuadros 2560×1440 |

- Tests: `test_module_f36.py` +11 (B.1, B.2 ×2, B.3, B.4, B.5, B.6, B.7 ×2, B.8, B.9). Dos tests viejos cambian porque fijaban lo que B corrige: `test_module_f29c_rotulista.py::test_coherencia_720…` (720 m contra cotas de **otras** partes del video ya no contradice; con un nivel en la oración vecina sí) y `test_module_f34.py::test_a4_…` (los dos sellos repetidos se vuelven a pedir: 5 pedidos en vez de 3).
- **Ninguna constante nueva.** Los números de B: `1 cuadro` = 1/fps (derivado), `15 cps` (`LECTURA_CPS`, estándar), `title_dur` 3 s (identidad F3), medidas de la tarjeta = `tc_metrics()` y CSS del title card (identidad F3; `TC_LEFT + 4` es el `left: 184px` de `.tc-line`).

### Verificación
- `fase2b f8s3-vajont-f30 --plan-only --rotulista --rotulista-tope 0.97` dos veces: la primera (725 s, Gemini US$ 0.1256: crítico «¿estorba?» de 58 candidatos, crítico del rotulista para D128 y D195, re-pedidos de sellos) mostró que D195 caía por «beat pico» → arreglo de B.7 (gancho no es pico) → segunda corrida 249 s, Gemini US$ 0.0001 (caché), Claude US$ 0 (`b/plan_only.log`). Guion en `b/GUION_PANTALLA.md/.json`.
- md5 ch02 sin gfx `38e5ba14e3d24fd20f9297c9e1dfee24` · suite rápida 58 · suite amplia **1036 + las 5 previas** (`b/`).
- Firefox cerrado, RAM 13.6–16 GB libres antes de las corridas (la de B con 13.6 GB antes del md5: por debajo de los 14 GB de la regla; el md5 dio igual).
- Chequeos del guion: ✓ dos bloques en una escena, ✓ cruza corte, ✓ lectura, ✓ **cifra que contradice la voz** (antes ✗ 715 m), ✓ costuras, ✓ gancho no vacío, ✓ **inicio de música 7/7 con 0 cuadros** (ch01: title card 3.000 s · música medida 3.000 s), ✓ tarjeta; ✗ a_pantalla 4/5 (Q50, es de C); ✗ inicio de voz ch07 sin rampa (ya estaba en F32/F34).

### Salida de B: lo que queda en pantalla (t_mp4; todo +0.5 s por la tarjeta)
- ch01: **tarjeta «9 OCT 1963 · 22:39» 0:00 (3 s, reemplaza la intro)** · **ficha D195 «LONGARONE, 1963 · 1.269 de 1.328 habitantes murieron» 22.3** · sello PÁNICO 40.4 · reloj 9 OCT · 1963 76.5.
- ch02: recorte D117 129.2 · sello AMENAZA 155.4 · sello AVISO 176.3.
- ch03: agua OLA 20 m 251.2 · sello INMINENTE 267.2 · sello ALARMA 351.0. Sin texto (D49 ganó el beat pero como lupa visión no lo encuentra; D71 ya había perdido).
- ch04: reloj 4 NOV · 1960 391.1 · ficha T39 424.0 · sello COLAPSO 447.7 · **agua COTA AUTORIZADA 715 m 464.6, dur 3.94**.
- ch05: sello RABIA 532.4 · reloj 9 OCT · 1963 597.0 (**dur 1.88**: la escena 9 corta a los 89.43 s) · sello CALMA 660.6.
- ch06: sello SILENCIO 756.5 · **contador D128 «MUERTOS EN EL DESASTRE · 1.910 personas» 813.2** · ficha D192 822.7.
- ch07: reloj 20 FEB · 1968 944.1 (**dur 9.03**) · ficha D245 994.7. Sin sello (el AMENAZA ya no sale).

### B — simulador contra DEBERÍA
#### Guion de Vajont de F36-B contra el contrato (tabla «DEBERÍA por línea» de F34) — agente `simulador`, íntegro

**Cumple 6 de 15 líneas: 1, 5, 7, 11, 12 y 15.** Otras dos quedan en parte (3 y 9). De las 10 que B debía cerrar (1, 2, 3, 5, 6, 7, 9, 10, 11 y 15) se cerraron 5.

Salvo aviso, el t_mp4 que cito es el del contrato (el de F34 B). El de este guion es ese más 0.5 s.

Cómo lo medí:
- Leí `lab/hyperframes/f36/b/GUION_PANTALLA.json`.
- Crucé cada línea con `gfx_plan_chNN.resolved.json` (`sellos_tema`, `critico`, `critico_rotulista`, `rotulista.filas`) y con `sellos_clima_chNN.json`.
- Los `rotulista_chNN.raw.json` son de F34 (15:39–15:41, caché del modelo). La corrida de B solo regeneró lo que depende de las reglas.
- No toqué archivos ni corrí `fase2b`.

#### 1. Totales

Texto: eventos con `queda: true` de tipo ficha, recorte, cita, lupa, persona o contador. Sello: solo los sellos con `queda: true`.

| Concepto | Esperado (DEBERÍA) | Salió con la lista | ¿Sí/no? |
|---|---|---|---|
| Textos | 9: D195 o D118, D117, D49, T39, Q50, D128, D192, T85, D245 | 6: D195, D117, T39, D128 (contador), D192, D245. Faltan D49, Q50 y T85. D71 ya no sobra. | **No** (6 de 9; F34 tenía 5 con D71 de más) |
| Sellos | 9: PÁNICO · CALMA + AMENAZA · AVISO · AMENAZA · INMINENTE · COLAPSO + SILENCIO · MEMORIA | 9: PÁNICO (ch01), AMENAZA y AVISO (ch02), INMINENTE y ALARMA (ch03), COLAPSO (ch04), RABIA y CALMA (ch05), SILENCIO (ch06) | **No** en el contenido (ver abajo) |
| Relojes | 4 | 4: ch01 8.32 s, ch04 4.43 s, ch05 1.88 s, ch07 9.03 s | Sí |
| Tarjeta | 1, y que se dibuje | 1 a 0.0 s con 3.0 s de duración, y `intro_s` = 3.0 | **Sí, ahora también en pantalla** |
| Aguas | 2 | 2: ch03 «OLA 20 m» y ch04 «COTA AUTORIZADA 715 m» (3.94 s) | Sí |
| Punches | 6 | 6: ch02, ch03, ch04, ch05, ch06 y ch07 | Sí |

**Sellos.**
- Coinciden 7 de las 9 palabras: PÁNICO, CALMA, AMENAZA, AVISO, INMINENTE, COLAPSO y SILENCIO.
- Faltan MEMORIA y la segunda AMENAZA. Sobran ALARMA (ch03, 351.0) y RABIA (ch05, 532.4).
- Con el cap correcto coinciden solo 3: PÁNICO en ch01, AMENAZA en ch02 y SILENCIO en ch06.
- El contrato pide AMENAZA dos veces (ch02 y ch04), y B.3 prohíbe repetir una palabra en todo el video. Con B.3 activo la segunda AMENAZA no puede salir nunca.

**Chequeos del propio guion.**
- «bloque que cruza un corte» pasó de ✗ en F34 a ✓.
- «cifra que contradice la voz» pasó de ✗ en F34 a ✓.
- Siguen en ✗ «a_pantalla» (4 de 5, Q50) e «inicio de voz» de ch07. El de ch07 ya estaba en F34.

#### 2. Las 15 líneas

| # | cap · t_mp4 | DEBERÍA (resumido) | ¿Salió? | Qué salió y por qué (regla y motivo de la data bruta) | Parte que la arregla (§0.3) | ¿Lo previsto para B? |
|---|---|---|---|---|---|---|
| 1 | ch01 · 18.8 | Ficha D195 «LONGARONE · 1.269 de 1.328 habitantes murieron», sin año en la etiqueta. | **Sí** (con un matiz) | La ficha queda a 22.3 s (cap 19.3, oración 2, palabra «Longarone,») con 4.14 s. El crítico dio sí, sí, no estorba. El candado ya no la corta: B.7 acepta el 1963 que la voz dice en el reloj de 76.5 s. Matiz: la etiqueta sigue siendo «LONGARONE, 1963» y no «LONGARONE». El 18.8 de F34 parece ser el inicio de la oración y la ficha ahora se coloca en la palabra ancla. | B.7 | **Sí** |
| 2 | ch02 · 162.3 | CALMA queda en la escena 6. | **No** | El sello de 162.78 (palabra «vida») sigue cortado por el crítico. Ya no es por el tinte: ahora dice «CALMA estorba: el sello grande a media altura a la derecha tapa rostros de las personas sentadas en la cafetería y la Vespa». B.2 hizo lo previsto (solo pregunta «¿estorba?»), pero la respuesta es un estorbo físico por la posición del sello. | B.2 | **No.** El §0.3 suponía que el tinte era lo único que lo cortaba. |
| 3 | ch02 · 211.1 | AMENAZA en la escena 10 (primer AMENAZA del video). | **En parte** | AMENAZA entra en ch02, pero en **155.42** (escena 5, beat 2, palabra «colgados»), no en 211.1. En el beat 3 queda **AVISO a 176.34** (escena 7): ahora pasa el crítico («no estorba»). Por eso el «deslizamiento» de 211.56 (AMENAZA) cae con «un sello por beat: el beat 3 ya tiene el sello AVISO», y esta vez es legítimo. | B.2 | **No** del todo. La causa es que B.2 cambió la pregunta y AVISO ya no cae. Así AVISO queda en ch02, que no estaba en el contrato, y AMENAZA se va al beat 2. |
| 4 | ch03 · 266.7 | Sello AVISO. | **No** | Sale INMINENTE a 267.16. `sellos_clima_ch03` no tiene AVISO en ninguna respuesta (AMENAZA ×2, INMINENTE ×2, ALARMA ×4, NINGUNA). AMENAZA ya salió en ch02, se la volvió a pedir una vez y devolvió INMINENTE. Además AVISO ya está usado en ch02. | C.3 | Sí (no se esperaba) |
| 5 | ch03 · 316.2 | Ficha D71 fuera. | **Sí** | D71 cortado por «un texto por beat: el beat 5 ya tiene D49». Ganó D49 por el desempate de cifra. | B.6 | **Sí** |
| 6 | ch03 · 348.9 | Lupa o ficha D49 «ANCHO DE LA FISURA · Más de 1 metro» en la escena 11. | **No** | D49 ganó el desempate, pero cae en otro filtro: `rotulista (zona)`, «visión no encuentra “Más de 1 metro de ancho” en la escena 12». Con el desempate resuelto, D49 llegó por primera vez a `colocar` (`rotulista_colocar.py`), que pide a la visión ubicarla en la imagen. La lupa quedó en la palabra «fisura» (oración 17, cap 115.74 s), que es el arranque de la escena 12 y no de la 11. En F34 nunca llegaba a esa etapa. | B.6 | **No.** El desempate cumplió, pero apareció un filtro que el contrato no preveía. El contrato aceptaba «lupa/ficha», y el modelo eligió `lupa`, que es la que exige visión. |
| 7 | ch04 · 464.1 | Misma agua, duración 3.9 s. | **Sí** | «COTA AUTORIZADA 715 m» con duración **3.94**: termina en 468.50 y el corte es 468.53, o sea corte − 1 cuadro. «bloque que cruza un corte» pasó a ✓. La contradicción 715 vs 650/700 también desapareció (B.5). | B.4 | **Sí** |
| 8 | ch05 · 527.2 | Recorte Q50 de unos 75 caracteres y 5.0 s. | **No** | Mismo recorte largo (147 caracteres piden 9.8 s y hay 5.0 s hasta el corte en 30.8 s), cortado por `rotulista (lectura)`. La data bruta es la de F34, porque el prompt no cambió. | B.8 + C.2 | Sí (no se esperaba) |
| 9 | ch05 · 531.95 | Sin sello sobre el recorte. | **En parte** | AMENAZA ya no sale («ya salió en el video»), pero en el mismo instante queda **RABIA a 532.45** (escena 2, beat 8, «no estorba»), y es otro sello en el lugar que el contrato quería vacío. «Nunca sobre un texto» no aplica porque Q50 está muerto (línea 8). | B.2, que en el §0.3 ya se condicionaba a «con Q50 vivo» | **No.** La línea depende de la 8, que es de C. El §0.3 la marcó como cerrada en B. |
| 10 | ch06 · 710.1 | Sello COLAPSO en la escena 2. | **No** | En ch06 no hay sello en 710.59. Gemini devolvió COLAPSO ×4, pero las cuatro respuestas caen por «COLAPSO ya salió en el video»: ch04 lo había tomado a 447.74 (el lugar de la AMENAZA del contrato). La segunda petición dio NINGUNA. El INMINENTE que ocupaba el beat ya no existe. | B.2 | **No.** B.2 sí limpió el beat, pero B.3 reparte las palabras por orden de cap y ch04 tomó COLAPSO antes. |
| 11 | ch06 · 812.7 | D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas» en la escena 13. | **Sí** | Un `contador` «MUERTOS EN EL DESASTRE · **1.910 personas**» a 813.2, escena 13, duración 3.7 s, crítico sí, sí, no estorba. El realizador ya no lo borra y el texto es el valor, no «Guglielmo». D192 sigue a 822.73 en la escena 14. Sale como contador y no como ficha: es el mismo dato. | B.1 | **Sí** |
| 12 | ch07 · 897.6 | AMENAZA fuera. | **Sí** | El sello de 898.15 cae por «AMENAZA ya salió en el video», con segunda respuesta NINGUNA. ch07 queda sin ningún sello. | B.3 + C.3 | **Antes de lo previsto.** Lo cerró B.3, porque AMENAZA ya estaba usada en ch02. |
| 13 | ch07 · 943.6 | Reloj con duración 4 s y ficha T85 a 949.9. | **No** | T85 sigue cortada por «beat pico (12): solo a_pantalla». El reloj «20 FEB · 1968» queda a 944.07 con **9.03 s**: termina en 953.10 y el corte es 953.13 (antes 12 s, B.4). | ninguna (regla de Omar) | **Sí** (no se esperaba) |
| 14 | ch07 · 1025.7 | Sello MEMORIA en la escena 13. | **No** | MEMORIA llegó antes de lo previsto: el sello de 1013.65 («ola») recibió MEMORIA tras repetir RABIA, y el crítico lo pasó («no estorba»). Pero lo corta el catálogo con «la escena 13 ya tiene ficha», que es la excepción que el contrato marca «Omar decide». Además el sello quedó en 1013.6 y no en 1025.7. El de 1023.85 («inundación») pidió SILENCIO, repetido, y la segunda respuesta fue NINGUNA. | B.3 + C.3 | **Sí** (no se esperaba), pero por otra causa: la palabra ya llega, lo que lo frena es la regla «una cosa por escena». |
| 15 | 0:00 | La tarjeta reemplaza la intro (3 s). | **Sí** | La tarjeta «9 OCT 1963 · 22:39» está a 0.0 s con 3.0 s. `intro_s` = 3.0 y la costura dice «intro 3.0 s (tarjeta sobre negro, sin voz) → title card». La música de ch01 mide `title_card_s` 3.0 con desvío 0 cuadros. | B.9 | **Sí** |

**Fuera del contrato pero visible en este guion.**
- ch05 pasa de un reloj de 12 s a uno de 1.88 s, porque la escena termina antes. Sigue contando como reloj.
- SILENCIO está en el beat 10 (756.5) y no en el 11 (799.0 en F34). Con eso, el «fango» de 799.5 cae por «SILENCIO ya salió en el cap».
- ALARMA en ch03 (351.0) ahora pasa el crítico y no estaba en el contrato.
- ALARMA y RABIA son los dos sellos sobrantes.

#### 3. Resumen

**Cumple 6 de 15 (1, 5, 7, 11, 12 y 15) y dos en parte (3 y 9).** De las 10 que B debía cerrar, se cerraron 1, 5, 7, 11 y 15.

- **Antes de lo previsto:** la 12 (C.3) la cerró B.3 porque AMENAZA ya estaba usada. La 14 no cierra, pero MEMORIA ya llega (previsto para C).
- **Como se esperaba, sin cerrar:** 4, 8 y 13.
- **B debía cerrar y no cerró** (2, 3, 6, 9 y 10):
  - **2:** el crítico, ahora solo con «¿estorba?», igual la corta porque el sello tapa rostros y la Vespa.
  - **3:** B.2 dejó pasar AVISO en ch02, así que ocupa el beat 3 y AMENAZA se va al beat 2.
  - **6:** D49 ganó el desempate (B.6), pero la visión no encuentra el texto en la escena 12 y lo corta por zona.
  - **9:** el sello AMENAZA se fue, pero RABIA lo reemplazó, y la regla «nunca sobre un texto» necesita Q50 vivo (línea 8, C).
  - **10:** B.3 reparte las palabras por orden de cap: COLAPSO la tomó ch04 y ch06 quedó sin ella.
- **Contradicción del contrato:** pide AMENAZA ×2 y B.3 no repite palabras, así que los 9 sellos solo pueden cerrar con otra palabra en el segundo lugar.

### Lectura de CC sobre B (sin tocar nada más)
- Las cinco líneas que B debía cerrar y no cerró no son fallas de los arreglos: cada arreglo hizo lo pedido (los tests con el caso real pasan) y al sacar el obstáculo apareció el siguiente. CALMA (2) cae ahora por una razón válida para la regla nueva (tapa rostros); la línea 3 cambió porque AVISO ya no cae; la 6 destapa un bug nuevo («un bloque que cae al colocar ya ocupó su beat»); la 9 depende de Q50 (C); la 10 sale de B.3 contra un contrato que pide AMENAZA ×2.
- **Contradicción del contrato con B.3** (la marca el simulador): la tabla DEBERÍA pide AMENAZA dos veces (ch02 y ch04) y B.3 prohíbe repetir una palabra en todo el video. Decide Omar.

**PARADA B:** md5, suites y tests cierran → se sigue a C (el guion no exige diff vacío en B).

---

## PARADA antes de C — dos cambios de prompt que el pedido de Omar no autoriza
El pedido de Omar dice «Prompts: solo los cambios literales de C.2 y C.3». El handoff pide dos cambios más al prompt del
rotulista, y C llama a Sonnet (cada vuelta cuesta), así que CC frena antes de C y pregunta (a la sesión que lanzó la
tanda, 2026-10-26):
1. **C.1:** la instrucción literal nueva para `ROTULISTA_USER` («Los datos marcados con tu beat son los que la escaleta
   cuenta ahí; los demás son el resto del archivo del caso: usalos si suman más que los del beat y no adelantan nada
   que la narración cuente después.»). Sin ella, el pool completo puede ir igual en la entrada (con
   `beats_que_lo_cuentan`), pero sin la instrucción.
2. **C.4:** «el agua la propone el modelo como `tipo: "agua"`» y `agua_de_voz` deja de correr. Para que Sonnet proponga
   ese tipo hay que agregar «agua» a los tipos del prompt, y el handoff no da ese texto literal. Sin él y sin
   `agua_de_voz`, las dos aguas de Vajont (OLA 20 m, COTA 715 m) se pierden: son cifras que dice la voz y el filtro «no
   dicho» las corta.
Alternativa que CC puede hacer sin tocar más prompt: C sin la frase de C.1 y con `agua_de_voz` vivo (solo sin
`AGUA_ETIQUETAS`: la etiqueta, tomada de la oración).

Lo que C ya sabe que necesita (sin decidir nada): con C.3 el rotulista elige el sello «sin repetir en el video (lista de
usadas)», así que el prefetch de los 7 caps tiene que pasar de paralelo a fila (cada cap necesita las palabras que el
modelo eligió en los anteriores); y C.2 necesita los cortes de escena en la entrada, que hoy se arma antes de tener
escenas (se toman de `build_scenes` sin el ajuste fino de `snap_cuts`, iguales en el prefetch y en el plan, para que la
caché del modelo no se rompa).

---

# F36 C y D nuevos — handoff `lab/hyperframes/f36/HANDOFF_F36_C_D_pantalla.md` (reemplaza C y D de `HANDOFF_F36_estructura.md`)

CC · 2026-10-26 (sesión nueva, procedimiento `/tanda` 1–12). Base `bce140e`. Decisiones de Omar 18:17 («catálogo definitivo») y
19:54 («el autor de la pantalla va a Fase 1»). Pedido literal de Omar: C (paso suelto para Vajont, tope US$ 0.50, `--plan-only`,
simulador contra el contrato de 13 líneas, `01e_pantalla.md` entero, los 6 tests de la aclaración 8, PARADA) y D (borrar,
diff vacío contra C, mapa con 0 muertos, claves huérfanas del perfil, PARADA final). El prompt de Omar autoriza C y D en
la misma tanda; las paradas condicionales (JSON inválido dos veces, narración que no alinea, D sin diff vacío) no se
dieron (ver cada parte).

## Lecturas declaradas (paso 1)
`CLAUDE.md`, `DECISIONES.md` entero (con 18:17 y 19:54), `lab/ESTADO_SESION.md` (cabecera, F36, F34), el handoff nuevo
entero con sus 9 aclaraciones, `.claude/commands/tanda.md`, la nota de traspaso de la sesión de A y B,
`lab/hyperframes/f34/REVISION_GUION.md` (contrato), `lab/hyperframes/f36/RESPUESTA_C.md`, este reporte (A y B),
`rotulista_llm/filtros/colocar`, `clima`, `voz_datos`, `voz_utils`, `gfx_rotulista`, `gfx_layer.apply_gfx` (tramo del
plan), `gfx_guion` (eventos, cortes, chequeos), `gfx_critic.estorba/criticize_rotulista`, `gfx_realizador.cargar/ventanas/
finalizar/cerrar`, `fase1_5.run_guion_v3/v4/_step_cost`, `m01d_particion` (cabecera), `fase2b._solo_plan` y `--plan-edit`,
`claude_helpers.call_json/_post/cost_of`, `lab/tools/mapa_*.py`.

## Paso 0 (commit `52c7d48`)
- La C vieja sin commitear fue a **`stash@{0}: f36-c-vieja-descartada`** con `git stash push -u -m f36-c-vieja-descartada --
  <archivos>` (solo esos archivos; el `-u` con pathspec solo se lleva los untracked de la ruta nombrada). Qué había (776
  líneas +, 563 −): `clima.py` (449: sellos con Sonnet en la llamada del rotulista), `gfx_guion.py` (62: «dos bloques al
  mismo tiempo»), `gfx_layer.py` (26), `gfx_pool.py` (2), `gfx_rotulista.py` (38), `rotulista_colocar.py` (217: «nunca al
  mismo tiempo», `caben_hasta`, `agua_de_bloque`), `rotulista_filtros.py` (37), `rotulista_llm.py` (90: pool completo,
  `caben`), `voz_datos.py` (85), tests `f29c_rotulista`, `f32`, `f34`, `f36` (242) y el untracked `lab/hyperframes/f36/c/`
  (`prompt_antes.txt`, `prompt_despues.txt`). No se borró nada.
- Lo ajeno a F36 quedó en el árbol sin tocar: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`,
  `gfx_profiles/misterio.json`, `lab/hyperframes/f28/a/f28a.log` y los `??` viejos. `git status` después: el árbol de F36
  en `bce140e`.
- Commit `52c7d48`: `DECISIONES.md` tal cual (18:17 y 19:54) + el handoff nuevo, `RESPUESTA_C.md` y `REVISION_GUION.md`
  del analista, tal cual.
- Reuso declarado: la función «nunca al mismo tiempo» de `rotulista_colocar.escena_final` y el chequeo «dos bloques al
  mismo tiempo» del guion se tomaron del stash (son la misma regla de DECISIONES 17:58 que la aclaración 3 deja en Fase 2);
  nada más del stash.

## Módulos que toca la tanda (paso 2; sticker de `lab/MAPA_MODULOS.md` → después)
| módulo | hoy (sticker) | después de C | después de D |
|---|---|---|---|
| `m01e_pantalla` (nuevo) | — | Fase 1: el guion de pantalla en papel (una llamada a Sonnet, validación en papel, `.json`/`.md`) | igual |
| `fase1_5` | corre escaleta → guion → partición → juez | `run_pantalla` después de la partición, antes de la voz (paso «pantalla» en `01_v3_costos.json`) | igual |
| `gfx_rotulista` | fachada + prefetch del rotulista | `preparar_cap` lee el papel, `alinear`, `palabra_idx`; sin `prefetch` | solo `preparar_cap` y lo que usa |
| `rotulista_llm` | el pedido al modelo | nadie del camino lo llama | **borrado** |
| `rotulista_filtros` | `ORDEN` de 9 filtros | `ORDEN` = anclar el papel, no dicho del gancho, candado, no dicho, spoiler, lectura; el viejo como `ORDEN_MODELO` | sin `ORDEN_MODELO` ni sus filtros |
| `rotulista_colocar` | tiempos, colocar, ediciones, «una por escena» | colocar del papel (cita = ficha con autor), «nunca al mismo tiempo» | sin agua, contador, lupa ni ediciones del plan |
| `clima` | sellos con Gemini Flash | `sellos_del_papel` | sin Gemini |
| `voz_datos` | pico, reloj, agua, tarjeta | sin agua en el camino; tarjeta derivada solo para comparar | sin agua |
| `gfx_layer` | director de orquesta | lee el papel, tarjeta y relojes del papel, crítico «¿estorba?» | sin los caminos borrados |
| `gfx_critic` | crítico F4e + rotulista | `solo_estorba` para el papel | solo el del rotulista con «¿estorba?» |
| `gfx_guion` | guion + chequeos | columna `papel`, «dos bloques al mismo tiempo», «papel sin colocar / sin alinear», relojes del papel | igual |
| `fase2b` | prefetch del rotulista, `--plan-edit` al plan | sin prefetch; `--plan-edit` edita el papel | sin sfx por bloque |
| `lab/MAPA_MODULOS.*` | 43 módulos, 14 muertos | 44 módulos, 18 muertos (los 4 nuevos los deja C para D) | 0 muertos |

---

## Parte C — `m01e_pantalla`: el guion de pantalla en papel (commit C)

### Simulación previa (paso 5, antes del código de Fase 2)
Agente `simulador` sobre el guion de B: `lab/hyperframes/f36/c/simulacion_previa.md` (íntegro ahí). Las tres tablas:

| regla | propuestos | cortados | quedan / vuelven |
|---|---|---|---|
| R1 «nunca al mismo tiempo» sobre lo colocado hoy | 18 | 0 | 18 quedan |
| R1 sobre lo cortado por «la escena ya tiene» | 2 | 1 | 1 vuelve (MEMORIA ch07 1013.65) |
| R2 sin `cantidad`/pico/desempate, sin agua | 8 | 3 | 5 vuelven (T21, D71, D104, D68, D32) |
| R3 catálogo 18:17 (agua, contador, lupa) | 3 | 3 | 0 |

Lectura: R1 no corta nada colocado y deja salir MEMORIA; R2 muestra que sin el modelo en Fase 2 el número de fichas depende
entero del papel («un sello por beat» queda en el papel); R3 saca las 2 aguas y el contador.

### C.1 Dónde corre y qué recibe
- `script_engine/m01e_pantalla.py` (nuevo). Fase 1: `fase1_5.run_pantalla` se llama en `run_guion_v3` y `run_guion_v4`
  justo después de `m01d_particion` (antes del juez m05 y de la voz), con `_step_cost(topic, "pantalla", …)`; si no hay JSON
  en dos intentos o no alcanza el tope, avisa y Fase 1 sigue. Suelto: `python -m script_engine.m01e_pantalla <topic>`
  (también `python script_engine/m01e_pantalla.py <topic>`), con su costo en `01_v3_costos.json` como paso «pantalla».
- Lee (aclaración 1) del directorio del topic de Fase 1: `01a_escaleta.json`, `01b_narracion_v3.json` (párrafos por cap y
  beat), `01a_skeleton.json` (títulos de la partición) y `00_pool_v3.json` (o el `evidence_pool` del topic, desde
  fase1_5). **Desvío declarado:** la aclaración dice «el de `ba6c3cac…` para Vajont», pero el topic de Fase 1 de Vajont es
  `data/scripts/_steps/f8s3-vajont` (`topic_id` del script `f8s3-vajont-f30.json`; `ba6c3cac` es Orleans): es el directorio
  que leen `gfx_realizador.cargar` y el rotulista, que es lo que pide la aclaración. Ahí se escribe y de ahí lee Fase 2.
- Oraciones: `voz_utils.oraciones_de_texto` (el corte de `gfx_peak.sentences` aplicado al texto) sobre cada párrafo; cada
  oración con su beat (el del párrafo) y `caben` = int(palabras × `SEG_POR_PALABRA` 0.35 `# medido: Vajont ch04` × 15 cps).
- Archivo: el pool con D con cifra (`numeros` del texto), T, Q y P: **400 ítems** en Vajont (D 171, T 120, Q 57, P 52); T con
  «(fecha …, hora …)» en su texto, P «nombre — rol», Q con `autor`. `beats_que_lo_cuentan` = beats donde es `dato_central`
  o apoyo + el beat de su `a_pantalla` (`gfx_realizador.beat_de_pantalla`). Beats: n, cap, función, pico (sí/no,
  `music_intensity.beat_pico_de_cap`), dato central, apoyo, cierre. Clima: `sellos_clima` del perfil (10 palabras).
- **Tokens de entrada de Vajont: 59 976** (USER 124 313 caracteres). El USER real recortado a ch03:
  `lab/hyperframes/f36/c/user_vajont_recortado_ch03.txt` (pegado abajo).
- Salida: `01e_pantalla.json` (por cap y beat `ficha|null` y `sello|null`, `relojes`, `tarjeta`, `descartados` con regla y
  motivo) y `01e_pantalla.md`; la cruda y la caché en `01e_pantalla.raw.json`. **Desvío declarado:** el «Formato de salida»
  que ve el modelo es el esquema de C.1 **sin `estilo`**: C.1 dice que el estilo no lo elige el modelo; lo pone
  `estilo_de` (Q → cita, P → nombre, D/T cuya etiqueta o el `por_que` de su `a_pantalla` nombran carta/acta/informe/documento
  → papel —`rotulista_filtros.pide_documento`, lectura declarada de «D/T que pide_documento»—, resto → normal).

### C.2 El prompt (literal) y la llamada
- `PANTALLA_SYSTEM` = el SYSTEM de C.2 copiado tal cual; `PROMPT_VERSION = "m01e-1"`. **md5 del prompt (SYSTEM + línea del
  formato) `aa1ebc33f964a9908ca486dfb12d0a0c`**; md5 del SYSTEM solo `0354c7641ab01bd9b7d2e1992bfecb8d`. USER = el JSON de
  entrada + «Formato de salida: …». md5 de la entrada de Vajont `e0e9d72ee684b05ef873d1314f4d9f53`.
- `claude-sonnet-5-5`, `medium`, POST propio (una llamada por intento; sin los reintentos de JSON de `call_json`, para que
  «dos intentos» sean dos), costo al `cost_tracker`, caché por md5 (versión + modelo + effort + SYSTEM + USER).
- **Vajont: 1 llamada, JSON válido, 59 976 tokens de entrada, 18 911 de salida (12 733 de razonamiento), US$ 0.3091,
  140.5 s.** La validación sacó 3 fichas → tocaba el reintento, pero **el tope no alcanzó**: gastado 0.3091 + el peor caso de
  la segunda llamada 0.2685 > 0.50 → sin reintento (anotado en la cruda y en el log). No se pasó el tope.

### C.3 Validación en papel
Por ficha, en orden: anclaje (cap, beat del cap, ítem del archivo, oración que existe y es de ese beat, una por beat) →
formato (etiqueta y dato no vacíos, cita con autor, `ficha_medida`: etiqueta 1 línea, dato ≤ 2) → `gancho_dicho`, `candado`
y `no_dicho` de `rotulista_filtros` (con el texto del ítem del archivo como fuente; en el gancho, la voz de todo el video) →
`spoiler` de `rotulista_filtros` sobre la narración posterior del cap **y de los caps siguientes** → el mismo dato una vez en
el video → `caben`. Por sello: de la lista, no es palabra de la voz del cap (raíz de 5), no repetido en el video, uno por
beat. Vajont: **3 fichas cayeron** (D47 spoiler «2»; D105 no dicho «1962»; Q43 caben 108 > 94); 0 sellos cayeron.

### C.4 Fase 2 consume el papel
- `gfx_layer.apply_gfx` → `gfx_rotulista.preparar_cap` (sin modelo): lee `01e_pantalla.json`, alinea cada oración del papel
  con las de la voz por texto normalizado (`voz_utils.norm_oracion`; la que no es igual se ancla a la más parecida y se
  anota «papel sin alinear»), ancla la ficha a la palabra (`palabra_idx`: igual, por raíz, o la primera palabra de
  contenido) y arma los bloques. **Vajont: 161/161 oraciones alineadas** (7/7 narraciones).
- `ORDEN` de `rotulista_filtros` recortado (aclaración 3): **`[ancla_papel, gancho_dicho, candado, no_dicho, spoiler,
  lectura]`** (reglas: anclaje, no_dicho, candado, no_dicho, spoiler, lectura). Fuera: `forma` y el anclaje del modelo
  (quedan en papel), `coherencia` (no está en la lista de la aclaración 3; su chequeo del guion sigue), `cantidad` (uno por
  beat, pico solo `a_pantalla`, desempate). El orden viejo queda como `ORDEN_MODELO` solo para `rotulista_llm` hasta D.
  Después de los filtros: ya mostrado (`colocar`), «nunca al mismo tiempo» (`escena_final`), crítico de foto «¿estorba?»
  (`criticize_rotulista(solo_estorba=True)`: mismo pedido sin `aporta` ni `por_que`, cuenta la (3)).
- Estilo → forma (aclaración 6): normal/nombre → ficha (title card); cita → ficha con «dato» — autor (title card, no
  `quote_card`); papel → recorte. La lectura de la cita cuenta las comillas y la raya que se dibujan (+5 caracteres,
  derivado), para que la duración y el chequeo «texto sin lectura» midan lo mismo.
- Sellos (aclaración 5): `clima.sellos_del_papel` — palabra y oración del papel; el instante = la palabra de más peso de la
  oración o, si cruza el corte, el inicio de la oración (lectura declarada de «palabra de más peso o inicio de la
  oración»); vocabulario, no salió antes en el video, no cruza el corte; crítico antes del reparto; «nunca al mismo tiempo».
  «Uno por beat» lo decidió el papel. Los sellos del director y el del pico salen (anotados).
- Relojes (aclaración 4): `reloj_de_voz`/cronología como antes; los del papel van al guion como informativos. Tarjeta: la
  del papel (si difiere de la derivada de la escaleta, se anota; en Vajont no difiere).
- Agua, contador y lupa no corren (catálogo 18:17; el código se borra en D).
- `fase2b`: sin el prefetch del rotulista; `--plan-edit` edita el papel (`m01e_pantalla.editar`: reemplaza ficha/sello de un
  beat o la tarjeta, copia `01e_pantalla.antes_de_edicion.json` la primera vez, reescribe el `.md`).
- `gfx_guion`: columna `papel: sí/no` en cada evento (y en lo cortado), chequeo «dos bloques al mismo tiempo» (reemplaza «dos
  bloques en la misma escena»), «papel sin colocar», «papel sin alinear», «relojes del papel (informativo)».

### Verificación
- `python -m script_engine.m01e_pantalla f8s3-vajont` → US$ 0.3091 (`01_v3_costos.json`: paso «pantalla»).
- `fase2b f8s3-vajont-f30 --plan-only --rotulista` (RAM 16.5 GB, Firefox cerrado): 161.5 s, **Claude US$ 0** (no hay
  llamada de texto: el papel sale de disco), Gemini 0 en la segunda corrida (la primera, 227 s, US$ 0.0012: el crítico
  «¿estorba?» de las fichas y sellos del papel). Log `c/plan_only.log`; guion `c/GUION_PANTALLA.md/.json`.
- Tests de la aclaración 8: `test_module_f36c_pantalla.py` (6, verdes): (a) esquema (con el papel de Vajont en disco);
  (b) candado: D195 con «1963» en la etiqueta fuera del gancho → candado (y en el gancho pasa por B.7: la voz dice el año);
  (c) 7 narraciones de Vajont 100 % alineadas, en orden; (d) un dato una vez en el video; (e) sello que no repite palabra
  (y no es palabra de la voz); (f) Fase 2 lee el papel de los 7 caps con `claude_helpers._post`, `call_json` y
  `rotulista_llm.llamar` reemplazados por un error, y el `ORDEN` recortado.
- Tests viejos adaptados a lo que cambió por decisión (no por comodidad): `test_module_f29c_rotulista.py::
  test_ficha_no_convive_con_reloj_ni_con_title_card` (DECISIONES 17:58: la ficha que no toca el title card se queda; la que
  se solapa espera), `test_module_f36.py::test_a_orden_de_filtros_es_el_de_f34` (el de F34 es `ORDEN_MODELO`) y
  `::test_a_la_fachada_da_todos_los_nombres_de_antes` (falta solo `prefetch`).
- Suites y md5: md5 de ch02 sin `--gfx` `38e5ba14e3d24fd20f9297c9e1dfee24` (igual; RAM 16.5 GB, Firefox 0), rápida **58**, amplia **1042 + las 5 previas** (01b_pauses ×3, m03_merge_timing ×2) — en B eran 1036 + 5: +6 de `f36c_pantalla`. `lab/hyperframes/f36/c/` (`onlycap_ch02_nogfx.log`, `suite_rapida.log`, `suite_amplia.log`, `ram_antes_md5.txt`). Mapa regenerado: 44 módulos, 156 aristas, 18 muertos (los 14 de antes + 4 que deja C para que D los borre: `rotulista_llm` y el `ORDEN_MODELO`, el Gemini de clima, agua y contador, las ediciones del plan).

### Salida de C (1): `01e_pantalla.md` entero (Vajont)
````markdown
# Guion de pantalla en papel — f8s3-vajont

`m01e_pantalla` m01e-1 (md5 del prompt `aa1ebc33f964a9908ca486dfb12d0a0c`) · claude-sonnet-5-5 medium · 1 intento(s) · US$ 0.3091 · tokens de entrada 59976

**Tarjeta:** 9 OCT 1963 · 22:39

Totales: 9 fichas · 9 sellos · 4 relojes · 1 tarjeta · 85 descartados

## ch01 — Cama en la oscuridad

- beat 1 · gancho · PICO · ficha **D131** [normal] «SALTO DE LA MASA DE AGUA · Más de 260 metros» en [15] sobre «encima» (41/68 car.) · aporta: La voz dice que la ola pasó por encima del dique, pero no dice de qué altura cayó el agua al valle. · sello **PÁNICO** en [4]
- relojes: 9 OCT 1963 en [13]

## ch02 — El muro que tapa

- beat 2 · planteo · ficha **D117** [papel] «SESIÓN DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes» en [2] sobre «aprobó» (60/210 car.) · aporta: La voz dice que el proyecto se aprobó en 1943, pero no que lo aprobó una sesión con solo 13 de 34 representantes presentes. · sello **CALMA** en [6]
- beat 3 · escalada · PICO · ficha — · sello **AMENAZA** en [10]
- relojes: —

## ch03 — La costura abierta

- beat 4 · giro · PICO · ficha **T16** [normal] «LA VÍCTIMA DE PONTESEI · Arcangelo Tiziani» en [3] sobre «Pontesei» (39/141 car.) · aporta: La voz dice que murió un trabajador, pero no dice cómo se llamaba. · sello —
- beat 5 · escalada · ficha **D49** [normal] «ANCHO DE LA FISURA · Más de 1 metro» en [17] sobre «fisura» (32/194 car.) · aporta: La voz da el largo de la fisura, casi dos kilómetros, pero no su ancho. · sello **INMINENTE** en [18]
- relojes: —

## ch04 — La ola de juguete

- beat 6 · giro · ficha — · sello —
- beat 7 · giro · PICO · ficha — · sello **AVISO** en [14]
- relojes: 4 NOV 1960 en [0]

## ch05 — Piedras rodando

- beat 8 · escalada · PICO · ficha **Q50** [cita] «ADMINISTRACIÓN DE ERTO Y CASSO · viviendo en continua aprensión y en continua alarma» — Administración del comune di Erto e Casso en [2] sobre «Erto» (122/152 car.) · aporta: La voz cuenta los avisos y las grietas, pero no que el propio municipio de Erto y Casso lo declaró por escrito. · sello **SILENCIO** en [10]
- beat 9 · giro · ficha — · sello —
- relojes: —

## ch06 — El gran rugido

- beat 10 · pico · PICO · ficha **D01** [normal] «ROCA DESPRENDIDA · 270 millones de metros cúbicos de roca» en [3] sobre «ladera» (54/94 car.) · aporta: La voz dice que la ladera entera cae al lago, pero no el volumen de roca. · sello **COLAPSO** en [20]
- beat 11 · respiro · ficha **D17** [normal] «EVACUADOS DE SU ALDEA · 486 personas» en [29] sobre «evacuaron» (33/136 car.) · aporta: La voz dice que evacuaron a toda la gente del pueblo, pero no cuántas personas eran. · sello **RABIA** en [31]
- relojes: —

## ch07 — Diarios y verdades

- beat 12 · revelacion · PICO · ficha **Q14** [cita] «RESPUESTA DE GIOVANNI LEONE · Y justicia tendréis» — Giovanni Leone en [1] sobre «justicia» (60/105 car.) · aporta: La voz cuenta el reclamo de la gente, pero no la respuesta que le dio el presidente del Consejo. · sello —
- beat 13 · cierre · ficha **D245** [normal] «CONDENA A MONTEDISON · 55.645.758.500 liras» en [18] sobre «liras» (40/62 car.) · aporta: La voz da la oferta de ENEL, pero no que en 1997 un tribunal condenó a Montedison a pagar a Longarone esta suma. · sello **MEMORIA** en [22]
- relojes: 20 FEB 1968 en [11], 29 NOV 1968 en [14]

## Lo que cayó

- ch02 beat 3 · ficha D47 «EL DESMORONAMIENTO DEL TOC · 2 km de frente y 600 m de desarrollo vertical» en [11] → **spoiler**: la voz lo dice en una oración posterior del cap o de un cap siguiente: ['2']
- ch04 beat 7 · ficha D105 «NACIMIENTO DE ENEL · Creado por ley en diciembre de 1962» en [15] → **no_dicho**: la voz lo dice en la oración ancla o en una vecina: ['1962']
- ch05 beat 9 · ficha Q43 «INGENIERO JEFE · Son sacudidas menores, no hace falta informar al ministerio» en [23] → **caben**: etiqueta + dato = 108 caracteres y en la oración [23] caben 94

## Descartados por el modelo

- Q49: Dato central del gancho, pero la voz ya lo dice en la oración 6 del capítulo 1.
- Q19: La voz ya cita a Trevisano y la puerta que se abre.
- D24: Dato central del beat 2, pero no existe en el archivo.
- D164: No existe en el archivo.
- D154: No existe en el archivo.
- D157: No existe en el archivo.
- D71: No existe en el archivo.
- D103: No existe en el archivo.
- D227: No existe en el archivo.
- D229: No existe en el archivo.
- D50: No existe en el archivo.
- Q53: La voz ya dice «la montaña que camina».
- T05: La voz ya cuenta que Müller detectó el desmoronamiento en los cincuenta.
- T04: La voz ya dice que el proyecto se aprobó en 1943.
- T03: La voz ya cuenta la compra de terrenos en Erto y Casso.
- D147: Construida entre 1956 y 1960: dato sin gancho frente a D117, que tiene cifra y no está en la voz.
- T12: La voz ya dice los 400 obreros.
- D237: La voz ya dice los cerca de 400 operarios.
- T18: La voz ya dice que Merlin denunció hacia 1959.
- D72: La voz ya nombra a SADE, FIAT, Volpi y Cini como dueños de parte de Il Gazzettino.
- T29: La voz ya dice que el llenado empezó en febrero de 1960.
- T23: La voz ya dice la fisura de casi dos kilómetros.
- D94: La voz ya dice la ola de veinte metros.
- T15: El deslizamiento de Pontesei es de 3 millones de m³ y no suma frente al nombre de la víctima.
- T21: Mismo dato de Pontesei en marzo de 1959, que la voz ya cuenta.
- T27: La voz ya dice que el informe de Dal Piaz le restó peso a Semenza.
- D119: No existe en el archivo.
- Q37: La voz ya cita a Dal Piaz.
- T36: Dato central del beat 6, pero la voz ya dice los setecientos mil metros cúbicos.
- D223: Duplica lo que la voz ya dice del 4 de noviembre y los 700.000 metros cúbicos.
- D156: La voz ya dice los 650 metros sobre el nivel del mar.
- T33: La voz ya cuenta el juicio a Merlin.
- T37: Fecha del primer artículo de Merlin (8 nov 1960) que contradice el 1959 que la voz dijo en ch03.
- T39: La voz ya cuenta la advertencia de febrero de 1961.
- D134: Da una altura de ola de 10 metros y la voz dice que nadie coincide en la altura; las fuentes se contradicen.
- D155: Da una altura de ola de 2 metros; contradice D134 y a la voz.
- D243: Da 800.000 metros cúbicos, que contradice la cifra que la voz dice.
- T34: Mismo dato de 800.000 metros cúbicos que contradice a la voz.
- D158: La fecha del movimiento de 3 cm a 1 mm por día es ambigua y roza lo que el cap 5 cuenta sobre el nivel de seguridad.
- D197: Compara con el deslizamiento final y adelanta el desastre.
- D106: Dato central del beat 7, pero la voz ya dice los 715 metros.
- D104: La voz ya dice los setecientos metros.
- Q44: La voz ya cita la frase del laboratorio.
- T50: Da 720 metros en mayo de 1963, que choca con los 700 metros de junio que la voz dice en ch05.
- T52: La voz ya dice el cambio de propiedad en julio.
- D68: La voz ya dice el centímetro y medio por día.
- D226: Dato central del beat 8, pero la voz ya dice el 2 de octubre y los avisos.
- D162: La voz ya dice el 26 de septiembre y el nivel de seguridad.
- D160: La voz ya dice junio, los setecientos metros y el medio centímetro.
- Q46: La voz ya cita la frase.
- Q28: La voz ya cita la frase.
- Q45: La voz ya cita la frase.
- T61: La voz ya cuenta la carta de Biadene a Pancini.
- Q51: La voz ya cita la posdata.
- T64: La voz ya dice las seis de la tarde y el aparejador.
- D111: La voz ya dice que nadie dio la alarma.
- D192: Revelaría la muerte de los técnicos en la central antes del capítulo 6.
- T57: Dato central del beat 10, pero la voz ya cuenta el desprendimiento.
- Q15: La voz ya cita al párroco.
- Q16: La voz ya cita a Castellano.
- Q17: La voz ya cita a Accamillesi.
- T58: La voz ya cuenta que la ola pasó por encima de la presa.
- D124: La voz ya dice los cuatro minutos.
- D132: La voz ya dice los 400 metros que arrastró a Micaela.
- D86: Los 70 metros de la ola son buen dato, pero el beat 10 admite una sola ficha y se eligió D01.
- Q25: Dato central del beat 11, pero la voz ya cita la frase.
- Q06: La voz ya cita al hombre de la aldea y los helicópteros.
- D18: La voz ya dice los seis helicópteros.
- Q13: Dato central del beat 12, pero la voz ya cita el grito de la gente.
- Q20: La voz ya cita a Buzzati.
- Q22: La voz ya cita a Bocca.
- Q23: La voz ya cita a Coppola.
- D136: La voz ya dice los dieciocho meses de la primera comisión.
- T85: La voz ya dice el 20 de febrero de 1968 de la remisión a juicio.
- T102: Dato central del beat 13, pero la voz ya dice la Casación de marzo de 1971.
- D32: La voz ya dice los ocho acusados y el suicidio de Pancini.
- T89: La voz ya dice la muerte de Pancini el día anterior al juicio.
- T92: Condena de primera instancia en 1969, valiosa pero el beat 13 admite una sola ficha y se eligió D245.
- D139: La voz ya dice los diez mil millones de liras de ENEL.
- D140: La voz ya dice la última transacción en el año 2000.
- Q56: La voz ya cita a Canestrini.
- D195: Cifra de muertos en Longarone que revelaría la magnitud del desastre en el gancho, antes de que la voz lo cuente.
````

### Salida de C (2): el USER real de Vajont recortado a ch03
````
{
 "caps": [
  {
   "cap": "ch03",
   "titulo": "La costura abierta",
   "oraciones": [
    {
     "idx": 0,
     "beat": 4,
     "texto": "El embalse se llamaba Pontesei.",
     "caben": 26
    },
    {
     "idx": 1,
     "beat": 4,
     "texto": "Ese marzo, una masa de roca entró al agua y levantó una ola de veinte metros.",
     "caben": 84
    },
    {
     "idx": 2,
     "beat": 4,
     "texto": "Un trabajador murió.",
     "caben": 15
    },
    {
     "idx": 3,
     "beat": 4,
     "texto": "Después de Pontesei, SADE encargó nuevas pericias sobre el Toc, y esas pericias identificaron una paleofrana: un deslizamiento antiguo, la cicatriz que Edoardo Semenza había estado buscando.",
     "caben": 141
    },
    {
     "idx": 4,
     "beat": 4,
     "texto": "El informe sobre esos riesgos lo escribió Giorgio Dal Piaz en mil novecientos sesenta.",
     "caben": 73
    },
    {
     "idx": 5,
     "beat": 4,
     "texto": "Dal Piaz había dicho alguna vez sobre la obra: «Si el proyecto original me parecía osado, ahora lo considero una completa locura».",
     "caben": 115
    },
    {
     "idx": 6,
     "beat": 4,
     "texto": "Su informe, en cambio, le restó peso a lo que señalaba Edoardo Semenza.",
     "caben": 68
    },
    {
     "idx": 7,
     "beat": 4,
     "texto": "Una ola de veinte metros.",
     "caben": 26
    },
    {
     "idx": 8,
     "beat": 4,
     "texto": "Un hombre muerto.",
     "caben": 15
    },
    {
     "idx": 9,
     "beat": 4,
     "texto": "Una paleofrana con nombre en un papel.",
     "caben": 36
    },
    {
     "idx": 10,
     "beat": 4,
     "texto": "El informe oficial dijo que no era grave.",
     "caben": 42
    },
    {
     "idx": 11,
     "beat": 4,
     "texto": "Una periodista de provincia escribió lo contrario.",
     "caben": 36
    },
    {
     "idx": 12,
     "beat": 5,
     "texto": "Se llamaba Tina Merlin y escribía en L'Unità.",
     "caben": 42
    },
    {
     "idx": 13,
     "beat": 5,
     "texto": "Hacia mil novecientos cincuenta y nueve publicó su primera denuncia: el Toc podía desprenderse sobre el lago.",
     "caben": 89
    },
    {
     "idx": 14,
     "beat": 5,
     "texto": "L'Unità fue el único diario nacional que siguió lo que pasaba en el Vajont antes del desastre, y lo siguió a través de ella.",
     "caben": 125
    },
    {
     "idx": 15,
     "beat": 5,
     "texto": "El diario que se leía en la zona era Il Gazzettino, y una parte de Il Gazzettino pertenecía a SADE, a FIAT, a Volpi y a Cini.",
     "caben": 141
    },
    {
     "idx": 16,
     "beat": 5,
     "texto": "En febrero de mil novecientos sesenta empezó el llenado, y el agua fue subiendo día a día por la garganta.",
     "caben": 105
    },
    {
     "idx": 17,
     "beat": 5,
     "texto": "Ese año hubo un pequeño desmoronamiento en el Toc, y después del desmoronamiento los habitantes vieron algo nuevo en la ladera: una fisura de casi dos kilómetros de largo, corriendo por la montaña como una costura abierta.",
     "caben": 194
    },
    {
     "idx": 18,
     "beat": 5,
     "texto": "Abajo, el lago seguía subiendo.",
     "caben": 26
    },
    {
     "idx": 19,
     "beat": 5,
     "texto": "El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta.",
     "caben": 68
    }
   ]
  }
 ],
 "beats": [
  {
   "n": 4,
   "cap": "ch03",
   "funcion": "giro",
   "pico": true,
   "dato_central": "T16",
   "apoyo": [
    "D94",
    "T15",
    "T21",
    "D119",
    "T27",
    "Q37"
   ],
   "cierre": "El informe oficial dijo que no era grave. Una periodista de provincia escribió lo contrario."
  },
  {
   "n": 5,
   "cap": "ch03",
   "funcion": "escalada",
   "pico": false,
   "dato_central": "T18",
   "apoyo": [
    "D71",
    "D72",
    "T29",
    "D49",
    "T23"
   ],
   "cierre": "El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta."
  }
 ],
 "archivo": [
  {
   "id": "D49",
   "texto": "En 1960, un pequeño desmoronamiento provocó una fisura de más de 1 metro de ancho y casi 2 kilómetros de largo en la montaña.",
   "fuente": "La inundación del Vajont. Representaciones periodísticas de un desastre italiano, 2005",
   "beats_que_lo_cuentan": [
    5
   ]
  },
  {
   "id": "D72",
   "texto": "Il Gazzettino, uno de los principales periódicos del noreste de Italia, era propiedad en parte de SADE y de sus dos directores, el Sr. Volpi y el Sr. Cini.",
   "fuente": "DOMINATION OF OR ADAPTATION TO NATURE? A LESSON WE CAN STILL LEARN FROM THE VAJONT, 2013",
   "beats_que_lo_cuentan": [
    5
   ]
  },
  {
   "id": "D94",
   "texto": "En el desprendimiento del embalse de Pontesei se generó una ola de 20 metros.",
   "fuente": "Vajont, la construcción de una catástrofe a la italiana, 2022",
   "beats_que_lo_cuentan": [
    4
   ]
  },
  {
   "id": "T15",
   "texto": "Un deslizamiento de 3 millones de metros cúbicos cayó en el lago de la cercana represa de Pontesei, matando a un hombre. (fecha 1959)",
   "fuente": "DOMINATION OF OR ADAPTATION TO NATURE? A LESSON WE CAN STILL LEARN FROM THE VAJONT, 2013",
   "beats_que_lo_cuentan": [
    4
   ]
  },
  {
   "id": "T16",
   "texto": "Se produce un desprendimiento en el embalse de Pontesei que genera una ola de 20 metros y mata a Arcangelo Tiziani. (fecha 1959)",
   "fuente": "Vajont, la construcción de una catástrofe a la italiana, 2022",
   "beats_que_lo_cuentan": [
    4
   ]
  },
  {
   "id": "T18",
   "texto": "La periodista Tina Merlin denuncia el peligro del desprendimiento en el periódico l'Unità. (fecha 1959)",
   "fuente": "Il disastro del Vajont non fu una calamità naturale, 2023",
   "beats_que_lo_cuentan": [
    5
   ]
  },
  "… (394 ítems más del archivo)"
 ],
 "clima": [
  "PÁNICO",
  "CALMA",
  "AMENAZA",
  "AVISO",
  "ALARMA",
  "INMINENTE",
  "COLAPSO",
  "SILENCIO",
  "RABIA",
  "MEMORIA"
 ]
}

Formato de salida: {"beats": [{"cap": "ch03", "beat": 5, "ficha": {"pool_id": "D49", "sentence_idx": 17, "palabra": "fisura", "etiqueta": "ANCHO DE LA FISURA", "texto": "Más de 1 metro", "aporta": "…"} | null, "sello": {"palabra": "AVISO", "sentence_idx": 3} | null}], "relojes": [{"cap": "ch03", "sentence_idx": 4, "fecha": "9 OCT 1963"}], "tarjeta": {"texto": "9 OCT 1963 · 22:39"} | null, "descartados": [{"pool_id": "…", "motivo": "…"}]}
````

### Salida de C (3): lo que queda en pantalla (guion, t_mp4)
| cap | t_mp4 | qué | texto | dur | papel |
|---|---|---|---|---|---|
| ch01 | 0.0 | tarjeta | 9 OCT 1963 · 22:39 | 3.0 | sí |
| ch01 | 27.1 | sello | PÁNICO | 2.5 | sí |
| ch01 | 76.5 | reloj | 9 OCT · 1963 | 8.32 | no |
| ch01 | 86.2 | ficha D131 | SALTO DE LA MASA DE AGUA · Más de 260 metros | 11.24 | sí |
| ch02 | 176.3 | sello | AMENAZA | 2.5 | sí |
| ch02 | 184.2 | punch | zoom_punch | — | no |
| ch03 | 251.2 | punch | zoom_punch | — | no |
| ch03 | 259.4 | ficha T16 | LA VÍCTIMA DE PONTESEI · Arcangelo Tiziani | 12.74 | sí |
| ch03 | 358.3 | ficha D49 | ANCHO DE LA FISURA · Más de 1 metro | 2.64 | sí |
| ch04 | 383.6 | reloj | 4 NOV · 1960 | 7.54 | no |
| ch04 | 458.8 | punch | zoom_punch | — | no |
| ch05 | 527.6 | punch | zoom_punch | — | no |
| ch05 | 597.0 | reloj | 9 OCT · 1963 | 1.88 | no |
| ch06 | 708.0 | punch | zoom_punch | — | no |
| ch06 | 708.2 | ficha D01 | ROCA DESPRENDIDA · 270 millones de metros cúbicos de roca | 5.44 | sí |
| ch06 | 840.1 | ficha D17 | EVACUADOS DE SU ALDEA · 486 personas | 5.72 | sí |
| ch07 | 877.6 | ficha (cita) Q14 | RESPUESTA DE GIOVANNI LEONE · «Y justicia tendréis» — Giovanni Leone | 5.26 | sí |
| ch07 | 877.6 | punch | zoom_punch | — | no |
| ch07 | 944.1 | reloj | 20 FEB · 1968 | 9.03 | no |
| ch07 | 986.3 | ficha D245 | CONDENA A MONTEDISON · 55.645.758.500 liras | 7.38 | sí |
| ch07 | 1013.6 | sello | MEMORIA | 2.5 | sí |

Totales: 7 textos (6 fichas + 1 cita), 3 sellos, 4 relojes, tarjeta, 6 punches, 0 agua. Chequeos: ✓ dos bloques al mismo
tiempo, ✓ bloque que cruza un corte, ✓ texto sin lectura, ✓ pregunta sin lectura, ✓ cifra que contradice la voz, ✗
a_pantalla (1/5), ✓ costuras, ✗ inicio de voz (ch07 sin rampa: previo, F32), ✓ gancho no vacío, ✓ inicio de música, ✓
tarjeta, ✗ papel sin colocar (8), ✓ papel sin alinear, ✓ relojes del papel (informativo).

### C — simulador contra el contrato (íntegro en `c/comparacion_simulador.md`)
**Lectura del contrato (13 líneas):** de las 15 de `REVISION_GUION.md`, fuera la 7 (agua, aclaración 9) y la 9 (AMENAZA ch05: RESPUESTA_C la deja condicionada a Q50, «se mide después de C»; si contara, cumple en lo literal: AMENAZA no sale en ch05). Quedan 1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15. Los t_mp4 del contrato son de F34 (intro 2.5 s); hoy la intro es 3.0 s (+0.5). Línea 2 aceptada cortada si tapa rostros; 3 en 155.4 o 211.1; 4 = ch03 AVISO y ch04 ALARMA; 6 ficha normal; 11 ficha normal D128; 13 depende del papel; 14 MEMORIA con «nunca al mismo tiempo» (referencia 1013.65).

#### (1) Las 13 líneas

| # | DEBERÍA | hoy (t_mp4, texto) | cumple | causa |
|---|---|---|---|---|
| 1 | ficha D195 «LONGARONE · 1.269 de 1.328» en el gancho (o D118 en 0:10) | gancho = D131 «SALTO DE LA MASA DE AGUA · Más de 260 metros» 86.2 s, dura 11.2 s | no | papel: descartó D195 («revelaría la magnitud del desastre en el gancho, antes de que la voz lo cuente»); D118 ni elegida ni descartada |
| 2 | CALMA ch02 162.3, aceptada cortada si tapa rostros | CALMA cortada en 162.78 (escena 6) | cumple (aceptada cortada) | papel la eligió en [6]; Fase 2: crítico «¿estorba?» — «tapa rostros de las personas sentadas en la cafetería y la Vespa» |
| 3 | AMENAZA ch02 en 155.4 o 211.1 | AMENAZA 176.34 (beat 3, escena 7, «la montaña que camina»), único AMENAZA del video | en parte | papel: la eligió en [10] (176.3), no en «colgados» ni en «deslizamiento» (211.56 hoy) |
| 4 | ch03 AVISO (≈ 267.2) y ch04 ALARMA | ch03 y ch04 sin sello | no | ch03: papel eligió INMINENTE [18] (364.84), el crítico la cortó («tapa la fisura»); AVISO el papel la puso en ch04 [14] (468.48) y Fase 2 la cortó por cruzar el corte de la escena 7 (88.03 s); ALARMA no la eligió el papel |
| 5 | ficha D71 fuera | no hay D71; ch03 beat 4 = T16 «LA VÍCTIMA DE PONTESEI · Arcangelo Tiziani» (259.4) | cumple | papel: D71 «no existe en el archivo» (D sin cifra no entra) |
| 6 | ficha «ANCHO DE LA FISURA · Más de 1 metro» en la escena 11 | D49 358.3 s, dura 2.64 s (lectura 2.1), escena 11 (349.4–360.9) | cumple | papel la eligió en [17]; Fase 2 la dejó (crítico: no estorba) |
| 8 | recorte Q50 de ~75 caracteres en 527.2 | cita Q50 cortada en 527.7 | no | papel la eligió con 127 caracteres; Fase 2 la cortó por lectura (127 car. piden 8.5 s, hay 3.4 s hasta el corte) |
| 10 | sello COLAPSO en 710.1 (escena 2) | COLAPSO cortado; el papel lo ancló en 796.3 | no | papel lo eligió en [20], 85 s después del lugar del contrato; Fase 2 lo cortó por cruzar el corte de la escena 11 (113.17 s) |
| 11 | ficha D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas» ≈ 813 | no hay D128; ch06 = D01 «ROCA DESPRENDIDA · 270 millones…» (708.2) y D17 «EVACUADOS · 486 personas» (840.1) | no | papel: D128 ni elegida ni descartada (hueco sin motivo) |
| 12 | AMENAZA fuera de ch07 | ch07 solo MEMORIA | cumple | papel |
| 13 | ficha T85 «11 imputados» ≈ 950, reloj antes | no hay T85; reloj 20 FEB 1968 en 944.07, dura 9.03 s | no (se anota; decide Omar) | papel: T85 «la voz ya dice el 20 de febrero de 1968 de la remisión a juicio» |
| 14 | MEMORIA ch07, sin chocar con D245 | MEMORIA 1013.647, 2.5 s; D245 986.3–993.7 | cumple | papel en [22]; «nunca al mismo tiempo» la dejó |
| 15 | tarjeta fecha-hora reemplaza la intro | «9 OCT 1963 · 22:39» 0:00, 3.0 s; title card ch01 a 3.0 s | cumple | papel la trae, Fase 2 la coloca |

**6 cumplen (2, 5, 6, 12, 14, 15), 1 en parte (3), 6 no (1, 4, 8, 10, 11, 13).**

#### (2) Totales

| | contrato | hoy | detalle |
|---|---|---|---|
| textos | 9 | **7** (6 fichas + 1 cita) | D131, T16, D49, D01, D17, D245; cita Q14 (877.6). Coinciden con el contrato solo D49 y D245 |
| sellos | 9 | **3** | PÁNICO 27.14, AMENAZA 176.34, MEMORIA 1013.65 |
| relojes | 4 | **4** | 9 OCT 1963 (ch01, 76.5, 8.3 s), 4 NOV 1960 (ch04), 9 OCT 1963 (ch05, 597, 1.88 s), 20 FEB 1968 (ch07) |
| tarjeta | 1 | **1** | |
| punches | 6 | **6** | ch02–ch07 |
| agua | fuera | 0 | |

El papel propuso 9 fichas y 9 sellos (la cuenta del contrato). Fase 2 dejó 7 fichas (cortó D117 crítico, Q50 lectura) y 3 sellos (cortó 3 por el crítico: CALMA, INMINENTE, RABIA; 3 por cruzar el corte: AVISO, SILENCIO, COLAPSO).

#### (3) Papel sin colocar (el chequeo del guion, tal cual: 8)

- ch02 ficha D117 «SESIÓN DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes»: cortó crítico (mira foto sola, ¿estorba?): (3) El bloque tapa parte del documento que el hombre mayor sostiene, el cual contiene texto y sellos.
- ch02 sello CALMA: «CALMA» estorba: El sello grande a media altura a la derecha tapa rostros de las personas sentadas en la cafetería y elementos clave de la escena, como la Vespa. (mira foto sola)
- ch03 sello INMINENTE: «INMINENTE» estorba: El sello tapa parte de la fisura o el paisaje que ilustra la narración. (mira foto sola)
- ch04 sello AVISO: cruza el corte de la escena 7 (88.03 s) en la palabra de más peso y en el inicio de la oración
- ch05 ficha Q50 «ADMINISTRACIÓN DE ERTO Y CASSO · viviendo en continua aprensión y en continua alarma»: cortó rotulista (lectura): sin tiempo de lectura: 127 caracteres piden 8.5 s y hay 3.4 s hasta el corte de escena (30.8 s)
- ch05 sello SILENCIO: cruza el corte de la escena 7 (74.13 s) en la palabra de más peso y en el inicio de la oración
- ch06 sello COLAPSO: cruza el corte de la escena 11 (113.17 s) en la palabra de más peso y en el inicio de la oración
- ch06 sello RABIA: «RABIA» estorba: El sello se superpone al rostro de una persona en el lado izquierdo de la imagen. (mira foto sola)

Otros chequeos: `a_pantalla` ✗ 1/5 (faltan D117, Q50, D128, D192); `inicio de voz` ✗ ch07 (previo: sin rampa, conocido desde F32); `papel sin alinear`, `dos bloques al mismo tiempo`, `bloque que cruza un corte`, `tarjeta fecha-hora`, `relojes del papel` ✓. Relojes del papel que difieren (anotados): ch05 (la voz dice 9 OCT 1963, el papel no trae reloj) y ch07 (el papel trae además 29 NOV 1968).

#### (4) Lectura del agente
- El papel no eligió 3 líneas (1, 11, 13), no siempre por una razón que el contrato comparta: D195 por «spoiler del gancho», T85 porque «la voz ya dice» la fecha, D128 (y D118) sin motivo escrito.
- Fase 2 sacó lo que el papel eligió en 5 casos de línea: AVISO, SILENCIO y COLAPSO caen por cruzar el corte (no por contenido; ninguno se recolocó); CALMA, INMINENTE y RABIA por el crítico; Q50 por lectura (127 car. en 3.4 s).
- La línea 10 falla doble: el papel ancla COLAPSO lejos de donde lo pide el contrato y Fase 2 lo corta por el corte. ch03 y ch04 quedan sin sello.

## PARADA C (dicha y seguida)
El pedido de Omar autoriza C y D en la misma tanda; las tres paradas condicionales no se dieron: el papel dio JSON válido en
el primer intento, las 7 narraciones alinean (161/161), y el reintento por ≥ 3 fichas no se hizo por el tope (no es una
parada: se anota). El contrato da 6/13 + 1 en parte: el papel eligió otras fichas que las del contrato (D131, T16, D01, D17,
Q14) y descartó D195 y T85 con motivo; Fase 2 cortó 2 fichas y 6 sellos del papel (crítico, lectura, corte). Eso lo mira
Omar con el papel a la vista (aclaración 9: la 13 depende del papel); CC no cambió ni el prompt ni el papel para acercarse
al contrato.
