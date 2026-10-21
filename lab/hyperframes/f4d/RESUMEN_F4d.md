# RESUMEN F4d — Pico con preferencia, recortes por cláusula, marca +1 px

Rama `f3-lab-identidad`, sobre F4c (`59d5893`). `main` intacta (`43f528a`). Solo `--only-cap ch02` y `ch05`, una corrida; no hubo render completo.

## Resultado

| Pedido | Resultado |
|---|---|
| 1. Pico | La frase con cifra de altura y palabra de agua gana salvo que otra la supere por más de 0.2. El orden es nivel de agua > recorte con fuente > zoom humano > recorte sin kicker > sello. Borré la caché de intensidad de ch02 y ch05. **ch02 vuelve al nivel de agua 4.6 m con PUTREFACTA adentro** (sello + mood veneno + ícono, palabra del pico). |
| 2. Recortes | Las opciones son cláusulas completas del fact (≤ 10 palabras, empiezan en artículo, nombre o sustantivo, y terminan en coma, punto o subordinada), ordenadas por aporte. Flash elige entre las 3 mejores. **ch02:** «El huracán Katrina tocó tierra el 29 de agosto» · 2005 y «días en celdas inundadas con agua contaminada con aguas residuales» · 2005. **ch05:** «cadáveres flotando en las aguas de la inundación» · **1 de septiembre** (ver abajo). |
| 3. Marca | `corner_dilate_px: 1`. Los recortes 1:1 nuevos están en `capturas/` (antes +2 px / después +1 px sobre el mismo cuadro, más el cuadro real del render). El grabado vuelve a leerse: los pliegues de la capa y el brazo con el farol. |
| 4. `\b` de los íconos | `gfx_icons/__init__.py:70` corregido. Los trazos Lucide ahora llevan `pathLength="1"`. |

- Candado literal: 0 rechazos. Sin `--gfx`, el md5 de ch02 sigue en `38e5ba14…` (`corrida/onlycap_ch02_nogfx_f4d.log`). Tests: 311 verdes.
- Tabla completa: `TABLA_antes_despues.md` (antes = F4c). Decisiones: `DECISIONES_F4d.md` (H1–H11).

## Lo que no hice como estaba pedido
- **Kicker «Human Rights Watch» en ch05: no.** El research no le atribuye ese fact a HRW: HRW es la fuente del dato de los 500 presos. Lo de Templeman III son «algunos reclusos… informaron», y el research dice que esas denuncias «nunca fueron verificadas oficialmente». Ponerle HRW sería inventar la fuente de un documento. Sale el kicker de fecha «1 de septiembre». Si la fuente existe, hay que cargarla en el fact o en el research y el kicker la toma solo (H8).

## Otras cosas
- Sumé «putrefacta/as/o/os» (peso 3) al léxico de veneno. Antes, que PUTREFACTA apareciera dependía de que Flash la propusiera (H4).
- Encontré un bug: la caché del PNG de la marca no distinguía el engrosado, así que cambiar `corner_dilate_px` reusaba el PNG viejo. Borré la caché antes del cosido y ahora el nombre del archivo lleva el engrosado y el halo (H10).
- ch05: el pico sigue en CADÁVERES (sello). El recorte arranca a 6 s del pico, fuera de ±5 s, así que no puede ser el bloque del pico.
- Flash, al re-llamarse, propuso «Katrina» como carga de peso 3 (categoría agua). Por eso el recorte de Katrina sale con ícono gota.

## Revisor (revisor-handoff), veredicto íntegro

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1a | Pico: la frase con cifra de altura y agua gana salvo que otra la supere por más de 0.2 | OK | gfx_peak.py: WATER_PEAK_TOL = 0.2, con -1e-9 para que el empate exacto gane el agua. |
| 1b | Orden del pico: agua > recorte con fuente > zoom humano | OK | plan_peak toma primero el recorte con kicker y después zoom_latido con human_box_for. gfx_layer._human_box filtra por gfx_vision.HUMAN más verify_crop. |
| 1c | Caché de intensidad de ch02 y ch05 borrada y respaldada | OK | _bak_f4d_pre/ existe. gfx_intensity_ch02.json es de 20:09 y ch05 de 20:16, ambos del 20-oct; ch01 y ch03 a ch07 siguen en 12:0x. |
| 1d | ch02 vuelve al nivel de agua con PUTREFACTA | OK | Plan ch02: pico.block=water_level, palabra=putrefacta, water_level 4.6 m en t=33.7. |
| 2a | Opciones = cláusulas completas, ≤ 10 palabras, ordenadas por aporte, Flash elige entre las 3 mejores | OK | gfx_fragments.clause_options, _doc_rank y DOC_TOP=3, tanto en build_items como en enforce_documents. |
| 2b | ch02 recupera «aguas residuales» y la fecha | OK | Plan ch02: «El huracán Katrina tocó tierra el 29 de agosto» y «días en celdas inundadas con agua contaminada con aguas residuales» (10 palabras). |
| 2c | ch05 «cadáveres flotando…» con kicker Human Rights Watch | PARCIAL (desvío justificado) | Plan ch05: «cadáveres flotando en las aguas de la inundación» con kicker «1 de septiembre». El texto está; el kicker es otro. |
| 3 | corner_dilate_px: 1 y recorte 1:1 nuevo | OK | misterio.json:112. capturas/ tiene 10 PNG no vacíos. El nombre del PNG de caché ahora lleva esq_d{dil}_h{halo} (gfx_bug.py); extra útil. |
| 4 | \b roto en gfx_icons/__init__.py:70 | OK | Ahora dice \b y r'<\1 pathLength="1"', sin caracteres de control en el diff. |
| 5 | Solo --only-cap ch02 y ch05, sin render completo | OK | Los logs de corrida/ terminan con rc=0 y "Procesados 1/1". Los finales _final_gfx*.mp4 conservan fecha 20-oct 15:54, anterior al trabajo. |
| 6 | Tabla antes/después refleja los planes reales | OK | Cotejé pico, water_level, recortes (texto, kicker, ícono) y zoom de ch02 y ch05 contra gfx_plan_ch0{2,5}.resolved.json. Coinciden. |
| 7 | Tests y main | OK | 311 passed con el comando pedido, más 6 de test_module_gfx_f4d.py. main en 43f528a; HEAD en 59d5893. |
| 8 | Revisor, commit y RESUMEN_F4d.md | NO VERIFICABLE | Todavía no existen, como se declaró. |

Desvío del kicker de ch05: justificado. verified_facts[8] es «Reclusos de la sección 'Templeman III' informaron haber visto cadáveres flotando… el 1 de septiembre» y el JSON no tiene source ni "Human Rights Watch" en ese fact. El único fact con HRW es el [7], el de los 500 presos. En el pool etiquetado, HRW aparece asociado a los 500 no contabilizados y a los 517 desaparecidos, no a los cadáveres. Poner HRW sería una atribución falsa; el kicker de fecha sale de la cadena de respaldo declarada en F4c.

Observaciones
- El pipeline modificó gfx_profiles/lexico_propuestas.json por sí solo: sumó "katrina" (peso 3) y subió desvanecidas e infierno de 2 a 3. Es efecto de la re-llamada a Flash y está declarado, pero entra en el commit.
- ch05 no tiene nivel de agua. Su pico queda en emphasis (CADÁVERES), porque el recorte arranca a 6 s del pico, fuera de ±5 s. Es coherente con el orden pedido.
- La tabla ch05 muestra DESVANECIDAS con peso 2 → 3, un cambio de Flash no pedido que no afecta al contrato.

Fuera de alcance: ninguno de F4d. diag_234_cap4.py (solo cambia el TOPIC) ya figuraba modificado en el git status inicial. Si se hace git add -A, ese archivo y la larga lista de ?? previos entrarían al commit: conviene un add explícito.

Riesgos que el contrato no cubre: clause_options y _start_ok son heurísticas del español (participios, EDGE_STOP) probadas solo en 2 caps; otros facts podrían quedar sin opciones y el recorte se quitaría. La re-llamada a Flash cambia las cargas entre corridas, así que el pico de ch02 depende en parte de que Flash vuelva a proponer «sumergidos» y «putrefacta». El RESUMEN_F4d.md debe citar este veredicto íntegro.

**Sobre el último riesgo:** «putrefacta» ya no depende de Flash, porque ahora está en el léxico (H4). «sumergidos» estaba en el léxico desde antes (peso 3), y el nivel de agua sale por la cifra literal de la frase, no por las cargas. Lo que sí depende de Flash es la intensidad: el agua gana mientras ninguna otra frase la supere por más de 0.2.

## Archivos
- Código: `script_engine/gfx_{peak,layer,fragments,bug}.py`, `script_engine/gfx_icons/__init__.py`, `gfx_profiles/misterio.json` (+ `lexico_propuestas.json`, que escribe el pipeline), `test_module_gfx_f4d.py`.
- Evidencia: `lab/hyperframes/f4d/` (`DECISIONES_F4d.md`, `TABLA_antes_despues.md`, `corrida/`, `capturas/`, scripts).
- Respaldo del estado F4c de ch02 y ch05 (planes, caché de intensidad, capas): `_fase2b_work/_bak_f4d_pre/`.
