# HANDOFF F50g-A — el aspecto del grupo (canon) va al prompt de foto, por código, sin LLM

Modelo para CC: Claude Opus 5.5, effort medium. Subagentes en paralelo donde haya trabajo independiente (tests y re-armado).
Rama `f11-guion-v4`. `main` no se toca. Costo: **US$ 0** (ninguna llamada a modelo ni a fal).

## Por qué (dato, 2026-10-29 01:11)
Omar generó la foto 1/2 de Wittenoom en fal (Seedream 5.0 Lite) con 4 prompts. Los 2 que decían solo «Spanish migrant» (nacionalidad) dieron asiáticos; el que decía «Mediterranean features, dark slicked hair» (rasgos) dio españoles. Seedream obedece rasgos visibles, no etiquetas.
El canon (`canon_f50f.json`, `people_groups[].appearance`) ya trae los rasgos de cada grupo («Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes…»), pero `m03_imagenes_v3.armar` deja el renglón `aspecto` vacío (l. 642, «así se midió» en F46b, con otro modelo de casilleros y antes de que el canon tuviera `appearance`). El dato se paga y no se manda. Guía oficial de fal para 5.0 Lite: en prompts con varias personas, los atributos asignados a cada una sí se siguen.

## Qué cambia (una variable)
`aspecto` = la oración `appearance` de cada grupo de la foto (`it["people_group"]`, que Opus llena), en el orden en que Opus los listó, una oración por grupo, pegada tal cual del canon (`oracion()` como el resto de casilleros). Sin grupo, o grupo sin `appearance` → nada (regla con su «si no hay, nada»). Nada más cambia en el armado: ni orden, ni estilo, ni ropa (la ropa por tramo ya la escribe Opus en `subject`; cablearla literal es otra variable, otra tanda).

## Constantes
| valor | origen | quién |
|---|---|---|
| una oración por grupo, orden de Opus | estructura del canon (`appearance` es una oración) | analista, dentro de la decisión de Omar 2026-10-29 01:29 |
| (sin tope de grupos ni de palabras) | — | — |

## Simulación contra la data real (analista, sobre `_steps/123bbb64…/03_visual.json` + `canon_f50f.json`)
- 94 fotos con prompt. Grupos por foto: 1 → 49 fotos; 2 → 9; 0 → 36. Todos los ids existen en el canon.
- Después del cable: 58 fotos con aspecto, 36 sin (las 36 sin grupo ≈ las 37 «sin personas» del papel: Opus deja el grupo vacío cuando no hay gente; correcto).
- Palabras por prompt: mediana 136 → 157,5; máximo 245 → 273. Las 9 fotos con 2 grupos suman 2 oraciones (~45 palabras). Se acepta: es dato, no invento; la prueba L/C (recortar invento y repeticiones) sigue pendiente y es otra variable.
- 1/2: grupo `spanish_migrant_families` → el prompt pasa a decir, después del sujeto y la acción: «Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom.»

## Módulos tocados
1. `script_engine/m03_imagenes_v3.py` — `armar`: hoy `"aspecto": ""`; después, la(s) oración(es) de `grupos[g]["appearance"]` para `g` en `it["people_group"]`. Docstring actualizado (sacar «no se escriben: así se midió»).
2. `lab/hyperframes/f50g/rearmar.py` — copia adaptada de `lab/hyperframes/f50b/rearmar.py`: re-arma EN SECO las fotos de Wittenoom desde `raw_llm_prompt` + `anio` guardados + el canon del topic (`topics_db` / `05_visual_canon`, el mismo que usa producción), igual que `m03_visual._render_prompts_seedream` (armar → f8_backstop → texto legible). Escribe `prompt/sensible/motivos` en `03_visual.json` solo con `--escribir`. Antes de escribir, copia `03_visual.json` a `lab/hyperframes/f50g/antes/`.
3. `tests/test_module_f50g.py` — (a) foto con 1 grupo con appearance → la oración está en el prompt, entre sujeto y mirada; (b) 2 grupos → 2 oraciones en el orden de `people_group`; (c) sin grupo → prompt idéntico al de hoy; (d) grupo sin appearance (p. ej. `airport_police`) → nada; (e) el resto de partes no cambia.
4. `lab/hyperframes/f50g/PAPEL_FOTOS_WITTENOOM.md/.json` — papel nuevo con `papel.py --salida` (el de f50f).

## Orden de etapas (cada una termina con su salida en texto)
0. md5 de este handoff en el reporte. Línea en `DECISIONES.md` tal cual:
   `- 2026-10-29 01:29 · **F50g-A:** el aspecto del grupo (`people_groups[].appearance` del canon) va al prompt de foto por código, una oración por grupo en el orden de Opus, pegada tal cual; sin grupo o sin aspecto, nada. Motivo: la 1/2 generada en fal dio asiáticos con «Spanish migrant» y españoles con «Mediterranean features»; el canon ya lo traía y `armar` lo dejaba vacío desde F46b · Omar · F50g-A`
1. `armar` + tests (módulos 1 y 3). Salida: los 5 tests en verde + el prompt de la 1/2 armado por el test, pegado.
2. `rearmar.py` sin `--escribir`: tabla por cap: fotos · con aspecto · sin aspecto · palabras (mediana, máx) antes/después; debe dar 58/36 y mediana ~157. Si no coincide, PARADA y se explica.
3. `rearmar.py --escribir` + papel nuevo en `lab/hyperframes/f50g/`. Salida: pegar en el reporte 3 prompts enteros: **1/2**, una foto con 2 grupos (la que elijas, decir cuál) y una con `banjima_traditional_owners`.
4. Suite rápida; candado de ch02 (md5 no cambia: ch02 no se renderiza aquí). Commit por etapa con mensaje que nombre F50g-A. ESTADO_SESION + `F50g_A_REPORT.md` con lo abierto entero y el veredicto íntegro de `revisor-handoff`.
5. **PARADA.** No correr fal, no correr m03 con modelo, no tocar F50g-B (bug «Court», corte Veo, `anio_final`: van después, en su handoff).

## Abierto que este handoff no toca (para que conste)
- Aspecto de personas documentadas (`documented_people[].appearance_canon`, p. ej. Daniel): hoy solo reemplaza nombres; cablearlo como descripción es otra variable.
- Look del lugar (`era_visual_canon.materials_textures/interiors`): no va al prompt; otra variable.
- Prueba L contra C (largo del prompt): sigue pendiente; se diseña sobre los prompts de F50g-A.
