# HANDOFF F33 — Infraestructura: que el proceso viva en archivos, no en cabezas

Analista · 2026-10-26 · Para CC. Base: `cd60c74` (F32 C). Cinco partes A→E; **PARADA al final de E**. API: 0. **Sin render, sin cambios de reglas de contenido, sin tocar prompts.** Todo lo de aquí es procedimiento, compuertas y mapa; lo decidió Omar el 26-10 (12:52–14:11; ver `DECISIONES.md`, «Pendientes de infraestructura»).

## 0. Constantes
Ninguna nueva. Los valores que aparezcan en hooks/tests (p. ej. tamaño de un sticker) son de formato, no del pipeline, y se anotan en el reporte.

## A. `DECISIONES.md` y `ENTRADA` entran al repo; las constantes declaran su origen
1. Commitear `DECISIONES.md` (raíz) y `lab/hyperframes/f32/ENTRADA_ANALISTA_2026-10-26.md` tal como están (los escribió el analista; no editar el contenido; si algo es falso, anotarlo en el reporte).
2. **Test `test_constantes_con_origen.py`:** toda constante numérica de `gfx_config.py` (`GfxRules`, `GfxRenderSettings`, `TransitionRenderSettings` en `transition_config.py`) tiene en la misma línea un comentario de origen con una de estas formas: `# DECISIONES: <línea o fecha>`, `# identidad F3`, `# estándar: <nombre>`, `# derivado: <de qué>`, `# medido: <dónde>`. El test lista las que no lo tienen. **En esta tanda el test corre en modo inventario** (no falla): el reporte trae la lista completa de constantes sin origen para que Omar y el analista las clasifiquen; CC solo etiqueta las que ya son evidentes (valores de identidad F3 del perfil, cps=15 estándar, las que `DECISIONES.md` nombra). Nada se cambia de valor.
3. `CLAUDE.md`: una línea nueva al inicio: «Leé `DECISIONES.md` antes de cualquier tanda; un número que no esté ahí, en la identidad F3 o en un estándar citado, no entra al código».

## B. Compuerta del render: sin guion aprobado no hay `--gfx`
1. **Aprobación:** `fase2b <topic> --aprobar-guion "<quién> <fecha>"` escribe en `output/<topic>/GUION_PANTALLA.json` el bloque `aprobado: {por, fecha, md5_planes}` donde `md5_planes` es el md5 conjunto de los `gfx_plan_chNN.resolved.json` del topic en ese momento. Lo corre CC **solo cuando el prompt de Omar dice literalmente «aprobado»** y con el nombre de Omar. Cualquier `--plan-edit` o regeneración posterior invalida la aprobación (el md5 ya no coincide).
2. **Hook `guard_render`** (`.claude/hooks/`, mismo patrón que `guard_git`): intercepta comandos que contengan `fase2b` y `--gfx` (no `--plan-only`, no `--only-cap` con `--gfx-debug`): si el `GUION_PANTALLA.json` del topic no existe, no tiene `aprobado`, o su `md5_planes` no coincide con los planes actuales → **bloquea** con un mensaje que diga qué falta. Salida de escape explícita solo para el candado md5 de ch02 (`--only-cap ch02` sin `--gfx` no pasa por el hook).
3. Tests: sin aprobación bloquea; con aprobación pasa; después de `--plan-edit` vuelve a bloquear; `--plan-only` nunca se bloquea.

## C. `/tanda` y skills de CC (repo + usuario)
1. **`.claude/commands/tanda.md`** (y copia en `~/.claude/commands/tanda.md`): el comando que arma cualquier tanda. Contenido mínimo, en este orden: leer `CLAUDE.md`, `DECISIONES.md`, `lab/ESTADO_SESION.md` (cabecera + últimas 2 tandas) y el handoff indicado; declarar **módulos que toca** (lista con qué hace cada uno hoy y qué hará); una variable por etapa; constantes solo con origen; **cada módulo/parte termina con su salida en texto pegada en el reporte y PARADA corta** (seguir solo si el prompt lo autoriza expresamente; si no, esperar); nunca `fase2b --gfx` sin guion aprobado (el hook lo frena igual); suite rápida y amplia + md5 ch02 en cada commit; reporte `FNN_REPORT.md` con «lo que queda abierto» entera y el veredicto íntegro del `revisor-handoff`; `ESTADO_SESION.md` al final; PARADA.
2. **`.claude/skills/guion-de-pantalla/SKILL.md`:** cómo se genera (`--plan-only`), qué trae cada sección, cómo se lee la tabla por beat, cómo se aplica `--plan-edit` (formato del JSON de edición con ejemplos reales de Vajont), cómo se aprueba, y la regla: el render usa los planes aprobados y no re-decide (el crítico de sellos reusa veredictos por identidad de bloque).
3. **`.claude/skills/simular-reglas/SKILL.md`:** cómo correr una regla en seco contra `GUION_PANTALLA.json` / planes resueltos antes de programarla: entrada (descripción de la regla), salida (tabla propuestos → cortados por esa regla → quedan, con 3 ejemplos de lo que corta). Incluir un script `lab/tools/simular_regla.py` que reciba un predicado Python sobre los eventos del guion y produzca esa tabla.
4. **`.claude/agents/simulador.md`:** subagente que usa el skill anterior; `/tanda` lo invoca obligatoriamente cuando el handoff trae una regla o filtro nuevo, **antes** de escribir código, y pega su tabla en el reporte.
5. Copias en `~/.claude/` de `/tanda` y del agente `revisor-handoff` (si ya es de usuario, anotar). Lo específico del pipeline (los dos skills) queda solo en el repo.

## D. Mapa de módulos con stickers
1. **`lab/MAPA_MODULOS.md`** generado por CC leyendo el código real (no de memoria): una fila por archivo de `script_engine/gfx_*.py`, `gfx_config.py`, `fase2b.py`, `transition_config.py`, `transition_applier.py`, `gfx_templates/*.tmpl` y los módulos de fase 1 que intervienen en gfx (`m01a_escaleta`, `m01d_particion`, `music_intensity`): columnas **módulo · sticker (1–2 líneas en cristiano, sin jerga: qué hace para el video) · recibe · entrega · quién lo llama · tanda en que nació · estado (vivo / solo sin escaleta / muerto)**. «Muerto» = nadie lo llama en el camino con escaleta (p. ej. `gfx_fragments` para D/T, `garantizar_pico`): listarlos aparte con la fecha en que dejaron de usarse.
2. **`lab/MAPA_MODULOS.json`** con los mismos datos + las aristas (quién llama a quién), para que el analista construya la página con flujograma y stickers al pasar el mouse (la página la hace el analista; CC entrega los datos).
3. **Hook `guard_mapa`:** si un commit toca `script_engine/gfx_*.py` o `fase2b.py` y no toca `lab/MAPA_MODULOS.md`/`.json`, avisa (no bloquea) en el commit; el reporte de la tanda tiene que decir por qué no cambió el mapa.
4. Cada handoff futuro declara «módulos que toca» con el nombre y el sticker del mapa (lo exige `/tanda`).

## E. Verificación y cierre
1. Suite rápida y amplia verdes; md5 ch02 sin `--gfx` `38e5ba14…`; el hook de render probado en seco con Vajont (`fase2b f8s3-vajont-f30 --gfx --dry-run` o el equivalente: debe bloquear porque el guion no está aprobado).
2. Reporte `lab/hyperframes/f33/F33_REPORT.md`: inventario de constantes sin origen (A.2), prueba del hook (B.3), contenido de `/tanda` y de los dos skills pegado, el mapa de módulos completo pegado, lista de módulos muertos, veredicto íntegro del revisor. `ESTADO_SESION.md`. **PARADA.**

## Frenos
- No se toca ninguna regla de contenido, prompt, plantilla ni valor del pipeline: esta tanda no cambia el video. `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git. Un commit por parte. Sin merge, sin publicar, sin borrar.
