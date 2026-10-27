# HANDOFF F39 — Fase 1 de la semilla al papel, en producción + Kyshtym en limpio (analista, 2026-10-27)

**Para qué:** la regla de Omar es que nada se publica hasta que Fase 1 corra sola para cualquier tema. Hoy no corre sola: las corridas «desde la semilla» (F23, F24) se cosían con scripts de laboratorio. Esta tanda **(A)** cose la cadena en el código de producción y **(B)** la prueba con Kyshtym como si fuera un tema nuevo. Termina en el **papel** (`01e_pantalla.md`): sin voz, sin imágenes, sin render. Decisión: DECISIONES 2026-10-27 15:23.

## 0. Orden re-derivado (handoff-analista §0)
- ¿Construye sobre código a reemplazar? No: `fase1_5` es el orquestador vigente y `topic_researcher` el research vigente (v3 por defecto desde F7d). Lo único reemplazado es la rama de la escaleta **sin ficha**: está reemplazada desde F16 y seguía viva como respaldo callado. Se borra.
- ¿Cambia el orden alguna decisión de hoy? Sí, y ya está aplicada: Omar 15:23 (A y B en una tanda). La ENTRADA 27d decía «hasta `--plan-only`». Se corrige: el final es el papel, porque el `--plan-only` necesita voz e imágenes y eso se paga después del OK de Omar (DECISIONES 2026-10-26 19:54).

## 1. Diagnóstico (con datos, del analista)
1. `researcher_steps/ficha_caso.run` solo se llama desde `lab/hyperframes/f12…f24/*_corridas.py`. En producción, `fase1_5` solo hace `ficha_caso.load`.
2. `script_engine/m01a_escaleta.generate_escaleta` (~línea 1084): si no hay `ficha_caso.json` con `historia`, sigue por el camino viejo (Pro, `SCHEMA`, sin ficha) **sin avisar**.
3. `topic_researcher.research_topics` saltea las semillas ya investigadas (`_get_existing_seed_ids`) y crea el topic con `uuid4`. No hay forma de correr una semilla en un topic dado.
4. `fase1_5.process_topic`, después de m01b (que ya escribe el papel con `run_pantalla`), sigue a `normalizer_gate → audio`, o sea a la voz, que se paga, sin mirar si Omar aprobó el papel.

**Simulación de la regla «escaleta sin ficha v2 = error»** sobre todos los `data/scripts/_steps/*` con `00_pool_v3.json` (corrida del analista):

| topic | `ficha_caso.json` | ¿para con la regla nueva? |
|---|---|---|
| 4ac37187-pennhurst | f23-1, con historia | no |
| ba6c3cac-f7r3 (Orleans) | f15-1, con historia | no |
| f8s1-ycua-bolanos | f15-1, con historia | no |
| f8s3-vajont / f8s3-vajont-f28c | f23-1, con historia | no |
| f18-kyshtym-mayak | f23-1, con historia | no |
| ba6c3cac-f10seco | — | sí (topic de lab F10, no de producción) |
| f8s2-cromanon | — | sí (topic de lab F8, nunca tuvo escaleta) |

Ningún topic de producción se rompe. A.5 recalcula esta tabla con código.

## 2. Constantes (ninguna nueva en el código)
| valor | dónde | origen | quién |
|---|---|---|---|
| tope de la tanda US$ 5,00 | `lab/TOPE_TANDA.json` (hook `tope_tanda`) | derivado: F23 semilla → guion US$ 2,75 + papel ≤ 1,00 + margen | voto del analista; Omar lo confirma al pegar (DECISIONES 15:23) |
| 8 hilos en R2/R3 | `research_v3.WORKERS` | existente (F26 §C) | — |
| papel ≤ US$ 1,00 | `costos.m01e_tope_usd` del perfil | existente (F37/F38d) | Omar |
| ficha `gpt-6.1-sol` high, prompt `f23-1` | `ficha_caso.MODELO`, `PROMPT_VERSION` | existente | — |
| escaleta `claude-fable-5-1` | default de `--modelo-escaleta` | existente (F25c) | — |
| guion `claude-fable-5-1` | `guion_v4.DEFAULT_MODELO_GUION` | existente (F22e) | — |
| md5 ch02 `38e5ba14…` | candado | existente (ESTADO) | — |

## 3. Módulos tocados (3; sticker = `lab/MAPA_MODULOS.md`)
| módulo | hoy | después |
|---|---|---|
| `fase1_5.py` (orquestador de Fase 1) | m01a = compuerta + escaleta; no arranca desde una semilla; después de m01b sigue a la voz | `--semilla <archivo> --topic <id>` corre primero el research de esa semilla; m01a = compuerta → **ficha si falta** → escaleta; después de m01b, **PARADA del papel** salvo `--aprobar-papel` vigente |
| `topic_researcher.py` (research de semillas) | topic con `uuid4`, saltea semillas ya investigadas | función pública que investiga **una** semilla en un `topic_id` dado y la registra en `topics_db` (la misma cadena de hoy: `run_seed` + 4a–4e + `_enrich_with_seed_metadata`); `research_topics` la usa por dentro y queda igual por fuera |
| `script_engine/m01a_escaleta.py` (escaleta) | sin ficha v2 cae callada al camino viejo | sin ficha v2 → excepción `EscaletaSinFicha` (para y dice por qué); la rama vieja se **borra** (prompt, schema y validación que solo ella usa) con sus tests |
| `researcher_steps/ficha_caso.py` | — | **no se toca**: se llama `run` tal cual |

## 4. Paralelo (DECISIONES 01:23)
- **Paso 0** en serie.
- **A en paralelo:** subagente 1 = `m01a_escaleta` (A.2 + tests); subagente 2 = `topic_researcher` (la función de una semilla + tests); subagente 3 = simulador (A.5 d, la tabla por código). CC principal = `fase1_5` (A.1, A.3, A.4), que usa lo de 1 y 2 cuando estén. El candado (md5 de ch02 + suite amplia) lo corre CC **en serie al final de A**, no cada subagente (regla aprendida en F38e).
- **B después de A** (necesita el código). Mientras corre el research de B, `revisor-handoff` puede revisar el diff de A. Revisor final sobre todo.

## 5. Paso 0
1. **Secretos antes del push** (el repo es público): `git log --branches --not --remotes -p` → buscar claves (`api_key`, `sk-`, `AIza`, `Bearer `, `-----BEGIN`, archivos `.env`). Si aparece algo: **PARADA, sin push**, y decir dónde.
2. Commit tal cual, con md5 en el mensaje: `DECISIONES.md` (md5 `3ab8559116cb0ff3740eab7dbb1e1b0f`, línea 15:23) y este handoff. Si un md5 no coincide: PARADA.
3. **Perfil sin commitear:** `gfx_profiles/misterio.json` y `gfx_profiles/lexico_propuestas.json` están modificados desde el 21-oct (último commit `7c0b2e5`, wip F5e). Los renders v5 y v6 se hicieron con esta copia de trabajo, así que **esta copia es el perfil vigente**. Va en un commit aparte, tal cual y por ruta explícita, con el resumen en el mensaje (`git diff --stat` + las claves de primer nivel que cambian). `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log` **no entran**: el reporte dice de qué tanda son.
4. `git push -u origin f11-guion-v4` (respaldo, no merge; `main` no se toca). Pegar la salida.

## 6. A — La cadena de producción, de la semilla al papel
**A.1 Ficha en m01a.** En `fase1_5`, el orden es compuerta del pool → ficha → escaleta. La ficha no se genera si la compuerta da rojo (no se paga Sol). Si no hay `ficha_caso.json` con `historia`, se genera con `ficha_caso.run`, con el modelo y el prompt vigentes. El título es el mismo que usaron F23/F24 (`seed_title`); si el topic no lo guarda, se guarda al registrar (A.3). El costo va a `01_v3_costos.json` como paso «ficha» (`_step_cost`). Si ya hay ficha v2, se usa y no se regenera.

**A.2 Escaleta sin ficha = error.** `generate_escaleta` sin ficha v2 lanza `EscaletaSinFicha("<topic>: sin ficha_caso.json con historia")`, y `fase1_5` lo muestra como PARADA del topic. Se borran la rama vieja y lo que **solo** ella usa (prompt, `SCHEMA`, validación, `MAX_APOYOS` sin ficha…). Lo que tenga otro llamador vivo se deja y se lista en el reporte. El camino `escaleta_frozen` no se toca. Los tests de la rama vieja se borran por nombre (lista en el reporte); los que la usaban de paso, pero prueban otra cosa, se pasan a ficha v2.

**A.3 Arrancar desde una semilla.** `python fase1_5.py --semilla <archivo.json> --topic <id> --v3 --guion v4 --batch`:
- si `_steps/<id>/` ya existe o `<id>` ya está en `topics_db`: **PARADA** (no pisa nada);
- respaldo de `data/topics_db.json` como `topics_db.pre_<id>.json`;
- research de la semilla con la función nueva de `topic_researcher` (con `topic_id` dado, sin el filtro de semillas ya investigadas, sin tocar el inbox ni el archivo de semillas) y registro del topic en `topics_db` con ese id. La compuerta roja (`PoolGateRed`) es PARADA con sus motivos;
- y sigue la cadena de siempre: m01a (A.1), m01b, PARADA del papel (A.4).

**A.4 Compuerta del papel** (DECISIONES 2026-10-26 19:54, igual que `--aprobar-guion` de F33 §B):
- después de m01b, si `01e_pantalla.json` no tiene `aprobado` con el md5 de su contenido actual (sin el campo `aprobado`), la cadena **para**. Imprime la ruta de `01e_pantalla.md` y el comando para aprobar;
- si m01e no dejó papel (`run_pantalla` devolvió None), también para: no hay nada que aprobar;
- `python fase1_5.py --topic <id> --aprobar-papel "QUIÉN FECHA"` escribe `aprobado: {por, fecha, md5}` y no corre nada más;
- cualquier paso posterior a m01b (`--from normalizer_gate`, `audio`, `m07`, `m03`) mira lo mismo. Un papel regenerado cambia su md5 y queda sin aprobar.

**A.5 Salida en texto** (pegada en el reporte):
- (a) las líneas nuevas de `--help`;
- (b) el comando de A.3 corrido en un test con llamadas falsas: el orden de los pasos que imprime y el mensaje de PARADA del papel;
- (c) `grep` antes y después de la rama borrada en `m01a_escaleta.py`;
- (d) la tabla de §1 recalculada por código;
- (e) tests nuevos (`test_module_f39_*.py`), tests borrados o ajustados por nombre, suite rápida, suite amplia (898 verdes + las 5 previas, o lo que quede, con cada diferencia explicada) y md5 de ch02 `38e5ba14…`.

PARADA corta: se anota y sigue a B.

## 7. B — Kyshtym en limpio, desatendido
**B.0 Semilla:** la de `f18-kyshtym-mayak` (`seed_id b6b84f96-03b7-40cd-8173-414d60514c76`). Buscarla en `data/seeds_archive.json`; si no está o difiere de `lab/hyperframes/f18/seed_f18.json`, usar la de F18, decir cuál se usó y por qué, y pegar su `seed_title`. Copiarla a `lab/hyperframes/f39/b/semilla_kyshtym.json`.

**B.1 Topic limpio:** `f39-kyshtym`. **Nada** se copia de `f18-kyshtym-mayak`: ni perfil, ni `fuentes.json`, ni `_r1_cache.json`, ni `_r3_cache/`. Tiene que comportarse como un tema que el sistema nunca vio.

**B.2 Tope:** `lab/TOPE_TANDA.json` = `{"usd": 5.00, "desde": <hora de arranque de B>}`.

**B.3 Una sola corrida, sin manos:**
```
python fase1_5.py --semilla lab/hyperframes/f39/b/semilla_kyshtym.json --topic f39-kyshtym --v3 --guion v4 --batch
```
CC no interviene entre pasos: es la prueba de «desatendida». Si un paso falla, **PARADA** con el paso, el error y lo gastado hasta ahí. No hay reintento a mano ni atajo: la falla es un hallazgo («frena»), no algo a esquivar. Log en `lab/hyperframes/f39/b/corrida.log`.

**B.4 Salida en texto, por paso** (pegada en el reporte):
- **research:** perfil (años, tipo de evento, idiomas), fuentes de R1, bajadas y con aporte por idioma, `POOL_GATE.md` (color y métricas), hilos usados, US$ y tiempo;
- **4a–4e** (Flash): US$ y tiempo;
- **ficha:** conteos (hechos, citas, escenas, personas, sacados), US$;
- **escaleta:** intentos y bloqueantes por intento, humano, antagonista, pico (beat), cuántos `a_pantalla`, US$;
- **guion:** palabras, ≈ minutos (2,4 palabras/s, la voz de «MS Narrador»), bloqueantes antes y después de la reparación, citas, palabras por cap (los 7), juez m05, US$. También la fecha del evento según el perfil y si la voz la dice (en F23 no la decía);
- **partición:** los 7 títulos;
- **papel:** `01e_pantalla.md` **entero**, más vueltas, motivos por vuelta, cierre (`sin motivos` / `tope` / `sin progreso`), cortados al cierre y US$ (vigilar c3/g4 de F38e: vueltas gastadas en un `a_pantalla` que el autor descarta);
- **tabla de costos y tiempos por paso** y total;
- **lado a lado con F23** (la misma semilla, solo números): fuentes, métricas de la compuerta, palabras, citas y caps cortos.

**B.5 Comprobar que no corrió nada después del papel:** ni `normalizer_gate`, ni `audio`, ni `m07`, ni fase2a. Pegar la lista de archivos nuevos de `_steps/f39-kyshtym/` y `output/` (este último debe estar vacío para el topic).

## 8. Frenos
- Nada de voz, imágenes, música, fase2a/2b, render, fase3, merge ni `main`.
- **Ningún cambio de prompt** (ficha, escaleta, guion, títulos, papel): se corren los vigentes. Pegar sus md5 y `prompt_version`.
- B no se edita a mano ni se reintenta a mano.
- Nada copiado de `f18-kyshtym-mayak`.
- Escrituras en `data/` **esperadas y declaradas**: `_steps/f39-kyshtym/`, `topics_db.json` (con respaldo), `cost_history.json`. Ninguna otra.
- Si el gasto de la tanda pasa US$ 5,00, se declara con el paso que lo pasó.

## 9. PARADA
`lab/hyperframes/f39/F39_REPORT.md` con: paso 0 (salida del push y resumen del perfil), A.5, B.4, B.5, costos, candado, «lo que queda abierto» entero, procesos vivos (ninguno) y el veredicto íntegro de `revisor-handoff`. Se actualiza `lab/ESTADO_SESION.md` (cabecera, «Para Omar», bloque F39). Commits por parte, con rutas explícitas. **PARADA:** el analista lee el papel y da la nota 1–10 de Fase 1.
