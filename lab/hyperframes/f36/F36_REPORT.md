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
