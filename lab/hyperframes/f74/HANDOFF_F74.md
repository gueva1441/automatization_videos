# HANDOFF F74 — semilla manual desde el form (QA Studio) + receta para medirla
Fecha 2026-11-04 · rama f11-guion-v4 · HEAD 5bebb54 · analista → CC

## Por qué
Omar quiere arrancar YA el tema 2 escribiendo él la semilla (modo C, inyección manual). Hoy:
1. El form trae el modo C apagado a propósito (`niche_discoverer.py:1478`, `"disabled": True`, «corre de terminal»): `_run_manual()` pide el tema con `input()` y no hay marcador de texto libre en el form (solo `accept='key'` botones y `accept='keys'` checkboxes).
2. La semilla manual sale de `_build_seed(mode="manual")` SIN `remeasure` → `fase1._verify_pick_es_saturation` (fase1.py:393-396) la deja pasar sin medir saturación ES. Un tema saturado entraría a producción sin aviso.

## Constantes
| valor | origen | quién |
|---|---|---|
| `already_es=True` en la receta manual | derivado: la semilla se escribe en el form del canal ES, en español; `_measure_es` con already_es no traduce la query (Q2 lab: traducir texto ya-ES lo mancha) pero sí pide aliases ES para el juez | analista (avisado a Omar 2026-11-04) |
| `es_query = entity = título tal cual` | mismo contrato que el camino atómico (niche_discoverer.py:1076) | ya existe en el proyecto |
| n de re-mediciones del gate | el que ya usa `_verify_pick_es_saturation` (no se toca) | ya existe |
Ningún número nuevo.

## Regla que reemplaza / quita
- QUITA el `"disabled": True` del modo C y su comentario. No queda camino de terminal separado: `_run_manual()` es UNO solo; con QA_FORM emite marcadores, sin QA_FORM sigue con `input()` (mismo patrón que A/B).
- La semilla manual pasa a tener receta `remeasure` (hoy no tiene → no se medía). No se agrega ningún filtro nuevo: el gate existente decide (SATURADO/DISPUTADO → pregunta [P]/[S]/[Q], como ya hace).

## Simulación (data real)
- Palomares 1966 medido hoy con `_measure_es` (ENTRADA_ANALISTA_2026-11-04b): DISPUTADO, sat ES 62 k → con la receta nueva el gate lo re-mide y le muestra a Omar [P]roducir igual / [S]acar / [Q]. Sin la receta: pasa sin medir (fase1.py:395 «sin receta remeasure»). Ese es el cambio.

## Módulos que toca
1. `niche_discoverer.py` (copia local del emisor, la que corre; `qa_form_markers.py` opcional por simetría): hoy solo `key`/`keys` → agrega `accept='text'`; el host manda la línea escrita tal cual al `input()`.
2. `qa_form.html` + `qa_studio_server.py` (host del form): hoy enrutan `__choice__`/`__multi__` → agregan `__text__`; además `_form_answer` limpia el marcador ANTES de escribir a stdin (arregla el race de dos marcadores seguidos).

## Auditoría (subagente, 2026-11-04) — correcciones aplicadas al prompt
1. «Terminar» manda action:'choose' value:'' (cancel → 'Q' crearía semilla «Q»). 2. Deshabilitar al primer envío (doble línea). 3. Race marcador/stdin en `_form_answer`. 4. Clave `menu|text|prompt`, branch antes de renderSeeds. 5. Menús `manual_title`/`manual_root`. 6. El emisor real es la copia local de niche_discoverer. 7. Tests de C deshabilitado: buscar con grep, no suponer.
3. `qa_text.html` (NUEVO, hermano de `qa_choice.html`/`qa_multi.html`, mismo estilo).
4. `niche_discoverer.py` `_run_manual()` / `_build_seed`: con QA_FORM emite `text` para «Tema» y `choice` para «Nicho raíz» (las mismas opciones del menú de terminal + «0 Ninguno»); la semilla lleva `remeasure={"es_query": título, "entity": título, "already_es": True}`.
`fase1.py` NO se toca (el gate ya lee `remeasure`).

## Prompt para CC


```
Modelo → CC: Opus medium

F74 — semilla manual desde el form + receta para medirla. Rama f11-guion-v4 (main no se toca). Handoff: lab/hyperframes/f74/HANDOFF_F74.md (leelo entero primero). Usá todos los subagentes en paralelo que la tarea permita.

Objetivo: que Omar pueda elegir «C · Inyección manual» en el form del QA Studio, escribir el tema, elegir nicho raíz, y que esa semilla pase por el gate de saturación ES (fase1._verify_pick_es_saturation) igual que las de los modos A.

Etapa 1 — marcador de texto libre
1. El emisor que corre es la copia LOCAL de niche_discoverer.py (líneas ~70-98; no importa qa_form_markers.py por import circular). Ahí agregar `_emit_qaform_text_marker(menu, prompt, *, placeholder=None, body=None)` con accept='text' (contrato LOCKEADO: ASCII, 1 línea, flush, solo con QA_FORM). En qa_form_markers.py la misma función es opcional (por simetría). Menús: `manual_title` (texto) y `manual_root` (choice, default="0"); ningún nombre especial (seed_pick, reuse_seeds, judge_action, remeasure_pick, *_gate).
2. qa_form.html: markerKey → `menu+'|text|'+prompt` para accept==='text'; en showDialog el branch isText → menuFile '__text__' → renderText(marker), ANTES del fallback renderSeeds. qa_studio_server.py: mapa de menús `"__text__": BASE_DIR / "qa_text.html"`; y en `_form_answer` (~2091-2096) poner `_FORM["marker"]=None` ANTES de escribir a stdin (hoy va después: con dos marcadores seguidos —Tema y Nicho, sin trabajo en medio— el lector guarda el del nicho y la limpieza lo borra → form sin diálogo con el proceso esperando).
3. qa_text.html nuevo, hermano de qa_multi.html (mismo estilo y mismo qaFormAnswer): prompt, body opcional, input de texto con foco, «Enviar» (Enter también) y «Terminar». Ambos mandan `{menu, action:'choose', value:<texto>}` con value SIEMPRE string ('' para Terminar). NUNCA action:'cancel' (onAnswer lo convierte en 'Q' → semilla «Q»). Al primer envío deshabilitar input y botones (como showDocGate) para que Enter+click no manden dos líneas.
Salida de la etapa: el JSON de un marcador text real impreso + captura/descripción del diálogo + tests del contrato.

Etapa 2 — modo C en el form
1. niche_discoverer.py:1478: quitar `"disabled": True` del modo C y el comentario «corre de terminal»; label «✏️ Inyección manual — escribí el tema».
2. `_run_manual()`: un solo camino. Con QA_FORM, antes de cada input(): marcador text «Tema (enter vacío = terminar)» y, para el nicho raíz, marcador choice con las mismas opciones del menú de terminal (1..n de ROOT_NICHES + 0 «Ninguno / otro»). Sin QA_FORM queda igual que hoy.
3. `_build_seed(..., mode="manual", ...)` recibe `remeasure={"es_query": title, "entity": title, "already_es": True}` (mismo contrato que el camino atómico, niche_discoverer.py:1076). fase1.py NO se toca.
4. Tests: semilla manual trae remeasure; el gate la re-mide (mock de _measure_es → DISPUTADO → muestra [P]/[S]/[Q]); sin QA_FORM el input() sigue igual. Buscá primero `grep -rn '"disabled": True\|desde la terminal' --include=*.py .` y ajustá/borrá los tests que afirmaban el modo C deshabilitado (si no hay, decilo en el reporte).
Salida de la etapa: el JSON de la semilla manual de prueba «Palomares 1966» (con remeasure) y el log del gate con _measure_es MOCKEADO (no gastes scrape real).

Reglas fijas: sin números nuevos; nada de topes de dólares; suite rápida verde; commit + push al final con md5 del handoff en el mensaje; DECISIONES.md: anotar (2026-11-04) modo C habilitado en el form con receta remeasure already_es=True, Wittenoom publicado a −24 LUFS, −14 LUFS + limitador antes del render del tema 2, subida por API (m09b) aprobada para una tanda posterior.
NO corras fase1 ni el pipeline. NO toques el audio (−14 LUFS va en otra tanda).

PARADA: reporte lab/hyperframes/f74/F74_REPORT.md con las salidas de las 2 etapas, diff --stat, sección «lo que queda abierto» y veredicto del revisor-handoff íntegro. Actualizá lab/ESTADO_SESION.md. Después te parás y esperás.
```
