# HANDOFF F65b — QA del papel: pestaña en el QA Studio con «sugerir» por beat

Rama `f11-guion-v4` (HEAD `a9aa200`). Modelo para CC: **Opus high** en Etapa A (módulo nuevo `sugerir`), **Opus medium** en B y C. Subagentes en paralelo donde haya trabajo independiente (tests, HTML vs servidor). Cero llamadas al modelo salvo las 2 pruebas reales de la Etapa A (≈ US$ 1, se informa).

## 0. Por qué
- El papel de Wittenoom (m01e-7, 13/13, 7/10) está escrito y sin aprobar. Hoy Omar lo aprueba a ciegas con `--aprobar-papel` o lo edita con `fase2b --plan-edit` a mano, pegando JSON. No hay dónde VER cada ficha sobre su oración, ni pedir otra sin re-correr el papel entero (≈ US$ 1,3).
- Decisión: DECISIONES 2026-10-31 15:49 (3.ª línea) y 16:13 (QA del papel F65b). El QA del papel es la red de seguridad para el peor caso: el autor automático manda; Omar solo corrige gusto.
- Lo que NO es: no es otra regla en el autor ni en los filtros. Nada de lo que Omar haga acá vuelve como regla al prompt.

## 1. Constantes
| valor | origen | quién |
|---|---|---|
| hasta **3** alternativas por clic de «sugerir» | DECISIONES 2026-10-31 16:13 | Omar (a confirmar al pegar) |
| autor de «sugerir» = `m01e_pantalla.MODELO`/`EFFORT` (Opus 5.5 medium) y el mismo `PANTALLA_SYSTEM` | DECISIONES 2026-10-31 14:16 / 16:13 (mismo autor, mismo archivo completo) | Omar |
| verificador de las alternativas = `pantalla_verificador.verificar` (1 llamada por clic) | DECISIONES 2026-10-31 14:20 | Omar |
| costo por clic **se informa, no frena** | DECISIONES 2026-10-29 (sin topes) | Omar |
| `cache_control: ephemeral` en SYSTEM + primer bloque del USER del autor (y de «sugerir») | propuesta del analista: hoy ningún POST usa caché; USER ≈ 90–96k tokens → US$ 0,36–0,38 por llamada; con caché leída 0,1× → ≈ 0,04 (`claude_helpers.cost_of` ya cobra cache_creation 1,25× y cache_read 0,1×, l.144-145) | analista → **Omar decide** |
| puerto/host del servidor, `BASE_DIR`, rutas `_steps` | ya existen en `qa_studio_server.py` / `fase1_5.py` | proyecto |
Nada específico de Wittenoom en el código. Ningún otro número.

Costo medido para la constante del caché (raw de F64, `por_intento`): intento 1 = 88.647 in · 17.944 out · US$ 0,71; vuelta 1 = 95.768 in · 3.051 out · US$ 0,44. Un «sugerir» tiene la entrada de la vuelta 1 (USER + papel actual; medido: 212.364 caracteres × 0,444 tok/char —la relación real de F64: 88.647 tok / 199.691 chars— ≈ 94.300 tokens in ≈ US$ 0,38) y ≈ 1–1,5k out → **≈ US$ 0,40 + verificador ≈ 0,07 = 0,47 por clic sin caché**; con caché (clics dentro de 5 min) ≈ 0,04 + 0,03 + 0,07 = **≈ 0,14**. El ≈ 0,10 de DECISIONES 16:13 solo se cumple con caché.

## 2. Módulos
1. `script_engine/m01e_pantalla.py` — hoy: autor del papel (`llamar`), `validar`, `editar`, `armar`, `a_markdown`. Después: + `sugerir(topic_id, cap, beat, n, *, steps_dir=None, post=None, juez=None, log=None) -> dict` (Etapa A) y dos constantes de texto junto a `REINTENTO_PARCIAL`/`FORMATO_REINTENTO`: `SUGERIR_USER` y `FORMATO_SUGERIR` (§3 A). `editar` acepta y conserva `juicio_verificador` en la ficha (hoy ya lo hace vía `**fi`: confirmarlo con test, no cambiar código si pasa). `PANTALLA_SYSTEM` **no cambia** (md5 85d094be… intacto). Candado = un **test** en `test_module_f65b.py` que compara `md5(PANTALLA_SYSTEM)` con `85d094bed6090b14d1802ca97433d982` y `md5(SYSTEM_V)` con su valor actual (el hook `md5_prompt` NO mira este archivo: solo `PROMPT_*.md`). **NO sumar `SUGERIR_USER`/`FORMATO_SUGERIR` a `prompt_md5()` ni cambiar `PROMPT_VERSION`**: si cambian, la `clave` de caché de `llamar` cambia y la próxima corrida del autor paga US$ 1,3 de nuevo (hoy `prompt_md5()` = `f2bfdf20…` = el del papel; verificar que sigue igual al cerrar).
2. `qa_studio_server.py` — hoy: visor de fotos/clips/audio por cap, form, miniaturas; `_preflight` (l.2200-2210) sale con `sys.exit(1)` si no hay `output/audio/<tid>` ni `output/<tid>/assets`. Después: + rutas del papel (§3 B) que leen y escriben SOLO vía `m01e_pantalla` (`cargar_papel`, `editar`, `sugerir`, `marcar_revisado`) y `fase1_5` (`aprobar_papel`, `estado_papel`, `md5_papel`); `_preflight` acepta también «existe `data/scripts/_steps/<tid>/01e_pantalla.json`» y el visor de caps tolera 0 caps (en el flujo real el papel se aprueba ANTES de la voz: sin esto el QA Studio no arranca para ningún topic nuevo; Wittenoom hoy tiene audio viejo y por eso arranca). La vista PAPEL usa el `TOPIC_ID` global del servidor (el de `--topic`); no acepta otro topic por query. El servidor no toca el JSON del papel directo.
3. `qa_studio.html` — hoy: barra de caps + `#view` por cap. Después: + botón «📄 PAPEL» en la barra (al lado de ENSAMBLAR) que abre la vista del papel en `#view` (§3 C). Un solo archivo, sin framework nuevo.
4. `claude_helpers.py` — solo si Omar aprueba la constante del caché: nueva `hx.body_cacheado(system, user, model, effort)` que arma `system=[{"type":"text","text":SYSTEM,"cache_control":{"type":"ephemeral"}}]` y `messages=[{"role":"user","content":[{"type":"text","text":USER,"cache_control":{"type":"ephemeral"}}]}]` (el prefijo cacheable es system + primer bloque); la usan `autor()` en `llamar` y `sugerir`. `_post` y `cost_of` no cambian (`_post` manda `messages` tal cual, l.122-128; `usage` llega completo). Si no la aprueba, este módulo no se toca.
Tests: `test_module_f65b.py` (nuevo) y `test_qa_studio.py` (+ rutas). Sin tocar fase1_5.py.

## 3. Etapas (un commit cada una; cada una termina con su salida en texto; una variable por etapa)

### Etapa A — `m01e_pantalla.sugerir` (sin UI)
Qué hace, en orden:
1. Carga `01e_pantalla.json` (papel actual) y `01e_pantalla.raw.json` → `ent = raw["entrada"]`. Candado: `entrada_md5(ent) == papel["entrada_md5"]` (verificado hoy: `018f9cc1…` en los dos); si no, `ValueError` («el raw no es de este papel»). `ent` del raw no trae `_pool` y `validar` lo tolera (`pool = {}`, l.455): no recargar nada del pool. La entrada es LA del autor.
2. `user = pedido(ent)` (el USER completo del autor, idéntico) + `"\n\nTU RESPUESTA ANTERIOR (el papel completo, como contexto):\n" + json.dumps(raw["final"])` + `SUGERIR_USER.format(cap=…, beat=…, n=…, excluidos=…)` + `"\n\nFormato de salida: " + FORMATO_SUGERIR`. `excluidos` = pool_ids de las fichas de TODOS los beats del papel actual (incluida la del beat pedido). Además `sugerir` descarta **en código, antes de `validar`**, toda alternativa con `pool_id ∈ excluidos` (motivo «ya está en pantalla»): no se puede confiar en `una_vez`, porque `validar` ordena por cap/beat y para ch01 beat 1 la alternativa se valida primera con `usados_ids` vacío (caería la ficha legítima del otro beat, no la alternativa).
3. POST con `PANTALLA_SYSTEM`, `MODELO`, `EFFORT`, `max_tokens` de `hx` (igual que `autor()` en `llamar`); `_track(…, "m01e_sugerir")`. `primer_json`; sin JSON → 1 reintento con `_reintento` (como el autor); si sigue sin JSON → `{"alternativas": [], "error": "sin JSON", "usd": …}`.
4. Cada alternativa pasa por `validar`: se arma `resp_k = copia de raw["final"]` con la ficha del beat pedido reemplazada por la alternativa k, `validar(resp_k, ent, juez=juez_k)` donde `juez_k` NO llama: devuelve `{}` y acumula las marcas **filtradas por `(cap, beat)` del beat pedido** (`validar` re-marca las 13 fichas del papel —D108 «Australia», Q25 «2», D23…— y esas ya están juzgadas: no van al verificador). Lo que `validar` cortó por anclaje/candado/caben/una_vez se lee de su `descartados` con `que == "ficha"` y `(cap, beat)` del beat pedido (`fichas_fuera` es un **contador**, l.467/480, no una lista). Luego UNA llamada a `pantalla_verificador.verificar(marcas acumuladas de todas las alternativas, caps)`. Como `validar` con juez `{}` deja a toda ficha marcada en «pasa» con `juicio_verificador = {motivo: "sin veredicto"}` (l.566-572), `sugerir` aplica el veredicto real después: marca «corta» → fuera con el motivo del verificador; sin marcas o «pasa» → queda con `juicio_verificador` `{regla, motivo, tokens}`. El armado de `juicio_verificador`/«corta» hoy es **inline** en `validar` (l.556-572): se **extrae** a una función (`aplicar_veredictos(fichas, veredictos)` o el nombre que CC prefiera) y la usan `validar` y `sugerir`; no se copia.
5. Devuelve `{"cap", "beat", "alternativas": [ficha validada completa (los campos de `validar` + `caben`, `caracteres`, `estilo`, `oracion`, `juicio_verificador`)], "descartadas": [{ficha propuesta, "motivo"}], "usd", "usd_autor", "usd_verificador", "segundos", "tokens_in"}`. No escribe nada en el papel. Guarda el pedido y la respuesta cruda en `01e_sugerir.log.jsonl` (append) para auditar.

Textos (completos; CC no los ajusta):
```
SUGERIR_USER = ("\n\nOmar revisó el papel y quiere OTRAS opciones para {cap} beat {beat}. Proponé hasta {n} fichas "
                "alternativas para ESE beat, con las mismas reglas que el papel completo: cada una ancla en una oración "
                "de ese beat, su `respaldo` se copia del `texto` del dato, y dice algo que la voz NO dice en ese momento. "
                "No repitas estos pool_id (ya están en pantalla en este video): {excluidos}. Ordenalas de la que más "
                "aporta a la que menos. Si no hay ninguna que valga la pena, devolvé la lista vacía.")
FORMATO_SUGERIR = ('{"alternativas": [{"pool_id": "D49", "sentence_idx": 17, "palabra": "fisura", '
                   '"etiqueta": "ANCHO DE LA FISURA", "texto": "Más de 1 metro", "respaldo": "…", "autor": "…" | null, '
                   '"aporta": "…"}]}')
```
Revisión del analista sobre el caso real (ch01 beat 1, ficha D108 «peor desastre industrial»): el modelo ve la oración 7 «Esa foto se tomó en un pueblo que hoy no figura en ningún mapa» y el archivo con 362 ítems; excluidos = los 13 en pantalla. Salida esperada: 2–3 fichas del gancho (p. ej. población/año de desaparición del mapa, la cifra de muertos si no es spoiler del pico) ancladas en idx 0–7. Riesgo conocido: proponer algo que la voz dice en ch01 → `no_dicho` lo marca y el verificador decide (el camino de F64). No hay regla nueva de estilo.

Salida de la etapa (texto): correr `sugerir` **2 veces** sobre el papel actual de Wittenoom: (a) `ch01` beat 1 (gancho, ficha fuerte D108), (b) `ch05` beat 9 (D51, ficha técnica forzada). Pegar en `lab/hyperframes/f65/SUGERIR_PRUEBA.md`: para cada corrida, las alternativas propuestas (etiqueta · texto · pool_id · oración ancla · aporta), cuál cayó y por qué (regla / verificador con su motivo), tokens in/out, segundos, US$ (autor + verificador). PARÁ si la primera corrida pasa de US$ 1 (señal de que algo mandó más de lo debido; no es tope de gasto, es alarma de bug). El papel NO se modifica.

Si Omar aprobó el caché: la primera de las 2 corridas paga la escritura (1,25×) y la segunda, si va dentro de 5 min, lee (0,1×): pegar los `usage` de ambas (cache_creation_input_tokens / cache_read_input_tokens) como prueba.

### Etapa B — rutas del servidor (sin HTML)
GET `/papel` → `{estado: estado_papel(tid) → {aprobado: bool, motivo}, md5: md5_papel, usd del papel, modelo, caps: [{cap, titulo, oraciones}], beats: [{cap, beat, funcion, pico, revisado, ficha|null, sello|null, descartes: [...]}], relojes, sin_beat: [descartes no atribuibles], a_pantalla_vacios}`. `descartes` de un beat = `papel.descartados` cuyo `pool_id` en `raw.entrada.archivo` tiene `a_pantalla.beat == beat` o `beat ∈ beats_que_lo_cuentan` (medido hoy: 61 de 62 descartes del papel de Wittenoom se atribuyen así; el restante, D138, va a `sin_beat`; no parsear el beat del texto del `motivo` del autor). Cada descarte: `{pool_id, texto del dato (archivo), tipo, motivo, quien}`.
POST `/papel/revisar` `{cap, beat, on}` → `m01e_pantalla.marcar_revisado(tid, cap, beat, on)` escribe en **`01e_pantalla.revision.json`** (`{"revisados": [[cap, beat], …]}`), NO en el papel: `md5_papel` excluye solo `aprobado` (fase1_5 l.339), así que un ✓ dentro del papel después de aprobar lo dejaría «cambió después de la aprobación». Informativo: no bloquea nada. `fase1_5.py` no se toca.
POST `/papel/editar` `{cap, beat, ficha | null}` → `m01e_pantalla.editar(tid, [{cap, beat, ficha}])` tal cual (null = quitar). La ficha que viene de una alternativa de «sugerir» trae `juicio_verificador`, `respaldo`, `aporta` y `autor` del modelo y se guardan así (`editar` los conserva vía `**fi`: test, no cambio). La edición de texto a mano trae lo que Omar tipeó y `editar` le pone `aporta: "(edición a mano)"` si no viene; **`editar` no corre candados ni verificador** (solo recalcula `caracteres`/`caben`/`palabra_en_oracion` y marca `editado`; Fase 2 la filtra después, como dice su docstring): CC no agrega validación ahí; la UI muestra el `caracteres/caben` recalculado. **Cualquier edición invalida la aprobación** (md5 cambia: ya lo hace `estado_papel`), y la UI lo muestra.
POST `/papel/sugerir` `{cap, beat}` → arranca `sugerir` en un hilo (patrón `_start_fix`/`_fix_status`: 409 si hay uno en curso); GET `/papel/sugerir_status` → `{running, result, error}`. `n` = la constante 3 (en `gfx_config` o `m01e_pantalla`, con comentario «DECISIONES 2026-10-31 16:13»).
POST `/papel/aprobar` `{por}` → 400 si `por` viene vacío; `fase1_5.aprobar_papel(tid, f"{por} {fecha}")` con `fecha = strftime("%Y-%m-%dT%H:%M")` (sin espacio interno: `aprobar_papel` parte por espacios y toma el último token como fecha, l.365-366); devuelve `aprobado`. **Nada más corre**: ni voz ni fotos.
Salida de la etapa: `curl` (o el test) de cada ruta contra el papel actual de Wittenoom pegado en `lab/hyperframes/f65/RUTAS_PAPEL.md`: el GET entero del beat 1 (oración, ficha, descartes), un `/revisar`, un `/editar` con null y su vuelta atrás (restaurando la ficha desde `01e_pantalla.antes_de_edicion.json`), el `estado` antes/después (aprobado → no aprobado por md5). **No llamar a `/papel/sugerir` real acá** (ya se midió en A; en tests va con `post` falso). No aprobar el papel.

### Etapa C — la vista en `qa_studio.html`
Botón «📄 PAPEL» en la barra. Vista: cabecera con estado (aprobado por/fecha o «sin aprobar»), US$ del papel, «X de N fichas revisadas», botón **«Aprobar papel»** (abre campo «quién», prellenado con el último `por` del JSON si existe, vacío si no) y, abajo, un bloque por cap con su título y, por beat (en orden):
- función · pico ⚡ · ✓ revisado;
- la **oración ancla** completa con la `palabra` resaltada (si `palabra_en_oracion` es false: aviso rojo «la palabra no está en la oración»);
- la **ficha como se vería**: `etiqueta` arriba (mayúsculas chicas), `texto` grande, `autor` abajo si existe; a la derecha `caracteres / caben` (rojo si no cabe) y `estilo`;
- `aporta` en cursiva; si hay `juicio_verificador`: «✔ verificador: {motivo}»;
- `sello` del beat si existe (palabra + oración);
- desplegable «descartes del autor en este beat (N)»: pool_id · texto del dato · tipo · motivo;
- botones: **✓ Aprobar ficha** (toggle `/revisar`) · **✎ Editar texto** (etiqueta y texto editables inline; guarda con `/editar` manteniendo pool_id/sentence_idx/palabra) · **✕ Quitar** (`/editar` con null, confirmación en la misma fila, sin `confirm()` del navegador) · **💡 Sugerir** (llama `/papel/sugerir`, muestra spinner + «≈ US$ … al terminar», y al volver lista las alternativas como fichas iguales a la de arriba con su `aporta` y su veredicto, con botón «Usar esta» → `/editar` con esa ficha, o «Ninguna»; las descartadas por el verificador se muestran en gris con el motivo).
- Beats sin ficha: la fila dice «sin ficha» y ofrece solo **Sugerir**. `a_pantalla_vacios` del beat se muestra como ⚠ con el `por_que` del dato (es el aviso de F65a que hoy nadie lee).
- Relojes del cap al final de cada cap (fecha · oración).
Después de cada acción la vista se recarga del GET `/papel` (la verdad es el disco).
Salida de la etapa: 3 capturas (`lab/hyperframes/f65/ui/`): la vista general, un beat con la lista de alternativas de «sugerir» (usando el resultado guardado de la Etapa A, inyectado con un `post` falso: no otra llamada real), y el estado «aprobación invalidada por edición». Más el `01e_pantalla.revision.json` resultante.

## 4. Candados
- `PANTALLA_SYSTEM` y `SYSTEM_V` no cambian (test de md5, §2.1); `prompt_md5()` y `PROMPT_VERSION` tampoco. Cero reglas nuevas de estilo. Nada de Wittenoom en el código ni en los textos.
- Llamadas reales SOLO las 2 de la Etapa A (y ninguna en tests: `post`/`juez` falsos; blindar ANTES de correr la suite, lección F64).
- El servidor no escribe el JSON del papel: todo pasa por `m01e_pantalla.editar`/`marcar_revisado`/`sugerir` y `fase1_5.aprobar_papel`. Fase 2 sigue leyendo el mismo `01e_pantalla.json`.
- Lo viejo que esto reemplaza: nada se borra (`--plan-edit` y `--aprobar-papel` siguen por consola, son la misma función). Sí se borra cualquier copia parcial que CC haga del armado de `juicio_verificador`: se extrae y se reusa.
- `main` intacta. Reporte `lab/hyperframes/f65/F65b_REPORT.md` con «lo que queda abierto», costo real por llamada, veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md` actualizado. **PARADA al final: el papel sigue sin aprobar, voz y fotos sin correr.** Omar lo abre con `python qa_studio_server.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1` → PAPEL.

## 5. Decisiones que quedan para Omar (no frenan la tanda; la tanda arranca con el voto del analista)
1. Caché de SYSTEM + USER (`cache_control`): voto del analista **sí** (baja «sugerir» de ≈ 0,47 a ≈ 0,14 por clic y la vuelta del autor de 0,44 a ≈ 0,10; no cambia ninguna salida).
2. ¿«Aprobar papel» debe exigir todas las fichas revisadas? Voto: **no**; Omar decide, la UI solo muestra «X de N».
