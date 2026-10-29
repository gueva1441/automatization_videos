# HANDOFF F51b — el canon separa el aspecto fijo del estado (+ chascada: estilo C sin año)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · tope **US$ 1,00** (1 llamada a Opus ≈ 0,34, más 1 reintento) · 3 etapas y PARADA.

## Por qué
F50i probó que el estado metido en `people_groups[].appearance` («dusted red», «frail from lung disease») hace que Seedream pinte manchas tipo sangre en fotos donde el grupo no está en Wittenoom (barco, hospital, aeropuerto). La causa está en la **definición del campo**, en `TEXTO_1_PEOPLE_GROUPS`, que hoy dice «según su origen documentado **y su época** … contextura típica de su trabajo». Así Opus mezcla el estado con los rasgos. Omar, 2026-10-29 03:23 (c): «el canon separa el aspecto fijo (piel, pelo, ojos, complexión) del estado (polvo, enfermedad) y el código pega solo el fijo».

## Simulación sobre el canon vivo de Wittenoom (`05_visual_canon.json`, marca a08c790c)
De 12 grupos, **5 traen estado** dentro del aspecto, 5 están limpios y 2 vienen vacíos:

| grupo | estado metido hoy |
|---|---|
| prospectors_mine_owners | «deeply sun-tanned and weathered», «from bush prospecting» |
| mine_and_mill_workers | «darkened by sun», «often coated in fine dust» |
| spanish_migrant_families | «women and children tanned and dusted red in Wittenoom» |
| town_children | «tanned», «dusted with red earth and fine asbestos powder» |
| victims_advocates_and_lawyers | «ill former workers aged, thin and frail from lung disease» |
| company_managers, mine_and_health_officials, union_and_arbitration, australian_politicians, banjima_traditional_owners | limpios |
| international_un_official, airport_police | vacíos |

La clasificación es del analista. No usé ninguna lista de palabras: leí las 12 frases a mano.

## Orden re-derivado
- ¿Construye sobre código que ya se decidió reemplazar? No. Cambia la definición de un campo del pedido del canon (`step_4e_visual_canon.py`) y nada más del armado.
- ¿Alguna decisión de hoy cambia el orden? No. F51a ya está; F51d (regenerar Wittenoom) necesita este canon.

## Módulos que toca
| módulo | hoy | después |
|---|---|---|
| `researcher_steps/step_4e_visual_canon.py` | `TEXTO_1_PEOPLE_GROUPS` define `appearance` «según su origen documentado y su época … contextura típica de su trabajo» | `appearance` = solo los rasgos fijos; un campo nuevo, `condition_by_period`, guarda el estado (textos abajo). La marca del canon cambia sola, porque cambia el pedido |
| `script_engine/m03_imagenes_v3.py` | `ESTILO_C` con `{anio}` vacío da «taken in , with…» | chascada: sin año, la oración va sin «taken in {anio}» |
| tests (`test_module_f50a.py` si fija el texto viejo; `test_module_f51b.py` nuevo) | — | ver etapa 1 |
| `DECISIONES.md` | — | 1 línea (etapa 0) |

**No se toca:** `armar` sigue pegando solo `appearance`, porque ya es lo que hace. Nadie pega `condition_by_period`: ni `armar` ni el expediente (`m03_expediente.py` l. 208). Si algún día se usa, es otra variable y queda en la lista.

**Regla que reemplaza:** la definición vieja de `appearance` («y su época», «contextura típica de su trabajo»). No se agrega ninguna regla de estilo: se separa un campo en dos.

## Textos nuevos (enteros, revisados)
En `TEXTO_1_PEOPLE_GROUPS`, la línea `- appearance: …` se reemplaza por estas dos:
```
- appearance: solo los rasgos físicos fijos de la persona según su origen documentado: tono de piel, color y tipo de pelo, color de ojos, rasgos de la cara y contextura (EN, una frase). Nada que cambie según dónde estén, qué hagan o qué les pase: eso va en condition_by_period
- condition_by_period: una entrada por cada tramo de años en que el material documenta un estado físico de ese grupo (polvo, suciedad, bronceado, heridas, enfermedad, desgaste); years "AAAA-AAAA" y condition (EN, una frase). Si el material no documenta ningún estado, lista vacía
```
El resto del texto queda igual, incluida la frase final («si el material no dice el origen de un grupo… dejá appearance vacío»).

**Revisión simulada** (lo que debería escribir Opus con el material de Wittenoom):
- `spanish_migrant_families`: appearance «Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds.» · condition `[{"years":"1950-1966","condition":"women and children tanned and dusted with red earth"}]`. Es justo la C′ de F50i, que salió limpia en 8/8.
- `victims_advocates_and_lawyers`: appearance «Mixed Australian and European-born adults with fair to olive skin…» · condition `[{"years":"1980-2024","condition":"ill former workers thin and frail from lung disease"}]`.
- Riesgo: que Opus deje «weathered» o «tanned» en `appearance`. Lo mide la etapa 2. Si pasa en 1 o más grupos, **no** se agregan reglas al pedido: se reporta y decide Omar.

**Chascada (estilo sin año):** sin año, el estilo queda «A grainy 35mm documentary photograph, with muted colors and slight underexposure, in a dark-history realist style.». Es `ESTILO_C` sin « taken in {anio}». Con año, el texto queda byte a byte igual al de F51a, y el contrato 20/20 de F51a tiene que seguir verde.

## Constantes
| valor | origen | quién |
|---|---|---|
| tope US$ 1,00 | canon F50f = US$ 0,3415 (`F50f_REPORT.md` l. 127) × 1 llamada + 1 reintento + margen | analista, pide OK de Omar con el «dale» de las 03:52 |
| modelo y esfuerzo del canon | `MODELO_CANON` / `ESFUERZO_CANON`, sin cambios | Omar 2026-10-28 23:34 |

## Etapa 0 — DECISIONES
md5 de este handoff en el reporte. Al final de `DECISIONES.md`, tal cual:
```
- 2026-10-29 03:52 · **F51b:** en el pedido del canon, `people_groups[].appearance` pasa a ser solo los rasgos fijos según el origen (piel, pelo, ojos, cara, contextura); el estado documentado (polvo, suciedad, bronceado, heridas, enfermedad, desgaste) va a un campo nuevo, `condition_by_period` (years + condition), que el código no pega en la foto; Wittenoom rehace su canon con Opus (tope US$ 1); chascada: el estilo C sin año va sin «taken in» · Omar · F51b
```
Commit. Salida: `tail -1`.

## Etapa 1 — código y tests (US$ 0)
1. Reemplazar la línea de `appearance` por las dos de arriba, tal cual.
2. Hacer que `condition_by_period` sobreviva la limpieza. Hoy `people_groups` pasa entero (`extract_visual_canon`, l. ~733), pero hay que verificarlo. También que entre en `CANON_KEYS` / 05_visual_canon si hace falta: `people_groups` ya entra.
3. Chascada en `armar`: el estilo sin año, como arriba.
4. Tests:
   - el pedido trae las dos líneas nuevas y no la vieja;
   - con `anio=""`, el estilo no dice «taken in»;
   - el contrato 20/20 de F51a sigue verde (`lab/hyperframes/f51a/contrato.py`).

Salida: el diff del texto del pedido (viejo → nuevo) y la marca nueva calculada en seco para Wittenoom (`marca_canon`), distinta de a08c790c.

## Etapa 2 — canon de Wittenoom con Opus (≤ US$ 1,00)
1. Copia de respaldo: `05_visual_canon.json` y la entrada del topic en topics_db → `lab/hyperframes/f51b/antes/`.
2. `asegurar_canon` para `123bbb64-9fca-4395-8bf4-57d60e219ef1`: 1 llamada, y un reintento solo si sale CanonError. Escribe topics_db y `05_visual_canon.json`, como en producción.
3. `lab/hyperframes/f51b/CANON_F51b.md`, con:
   - **Tabla grupo por grupo:** id · appearance viejo · appearance nuevo · condition_by_period nuevo. Los grupos que aparecen o desaparecen, marcados.
   - **Lo demás del canon que cambió:** Opus no repite palabra por palabra, así que se listan, para cada uno de `era_visual_canon.periods` (years, clothing), `documented_people` (nombre, appearance_canon), `documented_props` y `central_subject`, los cambios viejo → nuevo. Sin juicio: solo el diff.
   - **Los prompts de 4 fotos** armados con el canon nuevo (en memoria, sin escribir `03_visual.json`): 2/9, 4/11, 4/12 y 5/8 (las de las manchas). Al lado, el C′ de F50i (`PROMPTS_F50i.md`).
4. Costo real desde `cost_history` (Opus va por tokens).

## Al cerrar
- Suite rápida, suite amplia (`lab/hyperframes/f41/verificar.sh`), candado ch02 (`f792f3d4…`) y contrato F51a.
- Un commit por etapa, con F51b en el mensaje. ESTADO_SESION y `lab/hyperframes/f51b/F51b_REPORT.md`, con lo abierto entero y el veredicto íntegro de `revisor-handoff`.
- **PARADA.** El analista compara grupo por grupo antes de F51d.

## Reglas fijas
- Sin fal. No escribir `03_visual.json`.
- No tocar `name_matching` («Court»), el corte Veo, `anio_final` ni `cost_tracker` (F51c y F51e).
- Ninguna regla nueva al pedido aparte de las dos líneas de arriba. Si Opus no separa bien, PARADA y reporte, sin parches.
- Subagentes en paralelo donde se pueda: tests y respaldo mientras corre Opus, y la tabla de diffs.

## Lista (no se hace aquí)
- `documented_people[].appearance_canon` puede tener el mismo problema. Hoy no se pega en la foto: revisarlo si se cablea.
- Uso futuro de `condition_by_period`, por ejemplo pegarlo solo cuando la foto cae en el tramo y en el lugar: otra variable, y decide Omar.
