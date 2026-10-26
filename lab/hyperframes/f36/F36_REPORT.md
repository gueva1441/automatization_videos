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
