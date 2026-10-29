# HANDOFF F51f — la frase del cartel con una sola forma gramatical (y Wittenoom rearmado sin LLM)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · **US$ 0** (sin fal, sin LLM) · 3 etapas y PARADA.

## Por qué, con datos
La revisión del papel de F51d-A encontró la gramática rota en 6 de los 8 carteles de Wittenoom. Causa: `frase_cartel` (`m03_imagenes_v3.py` l. ~599) pega el casillero `font` como «in {font}» y después agrega «, in clear crisp lettering». Simulado sobre los 8 `text_in_image` crudos del `03_visual.json` vivo:

| foto (cap) | font | sale hoy | sale con la forma nueva |
|---|---|---|---|
| 3 | painted block lettering | «in painted block lettering, in clear crisp lettering» | «in clear crisp painted block lettering» |
| 3 | typewriter | «in typewriter, in clear crisp lettering» | «in clear crisp typewriter lettering» |
| 4 | handwritten ink | «in handwritten ink, in clear crisp lettering» | «in clear crisp handwritten ink lettering» |
| 5 | bold serif newsprint headline | «in bold serif newsprint headline, in clear crisp lettering» | «in clear crisp bold serif newsprint headline lettering» |
| 6 | highway sign sans-serif | «in highway sign sans-serif, in clear crisp lettering» | «in clear crisp highway sign sans-serif lettering» |
| 6 | block stencil | «in block stencil, in clear crisp lettering» | «in clear crisp block stencil lettering» |
| 7 | carved | «in carved, in clear crisp lettering» | «in clear crisp carved lettering» |
| 7 | block | «in block, in clear crisp lettering» | «in clear crisp block lettering» |

Los 8 quedan gramaticales. El caso viejo del test F50b, «Metal block letters», queda «in clear crisp metal block lettering».

Omar, 2026-10-29 12:54: arreglar el cartel; no tocar los grupos sin aspecto ni los casilleros narrativos (esos se ven en QA Studio después de generar).

## Orden re-derivado
- ¿Construye sobre código que ya se decidió reemplazar? No. Reemplaza la forma de `frase_cartel`, que es producción viva.
- ¿Alguna decisión de hoy cambia el orden? No. Es lo último antes de generar Wittenoom (F51d-B), junto con el modelo de video, que va en una tanda aparte.

## La regla (reemplaza a la de hoy, no se suma)
- **Hoy:** «… in {font}, in clear crisp lettering».
- **Nueva:** «… in clear crisp {font} lettering».
  - `font` va en minúscula (`_minuscula_media`), sin puntuación final.
  - Si termina en «lettering» o «letters», esa última palabra se saca, para no repetir. Es gramática del inglés, no algo de un tema.
  - Sin `font`: «… in clear crisp lettering».
- Las 3 aperturas («A sign reads …», «The words … are written {loc} …», «The {loc} reads …») quedan igual.
- **Chascada:** con un texto de una sola palabra, «The words "X" are» pasa a «The word "X" is». Caso: «WITTENOOM».

## Módulos que toca
| módulo | hoy | después |
|---|---|---|
| `script_engine/m03_imagenes_v3.py` | `frase_cartel` con «in {font}, in clear crisp lettering» | la forma nueva y la chascada; docstring actualizado |
| `test_module_f50b.py` (carteles), `test_module_f51f.py` nuevo | asserts de la forma vieja | la forma nueva; los 8 fonts reales de Wittenoom en una tabla; sin font; un texto de una palabra |
| `data/scripts/_steps/123bbb64…/03_visual.json` | prompts de F51d-A | se rearma **sin LLM**, solo cambian las fotos con cartel (etapa 2) |

## Constantes
No hay números. Las palabras «lettering» y «letters» son gramática del inglés: la misma palabra que la plantilla ya usa.

## Etapa 0 — DECISIONES
md5 de este handoff en el reporte. Al final de `DECISIONES.md`, tal cual:
```
- 2026-10-29 12:54 · **F51f:** la frase del cartel va «… in clear crisp {font} lettering» (sin repetir «lettering/letters»; sin font, «in clear crisp lettering»; una sola palabra → «The word … is»); Wittenoom se rearma sin LLM. Los grupos sin aspecto (4/3, 5/9) y los casilleros escritos como narración (1/2, 5/15, 6/8) se dejan así y se ven en QA Studio después de generar · Omar · F51f
```
Commit. Salida: `tail -1`.

## Etapa 1 — código y tests (US$ 0)
1. `frase_cartel` con la regla nueva.
2. Tests reescritos: los de F50b a la forma nueva y `test_module_f51f.py` con la tabla de arriba, que tiene que dar exacta.
3. **Contrato F51a:** 5 de sus 20 fotos tienen cartel, así que va a diferir **a propósito**. Se ajusta así: lo esperado = el C de F50h con la frase vieja del cartel cambiada por la nueva. El diff palabra por palabra contra F50h tiene que tocar **solo** la oración del cartel en esas 5. Cualquier otra diferencia → PARADA.
Salida: la tabla de los 8 tal como sale del código y el resultado del contrato.

## Etapa 2 — Wittenoom rearmado sin LLM
1. Copia de `03_visual.json` → `lab/hyperframes/f51f/antes/03_visual.json`.
2. `lab/hyperframes/f50g/rearmar.py --escribir`, o lo que corresponda después de F51c. Rearma con los casilleros crudos (`raw_llm_prompt`) que dejó m03 en F51d-A, **sin llamar a Opus**.
3. Diff antes → después. **Solo pueden cambiar las 8 fotos con cartel, y solo en la oración del cartel.** Cualquier otra diferencia → PARADA, con la lista.
4. Papel nuevo: `lab/hyperframes/f50/papel.py --salida lab/hyperframes/f51f/`, más los 8 prompts enteros.

## Al cerrar
- Suite rápida, suite amplia (`lab/hyperframes/f41/verificar.sh`), candado ch02 (`f792f3d4…`) y contrato F51a ajustado.
- Commit por etapa con F51f. ESTADO_SESION y `lab/hyperframes/f51f/F51f_REPORT.md`, con lo abierto entero y el veredicto íntegro de `revisor-handoff`.
- **PARADA.**

## Reglas fijas
- Sin fal y sin LLM. No tocar el canon, el pedido del canon, los casilleros, `anio_final`, el corte Veo ni `cost_tracker`.
- Ninguna regla nueva aparte de la de arriba: ni tamaño de plano para carteles ni idioma del texto. Esas van a la lista.
- Subagentes en paralelo: tests, contrato y diff.

## Lista (no se hace aquí)
- Cartel en plano extreme wide (3/3: texto en una puerta diminuta). Va a QA Studio.
- Idioma del texto escrito a mano por personajes de otro idioma (4/12: fecha en inglés en una foto de familia española).
- Grupos sin aspecto y casilleros narrativos: decisión de Omar 12:54, se ven en QA Studio.
