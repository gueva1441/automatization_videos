# HANDOFF F51d-A — Wittenoom: m03 en texto con el armado C, el canon F51b y los arreglos F51c → papel de fotos (sin fotos)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · tope **US$ 3,00** (m03 en F50f costó US$ 2,3320) · **cero fotos y cero clips** · 3 etapas y PARADA.

## Por qué
F51a (armado C), F51b (aspecto fijo separado del estado) y F51c («Court», corte Veo, `anio_final`) ya están en producción. Pero el `03_visual.json` de Wittenoom todavía tiene los prompts viejos, y 20 fotos apuntan a ids de grupo que el canon nuevo ya no tiene. Esta tanda vuelve a correr m03 de Wittenoom (casilleros con Opus + armado por código) y deja el **papel de fotos en texto**: las 96 fotos con ancla y prompt. Así el analista y Omar lo revisan antes de gastar en fal (texto antes que gasto, siempre). Omar, 2026-10-29 12:28: «si dale».

## Orden re-derivado
- ¿Construye sobre código que ya se decidió reemplazar? No: corre producción tal como quedó después de F51c.
- ¿Alguna decisión de hoy cambia el orden? No. Generar las fotos (F51d-B) espera el OK de Omar al papel. Los 2 clips Veo, además, esperan alinear su prompt de video con la guía de Google (DECISIONES 2026-10-28 11:15), que es una tanda aparte.

## Módulos que toca
| módulo | hoy | después |
|---|---|---|
| `script_engine/m03_expediente.py` (chascada) | rotula el respaldo «3)/4)/5)» | rotula «2)/3)/4)» en el origen |
| `script_engine/m03_imagenes_v3.py` (chascada) | `anio_final` renumera el rótulo con un regex | pasa el rótulo tal cual: se borra el regex |
| `data/scripts/_steps/123bbb64…/03_visual.json` | prompts viejos, ids viejos | lo reescribe m03 (producción) |
| `lab/hyperframes/f51d/` | — | papel y medidas |

La chascada viene de F51c (abierto 4, riesgo del revisor): con el regex, si el texto del rótulo cambia, la renumeración falla sin aviso. Un test fija los 3 rótulos nuevos y que `anio_final` no los toque.

## Constantes
| valor | origen | quién |
|---|---|---|
| tope US$ 3,00 | m03 de Wittenoom en F50f = US$ 2,3320 (`F50f_REPORT.md` l. 3) + margen; mismo tope que F50f | Omar, «si dale» 12:28 a «≈ US$ 2,3» |

No hay otros números.

## Etapa 0 — DECISIONES y chascada
1. md5 de este handoff en el reporte. Al final de `DECISIONES.md`, tal cual:
```
- 2026-10-29 12:28 · **F51d-A:** Wittenoom corre m03 en texto (casilleros con Opus + armado C + canon F51b + arreglos F51c), tope US$ 3, cero fotos y cero clips; el papel de fotos lo revisa el analista y Omar da el OK antes de generar (F51d-B) · Omar · F51d
```
2. Chascada de los rótulos y su test. Suite rápida y contrato F51a 20/20. Commit.

## Etapa 1 — m03 de Wittenoom (≤ US$ 3,00)
1. Copia de `03_visual.json` → `lab/hyperframes/f51d/antes/03_visual.json`.
2. `TOPE_TANDA` en 3,00. `fase1_5 --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --only m03`, igual que en F50f D. Los caps en paralelo si m03 lo permite: no cambiar código para eso, solo usar los workers que ya tiene.
3. Si un cap da PARADA o se pasa del tope, se para ahí y se reporta. No se reintenta a mano.
Salida: el log de m03 por cap (fotos, sin period, anclas por fallback sí/no) y el gasto real desde `cost_history`.

## Etapa 2 — papel y medidas (US$ 0)
`lab/hyperframes/f50/papel.py --salida lab/hyperframes/f51d/` → `PAPEL_FOTOS_WITTENOOM.md/.json`. Medidas en `lab/hyperframes/f51d/MEDIDAS_F51d.md`, cada una con su lista:
1. fotos con un `people_group` que no existe en el canon vivo → **tiene que dar 0**;
2. fotos cuyos grupos tienen todos `appearance` vacío (los 5 grupos de F51b) → lista: foto · grupo · `subject`, para ver si el sujeto ya trae la etnia;
3. fotos cuyo prompt contiene, como subcadena, algún texto de `condition_by_period` → **tiene que dar 0** (el código no lo pega);
4. prompts enteros de 2/9, 4/11, 4/12 y 5/8, las 4 fotos que tenían manchas;
5. 6/3, 7/11 y 3/16: el prompt entero, «Court» intacto y el año;
6. caps 1 y 7: el ancla Veo y las 2 anclas vecinas de las fotos de apoyo (ninguna empieza ni termina a mitad de palabra), más el `video_prompt` de los 2 clips, entero y tal cual;
7. conteo de fuentes del año (`anio_fuente`);
8. palabras por prompt: mediana y máximo;
9. gasto por paso.

## Al cerrar
- Suite rápida, suite amplia (`lab/hyperframes/f41/verificar.sh`), candado ch02 (`f792f3d4…`) y contrato F51a. Stickers y `MAPA_PROYECTO --check`.
- Commit por etapa con F51d-A. ESTADO_SESION y `lab/hyperframes/f51d/F51d_A_REPORT.md`, con lo abierto entero y el veredicto íntegro de `revisor-handoff`.
- **PARADA.** El analista revisa el papel con formato DEBERÍA y Omar da el OK antes de F51d-B.

## Reglas fijas
- **Cero llamadas a fal**: ni fotos, ni clips, ni foto madre.
- No tocar el canon, el pedido del canon, `cost_tracker`, el armado (salvo la chascada) ni el prompt de video Veo.
- Ninguna regla nueva. Subagentes en paralelo: la copia, los tests y las medidas mientras corre m03.

## Lista (no se hace aquí)
- Prompt de video Veo alineado con la guía de Google (DECISIONES 2026-10-28 11:15): tanda propia antes de generar los clips.
- Foto madre con el canon nuevo (DECISIONES 2026-10-28 21:23): va en F51d-B.
- `track_gemini_vision`: F51e. Scripts de lab rotos de F51c: abierto 2.
