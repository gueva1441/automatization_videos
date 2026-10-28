# HANDOFF F44 — ¿La ficha mejora si ve el caso? Prueba A/B antes de tocar producción

Analista · 2026-10-27 23:55 · rama `f11-guion-v4` · sesión de CC: la misma (Omar no pidió nueva).

## Por qué
- La ficha del caso (`researcher_steps/ficha_caso.py`, GPT «Sol») recibe hoy **el pool entero y un título** (`prompt()`: `<caso>{title}</caso>` + `<pool>` + `<tarea>`). No ve el ángulo, el misterio ni la revelación del video (`03_meta.json`, que sí están en el topic de `topics_db`). La escaleta (`m01a_escaleta.prompt_v2`) sí recibe esas 4 líneas.
- Hipótesis del analista (2026-10-27 23:44, aceptada por Omar para medir): la ficha elige historia, humano y pico sin saber qué video queremos, y la escaleta después la tuerce. Es la misma medicina de los títulos (DECISIONES 2026-10-27 03:37: más entrada, no regla nueva).
- Omar (23:47): **primero medir con la estructura actual, después el cambio, y ver si vale la pena; después la cascada.** Nada se commitea en producción si B no gana.
- **Dato que baja la expectativa (va dicho):** en Wittenoom la ficha ciega (A, 23:45) ya eligió como pico a Daniel Écija, que es también el ángulo de `03_meta`. Puede dar empate. Empate = no se cambia, y costó ≈ US$ 2,2 saberlo.

## Chequeo del analista (skill handoff-analista §0)
- ¿Construye sobre algo que se va a reemplazar? No: `ficha_caso.prompt()` es producción vigente (F39 la puso en la cadena).
- ¿Cambia el orden de tandas? No. F43 (auditoría) sigue pendiente y no depende de esto. F44 va ahora porque Wittenoom acaba de producir la rama A gratis (ficha a las 23:45 con `f23-1`, pool md5 `3eef2b44…`).
- Tema de la prueba: **Wittenoom** (`123bbb64-9fca-4395-8bf4-57d60e219ef1`), no Kyshtym: Kyshtym ya no está en `topics_db` (sin ángulo/misterio/revelación no hay `<caso>` que darle).

## Constantes
| valor | origen | quién |
|---|---|---|
| Tope de la tanda **US$ 3,00** (parte 1) | medido en Wittenoom A (`01_v3_costos.json`): ficha US$ 0,3533 + escaleta US$ 1,8637 = 2,22; B repite las dos + margen | analista; **Omar lo confirma al pegar el prompt** |
| Tope de la parte 2 (cascada, solo si B gana) **US$ 4,00** | guion v4 + títulos + papel ≈ US$ 2,75 (F39: semilla → guion 2,75 incluía research; DECISIONES 15:23) + papel ≤ 1,00 (`costos.m01e_tope_usd`) | analista; Omar confirma en la PARADA 1 |
| `prompt_version` de B = `f44-1` | convención del repo (`f23-1`, `f26-1`…) | estándar del repo |
| Las 4 líneas del `<caso>` | las mismas que ya recibe la escaleta (`m01a_escaleta.py` ~1465: TÍTULO/ÁNGULO/MISTERIO/REVELACIÓN) | valor que ya existe |

Sin ningún número nuevo de comportamiento. Sin reglas de estilo nuevas en el prompt de la ficha (DECISIONES: cero reglas nuevas en ficha/escaleta/guion).

## Módulos que toca (hoy → después)
| archivo | hoy | después (parte 1, solo en lab) | después (parte 3, solo si B gana) |
|---|---|---|---|
| `researcher_steps/ficha_caso.py` | `prompt(pool, title)`: `<caso>{title}</caso>` | `prompt(pool, title, caso=None)`: con `caso` (dict con angle/mystery/reveal) el bloque es `<caso>\nTÍTULO: {title}\nÁNGULO: …\nMISTERIO: …\nREVELACIÓN: …\n</caso>`; sin `caso`, **byte-idéntico a hoy**. `system()` no cambia. `run(..., caso=None)` lo pasa y anota `prompt_version` `f44-1` cuando va con caso | `fase1_5.asegurar_ficha` pasa el `caso` del topic; `prompt_version` pasa a `f44-1`; tests que fijan el prompt se actualizan al contrato nuevo |
| `lab/hyperframes/f44/f44_corridas.py` (nuevo, lab) | — | corre B con `steps_dir` de lab (como `f24_corridas.py`), lee A de producción **solo lectura**, y escribe la tabla de comparación | — |
| `fase1_5.py` | `asegurar_ficha` llama `fc.run(topic_id, steps_dir, title, tag)` | no se toca | pasa `caso={angle, mystery, reveal}` del topic |

`lab/mapa/stickers/`: cada commit que toque `ficha_caso.py` o `fase1_5.py` (parte 1 y parte 3) reescribe su sticker con el md5 nuevo y deja `python lab/tools/mapa_modulos.py --check` en 0 (regla del mapa, F42; el hook `guard_mapa` avisa).

## Parte 1 — A/B ficha + escaleta (US$ ≤ 3,00)
**A (producción, gratis, solo lectura):** `data/scripts/_steps/123bbb64…/ficha_caso.json` (ya existe, 23:45, `f23-1`, pool md5 `3eef2b448a82cfefa4abd4574341c985`) y `01a_escaleta.json` (ya existe, 23:51, `f26-1`, US$ 1,8637). No se regenera nada de A.

1. `ficha_caso.prompt()` con `caso` opcional (tabla de módulos). Test sin red en `test_module_f44.py`: sin `caso` el prompt es **byte-idéntico** al de hoy (md5 del prompt sobre un pool fixture del repo, antes y después); con `caso`, el bloque tiene las 4 líneas y nada más cambia.
2. `f44_corridas.py`: copia `00_pool_v3.json` de Wittenoom a `lab/hyperframes/f44/B/_steps/123bbb64…/` (md5 igual, verificalo), lee el topic de `topics_db` (solo lectura) y corre **ficha B** con `caso={angle, mystery, reveal}` del topic y el mismo `title` que usó A (`ficha_caso.json` → `titulo`: «Wittenoom ciudad fantasma contaminada Australia»). Mismo modelo, mismo esfuerzo que A.
3. Con la ficha B, **escaleta B** (`generate_escaleta_v2`, prompt vigente `f26-1`, `steps_dir` de lab, mismo topic dict). Nada de columna.
4. Tabla de comparación, por código, pegada en el reporte:
   - ficha A vs B: `conteos` entero, `sacados`, `usd`, `prompt_version`, `pool_md5`; `historia.humanos_candidatos` (nombre · rol · citas_verificadas), `historia.pico` (que · por_que), `historia.giros` (lista corta), `escenas` (nombres).
   - escaleta A vs B: `humano` (nombre · por_que), `pico` (beat · por_que), `promesa_gancho`, `cierre_humano`, número de beats, `_reparaciones`, `a_pantalla` (ids); por cap: `dato_central` + `datos_apoyo` de A y de B, y el solapamiento de ids (|A∩B| / |A∪B|) por cap y total.
   - Costo total de B.

**Salida de la parte 1:** la tabla entera + las dos fichas y las dos escaletas en `lab/hyperframes/f44/` (A copiada, B generada). **PARADA 1.** Omar decide: B gana / empate / A gana.

## Parte 2 — Cascada en lab (solo si Omar dice «B gana»; US$ ≤ 4,00)
1. Con escaleta B: guion v4 + reparación → partición y títulos → papel (`m01e_pantalla.generar`), todo con `steps_dir` de lab. Prompts vigentes, sin cambios.
2. Comparación contra la cadena A de producción (la que el form haya producido hasta donde llegue; si A paró en la compuerta del papel, mejor: el papel A está): títulos de cap A vs B; `01e_pantalla.md` A vs B (el analista los revisa con `revision-guion-pantalla`); bloqueantes del guion antes/después de reparar en A y B.

**Salida de la parte 2:** títulos A/B, los dos `01e_pantalla.md` y la tabla de bloqueantes. **PARADA 2.**

## Parte 3 — Producción (solo si Omar dice que la mejora llega al final)
1. `fase1_5.asegurar_ficha` pasa el `caso`; `PROMPT_VERSION` de la ficha = `f44-1`.
2. Los tests de `test_module_f12…f22d.py` que fijen el texto del prompt de la ficha pasan al contrato nuevo (no se debilitan: siguen comprobando el bloque entero).
3. Sticker de `ficha_caso.py` y `fase1_5.py`, mapa regenerado, `--check` 0. Suite rápida y `test_module_f44.py`. Línea en `DECISIONES.md` con fecha (la redacta el analista; CC la pega).
4. Topics con ficha ya hecha **no se regeneran** (`asegurar_ficha` reusa la que hay; se deja dicho en el reporte).

**Salida de la parte 3:** diff de `ficha_caso.py` y `fase1_5.py`, salida de los tests. **PARADA 3.**

## Reglas fijas
- **Nada en `data/` ni en `output/`.** A se lee; B vive en `lab/hyperframes/f44/`. El form de Omar sigue corriendo: no se toca ni se relanza; no se cierra ningún proceso suyo.
- US$: parte 1 ≤ 3,00; no se arranca la parte 2 sin la PARADA 1. `tope_tanda` con el tope de la parte en curso.
- Una variable por rama: B difiere de A **solo** en las 3 líneas (ÁNGULO/MISTERIO/REVELACIÓN). Mismo pool (md5), mismo título, mismo modelo, mismos prompts de escaleta.
- `config.py` y `.env` no se tocan. Sin merge a `main`.
- Commits por parte, rutas explícitas; parte 1 commitea solo `ficha_caso.py` (con el `caso` opcional, byte-idéntico sin él), `test_module_f44.py` y lo de `lab/hyperframes/f44/`. Push a `origin/f11-guion-v4`.
- Subagentes en paralelo donde haya paralelo (la copia y lectura de A, el script de comparación), pero las dos llamadas pagas de B van en serie (ficha → escaleta).
- Prohibido `pytest` en bloque sobre `test_*.py` (incidente F42); solo los archivos nombrados, con proxy muerto para lo que no necesite red (las llamadas de B sí necesitan red: solo ellas).
- Reporte `lab/hyperframes/f44/F44_REPORT.md`: salida de cada parte pegada, «lo que queda abierto» entero, veredicto íntegro de `revisor-handoff`. ESTADO al día. Cerrar subagentes y shells propios. **PARADA.**

## Abierto que el analista deja anotado (no es de esta tanda)
- **Escaleta A de Wittenoom (`_reparaciones`):** el modelo eligió como humano a «Daniel Écija (padre)» y la reparación lo cambió por **María Bernal** porque el nombre no coincidía exacto con el pool. Una reparación de nombre no debería cambiar de persona. Y los 7 caps vinieron con el doble de palabras (460 → 250). Las dos cosas se miran en la PARADA 1 con A y B a la vista; si se repiten en B son bug de la escaleta, no de la ficha.
- `seed_title` del topic Wittenoom es `None`; la ficha tomó el título de `seeds_archive`. Funciona, pero el topic debería guardarlo (F39 A.3 lo prometía). Para F43.
- Kyshtym y Vajont ya no están en `topics_db`: las pruebas comparativas contra temas viejos solo se pueden hacer con lo que quedó en `lab/hyperframes/f40/a/` (sin `<caso>`). Anotarlo en la lista de material de lab.
