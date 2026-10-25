# HANDOFF F26 — Nocturno: cerrar los ajustes, producir el primer video (Vajont), workers y hooks

Analista · 2026-10-25 04:40 · Para CC, **sesión nueva**, sin paradas intermedias (Omar duerme). Base: `c80e601` (rama `f11-guion-v4`). Orden fijo: A → B → C → D → E. Si una parte se traba, se deja anotada y se sigue con la siguiente. **Nada se publica, nada se mergea, nada se borra.** Topes por parte; pasado el tope, PARADA de esa parte y a la siguiente.

Contexto mínimo (leer antes): `lab/ESTADO_SESION.md` · `lab/hyperframes/f25c/F25c_REPORT.md` · `lab/hyperframes/f25c/NARRACION_gvE2.md` (el guion de Vajont, 9/10 según el analista; **es el guion del primer video**). Mapa de modelos cerrado: Gemini busca y lee → Sol ficha → Fable escaleta y guion (claude_helpers: streaming, max_tokens 100000, effort medium salvo guion high, JSON sin esquema para salidas grandes, cruda guardada).

## A. Dos ajustes de prompt de la escaleta y una re-corrida (tope US$ 8 crédito Claude)
1. `PROMPT_ESCALETA` f25-1 → f26-1, **solo** estas líneas:
   - En `<oficio>` §2, después de la oración de la promesa, agregar: «Probala así: si la oración se puede leer como un resumen de lo que viene («nadie lo sabrá durante años», «terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con lo que se ve o lo que no cierra.»
   - En `<oficio>` §10 (pantalla), agregar al final: «Un id que va a `a_pantalla` no va en ningún beat.»
   - En `<que_es_una_escaleta>`, al final del párrafo del antagonista: «Su nombre va exactamente como está escrito en la ficha, sin siglas ni paréntesis agregados.»
   md5 nuevo; SYSTEM_V2 idéntico al archivo. Nada más cambia. Ningún chequeo nuevo.
2. Re-corrida: Kyshtym (ficha fS2 de F25a) escaleta Fable ×2 → guion Fable ×2, en paralelo. Reportar promesa textual de cada una, si pasó en primera pasada, bloqueantes, palabras, citas. Si una promesa sigue adelantando, anotarlo (no insistir).
3. **Reparación (e) automática**: el guion con una cita sin verificar y con nombre se repara por edición como ya existe (quita el nombre, deja el rol). Confirmar que corre sola en estas corridas.

## B. Producción: el video de Vajont (tope: Claude US$ 2 · Gemini US$ 5 · imágenes ≤ 100 · voz lo que el plan permita)
Guion: `lab/hyperframes/f25c/gvE2/` (2.355 palabras). Pasos, por el camino normal que ya existe desde F10: partición en `fase1_5`, assets con `fase2a.py --topic f8s3-vajont` (imágenes, voz, gfx), ensamble con `fase2b.py`:
1. Partición en 7 caps (`m01d`) con los intents **desde la escaleta** (F23). Si la partición mueve un párrafo de cap por largo, anotarlo; no reescribir nada.
2. Imágenes v3 (F8/F8b, Seedream 5.0 Lite): ancla por beat, estilo, grade. **Tope 100 imágenes.** Con 19 minutos, repartir por duración real de cada cap, no por el contrato 45/105/45 fijo: la duración de cada cap sale de sus palabras ÷ 2.05.
3. Voz (F9): ElevenLabs v4, voz «MS Narrador v1», etiquetas de `tts_tags` con el intent real de cada cap. `narration` limpia para subtítulos.
4. gfx (F1–F5): director con doctrina, identidad `misterio`, bloques desde el pool. Si algo del gfx se rompe con un guion de 19 min, se **apaga el gfx para este video** y se anota; el video sale sin gfx antes que no salir.
5. Ensamble → `video_vajont_f26.mp4` + `compara`/QA Studio como siempre. **No publicar.**
Decisiones tomadas: título provisional «Vajont: la montaña que caminaba»; idioma español neutro; sin música nueva (la que ya usa el pipeline). Si un paso falla dos veces, PARADA de B con el log y seguir con C.

## C. Workers en el research (0 API)
- `researcher_steps/research_v3.py`: R2 (descargas) y R3 (extracción por documento) corren con un `ThreadPool` de **8 workers** por defecto (`--workers N`), respetando los cupos por idioma y los topes de costo con lock (como el runner de F25a). R4/R5 siguen igual. El `cost_tracker` recibe desde los hilos sin pisarse (lock o cola).
- `fase1_5`: `--temas a,b,c` corre varios temas en procesos separados (uno por tema), porque `set_vocabulario` es global de proceso.
- Tests sin red: los mismos resultados que en fila (mismo pool con un mock de R3 que devuelve lo guardado); dorado v3 verde.
- Prueba sin gasto: R2+R3 sobre los documentos ya bajados de Kyshtym con el registro de fuentes de F24 (reusa txt e ítems), medir pared con 1 vs 8 workers.

## D. Hooks de Claude Code (0 API)
En `.claude/settings.json` + `.claude/hooks/` del repo (commiteados), en Python:
1. `PreToolUse` Bash: bloquea (exit 2) cualquier `git commit`/`git add` que incluya `.env`, `config.py`, `lab/_gpt_probe_analista/` o archivos con `sk-ant-`/`sk-proj-` adentro; bloquea `git push`/`merge` hacia `main`.
2. `PreToolUse` Bash: antes de `git commit`, corre la suite rápida (`test_module_f25c.py test_module_f24.py test_module_f21.py`, < 2 min); rojo → bloquea con el tail del error.
3. `PostToolUse` Edit/Write sobre `PROMPT_*.md` o archivos con `## SISTEMA`/`SYSTEM_V2`: avisa el md5 nuevo y el viejo (no bloquea).
4. `PreToolUse` Bash: antes de `python fase1_5.py` o `python fase2a.py`, lee `lab/TOPE_TANDA.json` (`{"usd": N}`) y el gasto de la tanda en `cost_history`; pasado → bloquea.
Probar cada hook con un caso que bloquea y uno que pasa. Documentar en `.claude/hooks/README.md`.

## E. Si sobra tiempo (opcional, tope US$ 4 crédito)
Ficha con Opus 5.5 con la forma de los campos **dicha en el pedido** (un párrafo con los nombres exactos de los campos; sin esquema forzado) ×2 sobre el pool de Kyshtym; tabla contra fS2. Es para decidir después; no cambia nada en producción.

## Frenos
- Cero reglas de estilo nuevas; cero chequeos nuevos. Prompts solo en las líneas de A.1.
- No tocar `m03*`/`gfx_*`/voz salvo para que corran con el guion de 19 min (parámetros, no lógica); cada cambio de esos, anotado.
- Sin merge, sin publicar, sin borrar. No commitear `.env`, `config.py`, `lab/_gpt_probe_analista/`.
- `lab/ESTADO_SESION.md` actualizado al final con el estado exacto para que Omar lo lea al despertar.

## Reporte `lab/hyperframes/f26/F26_REPORT.md`
Por parte: hecho / no hecho / qué se trabó. A: tabla de promesas y bloqueantes. B: ruta del video, duración, imágenes generadas, costo por paso, lo que se apagó. C: pared 1 vs 8 workers. D: tabla de hooks con su prueba. Veredicto íntegro del revisor-handoff. **PARADA final.**
