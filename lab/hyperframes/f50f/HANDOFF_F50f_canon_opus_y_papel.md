# HANDOFF F50f — El canon pasa a Opus en producción + Wittenoom en texto (la D de F50d)

Analista · 2026-10-28 23:40 · rama `f11-guion-v4` · Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Tope **US$ 3,00**. Cero fotos, cero clips.

## Por qué
F50e (A y B, 9 corridas, mismo pedido): Flash dejó sin época a las fotos de 1971–2024 en 4 de 6 corridas e inventa el aspecto de los grupos; Opus cubrió 96/96 fotos en 3 de 3, con 4 tramos estables, 0 grupos con años sin ropa, y deja `appearance` vacío solo donde el material no da el origen (lo que pide el pedido). Opus corrió **sin esquema**: la API de Claude rechaza el esquema del canon (46 opcionales > 24). Producción tiene que hacer exactamente lo que se midió.

Orden (DECISIONES 22:30 y 23:34): F50f → F51 (fotos y clips de Wittenoom; fal apaga Veo 3.1 el 2026-11-17) → research nuevo en el próximo tema.

## Constantes
| valor | origen | quién |
|---|---|---|
| modelo del canon `claude-opus-5-5` | F50e-B, Omar 23:34 | Omar |
| effort `high` | `guion_v4.ESFUERZO["claude-opus-5-5"]` (existente) | existente |
| llamada sin esquema (salida JSON parseada del texto) | F50e-A: 46 opcionales > 24 | medido |
| tope US$ 3,00 (canon ≈ 0,36 medido en F50e + D ≈ 2,10 estimado en F50d + margen) | Omar 23:34 | Omar |
| criterio de la parte B: **todas** las fotos con año caen en algún period y ningún grupo tiene años de su `where_when` sin ropa | derivado (100 %, no es umbral) | analista, Omar 23:34 |

## Módulos (stickers del MAPA)
| archivo | hoy | después |
|---|---|---|
| `researcher_steps/step_4e_visual_canon.py` (research) | el canon en una llamada a Flash con esquema, respaldo sin esquema y canon vacío si falla | **una** llamada a Opus sin esquema (`claude_helpers.call_json`); `MODELO_CANON` y su effort como constantes del módulo con la línea de DECISIONES; si falla o el JSON no trae `era_visual_canon.periods` y `people_groups`: excepción (no canon vacío). Se **borran** el camino Flash, `_VISUAL_CANON_SCHEMA`, `VISUAL_CANON_SCHEMA_FICHA`, `_ERA_SCHEMA` (y lo que solo dependía de ellos), con sus tests; también `_probe_4e_schema_path.py` (raíz, probe viejo). El post-procesado de la respuesta (limpieza de campos) se queda |
| `fase1_5.py` (guion) | `asegurar_canon` con marca md5(ficha + pedido + esquema) | marca = md5(ficha + pedido + `MODELO_CANON` + effort): cambiar el modelo rehace el canon en cualquier tema. Canon con algún `periods[].years` que `m03_visual._tramo` no lee → Parada con la lista |
| `script_engine/m03_visual.py` (fase2a) | regla del «más cercano» callada | sin cambio de regla; una línea de log por cap con cuántas fotos no cruza ningún period y qué tramo les tocó (medida, no freno) |

Antes de borrar: `grep` de cada nombre en todo el repo (fuera de `lab/`) y pegar el resultado. Si algo de producción los usa, PARADA.

## Paso 0
1. md5 de este handoff contra el del prompt.
2. `DECISIONES.md`, tal cual: `- 2026-10-28 23:34 · **F50f:** el canon visual lo arma Claude Opus 5.5 (effort high) en una llamada sin esquema; se borran el camino Flash y sus esquemas; la marca del canon incluye el modelo; Wittenoom rehace el canon y corre m03 en texto (la D de F50d) con papel nuevo; tope US$ 3. Orden: F50f → F51 → research nuevo en el próximo tema (el analista diseña ese handoff mientras corren F50f y F51) · Omar · F50f`
3. `lab/TOPE_TANDA.json` = `{"usd": 3.0, "desde": <ahora>}`.

## A. Código (US$ 0)
Lo de la tabla de módulos. Tests: la marca cambia con el modelo y con una letra del pedido; un canon sin `periods` o con `years` ilegible → excepción/Parada; la llamada va a `claude_helpers.call_json` con `model=MODELO_CANON`, `effort` y **sin** `response_schema` (con un `post` falso, sin red). Salida: el diff de `step_4e` y la lista de lo borrado.

## B. Canon de Wittenoom por producción (≈ US$ 0,36)
`fase1_5.asegurar_canon` sobre Wittenoom (la marca nueva no coincide → rehace y guarda en topics_db y `05_visual_canon.json`). Copia previa en `lab/hyperframes/f50f/antes/`. Medida con `lab/hyperframes/f50e/canon_modelos_md.py` (4a–4g) sobre el canon nuevo, pegada en `CANON_F50f.md`.
**Si no se cumple el criterio de la tabla de constantes: PARADA** con la tabla (no se reintenta, no se fuerza).

## C. Pedidos en seco (US$ 0)
`lab/hyperframes/f50d/pedidos_f50d.py` con el canon de B → `lab/hyperframes/f50f/pedidos/`, diff contra `f50c/pedidos/`. Verificación: **0 líneas** cambiadas fuera del bloque del canon y de las líneas de grupo (la medida de F50d B). En los caps 5, 6 y 7, pegar el bloque ERA: tiene que traer los tramos de 1967+ (no 1958-1966). Si no: PARADA.

## D. Wittenoom en texto con Opus (≈ US$ 2,10)
`fase1_5 --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --only m03` (casilleros con Opus, armado, F8, movimiento de los 2 clips). **Cero fotos, cero clips.** Papel con `lab/hyperframes/f50/papel.py --salida lab/hyperframes/f50f/` y diff contra el papel de F50b (`lab/hyperframes/f50b/PAPEL_FOTOS_WITTENOOM.json`). Medido sobre el papel nuevo:
1. fotos de 1967+ cuyo prompt trae ropa, vehículos o tecnología de los 40–60 (F50b → F50f), con la lista;
2. fotos con nombre propio de persona en la prosa final (tiene que ser 0);
3. las 8 fotos testigo de F50c: ¿el sujeto coincide con la persona de PEOPLE?;
4. el log de m03 de las fotos sin period (tiene que ser 0 en Wittenoom);
5. gasto real por paso.

## PARADA
Al final de D, con el papel. Sin fotos. El papel lo revisa el analista con formato DEBERÍA antes del OK de Omar a F51.

## Reporte
`F50f_REPORT.md`: qué pasó en llano, salida de cada parte, lo que queda abierto (entero), veredicto íntegro de `revisor-handoff`. ESTADO, stickers y `MAPA_PROYECTO --check` 0, suite rápida y amplia, candado de ch02, commit por parte.
