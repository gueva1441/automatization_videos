# F74 — semilla manual desde el form + receta para medirla (PARADA)
2026-11-04 · rama f11-guion-v4 · base 5bebb54 · handoff `HANDOFF_F74.md` md5 `e0504c86da5e010d9cc2aff4926dc662`

Omar ya puede elegir «C · Inyección manual» en el form del QA Studio. Ahí escribe el tema y elige el nicho raíz. La semilla sale con la receta `remeasure`, así que `fase1._verify_pick_es_saturation` la re-mide 3 veces, igual que las del modo A. No se corrió fase1 ni el pipeline. No se tocó el audio. Gasto: US$ 0, porque `_measure_es` fue mockeado y no hubo scrape.

## Etapa 1 — marcador de texto libre

**Cambios**
- `niche_discoverer.py`: nueva `_emit_qaform_text_marker(menu, prompt, *, placeholder=None, body=None)` en la copia local del emisor, la que corre.
  - Tiene `accept='text'` y cumple el mismo contrato LOCKEADO: ASCII (`ensure_ascii=True`), 1 línea, flush, y solo emite con QA_FORM, que chequea adentro.
  - `qa_form_markers.py` lleva la misma función como `emit_text_marker`, por simetría.
- `qa_form.html`:
  - `markerKey` usa `menu|text|prompt`.
  - `showDialog` tiene una rama `isText` → `'__text__'` → `renderText(marker)`, ubicada antes del fallback `renderSeeds`.
  - `onAnswer` no se tocó: `{action:'choose', value:<string>}` ya se convierte en `String(value)`.
- `qa_studio_server.py`:
  - `_FORM_MENU_HTML["__text__"] = BASE_DIR / "qa_text.html"`.
  - `_form_answer` pone `_FORM["marker"]=None` ANTES de escribir a stdin. Arregla el race de dos marcadores seguidos (Tema → Nicho).
  - Si la escritura falla, devuelve el marcador, pero solo si no llegó otro mientras tanto.
- `qa_text.html` (NUEVO), hermano de `qa_multi.html`, con la misma paleta y el mismo `qaFormAnswer`:
  - Muestra el prompt y el body opcional. El input de texto toma el foco.
  - «Enviar» (también con Enter, salvo durante una composición IME) y «Terminar» mandan `{menu, action:'choose', value}`. `value` es siempre string: `''` para Terminar.
  - Nunca manda `action:'cancel'`.
  - Al primer envío deshabilita el input y los dos botones (flag `sent`), así que Enter más un click no mandan dos líneas.
- Menús: `manual_title` (texto) y `manual_root` (choice). Ninguno es nombre especial: `handleMarker` no los intercepta y van a `showDialog`.

**Marcador text real** (stdout crudo de `QA_FORM=1 python lab/hyperframes/f74/salidas.py`):
```
@@QAFORM@@ {"menu": "manual_title", "accept": "text", "prompt": "Tema (enter vacío = terminar)", "placeholder": null, "body": null}
```

**El diálogo.** Lo describo, no hay captura: no se abrió en un navegador real.
- Fondo oscuro, igual que `qa_multi`/`qa_choice`. Arriba, la ceja mono «ESCRIBÍ EL TÍTULO» y el prompt grande «Tema (enter vacío = terminar)».
- Desde el 2.º tema aparece la caja mono con «Temas agregados: N».
- Debajo, el campo de texto con foco, con borde verde al enfocarlo, y los botones verde «Enviar» y neutro «Terminar».
- Lo comprobó un subagente con node y un DOM falso:
  - Con Enter, después un click en Enviar y después un click en Terminar, sale una sola respuesta, `{"menu":"manual_title","action":"choose","value":"Hola"}`, y todo queda deshabilitado.
  - Terminar solo da `value:""`.
  - `placeholder:null` → `''`.
  - `node --check` OK en `qa_text.html` y `qa_form.html`.
- El nicho raíz usa el diálogo de botones existente (`qa_choice.html`).

**Tests del contrato** (`test_module_f74.py`):
- Contrato del marcador text para las dos copias del emisor, y que no imprime sin QA_FORM.
- Ruteo `__text__` antes de `renderSeeds`.
- `qa_text.html` sin `cancel` en el código y con `action:'choose'`.
- `_form_answer`: limpia antes de escribir, devuelve el marcador si la escritura falla, y acepta la línea vacía.
- Menús sin nombres especiales.

## Etapa 2 — modo C en el form

**Cambios en `niche_discoverer.py`**
- Modo C: se quitó `"disabled": True` y el comentario «corre de terminal». El label quedó «✏️ Inyección manual — escribí el tema».
- `_run_manual()` tiene un solo camino. Con QA_FORM, antes del MISMO `input()`:
  - un marcador text `manual_title` «Tema (enter vacío = terminar)», con `body` «Temas agregados: N» desde el segundo tema;
  - un marcador choice `manual_root` con las opciones del menú de terminal: 1..n de `ROOT_NICHES` con emoji y nombre, más «0 Ninguno / otro», `default="0"` y `body` = el título.
  - Sin QA_FORM, la terminal queda igual que hoy (test con los prompts exactos de `input()`).
- `_build_seed(..., mode="manual", remeasure={"es_query": title, "entity": title, "already_es": True})`: el mismo contrato que el camino atómico (`niche_discoverer.py:1076`). Se actualizó el docstring de `_build_seed`. `fase1.py` no se tocó.

**Tests que afirmaban el modo C deshabilitado.** `grep -rn '"disabled": True\|desde la terminal' --include=*.py .` dio dos resultados:
- `niche_discoverer.py:1478`, la línea que se cambió;
- `test_qa_studio.py:1147`, que es un menú genérico de prueba (`Usar`/`Buscar`) y no el modo C.

**Ningún test afirmaba el modo C deshabilitado**, así que no hubo nada que ajustar ni borrar. También busqué `_run_manual|Inyecci` en los tests: 0.

**Semilla manual de prueba «Palomares 1966»**, en `lab/hyperframes/f74/semilla_palomares.json`. Las respuestas fueron «Palomares 1966», nicho «0» y enter vacío:
```json
{
 "seed_id": "e3d22160-3805-4e2c-a9f1-1e58a83fc012",
 "seed_title": "Palomares 1966",
 "discovery_mode": "manual",
 "root_niche": null,
 "tags": [],
 "evidence": {"user_input": true, "entered_at": "2026-11-04T13:52:57.463854"},
 "created_at": "2026-11-04T13:52:57.463854",
 "remeasure": {"es_query": "Palomares 1966", "entity": "Palomares 1966", "already_es": true}
}
```
Los 3 marcadores que emitió `_run_manual` están en `lab/hyperframes/f74/run_manual.log`: `manual_title` → `manual_root` con las claves 1, 2, 3, 0 → `manual_title` con «Temas agregados: 1».

**Log del gate con `_measure_es` MOCKEADO.** El mock devuelve DISPUTADO, sat 62 000, la medida del analista del 2026-11-04. Se respondió [P]. Está en `lab/hyperframes/f74/gate_mock.log`:
```
  🔁 Verificando el pick 'Palomares 1966' — re-mido ES 3× (anti-varianza de scrape)...
      [mock _measure_es] q='Palomares 1966' entity='Palomares 1966' already_es=True
      corrida 1/3: DISPUTADO (sat=62,000)
      [mock _measure_es] q='Palomares 1966' entity='Palomares 1966' already_es=True
      corrida 2/3: DISPUTADO (sat=62,000)
      [mock _measure_es] q='Palomares 1966' entity='Palomares 1966' already_es=True
      corrida 3/3: DISPUTADO (sat=62,000)
      → peor de 3: DISPUTADO (sat=62,000) · el seed decía: —

  ⚠ El pick 'Palomares 1966' FLIPEÓ a DISPUTADO al re-medir — hay competencia real, no es hueco limpio — confirmá antes de gastar.
@@QAFORM@@ {"menu": "remeasure_pick", "accept": "key", ... "options": [{"key": "P", ...}, {"key": "S", ...}, {"key": "Q", ...}], "default": "S", ...}
     [P]roducir igual · [S]acar este pick · [Q]salir: P  <form>
     → producís igual (bajo tu criterio).

[resultado] kept = ['Palomares 1966']
```
Sin la receta, el mismo seed habría impreso «sin receta remeasure… no se re-mide» y pasado sin medir. Ese era el hueco.

**Tests de la etapa** (`test_module_f74.py`):
- El modo C sale habilitado en el marcador `discovery_mode` real: `discover_niches()` se corta en el primer `input()` y no escribe en disco.
- `_run_manual` con QA_FORM: orden y forma de los marcadores, y la semilla con `remeasure`.
- El nicho se elige por número.
- Sin QA_FORM: los prompts de `input()` son idénticos y no hay marcadores.
- Gate: el mock de `_measure_es` se llama 3 veces con `("Palomares 1966", "Palomares 1966", True)`. Da DISPUTADO y emite `remeasure_pick` con P/S/Q. Con P se queda; con S y con Q devuelve `None`.

## Verificación
- `test_module_f74.py`: **17 passed**.
- Suite rápida del hook (`f25c`, `f24`, `f21`), más `f74`, `test_qa_studio`, `f73`, `f39_fase1`, `f39_research`, `f41_cadena` y `chat51_menu_pre_research`: **170 passed, 3 skipped**.
- `lab/tools/mapa_modulos.py --check`: 0 fallas. Se actualizaron los stickers de `niche_discoverer.py`, `qa_form.html`, `qa_form_markers.py` y `qa_studio_server.py`, y hay sticker nuevo para `qa_text.html`.
- `DECISIONES.md` tiene 4 líneas del 2026-11-04:
  - modo C con `already_es=True`;
  - Wittenoom a −24 LUFS;
  - −14 LUFS más limitador antes del render del tema 2;
  - m09b aprobada para una tanda posterior.

## diff --stat
```
 DECISIONES.md                      |  4 ++++
 lab/mapa/stickers/orquestador.json | 20 +++++++++++++++++---
 lab/mapa/stickers/research.json    |  6 +++---
 niche_discoverer.py                | 37 ++++++++++++++++++++++++++++++++++---
 qa_form.html                       |  6 +++++-
 qa_form_markers.py                 | 15 +++++++++++++++
 qa_studio_server.py                | 14 ++++++++++++--
 7 files changed, 90 insertions(+), 12 deletions(-)
 nuevos: qa_text.html, test_module_f74.py, lab/hyperframes/f74/{F74_REPORT.md, salidas.py, semilla_palomares.json, run_manual.log, gate_mock.log}
```

## Lo que queda abierto
- **No se probó en el form real.** El diálogo no se abrió en un navegador ni con un subprocess de fase1 vivo. Lo comprueban los tests, node con DOM falso y el contrato. La primera vez que Omar elija C conviene mirarlo.
- **Una semilla manual sin nicho sale con `tags: []`.** Pasaba lo mismo por terminal.
- **Ceja fija.** La ceja de `qa_text.html` dice siempre «ESCRIBÍ EL TÍTULO». Si `accept='text'` se usa después para otro menú, la ceja debería salir del marcador.
- **Race viejo del sondeo, no arreglado.** Si un sondeo que salió antes de responder vuelve después de la respuesta, `handleMarker` puede re-mostrar el diálogo viejo un instante. Pasa en todos los menús y no es de F74. El race de `_form_answer` que pedía el handoff sí quedó arreglado.
- **«el seed decía: —».** La semilla manual no trae `evidence.es_gap`, así que el gate muestra «—» como etiqueta original. Es correcto, porque nunca se midió.
- **Audio y m09b.** −14 LUFS más limitador y la subida por API van en otras tandas: solo se anotaron.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Emisor `_emit_qaform_text_marker` en la copia local, con `accept='text'`, ASCII, 1 línea, flush y solo con QA_FORM; copia simétrica en `qa_form_markers.py` | OK | `niche_discoverer.py:102-114` (diff); `qa_form_markers.py` `emit_text_marker` |
| 2 | Menús `manual_title` (texto) y `manual_root` (choice, default "0"), sin nombres especiales | OK | `niche_discoverer.py` `_run_manual`, diff |
| 3 | `qa_form.html`: `markerKey` con `menu\|text\|prompt`, rama `isText` → `__text__` → `renderText` antes de `renderSeeds` | OK | diff de `qa_form.html`, líneas 252-299 |
| 4 | `qa_studio_server.py`: mapa `__text__` y `_form_answer` limpia el marcador antes de escribir a stdin | OK | diff de `qa_studio_server.py`, `_FORM_MENU_HTML` y `_form_answer`. Además repone el marcador si la escritura falla y nadie plantó otro. |
| 5 | `qa_text.html`: prompt, body, input con foco, Enviar y Enter, Terminar con `value=''`, nunca `cancel`, bloqueo al primer envío | OK | `qa_text.html` (`sendValue`, flag `sent`, `lock()`). La verificación con DOM falso la reporta CC y yo no la repetí. |
| 6 | Etapa 1: salida con el JSON de un marcador real, la descripción del diálogo y los tests del contrato | OK | `F74_REPORT.md`, `run_manual.log`, `test_module_f74.py`. No hay captura: CC lo declara y el pedido admitía "captura/descripción". |
| 7 | Etapa 2: quitar `"disabled": True` y el comentario; label "✏️ Inyección manual — escribí el tema" | OK | diff `niche_discoverer.py`, línea ~1502 |
| 8 | `_run_manual` en un solo camino: con QA_FORM emite text antes del `input()` y choice de nicho con 1..n y "0 Ninguno / otro"; sin QA_FORM queda igual | OK | diff `niche_discoverer.py` líneas 1314-1340 |
| 9 | `_build_seed(mode="manual")` con `remeasure={es_query, entity, already_es: True}`; `fase1.py` sin diff | OK | diff `niche_discoverer.py`; `git diff --stat -- fase1.py` salió vacío |
| 10 | Tests: remeasure en la semilla, gate con `_measure_es` mockeado → DISPUTADO → [P]/[S]/[Q], sin QA_FORM igual; grep de tests del modo C deshabilitado | OK | `pytest test_module_f74.py -q`: 17 passed, sin red. Corrí el grep: solo `test_qa_studio.py:1147`, un menú genérico. El reporte lo dice. |
| 11 | Salidas de etapa 2: JSON de "Palomares 1966" con remeasure y log del gate mockeado | OK | `semilla_palomares.json`, `gate_mock.log` (3 corridas, `remeasure_pick` P/S/Q, `kept=['Palomares 1966']`) |
| 12 | DECISIONES.md: 4 anotaciones del 2026-11-04 (modo C, Wittenoom −24 LUFS, −14 LUFS + limitador, m09b) | OK | diff `DECISIONES.md`, 4 líneas agregadas |
| 13 | Sin números nuevos ni topes de dólares; no se corrió fase1 ni pipeline; no se tocó el audio | OK | Ningún archivo de audio ni `fase1.py` en el diff. Gasto US$ 0 por mock. |
| 14 | `mapa_modulos.py --check` | OK | "161 archivos de producción · 0 fallas" |
| 15 | Actualizar `lab/ESTADO_SESION.md` | FALLA | Sin cambios en git y mtime 07:42, anterior a la tanda. `grep F74` no encuentra nada. El pedido y el CLAUDE.md lo exigen. |
| 16 | `F74_REPORT.md` con diff --stat, "lo que queda abierto" y el veredicto del revisor íntegro | PARCIAL | Existe y trae diff --stat y la sección abierta. El veredicto es un placeholder "(pegado abajo, íntegro)" sin contenido: falta pegar este. |
| 17 | Suite rápida verde y commit + push con md5 del handoff | NO VERIFICABLE | CC reporta "170 passed, 3 skipped"; yo solo corrí `test_module_f74` (verde). Commit y push todavía no existen, como se avisó. El md5 del handoff coincide: e0504c86…. |

Fuera de alcance: ninguno de CC. Los tres archivos ajenos (`diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt`) figuran modificados: no hay que incluirlos en el commit (`git add` por ruta, no `-A`). Un cambio menor: `research.json` perdió su "No newline at end of file", efecto del regenerado del sticker.

Observaciones:
- Falta actualizar `lab/ESTADO_SESION.md` (punto 15) y pegar este veredicto en el reporte (punto 16). Ninguna de las dos cosas toca código.
- El reporte afirma que `ESTADO_SESION` se actualiza en su diff --stat, pero ese archivo no aparece ahí.

Riesgos que el contrato no cubre:
- El diálogo nunca se abrió en un navegador real ni con un fase1 vivo. La primera vez que Omar elija C conviene mirarlo.
- La ceja de `qa_text.html` es fija ("ESCRIBÍ EL TÍTULO"). Si otro menú usa `accept='text'`, saldrá mal rotulada.
- `already_es=True` es una suposición del analista, avisada a Omar. Una semilla escrita en inglés se mediría sin traducir.

### Adenda de CC
- **Puntos 15 y 16:** cerrados después del veredicto. El veredicto está pegado acá y `lab/ESTADO_SESION.md` tiene la línea F74. Las dos cosas se ven en el commit.
- **«El reporte afirma que ESTADO_SESION se actualiza en su diff --stat»:** el diff --stat del reporte no lo listaba, porque se tomó antes de actualizar ESTADO_SESION. Este commit lo suma.
- **Punto 17:** la suite rápida del hook (`f25c`, `f24`, `f21`) corre de nuevo en el `git commit`. Si falla, no hay commit.
- **`already_es=True`:** es la receta del handoff, avisada a Omar. Si Omar escribe un tema en inglés, el gate lo mide sin traducir. Queda anotado como riesgo, no se cambió.
- **`research.json`:** el salto final de línea lo agregó el regenerado del sticker. Es inocuo.
