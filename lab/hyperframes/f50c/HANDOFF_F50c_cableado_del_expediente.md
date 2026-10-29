# HANDOFF F50c — Cableado del expediente de foto: personas, citas y grupos (código y en seco, US$ 0)

Analista, 2026-10-28 22:30. Tema `123bbb64-9fca-4395-8bf4-57d60e219ef1` (Wittenoom). Rama `f11-guion-v4`.
**Qué es, en llano:** el expediente (el dossier que recibe Opus por cada foto) deja afuera datos que el research y la ficha ya tienen: las personas casi nunca llegan (17 de 96 fotos), las citas llegan sin quién las dijo y los grupos de gente llegan sin aspecto ni ropa. Esta tanda los conecta, **solo con código**, y arma los pedidos de los 7 caps **en seco** (sin llamar a Opus). Cero fotos, cero modelos.
Origen: `claude/AUDITORIA_prompt_foto.md` (P1 #1, #2a, #3), con OK de Omar 22:09.

## Orden (vuelto a derivar)
1. ¿Construye sobre algo que se decidió reemplazar? No: `m03_expediente.py` entró a producción en F50 y es el camino vigente.
2. ¿Una decisión de hoy cambia el orden? Sí, y ya está aplicado: Omar decidió (22:09) cablear primero y llenar cajones nuevos del research después. La ropa por tramo de años del canon (P1 #2b) va en **F50d**, antes de F51 (fotos). F51 espera a F50d.

## Constantes
Ninguna numérica. Textos literales nuevos en el pedido (datos, no reglas): `(named earlier in the paragraph)`, `witness`, `APPEARANCE:`, `CLOTHING:`. Palabras de gramática inglesa en la chascada: «No» seguido de «.» y una cifra (abreviatura de número) y «nothing but».

## Módulos
| Archivo | Hoy | Después |
|---|---|---|
| `script_engine/m03_expediente.py` | Personas: ids `P` del beat (la escaleta nunca los pone) + `_sale_entero(nombre del pool, ancla)`. Citas: solo el texto. Grupos: `id · who · where_when`. | Personas desde `ficha.personas` (A). Citas con autor (B). Grupos con aspecto y ropa (C). Se borran `_sale_entero` y la búsqueda de personas en el pool por nombre. |
| `script_engine/m03_imagenes_v3.py` | `_sin_negadas` saca «No. 4 Shaft» y «nothing but red dust» si abren cláusula. | Chascada D: no los saca. |
| `test_module_f50c.py` (nuevo) | — | Tests de A–D. |

## A. Personas desde la ficha (simulado: 17 → 73 fotos con PEOPLE)
Por qué: la escaleta no usa ids `P` en ningún beat (0/14) y ningún párrafo de la voz tampoco (0/78 en Wittenoom, Kyshtym y Vajont). Y el pool escribe «Daniel Écija (padre)» mientras la voz dice «Daniel Écija»; además el P17 del pool trae el rol del hijo (la ficha ya lo corrigió en `decisiones`).
Regla, en este orden, por cada foto de un cap (en el orden de las anclas):
1. **Formas de cada persona** = `nombre` y cada `variantes[]` de `ficha.personas`, sin lo que va entre paréntesis («Daniel Écija (padre)» → «Daniel Écija»). Se busca cada forma como palabra entera, sin mayúsculas, en el **ancla**. Por persona vale la forma más larga que aparece.
2. **Si una misma forma la tienen varias personas** (padre e hijo):
   a. si en el ancla la forma va seguida del calificativo que la persona tiene entre paréntesis («Daniel Écija hijo» → «(hijo)»), gana esa;
   b. si no, gana la persona cuyos años quedan más cerca del año de la foto. Años de una persona = los años de 4 cifras de `fechas_presente` de sus ids `P` y de `fecha` de sus ids de `cronologia` y `datos` en el pool, **sin los ids que comparte con las otras candidatas**. Año de la foto = el que el expediente ya calcula (`anio_ancla`, si no el `respaldo`). Si empatan o no hay año: **no se manda a nadie** por esa forma.
3. **Arrastre:** si el ancla no nombra a nadie, la foto recibe las personas de la última ancla **del mismo párrafo** que sí nombró a alguien (así resuelve un lector «se casan»). Esas líneas llevan al final ` (named earlier in the paragraph)`. No se arrastra entre párrafos.
4. **Línea PEOPLE** (sin nombre propio, como hoy): `rol de la ficha · lugar · años`, donde `lugar` y `años` salen del primer id `P` de esa persona que los tenga en el pool (`lugar`, `fechas_presente`); si ninguno, `-`.
5. Se borra la búsqueda vieja (ids `P` del beat + `_sale_entero` sobre `pool.personajes`).

Simulación del analista (`lab/_gpt_probe_analista/auditoria_foto/sim_personas3.py`, mismos años que producción):
| | Fotos |
|---|---|
| Con PEOPLE antes | 17 / 96 |
| Con PEOPLE después | **73 / 96** (35 por el ancla, 38 por arrastre) |
| Forma ambigua sin resolver | 0 |
| 1 persona / 2 / 3 | 48 / 23 / 2 |

Fotos testigo (deben dar exactamente esto):
| Foto | Ancla | Esperado |
|---|---|---|
| 1/3 | «El hombre se llama Daniel Écija y es minero…» | Daniel Écija (padre) |
| 1/4 | «Wittenoom, Australia Occidental, 1962» | padre, por arrastre |
| 2/1 | «…Daniel Écija conoce a María Bernal» | padre + María Bernal |
| 2/8 | «Víctor Calvo era un niño…» | Víctor Calvo |
| 3/7 | «…lo contó él mismo: «Me desestimaron…» | Eric Saint, por arrastre |
| 3/16 | «…dijo McNulty» | Jim McNulty |
| 5/9 | «…el documento de Daniel Écija hijo…» | Daniel Écija (hijo) |
| 5/14 | «Madrid, 1991. Daniel Écija va al médico» | Daniel Écija (padre) |

Se queda, declarado: 2/7 «Un niño que hizo ese viaje…» arrastra a Milagros Barroso y Ramón de Juan (el niño es Víctor Calvo, de la oración siguiente). La marca `(named earlier in the paragraph)` le dice a Opus que es contexto. Y `ficha.personas` mezcla organizaciones (CSR, Tribunal Federal) con personas: la ficha no trae un campo que las distinga, así que entran como entran hoy en la ficha.

## B. Citas con autor (84/96 fotos con QUOTES, hoy 0 con autor)
`«texto» — autor · rol` + ` · fecha` si la cita la trae + ` · witness` si `testigo` es true. Todos los campos son del pool (58/58 citas tienen autor).

## C. Grupos con aspecto y ropa
`  - id: who · where_when · APPEARANCE: appearance · CLOTHING: clothing`. F46b C2 sacó el aspecto de la **prosa armada** (la oración «The people are…»), no del pedido: esto no lo contradice.
**Riesgo declarado:** 11 fotos usan un grupo fuera de sus años (familias migrantes 1958–66 en fotos de 1985–2023). Con la ropa a la vista, Opus podría vestirlas de los 60. Se arregla en F50d (ropa por tramo en el canon). Por eso F51 no corre antes de F50d.

## D. Chascada de `_sin_negadas`
No se saca un trozo que sea solo «No» seguido de «.» y una cifra («Cell No. 5», «No. 4 Shaft»), ni uno que empiece con «nothing but». En Wittenoom: 0 casos (no cambia ninguna foto).

## Paso 0
`DECISIONES.md`, tal cual: «2026-10-28 22:09 · Prompt de foto: primero se cablea el expediente (personas desde la ficha, citas con autor, aspecto y ropa por grupo) con código y en seco; la ropa por tramo de años del canon va en F50d y el llenado de cajones nuevos del research (aspecto de personas conocidas, de lugares y de objetos) después; F51 espera a F50d · Omar · F50c».

## Pasos (subagentes en paralelo donde se pueda: A, B+C y D son independientes)
1. A, B, C y D con tests: las 8 fotos testigo de A; la forma ambigua sin año → nadie; el calificativo «hijo»; arrastre que no cruza párrafos; cita con y sin fecha y con `testigo` false; grupo con aspecto y ropa; «Cell No. 5» y «nothing but red dust» se quedan; «with no figure anywhere» sigue saliendo.
2. **Pedidos en seco** de los 7 caps de Wittenoom con el código nuevo (lo mismo que arma producción, sin llamar a Opus; ver `lab/hyperframes/f50/verificar_b.py`). Guardar en `lab/hyperframes/f50c/pedidos/pedido_chNN.txt`.
3. `lab/hyperframes/f50c/EXPEDIENTES_F50c.md`: por foto, PEOPLE y QUOTES antes → después; tabla de conteos.
   **Verificación automática:** fotos con PEOPLE = 73 (35 ancla, 38 arrastre), 0 ambiguas, las 8 testigo como en la tabla, citas con autor en las 84, 7 grupos con APPEARANCE y CLOTHING; y en cada pedido, fuera de las líneas PEOPLE, QUOTES y PEOPLE GROUPS, **nada cambia** respecto del pedido con el código de F50b (diff). Cualquier diferencia: PARADA con el diff.

## Reglas fijas
- Cero llamadas a modelos, cero fal, `TOPE_TANDA` 0. Nada en `main`. No se toca `03_visual.json` ni el papel.
- Sticker y `MAPA_PROYECTO` (`--check` 0); suite rápida y amplia (antes y después); candado de ch02.
- `F50c_REPORT.md` con lo abierto entero y el veredicto íntegro de `revisor-handoff`; `ESTADO_SESION`; commit por parte.

## PARADA al terminar el paso 3.
