# F65b_REPORT — QA del papel: pestaña en el QA Studio con «sugerir» por beat

Handoff `lab/hyperframes/f65/HANDOFF_F65b_qa_del_papel.md` (md5 4dfdc288cd32a3d5499861e76e5bafcc) · rama `f11-guion-v4` · corrió después de F66, sobre el papel que dejó F66 · 2026-10-31 · CC Opus 5.5 high (A), medium (B, C) · commits `9ecadee` (A), `7fe1ab2` (B), `163a487` (C). Decisiones del §5: caché **sí** y n = 3 (pedido de la tanda); «aprobar papel» no exige todas revisadas (voto del analista; la UI muestra «X de N», Omar decide).

Cómo se abre:

```bash
python qa_studio_server.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1
```

y arriba el botón **📄 PAPEL**. El papel sigue sin aprobar: leé primero «Lo que queda abierto» 1.

## Etapa A — `m01e_pantalla.sugerir` (`9ecadee`)

**Diff:** `m01e_pantalla.py`: `SUGERIR_N`, `SUGERIR_USER`, `FORMATO_SUGERIR` (textos del handoff, fuera de `prompt_md5()` y `PROMPT_VERSION`), `sugerir`, y `aplicar_veredicto` extraída del armado inline de `validar` y usada por los dos (sin copia). `claude_helpers.py`: `body_cacheado` (con `resto` para lo que no entra al prefijo) y `tokens_entrada`; `cost_of` y `_post` sin tocar. `autor()` de `llamar` usa el caché: el USER de entrada en el primer bloque, lo nuevo de una vuelta en el segundo. `PANTALLA_SYSTEM` 85d094be…, `SYSTEM_V` 104b9ea8…, `prompt_md5()` f2bfdf20… y m01e-7 sin cambios (test).

**Desvíos declarados:**
1. **La entrada de validar no es `raw["entrada"]`.** El handoff dice usar esa y no recargar el pool, pero `_para_modelo` guarda solo lo que ve el modelo: faltan `a_pantalla` (`_validar_ficha` tira KeyError), `anios`, `flash_forward` y el pool (`validar` lo toleraría, pero sin `fecha` ni `testimonio` una cita caería en falso por `cita_sin_fecha`). `sugerir` hace el USER desde `raw["entrada"]` (la del autor, idéntica) y arma la de validar con `cargar`/`entrada` más el `seg_por_palabra` y el clima del papel; **el candado exige que las dos den el mismo `entrada_md5`**, y si no, `ValueError`. Más estricto que lo pedido: si cambió la narración o el pool, no sugiere. Test `a8` y `a10`.
2. **Segunda corrida: ch02 beat 2.** ch05 beat 9 ya no es técnica (el papel nuevo trae D94); las fichas con `juicio_verificador` tienen 1 marca cada una, salvo D23 que ya no está: en el empate, la primera que no es la corrida (a).

**Salida:** `SUGERIR_PRUEBA.md`, entero:

#### F65b Etapa A — SUGERIR_PRUEBA: `sugerir` real sobre el papel nuevo

Papel `m01e-7` md5 `cceafae3cf8095e33a224f4eed326ca8` · claude-opus-5-5 medium · n = 3 · caché `cache_control: ephemeral` en SYSTEM + USER de entrada (§2.4). Segunda corrida: ch02 beat 2 (ch05 beat 9 ya no tiene ficha técnica (D94); el beat con juicio_verificador con más marcas (1; empate: el primero que no es el de la corrida a)).

#### ch01 beat 1 (gancho): hoy D108 «ESE PUEBLO · Escenario del peor desastre industrial de Australia»

| | tokens in | escritos al caché | leídos del caché | tokens out | US$ | s |
|---|---|---|---|---|---|---|
| autor | 6367 | 88299 | 0 | 1899 | 0.5049 | 23.5 (total) |
| verificador | — | — | — | — | 0.0000 | — |
| **total** | | | | | **0.5049** | |

Excluidos: D02, D102, D108, D138, D34, D44, D69, D83, D94, Q19, Q25, Q35, T80

##### Alternativas que pasan

- **D35** [normal] «ESE MINERAL · El más mortal de todos los asbestos» · en [3] «Una herida hecha por un pedazo de mineral que no cierra.» sobre «mineral» · 46/56 car.
  - aporta: Dice que el mineral que lo hirió era el tipo de asbesto más mortal, algo que la voz nunca dice en todo el video.
  - respaldo: «El asbesto azul (crocidolita), el tipo que se extraía en Wittenoom, es el más mortal de todos los tipos de asbesto.»
  - verificador: sin marcas, no se le preguntó
- **D80** [normal] «HOY, ESE PUEBLO · La mayor zona contaminada del hemisferio sur» · en [6] «Esa foto se tomó en un pueblo que hoy no figura en ningún mapa.» sobre «mapa» · 59/71 car.
  - aporta: Muestra en qué se convirtió el pueblo borrado del mapa, una escala que la voz no da en ningún momento.
  - respaldo: «El pueblo fantasma de Wittenoom es la mayor zona contaminada del hemisferio sur.»
  - verificador: sin marcas, no se le preguntó
- **D101** [normal] «ASÍ LO LLAMAN LOS AFECTADOS · El Chernobyl australiano» · en [7] «Arrancaron las señales de la carretera y borraron el nombre.» sobre «nombre» · 51/51 car.
  - aporta: Muestra el nombre con que los afectados recuerdan el pueblo cuyo nombre se borró. La voz nunca lo menciona.
  - respaldo: «La tragedia de Wittenoom es llamada por muchos afectados el 'Chernobyl australiano'.»
  - verificador: sin marcas, no se le preguntó

##### Las que cayeron

- (ninguna)

#### ch02 beat 2 (planteo): hoy Q25 «POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos.»

| | tokens in | escritos al caché | leídos del caché | tokens out | US$ | s |
|---|---|---|---|---|---|---|
| autor | 6367 | 0 | 88299 | 2434 | 0.1095 | 30.7 (total) |
| verificador | 8342 | — | — | 244 | 0.0382 | 3.9 |
| **total** | | | | | **0.1477** | |

Excluidos: D02, D102, D108, D138, D34, D44, D69, D83, D94, Q19, Q25, Q35, T80

##### Alternativas que pasan

- **D105** [normal] «LO QUE LOS ESPERABA · Un solo súper y un camión de víveres cada 15 días» · en [2] «De esa noche y de lo que vino después, ella no cuenta la música ni el vestido; cuenta que iba muy cerca de él y que confiaba en lo que venía.» sobre «venía» · 68/90 car.
  - aporta: Muestra qué tan aislada era la vida que ella imaginaba con confianza: un único súper que recibía víveres cada quince días.
  - respaldo: «Un camión traía suministros al único supermercado de Wittenoom cada 15 días.»
  - verificador: sin marcas, no se le preguntó
- **D125** [normal] «UN PUEBLO DE HOMBRES · Unos 2 hombres por cada mujer» · en [3] ««Me pegué a mi marido, como una niña pequeña», dice ella, muchos años después.» sobre «marido» · 49/71 car.
  - aporta: Muestra el pueblo al que ella llegaba pegada a su marido: un lugar con el doble de hombres que de mujeres.
  - respaldo: «La proporción de hombres y mujeres en Wittenoom era de aproximadamente 2 a 1.»
  - verificador: pasa (spoiler {'spoiler': ['2']}) — La voz nunca da la proporción de hombres y mujeres en Wittenoom; el «2» marcado no está como cifra en la oración de los españoles y los viajes de CSR, que habla de otra cosa.
- **D124** [normal] «MINA DE JÓVENES · 57% de los trabajadores, menores de 30» · en [4] «Se casaron un año más tarde, el 20 de septiembre de 1962.» sobre «casaron» · 53/61 car.
  - aporta: Muestra que la mina a la que iba el recién casado estaba llena de hombres jóvenes como él.
  - respaldo: «El 57% de la fuerza laboral de Wittenoom tenía menos de 30 años»
  - verificador: pasa (spoiler {'spoiler': ['30']}) — La voz no da la edad de la fuerza laboral; el «treinta» marcado son los años entre la salida de Daniel y su muerte, otro hecho.

##### Las que cayeron

- (ninguna)

#### Resultado

- Costo: a US$ 0.5049 (escribe el caché) · b US$ 0.1477 (lee el caché) · total US$ 0.6527.
- Papel sin modificar: md5 antes `cceafae3cf8095e33a224f4eed326ca8`, después `cceafae3cf8095e33a224f4eed326ca8` (iguales).
- `usage` a: [{"input_tokens": 6367, "cache_creation_input_tokens": 88299, "cache_read_input_tokens": 0, "cache_creation": {"ephemeral_5m_input_tokens": 88299, "ephemeral_1h_input_tokens": 0}, "output_tokens": 1899, "service_tier": "standard", "inference_geo": "global", "speed": "standard", "output_tokens_details": {"thinking_tokens": 1339}}]
- `usage` b: [{"input_tokens": 6367, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 88299, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0}, "output_tokens": 2434, "service_tier": "standard", "inference_geo": "global", "speed": "standard", "output_tokens_details": {"thinking_tokens": 1904}}]
- tokens_entrada a/b: [94666] / [94666]


**Lectura de CC:** el caché cumple lo que el analista estimó: la primera corrida escribe 88.299 tokens y la segunda los lee (US$ 0,50 → 0,15). Las 6 alternativas pasaron candados y verificador, 0 cayeron, y se leen bien (D80 «La mayor zona contaminada del hemisferio sur» es la que el analista marcaba como DEBERÍA del gancho). «Esa foto» y los índices de oración son los de la narración corregida de F66.

**Tests:** `test_module_f65b` Etapa A (13), con `claude_helpers._post` explotando si alguien lo alcanza. Tests viejos que leen el body del autor adaptados (f37a, f38e_c, f40, f64: el USER ahora va en bloques).

## Etapa B — rutas del servidor (`7fe1ab2`)

**Diff:** `qa_studio_server.py`: `papel_vista` (GET `/papel`), `papel_post` (`/papel/revisar`, `/papel/editar`, `/papel/sugerir`, `/papel/aprobar`), `_start_sugerir`/`_sugerir_status` (patrón del fix; 409 si hay uno en curso), `_preflight` acepta un topic con solo el papel. `m01e_pantalla.py`: `marcar_revisado`/`revisados` (`01e_pantalla.revision.json`, fuera del papel). El servidor no escribe el JSON del papel (test sobre el código). `fase1_5.py` sin tocar.

**Agregado no pedido (declarado):** un papel nuevo borra `01e_pantalla.revision.json` (un ✓ de otro papel mentiría); un hit de caché no.

**Salida:** `RUTAS_PAPEL.md`, entero. Corre sobre una **copia** del papel, no sobre producción: el handoff pide mostrar aprobado → invalidado y a la vez no aprobar, y la vuelta atrás por `/editar` no deja el mismo md5 (queda `editado` y `ediciones`), así que hacerlo en producción habría cambiado el papel.

#### F65b Etapa B — RUTAS_PAPEL: cada ruta por HTTP (copia del papel actual, 0 llamadas)

Copia temporal de `01e_pantalla.json, 01e_pantalla.md, 01e_pantalla.raw.json`; md5 del papel `cceafae3cf8095e33a224f4eed326ca8`. Lo que se aprueba y se edita acá no llega a producción.

#### GET /papel

Cabecera: `estado` {"aprobado": false, "motivo": "el papel no está aprobado"} · md5 `2df09a51ac79ece83e0a1eaf54cda99a` · US$ 1.23091 · claude-opus-5-5 · fichas 13 · revisadas 0 · cierre sin motivos · sin_beat 1 · a_pantalla_vacios 5 · aviso_narracion 1

Descartes atribuidos a algún beat: 56 filas · sin beat: ['Q22']

El beat 1 entero:

```json
{
 "cap": "ch01",
 "beat": 1,
 "funcion": "gancho",
 "pico": true,
 "revisado": false,
 "ficha": {
  "pool_id": "D108",
  "sentence_idx": 6,
  "palabra": "pueblo",
  "palabra_en_oracion": true,
  "etiqueta": "ESE PUEBLO",
  "texto": "Escenario del peor desastre industrial de Australia",
  "respaldo": "La industria de la crocidolita de Wittenoom es considerada el peor desastre industrial en la historia de Australia.",
  "estilo": "normal",
  "aporta": "Dice la escala de lo que pasó en el pueblo de la foto, algo que la voz nunca dice.",
  "oracion": "Esa foto se tomó en un pueblo que hoy no figura en ningún mapa.",
  "caracteres": 61,
  "caben": 71,
  "anio": null,
  "relato": null,
  "juicio_verificador": {
   "regla": [
    "no_dicho"
   ],
   "motivo": "La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra 'Australia'.",
   "tokens": {
    "no_dicho": [
     "Australia"
    ]
   }
  }
 },
 "sello": {
  "palabra": "AMENAZA",
  "sentence_idx": 3,
  "oracion": "Una herida hecha por un pedazo de mineral que no cierra."
 },
 "descartes": [
  {
   "pool_id": "D85",
   "texto": "Daniel Écija padre se hirió el pie con un trozo de amianto y la herida no se cerraba.",
   "tipo": "voz_lo_dice",
   "motivo": "La herida que no cerraba la cuenta la voz en ch01.",
   "quien": "modelo",
   "que": null
  }
 ],
 "a_pantalla_vacio": []
}
```

#### POST /papel/revisar

`{cap: ch01, beat: 1, on: true}` → `{"revisados": [["ch01", 1]]}`
- `01e_pantalla.revision.json`: `{
 "revisados": [
  [
   "ch01",
   1
  ]
 ]
}`
- md5 del papel sin cambios: True · revisadas 1

#### POST /papel/aprobar (solo en la copia)

`{por: Prueba}` → `{"aprobado": {"por": "Prueba", "fecha": "2026-10-31T17:08", "md5": "2df09a51ac79ece83e0a1eaf54cda99a"}}`
- estado: `{"aprobado": true, "motivo": "papel aprobado por Prueba (2026-10-31T17:08), md5 2df09a51…"}`

#### POST /papel/editar con null

`{cap: ch05, beat: 9, ficha: null}` (quitaba D94) → `{"ok": true}`
- ficha ahora: None
- estado antes: `{"aprobado": true, "motivo": "papel aprobado por Prueba (2026-10-31T17:08), md5 2df09a51…"}`
- estado después: `{"aprobado": false, "motivo": "el papel cambió después de la aprobación de Prueba (2026-10-31T17:08): md5 2df09a51… → 23e2caba…"}`
- `01e_pantalla.antes_de_edicion.json` existe: True

#### Vuelta atrás (la ficha desde `01e_pantalla.antes_de_edicion.json`)

→ `{"ok": true}` · ficha D94 «EN 1989, CSR PAGÓ · 18,3 millones de dólares australianos a 200 afectados» · juicio_verificador conservado: True · editado: True
- md5 vuelve al original: False (`editar` deja `editado` y `ediciones`: el papel «restaurado» por la ruta tiene otro md5; para volver byte a byte, copiar el `antes_de_edicion`)
- estado: `{"aprobado": false, "motivo": "el papel cambió después de la aprobación de Prueba (2026-10-31T17:08): md5 2df09a51… → 3fa43a8c…"}`

#### POST /papel/sugerir

No se llama acá (0 llamadas): ya se midió en la Etapa A. Probada en `test_module_f65b::test_b4` con un `sugerir` falso: hilo, 409 si hay uno en curso, `GET /papel/sugerir_status`.

#### Producción intacta

- 01e_pantalla.json: `cceafae3cf8095e33a224f4eed326ca8` · igual: True
- 01e_pantalla.md: `8e800b88921b640704ef3cf7e5da81c1` · igual: True
- 01e_pantalla.raw.json: `22375a5f4ad1bafdc16fd7a1f1a5f175` · igual: True
- `01e_pantalla.revision.json` en producción: False


**Tests:** `test_module_f65b` Etapa B (9, por HTTP en un puerto local). `test_qa_studio` verde.

## Etapa C — la vista (`163a487`)

**Diff:** `qa_studio.html`: botón «📄 PAPEL» al lado de ENSAMBLAR; vista con cabecera (estado, US$, cierre, «X de N», «Aprobar papel» con campo quién), aviso de la narración, y por cap los beats: función, ⚡, oración ancla con la palabra resaltada (aviso rojo si no está), la ficha como se vería, `caracteres / caben` (rojo si no cabe), `aporta`, «✔ verificador», sello, ⚠ de `a_pantalla` con su `por_que`, descartes desplegables, relojes, y los botones ✓ · ✎ · ✕ (confirmación en la fila, sin `confirm()`) · 💡 con sus alternativas («Usar esta» / «Ninguna», caídas en gris con motivo). Sin caps en disco, el visor abre el papel solo. Después de cada acción se recarga de GET `/papel`.

**Salida:** `ui/capturas.py` maneja la vista en Chrome de verdad (Playwright, headless), sobre una copia y con `sugerir` falso que devuelve el resultado de la Etapa A (0 llamadas): 13 beats, ✓ en 2 fichas, sugerir → 3 alternativas, ninguna, aprobar sin quién → error, aprobar, quitar con confirmación, editar texto. **0 errores de consola**, producción intacta (md5 `cceafae3…`). Capturas en `lab/hyperframes/f65/ui/`: `1_general.png`, `2_sugerir.png`, `3_invalidada.png`. `ui/01e_pantalla.revision.json`:

```json
{
 "revisados": [
  [
   "ch01",
   1
  ],
  [
   "ch02",
   2
  ]
 ]
}
```

No probé `python qa_studio_server.py --topic …` con el navegador abriéndose ni el flujo `sugerir` real desde el botón (costaría otra llamada); sí `_preflight`, `caps()` y el `Handler` real. Las capturas muestran el papel de hoy; el título dice «documental» en la copia porque ahí no está el guion final.

## Costo real por llamada

| llamada | in | escritos al caché | leídos | out | US$ |
|---|---|---|---|---|---|
| sugerir ch01 beat 1, autor | 6.367 | 88.299 | 0 | 1.899 | 0,5049 |
| (sin marcas: no llamó al verificador) | | | | | 0 |
| sugerir ch02 beat 2, autor | 6.367 | 0 | 88.299 | 2.434 | 0,1095 |
| sugerir ch02 beat 2, verificador | 8.342 | | | 244 | 0,0382 |
| **total F65b** (alarma del handoff: 1 por corrida) | | | | | **0,6527** |

## Lo que queda abierto

1. **No aprobar antes de decidir F66.** El papel ancla en una narración de la que F66 borró la promesa del gancho y el re-gancho (F66_REPORT, «Lo primero»). El QA no lo muestra: solo enseña el aviso de ch03 [15]. Si la narración se restaura o se corrige, el papel se re-escribe (≈ US$ 1,2) y lo revisado se borra solo.
2. **Decisión 5.2 de Omar:** «aprobar papel» no exige todas las fichas revisadas (voto del analista). Cambiarlo es una línea.
3. **El caché no siempre ahorra en el autor** (derivado de los tokens de F66, no medido): sin vuelta, escribir cuesta 1,25× sobre 88.300 tokens, ≈ US$ 0,09 más; con una vuelta, ahorra ≈ US$ 0,32. En `sugerir` dentro de los 5 minutos baja de ≈ 0,47 a ≈ 0,15 (medido); pasados los 5 minutos, ≈ 0,56 porque vuelve a escribir.
4. **Editar a mano no corre candados** (por diseño del handoff): la UI muestra `caracteres / caben` y Fase 2 la filtra después, sin `juicio_verificador`. Una ficha salvada por el verificador que se edita a mano pierde el juicio y puede caer en Fase 2.
5. **`sugerir` ve `raw["final"]`, no las ediciones de Omar**, como contexto; los excluidos sí salen del papel editado. Una alternativa puede repetir algo que Omar ya sacó: no rompe, se ve.
6. **La voz con `--from normalizer_gate`, no `--from audio`** (F66_REPORT, abierto 3): cuando se apruebe.
7. **PARADA:** el papel sigue sin aprobar; voz y fotos sin correr.

## Veredicto de revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

Corrí test_module_f65b + test_qa_studio + test_module_f64: 82 passed, con proxy muerto. No llamé a ninguna API ni re-corrí los scripts de lab. Producción antes y después: 01e_pantalla.json md5 cceafae3…, sin `aprobado`, sin 01e_pantalla.revision.json, sin antes_de_edicion, log jsonl con 2 líneas.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | SUGERIR_USER / FORMATO_SUGERIR byte a byte | OK | Extraje las líneas 42-49 del handoff, hice exec y comparé: igualdad exacta en las dos constantes |
| 2 | Prompts intactos, textos fuera de prompt_md5 | OK | PANTALLA_SYSTEM 85d094be…, SYSTEM_V 104b9ea8…, prompt_md5 f2bfdf20…, m01e-7. Test a1. La `clave` de caché no cambia (m01e_pantalla.py:903) |
| 3 | A.1 candado de entrada | OK, con desvío justificado | m01e_pantalla.py:1255-1266. Medí: raw["entrada"] no trae a_pantalla y `_validar_ficha` hace `ent["a_pantalla"]` (l.680, KeyError). md5 raw = papel = rearmada = db0fe240…. El candado es más estricto que lo pedido. Test a10 |
| 4 | A.2 USER y excluidos en código antes de validar | OK | l.1267-1270 y 1286-1292. pedido(raw["entrada"]) es idéntico a pedido(ent), mismo md5 y 198.930 caracteres. Tests a4 y a5 |
| 5 | A.3 POST, _track, reintento sin JSON | OK | l.1272-1296: body_cacheado, `_track("m01e_sugerir")`, 1 reintento, `error: "sin JSON"`. Test a9 |
| 6 | A.4 juez que acumula solo las marcas del beat, UNA llamada, aplicar_veredicto extraída | OK | juez_k filtra por (cap, beat); el verificador se llama una vez y solo si hay marcas. `aplicar_veredicto` (l.621-640) la usan validar y sugerir. No queda copia del armado inline. Tests a6, a7, a13 |
| 7 | A.5 salida, log jsonl, no escribe el papel | OK | Claves de salida completas; log con ts, cap, beat, n, user_md5, pedido, respuesta_cruda, resultado. Test a11. Papel intacto |
| 8 | body_cacheado y su uso | OK | claude_helpers.py (+17). `autor()` de llamar y sugerir lo usan; `cost_of` y `_post` sin tocar. Tests a2 y a3 |
| 9 | usage de SUGERIR_PRUEBA.md contra json y log | OK | Coinciden: a escribe 88299, b lee 88299, tokens_in 94666 = 6367+88299. Recalculé con hx.cost_of: 0.50494, 0.10947, verificador 0.03825, total 0.65266 ≈ 0.6527. El log tiene las mismas 2 corridas |
| 10 | Rutas B (GET /papel, revisar, editar, sugerir 409/status, aprobar 400, fecha sin espacio, nada más corre) | OK | qa_studio_server.py:1911-2026; tests b1-b9 por HTTP. Corrí papel_vista sobre producción: 57 descartes, 56 atribuidos y 1 sin beat (Q22), igual que RUTAS_PAPEL.md. Revisión fuera del papel y md5 sin cambio (b2). b8 comprueba que la zona no escribe el JSON |
| 11 | _preflight y visor con 0 caps | OK | Test b6 |
| 12 | Vista C (cada elemento) | OK | qa_studio.html. Verifiqué en el código: cabecera, X de N, quién prellenado, oración con `<mark>`, aviso rojo, caracteres/caben rojo, aporta, ✔ verificador, sello, ⚠ a_pantalla con por_que, descartes, relojes, ✓ ✎ ✕ con confirmación sin confirm(), 💡 con Usar esta / Ninguna, caídas en gris, "sin ficha" solo con Sugerir, recarga de GET. Faltan el spinner real y el estimado de US$ (ver obs. 4) |
| 13 | 3 capturas | OK | Las miré con Read: 1_general (cabecera, aviso ch03 [15], beats), 2_sugerir (3 alternativas D35/D80/D101 con Usar esta y Ninguna), 3_invalidada ("Aprobación invalidada", 2 de 12 revisadas). Las 3 muestran la copia, con título "documental" y "0 capítulos" |
| 14 | Candados generales | OK | Nada de Wittenoom en el código añadido (grep). fase1_5.py sin tocar. Un commit por etapa (9ecadee, 7fe1ab2, 163a487). Ninguno en main. Papel sin aprobar |
| 15 | ESTADO_SESION.md actualizado (§4 y CLAUDE.md) | FALLA hoy | lab/ESTADO_SESION.md no menciona F65b ni F66; su cabecera sigue en F65a (último commit a9aa200). En F65a se actualizó después del veredicto, así que es subsanable, pero hoy no está hecho |
| 16 | test_qa_studio.py "(+ rutas)" (§2) | PARCIAL | test_qa_studio.py no aparece en el diff. Las rutas se prueban en test_module_f65b (b1-b9) y test_qa_studio sigue verde |

Fuera de alcance: ninguno. El diff 17f830e..HEAD son solo los archivos declarados y los 2 stickers. Los ajustes a f37a, f38e_c, f40 y f64 son un helper `_txt` porque el USER pasó a bloques. Sin commitear: F65b_REPORT.md y ENTRADA_ANALISTA_2026-10-31c.md (esperable, falta el veredicto). DECISIONES.md y diag_234_cap4.py ya estaban modificados antes de la tanda.

Juicio de los desvíos:
1. Entrada por cargar/entrada con candado de md5: JUSTIFICADO, comprobado (ver fila 3).
2. Segunda corrida en ch02 beat 2: ACEPTABLE. ch05 beat 9 hoy trae D94, que no es técnica. D108, Q25 y D94 tienen 1 marca cada una (D23 ya no está). El desempate "el primero que no es la corrida a" es arbitrario, pero está declarado. D94 con `fecha_relato` empataba igual.
3. rutas_papel y capturas sobre una copia: JUSTIFICADO. El handoff pide a la vez no aprobar y mostrar aprobado → invalidado. Un /editar real en producción deja `editado`, `ediciones` y antes_de_edicion, y no se puede volver al md5 original. Producción intacta, comprobado.
4. Un papel nuevo borra la revisión: ACEPTABLE. No estaba pedido, está declarado y tiene el test b9.
5. `resto` en body_cacheado: CONFORME al handoff §2.4 ("primer bloque del USER"). Dos bloques en vez de un string cambia la tokenización en la unión, así que "no cambia ninguna salida" es plausible pero no demostrado.

"Lo que queda abierto": HONESTO. El punto 1 coincide con F66_REPORT ("Lo primero": se perdieron la promesa del gancho y el re-gancho, cap 1 pasó de 161 a 118 palabras). Es correcto que el QA no lo muestra: solo enseña el aviso de ch03 [15]. Que un papel regenerado borra lo revisado es cierto (b9). El punto 3 (caché) es aritmética de tokens y está marcado "no medido". Los puntos 4 y 5 son ciertos en el código.

Observaciones:
1. Falta actualizar ESTADO_SESION.md (fila 15). El reporte tiene "(pendiente)" en el veredicto, esperable.
2. Editar a mano (ppGuardar) manda una ficha sin `respaldo` ni `juicio_verificador`, y `editar` los pierde. El reporte declara el segundo, no que también se pierde el `respaldo`. Fase 2 no lee `respaldo` (grep en pantalla_entrada, colocar y filtros: 0 usos), así que el efecto práctico es solo el del juicio.
3. El log guarda `pedido` = solo el segundo bloque (papel anterior + SUGERIR_USER), más `user_md5`. No guarda el pedido literal completo. Es aceptable para auditar y no está declarado.
4. En la UI el "spinner" es solo texto ("💡 sugiriendo…"). El "≈ US$ 0,14 a 0,47" está hardcodeado en el HTML. Son números del handoff, no nuevos, pero no hay estimado calculado. Las caídas en gris están en el CSS y el JS, pero ninguna captura las muestra (0 caídas en el resultado inyectado).
5. `papel_vista` usa `_steps_dir(state)` para el papel y `fase1_5.estado_papel/aprobar_papel` usa `fase1_5.STEPS_DIR`. En producción es el mismo directorio; en una copia hay que parchear los dos, como hacen tests y capturas.

Riesgos que el contrato no cubre:
- El resultado de un "sugerir" (≈ US$ 0,15 a 0,56) vive solo en memoria del servidor y del navegador: si Omar recarga la página, lo pagado se pierde (queda en 01e_sugerir.log.jsonl).
- El TTL del caché de 5 min en la vuelta del autor (primera llamada de ~17k tokens de salida) no está medido, y el ahorro del autor está derivado, no medido.
- El botón "Aprobar papel" no advierte lo de F66 más allá del aviso de ch03 [15]. La decisión de no aprobar antes de resolver F66 depende de que Omar lea el reporte.

### Adenda de CC
- **Fila 15:** hecho en el commit de cierre, junto con este veredicto.
- **Fila 16:** desvío menor, declarado: las rutas se prueban por HTTP en `test_module_f65b` (b1-b9) y no en `test_qa_studio.py`, cuyo docstring promete «SIN socket, SIN red».
- **Obs. 2 y 3:** ciertas, quedan así. El `respaldo` no lo lee Fase 2; el log guarda el `user_md5` del USER de entrada porque ese texto ya está entero en `01e_pantalla.raw.json`.
- **Obs. 4:** el estimado sale de la tabla de constantes del handoff («≈ 0,14 … ≈ 0,47»). Medido hoy: 0,5049 y 0,1477; el rango del botón queda un poco corto arriba. No lo cambié (no hay número nuevo sin que Omar lo vea): queda anotado.
- **Riesgo 3:** es el mismo de «abierto» 1, y por eso el bloque «Para Omar» arranca con la recomendación de no aprobar todavía.
