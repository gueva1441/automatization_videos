# HANDOFF F36 — Estructura de la capa de texto: partir, arreglar, alimentar, borrar

Analista · 2026-10-26 · Para CC. Base: `1973ba1` (F34 cierre). **Cuatro partes A→B→C→D, cada una un commit y una PARADA corta con su guion regenerado.** Sin render, sin `--aprobar-guion`. Decisiones de Omar del 26-10, 16:30–16:49 (`DECISIONES.md`, «Contenido en pantalla» y «Orden de tandas»). Reemplaza al F35 (archivado).

**Contrato de toda la tanda:** la tabla DEBERÍA de `lab/hyperframes/f34/REVISION_GUION.md` (15 líneas) + los totales (9 textos, 9 sellos, 4 relojes + tarjeta, 2 aguas, 6 punches). Cada parte termina con `fase2b f8s3-vajont-f30 --plan-only --rotulista`, el simulador compara el guion nuevo contra esa tabla y pega: línea · salió/no · por qué · qué parte la arregla. La tabla de abajo (§0.3) dice qué parte debería resolver cada línea; si una línea se resuelve antes o después de lo previsto, anotarlo, no es error.

## 0. Antes de tocar nada
1. **¿Esta tanda construye sobre código que se reemplaza?** No: ella es el reemplazo. ¿Cambia el orden? Sí: se hace antes del v6 (16:45).
2. **Módulos que toca** (stickers del mapa): `gfx_rotulista` (se parte) · `gfx_realizador` (bug del contador) · `gfx_critic` (orden: antes del reparto; pregunta a sellos) · `gfx_guion` (chequeos) · `gfx_sparse` / `fase2b` (tarjeta en lugar de la intro) · `gfx_peak`, `gfx_fragments`, `gfx_question`, `gfx_identity`, `data_callout.html.tmpl`, `grade_css.html.tmpl` (D: se borran o se vacían) · `gfx_layer` (solo imports) · `lab/MAPA_MODULOS.*` (regenerar al final de cada parte).
3. **Constantes:** ninguna nueva. Lectura 15 cps (estándar). `title_dur` 3 s (identidad F3). Duraciones de agua y reloj = derivadas: `min(duración actual, corte de escena − inicio − 1 cuadro)`. Tope de caracteres por bloque = derivado: `segundos hasta el corte × 15`. El **desempate** de textos (B.6) es: `a_pantalla` → `rank` → tiene cifra/fecha → orden de oración (Omar 16:30, vía analista). Los números sin origen que ya existen (altura del agua 15–85 %, reloj 12 s) **no se cambian**: solo se etiquetan `# sin origen (pendiente de clasificar)` para la sesión de los 66.

**§0.3 — qué parte debería resolver cada línea DEBERÍA (simulación del analista sobre la data cruda de F34):**
| línea | hoy | parte que la resuelve | cómo |
|---|---|---|---|
| 1 D195 gancho | candado por «1963» | B.7 | el candado del gancho acepta lo que la voz dice en **todo** el video (1963 a 1:16) |
| 2 CALMA ch02 | crítico («tinte de muerte») | B.2 | el crítico a sellos de clima solo pregunta «¿estorba?»; el tinte es forma |
| 3 AMENAZA ch02 | ninguno (AVISO ocupó el beat y cayó) | B.2 | crítico antes del reparto: AMENAZA entra al beat 3 |
| 4 AVISO ch03 | AMENAZA | C.3 | Sonnet elige con el relato entero y sin repetir en el video |
| 5 D71 fuera / 6 D49 | D71 ganó por orden | B.6 | desempate: D49 tiene cifra |
| 7 agua ch04 | cruza 0.53 s | B.4 | duración hasta el corte |
| 8 Q50 | 147 caracteres | B.8 + C.2 | tope en el formato de salida + «caben N caracteres» en la entrada |
| 9 AMENAZA ch05 fuera | sobre el recorte | B.2 (orden) | con Q50 vivo, «nunca sobre un texto» lo saca |
| 10 COLAPSO ch06 | INMINENTE ocupó y cayó | B.2 | crítico antes del reparto |
| 11 D128 | realizador borra el contador | B.1 | el realizador no toca el `count_up` del rotulista; el texto del contador es el valor |
| 12 AMENAZA ch07 fuera / 14 MEMORIA | Gemini | B.3 + C.3 | no repetir en el video; Sonnet elige la palabra de cierre |
| 13 T85 | «pico: solo a_pantalla» | **ninguna** (regla de Omar 14:22) | queda cortado; al final, si Omar lo quiere, `--plan-edit`. Anotar. |
| 15 tarjeta | en el plan, no se dibuja | B.9 | la tarjeta reemplaza la intro de 2.5 s |

## A. Partir `gfx_rotulista.py` sin cambiar comportamiento (commit 1)
1. Cinco módulos nuevos en `script_engine/`, con el código **movido**, no reescrito:
   - `rotulista_llm.py`: prompts (`ROTULISTA_SYSTEM/USER`, `PROMPT_VERSION`), `entrada`, `prompt_user`, `llamar`, caché, ledger, tope, reintento.
   - `rotulista_filtros.py`: `validar` y todo lo que corta, **como una lista ordenada y nombrada** `ORDEN = [anclaje, forma, candado, no_dicho, spoiler, coherencia, lectura, cantidad]` donde cada filtro es una función `(bloque, ent, ctx) -> motivo|None`; el orden se lee en una línea y se testea. `finalizar`, `contradicciones`, `numeros`, `nombres` y los parsers de español van aquí (o en `voz_utils.py` si los usan otros módulos; decidir y anotar).
   - `rotulista_colocar.py`: `colocar`, `tiempos`, `despues_del_corte`, `escena_final`, `unidades`, `mover_a_escena`, ediciones (`aplicar_ediciones`, `guardar_ediciones`), `animacion_de_cifra`.
   - `clima.py`: `sellos_por_tema`, `elegir_clima`, `palabra_clima`, `vocabulario_clima`, `SELLO_CLIMA_PROMPT`, `TEMA_DE_MOOD`, y `peak_word` traído de `gfx_peak`.
   - `voz_datos.py`: `reloj_de_voz`, `fechas_completas`, `agua_de_voz`, `tarjeta_inicial`, `pico_cap`, `pico_plan`.
   - `gfx_rotulista.py` queda como fachada: `preparar_cap`, `prefetch` y re-exports, para que `gfx_layer`, `fase2b`, `gfx_guion` y los tests no cambien de import.
2. **Verificación de que nada cambió:** `--plan-only` con el rotulista y Gemini en caché → `GUION_PANTALLA.json` **idéntico** al de F34 B (`lab/hyperframes/f34/GUION_PANTALLA.json`) salvo `generado` y `tiempos_s`; pegar el diff (debe ser vacío) en el reporte. Suite rápida y amplia iguales a F34 (1021 + 5 previas). md5 ch02 sin gfx `38e5ba14…`. Un test nuevo: `ORDEN` de filtros es exactamente el de F34 (se lee del código, no de memoria).
3. Mapa regenerado. **PARADA.**

## B. Los bugs, con el caso real de cada uno como test (commit 2)
1. `gfx_realizador.finalizar` no borra el `count_up` que puso el rotulista (solo el del director, que es el que repite la voz); el campo `texto` del contador es el **valor** (1.910), no la palabra del ancla («Guglielmo»). Caso: D128 ch06.
2. **Crítico antes del reparto** (`clima` y `rotulista_colocar`): primero el crítico juzga **todos** los candidatos de sello y de texto; después corren «un sello por beat», «una por escena», «nunca sobre un texto». A los sellos de clima y al agua el crítico solo les pregunta «¿estorba? (tapa un rostro o zona clara)»; «repite» no aplica. Casos: ch02 CALMA, ch02 beat 3, ch06 COLAPSO.
3. **Sellos: no repetir la palabra en todo el video** (`ya salió en el video`, antes del reparto); si el modelo devuelve una repetida, se pide otra de la lista (una vez) y si no hay, el beat queda sin sello. Caso: AMENAZA ×4.
4. **Agua y reloj miran el corte:** duración = `min(actual, corte − inicio − 1 cuadro)`. Casos: agua ch04 (termina antes de 88.03 s), reloj ch07 (84.7 → corte 93.77).
5. `contradicciones`: una cota/altura solo contradice a otra si las dos son **la misma magnitud en la misma oración o la vecina**; niveles anteriores del relato no cuentan. Caso: 715 vs 650/700 → sin ✗.
6. **Desempate** de «un texto por beat»: `a_pantalla` → `rank` → tiene cifra o fecha → orden de oración. Caso: D49 gana a D71.
7. **Candado del gancho:** para el gancho (pool del video entero), el candado acepta números y nombres que la voz dice en **cualquier** cap, no solo en la oración ancla. Caso: D195 con «1963».
8. **Tope de caracteres en el formato de salida** del rotulista: el JSON de salida lleva `max_chars` por bloque (lo calcula la entrada: segundos hasta el corte × 15) y el modelo lo tiene que respetar; si no, el reintento se lo dice con el número. Caso: Q50 (hoy 147 contra 75).
9. **La tarjeta fecha-hora reemplaza la intro** (`fase2b`/`gfx_sparse`): con `tarjeta_inicial` en el plan de ch01, el mp4 arranca con 3 s de negro con la tarjeta (`title_dur`) y después la primera imagen; sin tarjeta, los 2.5 s de hoy. `intro_s` del guion = 3.0; la música de ch01 sigue arrancando con su title card (medir en la mezcla). Test con y sin tarjeta.
10. Regenerar el guion (caché del modelo: el prompt no cambia en B) → simulador contra DEBERÍA. Esperado después de B: líneas 1, 2, 3, 5–7, 9–11, 15 resueltas; 4, 8, 12, 14 todavía no (son de C); 13 no (regla). **PARADA.**

## C. Lo que entra al rotulista y quién elige los sellos (commit 3; llama a Sonnet: tope US$ 1.50)
1. **Pool completo:** la entrada trae **todos** los ítems del pool del video que tengan cifra, fecha o sean cita (D con número, T, Q), no solo los asignados al beat, cada uno con `beats_que_lo_cuentan: [n]` (de la escaleta) o `[]`. Los del beat van primero. `a_pantalla` sigue viniendo y sigue siendo prioridad, pero deja de ser la única llave. Instrucción nueva en `ROTULISTA_USER`, literal: «Los datos marcados con tu beat son los que la escaleta cuenta ahí; los demás son el resto del archivo del caso: usalos si suman más que los del beat y no adelantan nada que la narración cuente después.» Medir tokens de entrada por cap antes y después (pegar).
2. **Cuánto cabe:** cada oración de la entrada lleva `caben: N` caracteres (segundos hasta el próximo corte de escena × 15; en caps de una escena, hasta el fin de la oración siguiente). Instrucción literal: «Cada oración dice cuántos caracteres caben (`caben`). Etiqueta + dato no pueden pasar de ese número; si el dato no cabe, elegí otra oración o acortalo.» Sacar de `ROTULISTA_SYSTEM` la frase «UNA línea corta» (la reemplaza `caben`): regla nueva nombra la que quita.
3. **Sonnet elige el sello de clima, en la misma llamada:** el formato de salida suma `"sello": {"palabra": <una de la lista>, "sentence_idx": n, "word_idx": k} | null` por beat; la lista viene en la entrada (`sellos_clima` del perfil) con la instrucción literal: «Por beat, como máximo un sello de clima: una palabra de esta lista que nombre lo que se siente en ese momento del relato, nunca la palabra que la voz dice ni una que ya usaste en este video (lista de usadas: …). Sin sello si ninguna suma.» `clima.py` deja de llamar a Gemini (`elegir_clima`, `_gemini_clima` y su prompt se borran); el reparto y el crítico (B.2) siguen igual. `voz_antes` y `voz_video` dejan de ir duplicados.
4. **Fuera las listas de Vajont:** `UNIDAD_CONTADOR` se borra: el contador se arma con la `unidad` que devuelve el modelo (cantidad de personas o de dinero → contador; lo decide `animacion_de_cifra` leyendo `unidad`, no una lista). `AGUA_ETIQUETAS` se borra: el agua la propone el modelo como `tipo: "agua"` (unidad m, valor, etiqueta de la oración); `agua_de_voz` deja de correr (borrar con su test). El reloj desde la voz se queda (fechas, genérico).
5. Regenerar el guion (ahora sí llama al modelo) → simulador contra DEBERÍA + totales + lista de ítems del pool que el modelo eligió fuera de su beat (para que Omar vea qué usó). Esperado: 4, 8, 12, 14 resueltas; 13 anotada. Costo pegado. **PARADA.**

## D. Borrar lo muerto (commit 4)
Borrar con sus tests, no apagar: en `gfx_peak` todo menos lo que C y A movieron (`sentences`/`lexicon_hits` → `voz_utils.py`); `gfx_fragments` entero (el `category_icon` del sello pasa a `clima.py`); `gfx_question` entero (si la escaleta no trae cierre, el guion lo marca ✗ y no se inventa); `gfx_identity` sale del pipeline (queda solo en `gfx_lab_server`); `data_callout.html.tmpl`, `grade_css.html.tmpl`; en `gfx_style` las ramas «se llama y se descarta» (`identity_transitions`, `select_punches`); en `gfx_director` `place_emphasis` por léxico y `fill_gaps`; `garantizar_pico`; en `gfx_pool` `plan_pool_documents/quote`, `pool_count_up`, `enforce_reserved`; `gfx_vision.pick_zoom`. Regenerar el guion → **idéntico** al de C (diff vacío). Mapa regenerado: 0 muertos. Suite verde (los tests de lo borrado se borran, se cuenta cuántos). **PARADA final:** `F36_REPORT.md` con las 4 comparaciones del simulador, lo abierto entero, veredicto íntegro del revisor; `ESTADO_SESION.md`.

## Frenos
Sin render, sin aprobar, sin merge. Prompts: solo los cambios literales de C.2 y C.3 (pegar antes/después y md5). `.env`, `config.py`, `_gpt_probe_analista/`, `gfx_profiles/*` fuera de git. Si una parte no cierra con diff vacío donde se exige vacío, no seguir: PARADA y reportar. Cada parte tiene que poder revertirse sola (`git revert` de un commit).
