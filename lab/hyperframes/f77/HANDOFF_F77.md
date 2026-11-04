# HANDOFF F77 — gate ES por API · research más rápido · estante de temas · corrida real de 4 semillas
Rama `f11-guion-v4`, base `f63922f` (F76). Aprobado por Omar 2026-11-04 15:42 (D1–D6), 15:51 (V1–V6), 16:02 (estante: research + ficha, en el form, ordenado), 16:05 («poné a CC sin parar, voy a estar desatendido 2 horas»).
**Omar NO está.** No hay preguntas: CC decide lo razonable, lo declara en el reporte, y solo para ante algo irreversible (no hay nada irreversible en esta tanda). Subagentes en paralelo, todos los que el trabajo permita.

## Por qué
1. El gate ES contó Shorts como competencia (Palomares SATURADO por Shorts de 4,5M/3,1M/2,0M, < 70 s) y depende de un proxy lento (>8 s/fetch, 2 pasadas, en fila).
2. Fase 1 tarda ~45 min; el research es 55 %, y R1 solo ~13 min porque los 4 focos van en fila y Pro reintenta 4 veces antes de probar Flash (Kyshtym: 16 Pro + 4 Flash; Wittenoom, 2 corridas: 2 de 4 focos quedan «sin» fuentes).
3. Omar quiere 2+ videos/semana: lanzar varias semillas y elegir después cuál producir (estante).

## Constantes (ninguna nueva sin origen)
| valor | qué | origen |
|---|---|---|
| 180 s | duración mínima para contar como competidor (lo que dura un Short) | estándar: YouTube Shorts dura hasta 3 min (desde oct-2024) |
| 50 | resultados por página de search.list / IDs por videos.list | estándar: máximo de la API de YouTube |
| `YT_LIMIT_ARCHAEOLOGY` | cuántos resultados junta una medida ES | ya existe (`youtube_scanner.py`), el mismo que usa el raspado |
| `relevanceLanguage=es`, `type=video` | filtros de la búsqueda | ya existen en `_api_fallback_*` |
| `ES_SAT_HUECO` 30.000 / `ES_SAT_DISPUTADO` 150.000 / `ES_DECAY_*` | etiqueta | ya existen, **no se tocan** |
| `R1_RETRIES` = 3 | rondas de R1 mientras ningún modelo trae grounding | ya existe (F8b); ahora cuenta rondas de la carrera, no intentos de Pro |
| `WORKERS` = 8 | hilos de research | ya existe (`research_v3.py:46`) |
| workers del gate por API / de la tanda | = cantidad de ítems | regla de Omar: paralelo al máximo (sin número) |
| `ES_GAP_WORKERS` = 3 | queda SOLO para el respaldo por raspado (techo del proxy) | ya existe |

## Etapa A — gate ES por API oficial (D1–D3) · módulos: `script_engine/youtube_scanner.py`, `niche_discoverer.py`, `fase1.py`
- A1. `list_spanish_candidates` (hoy raspado): **primero API** (`search.list` paginado hasta `YT_LIMIT_ARCHAEOLOGY`, luego `videos.list` en lotes de 50 con `contentDetails,statistics,snippet`) → views, fecha → `months`, duración. **Solo entran videos > 180 s.** Mismo shape de salida (`title, views, months, video_id`) + `duration_s`. Si la API falla (403 cuota, red) → el raspado de hoy como respaldo, **también con el filtro > 180 s** (`_parse_length_scrapetube` ya existe; duración desconocida = se cuenta, para no esconder competencia) y queda anotado `source`.
- A2. `niche_discoverer.py:745` (loop ES en fila) y el loop de `ES_GAP_WORKERS` → paralelo con workers = ítems cuando la fuente es API; si cae al raspado, el raspado sigue con su techo de 3.
- A3. Chascada (abierto de F74): la **búsqueda** usa el título sin segmentos entre paréntesis y sin puntuación al final (`:;,.-`); el título del topic queda como Omar lo escribió.
- A4. Medir el uso de cuota por medida en el log (unidades = 100 × páginas + 1 × lotes).
- **Contrato A (corrida real, US$ ≈ 0, solo el juez Gemini):** medir «Palomares 1966» por la cadena nueva. Esperado (datos de vidIQ del analista, hoy): el competidor más pesado relevante es **A toda leche «4 BOMBAS NUCLEARES cayeron en España», video `4VgrwqGvIuc`, 10:47, ~212.637 views, publicado 2026-10-25 → peso 1,0 → SATURADO**. Otros largos ES: DMAX `_dabgyhU3tQ` 104K (dic-2021), SLICE Iberia `0d9xjzcx-fc` 63K (sep-2025), Herrera Plaza `lxQeaNdeaZI` 65K (ene-2021), Movistar `vduGqR001KM` 56K (abr-2021). Los Shorts de 4,5M (`IUpaoH-lvkI`) y 2,0M (`Yvo7kps24Fo`) **no** deben aparecer. **Salida en texto:** tabla de candidatos (id, título, duración, views, meses, peso, ¿relevante según el juez?) + label + unidades gastadas. Si no da SATURADO, decir por qué (juez, fecha, búsqueda) y seguir: no es PARADA.

## Etapa B — research más rápido (V1, V2, V3, V5) · módulo: `researcher_steps/research_v3.py`
- B1 (V1). R1: los 4 `DISCOVERY_FOCOS` en paralelo; después las pistas que falten, también en paralelo. La caché `_r1_cache.json` se escribe con candado (un solo escritor).
- B2 (V2). Carrera por foco: en cada ronda, **Pro con búsqueda y Flash con búsqueda a la vez**. Si los dos traen grounding, se suman los chunks (dedupe por URL, como hoy `_dedupe_ground`); si uno solo, ese; si ninguno, otra ronda (Pro con `R1_FORCE_SEARCH` + Flash), hasta `R1_RETRIES` rondas. Se borra la cadena vieja «Pro ×4 en fila → Flash» y sus tests (no se apaga con bandera). `via` pasa a `pro|flash|ambos|sin`.
- B3 (V3). R3: las partes de un mismo documento en paralelo (hoy F07 de Kyshtym, 4 partes en fila).
- B4 (V5). Reloj por sub-paso en el log y en `01_v3_costos.json`: gate, R1 (por foco y ronda), R2, R3 (por documento), pool. Así la próxima tabla de tiempos no sale de mtimes.
- **Salida en texto:** tests con mocks (focos en paralelo; carrera: solo Pro / solo Flash / ambos / ninguno hasta `R1_RETRIES`; caché sin carreras) y la tabla de tiempos real de la Etapa D.

## Etapa C — estante de temas (V6) · módulos: `fase1.py` (form), `fase1_5.py`, `run_pipeline.py`
- C1. Form: modo nuevo **«D · Tanda de semillas»** con el marcador de texto libre de F74 (`accept='text'`): varios títulos separados por «;» o salto de línea. Cada título pasa por el mismo camino que el modo C (registro manual + gate de la Etapa A), **todos en paralelo**, sin preguntas: VACIO/HUECO/DISPUTADO siguen; SATURADO queda registrado en el estante con ⚠ y **sin research** (no se gasta).
- C2. Los que siguen corren `fase1_5 --topic <tid> --batch --hasta-ficha` **en paralelo** (un subproceso por tema): research v3 → compuerta del pool → ficha, y paran (exit 0). Compuerta del pool roja = queda en el estante con ⚠, sin ficha (como hoy, no se paga).
- C3. «En estante» se **deduce del disco**, sin estado nuevo: topic con `ficha_caso.json` y sin `01a_escaleta.json` (o SATURADO / compuerta roja sin research). `etapa_de` devuelve `estante` para esos.
- C4. Form al arranque, menú nuevo **«E · Estante (N)»**, primero en la lista cuando N > 0. Body = una tabla por tema, **ordenada**: gate VACIO/HUECO → DISPUTADO → SATURADO; dentro, más `elegibles_humano` primero; ⚠ al final. Columnas: título · gate (label + competidor más pesado: título, views, meses) · pool (datos / citas / personas con nombre / eventos con fecha / compuerta) · ficha (título, n.º de hechos, escenas, personas; las 3 primeras escenas en una línea) · US$ gastado. Elegir uno → `run_pipeline --topic <tid>` sigue desde la escaleta hasta la compuerta de narración, como hoy. Los demás no se tocan.
- **Salida en texto:** el body del menú E con los temas de la Etapa D, tal cual lo vería Omar.

## Etapa D — corrida real, desatendida (la prueba de todo)
Lanzar por el camino del form (o su equivalente por línea de comando, declarado) la tanda de 4 semillas:
1. `Palomares 1966: el Proyecto Indalo y los vecinos usados como cobayas`
2. `Síndrome del aceite tóxico (colza) 1981`
3. `Accidente radiológico de Goiânia 1987`
4. `Tragedia del camping Los Alfaques 1978`
Hasta el estante (research + ficha). US$ esperado ≈ 1,9 por tema que pase el gate (se informa después, sin tope). **Salida en texto:** (a) tabla del gate de los 4 (label, competidor, unidades API); (b) tabla de tiempos por sub-paso de cada tema (B4) contra Kyshtym (R1 ~13 min, R3 ~5,8, research 22,6); (c) R1 por foco: `via` y n.º de URLs reales, comparado con Wittenoom (2 de 4 «sin»); (d) límites de velocidad: cuántos 429/reintentos de Gemini/OpenAI con 4 temas a la vez; (e) el body del menú E; (f) US$ por tema. **No se corre nada después de la ficha.**

## Chascadas
- `_perfil` de `audio_master` → nombre público (`perfil`), y los 3 que lo importan (abierto de F76).
- `DECISIONES.md`, con fecha 2026-11-04: master aprobado por oído (15:57); D1–D6; V1–V6; estante = research + ficha, en el form, ordenado (16:02).

## Reglas fijas
- Lo viejo se borra con sus tests (cadena R1 en fila, gate sin filtro de duración como camino primario). Suite rápida verde + las 3 heredadas; `mapa_modulos --check` 0 fallas.
- No tocar Wittenoom (mp4 publicado md5 `1fb47948e43951d4c009e13c0131d184`) ni los topics existentes. Nada de render, voz, fotos.
- La llave de la API vive en `config.py` (fuera de git): no se imprime en logs ni reportes.
- Reporte `lab/hyperframes/f77/F77_REPORT.md` con la salida en texto de A, B, C y D, «abierto» completo y veredicto íntegro del `revisor-handoff`. `ESTADO_SESION.md` al día. Commit y push en la rama, archivo por archivo (no `git add -A`).
- **PARADA al final** (estante lleno; Omar elige al volver).
