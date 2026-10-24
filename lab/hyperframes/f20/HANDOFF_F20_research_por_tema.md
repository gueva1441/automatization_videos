# HANDOFF F20 — Parte 1: el research se adapta al tema (vocabulario del perfil, descargas por idioma, humano elegible)

Analista · 2026-10-24 · Para CC (misma sesión). Base: `d7ce148` (rama `f11-guion-v4`). **Solo research y compuerta.** Sin ficha, columna, escaleta ni guion en esta tanda. **PARADA al terminar: el analista valida antes de la parte 2.**

## 0. Por qué (verificado en el código)
El research y la compuerta están hechos a la medida de Orleans:
- `research_v3.py:989` — testigo = «preso, guardia, familiar, rescatista, vecino»; `:1203` títulos `sheriff, deputy, sgt, captain…`; `:1208` «no es persona» = `inmate, recluso, preso, warden, deputies…`.
- `:1405`/`:1419` — un «conteo» solo si el número va pegado a «reclusos, presos, prisioneros, internos, detenidos». «Muertos», «evacuados», «irradiados» no son conteo: por eso Ycuá no tuvo cifra canónica y Kyshtym tampoco.
- `:1386` — humano elegible = testigo, no antagonista, **presente en el año del evento**, y 3 citas o 3 datos. Mata a quien investiga o reclama después (Tumerman 1960, Kutepova décadas después) y a los testigos de una sola frase (Osetrov, Komarov, Serov).
- `:41` — `MAX_DESCARGAS_OK = 10` total: con dos idiomas, las fuentes del segundo desplazan a las del primero (F19).
- `pool_gate.py` — los cuatro umbrales (150 / 8 / 2 / 10) son lo que Orleans tenía.
Resultado: el pool de Kyshtym tiene historia (tres testigos de la explosión, los niños friendo peces muertos, el pescado que vela la placa de rayos X, Kutepova contra la jueza) y la compuerta dio rojo.

## 1. Cambios
**1.1 El perfil del seed describe el caso** (`_perfil.json`, el mismo paso que hoy genera `nombres_locales`). Se agregan tres campos, generados por el modelo a partir del seed y de la primera pasada de fuentes (R1):
- `roles_testigo`: quiénes estuvieron ahí o lo vivieron, en las palabras del caso (Orleans: preso, guardia, oficial; Kyshtym: operario, liquidador, evacuado, médico, físico; Ycuá: cliente, cajera, bombero, sobreviviente).
- `roles_antagonista`: quién decide (sheriff; el ministerio, la dirección de la planta; el dueño).
- `sustantivos_conteo`: con qué se cuentan las víctimas (presos; muertos, evacuados, irradiados, hospitalizados; muertos, heridos, huérfanos).
Cada campo con 4–10 palabras, en español, más sus formas en los idiomas del research. Para Orleans y Ycuá el perfil se regenera **sin research** (una llamada Flash por tema, ~centavos) para poder comparar.

**1.2 El research lee el perfil, no las listas:**
- El prompt de R3 (`:989`) recibe `roles_testigo` y `roles_antagonista` del perfil en lugar de «preso, guardia, familiar, rescatista, vecino».
- `_TITLES` y `_NOT_PERSON` (`:1203`, `:1208`): se mantienen como base genérica (títulos militares y palabras gramaticales), **se quitan** los términos de tema (`inmate, recluso, preso, presa, warden, deputies, guardias, guards, abogado…`) y se suman los `roles_*` del perfil en tiempo de ejecución.
- Conteos (`:1405`, `:1419`, `:1661`): la regex de sustantivos se arma con `sustantivos_conteo` del perfil (más «personas» y «víctimas» siempre).
- Descargas: `MAX_DESCARGAS_OK` pasa a ser **por idioma** (10 por cada idioma del research), con el mismo orden de prioridad de hoy dentro de cada idioma.

**1.3 Humano elegible** (`person_stats`): `elegible_humano` = no antagonista **y** (una cita propia verificada **o** nombrado en ≥ 3 ítems). Se quita el requisito de presencia en el año del evento; en su lugar se guarda `presente_en_evento: bool` como dato informativo, que la ficha y la columna ya pueden ver. Un rol de `roles_antagonista` sigue excluido.

**1.4 La compuerta mide lo mismo con el conteo nuevo.** Los umbrales no cambian en esta tanda (eso es la parte 2). Solo cambia qué cuenta como elegible.

## 2. Corridas
1. **Orleans (`ba6c3cac-f7r3`) y Ycuá (`f8s1-ycua-bolanos`), sin research:** regenerar el perfil (1.1), re-correr `person_stats` y la compuerta sobre el pool existente, y guardar `POOL_GATE_f20.md` al lado del actual. **No se pisa nada.** Lo que importa: que sigan verde/verde y que los elegibles tengan sentido (quiénes entran, quiénes salen).
2. **Kyshtym:** perfil nuevo → research v3 completo con las descargas por idioma → compuerta. Respaldar el pool de F19 como `00_pool_v3_f19.json`. Tope US$ 3.50.
3. Tabla en el reporte: por tema, elegibles antes → después (con nombres), conteos canónicos antes → después, documentos por idioma antes → después, color de la compuerta antes → después.

## 3. Frenos
- Se toca `research_v3.py` y el perfil **solo** en lo de §1. No se tocan ficha, columna, escaleta, guion, `m05`, `evidence.py`, `config.py`, `m03*`, `gfx_*`.
- Cero reglas nuevas: todo lo de §1 reemplaza listas fijas por datos del perfil o cambia un conteo. Ningún chequeo nuevo.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests: perfil con los tres campos; `_NOT_PERSON` sin términos de tema; conteo con sustantivos del perfil (un caso de presos, uno de muertos); descargas por idioma; `elegible_humano` con los cuatro casos (Reed, Kutepova, Osetrov, Gusman). Suites verdes + las 5 previas.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f20/F20_REPORT.md`
1. Los tres perfiles (Orleans, Ycuá, Kyshtym) tal cual.
2. La tabla de §2.3.
3. Pool de Kyshtym: personajes con sus conteos y citas (la lista completa, para que el analista la lea).
4. Costo. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista valida: que Orleans y Ycuá no empeoraron, que los elegibles de Kyshtym son los que la historia necesita, y que las listas carcelarias ya no están en el código. Recién después, la parte 2 (la compuerta pregunta a la ficha).
