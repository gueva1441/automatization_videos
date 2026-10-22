# HANDOFF F7 — Research v3: leer documentos, no resumir Google

**Fecha:** 2026-10-21 · **Analista:** chat proyecto · **Ejecuta:** CC (sesión nueva) · **Gate:** Omar
**Rama:** `f7-research-v3` desde `f6-guion-v3` (último commit de F6c, `7ec2025` o posterior). Sin merge a `main`.
**Antes de empezar:** leer este archivo completo y `lab/hyperframes/f6/HANDOFF_F6_guion_v3.md` §2.1 (testimonios) y §5 (frenos). No hace falta leer los reportes F6a–F6c.

---

## 0. Por qué (la raíz, no el remiendo)

Guion v3 (F6) funciona: con el **mismo pool** que v2, el gancho, el ritmo y el pico mejoraron (7 → 7.5). Pero la narración inventa, repite y se desvía, y cada arreglo era un validador más. Causa: **el pool es pobre**.

Hoy el research (`topic_researcher._research_seed_deep`) son 4 preguntas a Gemini Pro con Google Search (técnico, humano, misterio, visual) que devuelven **texto resumido de snippets**: 8 fuentes citadas por nombre sin URL, ninguna leída. Pool de Orleans: 26 k caracteres, 2 citas verificadas, 1 humano con 2 datos.

Prueba de lo que se pierde: en F6c, CC bajó para verificar el informe de la ACLU *Abandoned & Abused* → `data/scripts/_steps/ba6c3cac-f6v3/fuentes/aclu_abandoned_and_abused.txt`, **566 k caracteres, 1,300 testimonios**. Ahí están, literales, citas que el pool no tenía o que la verificación por Google marcó "sin verificar" («It was like a concentration camp», «he left us there to die», «no food, no water, lights, or medical attention»). Y la contaminación (Lenore Burnley / Chad Joseph, una nota ACLU de 2026 sobre Trinidad) entró porque nadie leyó la página.

**Research v3 = descubrir fuentes → bajar documentos → extraer el pool leyendo → verificar por texto.** Un dato sin documento no entra.

---

## 1. Criterio de éxito

1. Pool de Orleans v3-research: ≥ 5× el actual en `datos`, ≥ 15 citas de testigos **con nombre y documento**, cronología con horas donde el documento las tenga, 100 % de ítems con `doc_id` + posición.
2. Correr Orleans por la tubería v3 (escaleta → guionista → editor) **sin tocar F6**, y que la narración suba sola. Si llega a 8.5–9 por lectura del analista y de Omar, la raíz era el research. Si no, el problema es el guionista y se ataca ahí.
3. Costo por tema ≤ US$ 2.5 (hoy ≈ 1.5–2).

---

## 2. Arquitectura

```
seed ─► R1 descubrimiento de fuentes (Pro + search, EN + idioma local) ─► fuentes.json (URL, tipo, año, por qué)
     ─► R2 descarga (HTML/PDF → txt) a _steps/<topic>/fuentes/ ─► fuentes/*.txt + manifest (hash, bytes, idioma)
     ─► R3 extracción por documento (Pro contexto largo) ─► pool_doc_<id>.json (cada ítem con doc_id + cita literal + offset)
     ─► R4 merge + dedupe + canon + contaminación ─► evidence_pool (mismo contrato que hoy + campos nuevos)
     ─► R5 verificación por texto (gratis) ─► estado verificada / sin_verificar por ítem
     ─► 4b canonical · 4c meta · 4d summary · 4e visual canon (SIN CAMBIOS, reciben el pool nuevo)
```

### R1 — Descubrimiento de fuentes (reemplaza las 4 queries de datos)
Una o dos llamadas Pro + Google Search que devuelven **documentos, no hechos**. Prompt en el idioma del seed, pero exige buscar **en inglés y en el idioma del lugar del evento**. Salida JSON:
```json
{"fuentes":[{"url":"…","titulo":"…","tipo":"informe_oficial|fallo_judicial|prensa_epoca|prensa_posterior|documental|libro|testimonio|academico|foia","anio":2006,"idioma":"en","por_que":"…","prioridad":1}]}
```
Tipos que debe cubrir (si existen): informe oficial o de ONG, fallo o expediente judicial, prensa local **de los días del evento**, prensa de aniversario/seguimiento, documental o transcripción, libro o capítulo, historia oral/testimonios, FOIA/archivo. Mínimo 8, máximo 20. Las URLs vienen del grounding (`_grounding` de `verify_quotes.py` ya extrae los chunks reales); una URL que no esté en el grounding se descarta.

### R2 — Descarga
Para cada fuente por prioridad hasta 10 bajadas OK: `requests` con UA de navegador, timeout 20 s, `resolve_redirect` (ya existe); HTML → texto con `trafilatura` (instalar) o fallback `readability`/BeautifulSoup; PDF → `pdfplumber` (instalado) con fallback `pypdf`. Guardar `fuentes/<slug>.<ext>` + `<slug>.txt` + `fuentes/manifest.json` (url, hash, bytes, idioma detectado, fecha de descarga, ok/error). Paywall o 403 → se anota y se sigue. Límite 300 k caracteres por documento (recortar por secciones, no por la mitad de un párrafo).

### R3 — Extracción por documento
Una llamada Pro por documento (contexto largo; si > 150 k tokens, por mitades con solape). Mismo contrato de ítems que `evidence_pool.py` (`datos`, `cronologia`, `lugares`, `citas`, `personajes`) **más**:
- `doc_id`, `cita_literal` (el fragmento del documento del que sale el ítem, ≤ 300 caracteres, en el idioma original), `offset` (posición en el txt), `idioma`.
- Citas: `autor`, `rol`, `testigo: true/false`, `presente_en`, `texto_original` + `texto_es` (traducción natural, fiel; la pantalla puede mostrar el original con la traducción).
- Cronología: `fecha`, `hora` si el documento la da, `lugar_id`.
Regla al modelo: **solo lo que está en este documento**; nada de conocimiento propio. Cada ítem debe poder encontrarse con `find_literal(cita_literal, txt)`; el que no, se descarta y se registra.

### R4 — Merge
Reusar `evidence_pool.merge`, `canonical_figures`, `acting_filter`, `unrelated_lines`, `geocode`. Nuevo:
- Dedupe por hecho entre documentos: mismo valor + misma entidad → un ítem con `docs: [a, b]` (dos fuentes = más confianza; se guarda `n_fuentes`).
- Contaminación: ítem cuya `fecha` > año del evento + 20, o cuyo documento no nombra el lugar/evento en sus primeros 5 k caracteres → fuera con motivo (`_descartados`).
- Cifras: `cifras_canonicas` con la de la fuente oficial primero (informe/fallo) y las demás como "estimación de <fuente>".
- Personajes: `testigo`, `presente_en`, `n_citas`; el guionista elige humano entre los que tengan ≥ 3 citas o ≥ 3 datos propios.

### R5 — Verificación
`verify_literal` (ya existe en `verify_quotes.py`) contra los txt bajados: es gratis y determinista. `verify_testimonios` con Google queda solo como respaldo para citas cuyo documento no se pudo bajar. Estados: `verificada` (literal en txt), `verificada_parcial` (≥ 5 palabras consecutivas), `sin_verificar`. El guionista no nombra autores de citas `sin_verificar` (regla ya existente en F6b).

### Contrato de salida
`evidence_pool` conserva todas las claves actuales; los campos nuevos son aditivos. `step_4b/4c/4d/4e`, `m01a_escaleta`, `m01b_guionista`, `m03`, `gfx_pool` **no se tocan**; `format_pool` de `evidence.py` es freno (la escaleta ya formatea lo suyo). Si algo río abajo necesita `cita_literal` o `texto_original`, es propuesta, no cambio.

---

## 3. FRENOS
- No tocar: `evidence.py`, `step_4b/4c/4d/4e`, `m01a_escaleta`, `m01b_guionista`, `m01c_editor`, `m03_visual`, `fase*`, `gfx_*`.
- El camino viejo (`_research_seed_deep` con 4 ángulos) sigue existiendo detrás de `RESEARCH_V3=0`; v3 es el default solo para seeds nuevos y para la re-corrida de Orleans.
- Nada de scraping agresivo: 1 request por URL, UA honesto, respetar 403/429, sin login, sin bypass de paywall.
- Nunca inventar una URL: solo las del grounding.
- `topics_db.json`: Orleans v3-research entra como topic nuevo (`ba6c3cac-f7r3`), copia de f6v3 con el pool nuevo; f5v2 y f6v3 no se tocan.

---

## 4. Fases para CC

| Fase | Qué | Horas | Entrega |
|---|---|---|---|
| F7a | R1 descubrimiento + R2 descarga, con Orleans como caso: `fuentes.json`, `fuentes/manifest.json`, ≥ 8 documentos bajados (ACLU completo, HRW 2005, DOJ 2010 findings letter, BBC 2006, Times-Picayune/NOLA de la semana del 29-ago-2005, The Lens 2025, Toledo Blade 2005, fallo Waganfeald/Kunkel si está público) | 3 | `F7a_fuentes.md`: tabla url/tipo/año/bytes/ok |
| F7b | R3 extracción por documento + R4 merge/contaminación + R5 verificación por texto; pool de Orleans v3-research con métricas vs el pool f6v3 (datos, citas verificadas, testigos con ≥ 3 citas, cronología con hora) | 4 | `F7b_pool.md` + `00_pool_v3.json` |
| F7c | Correr Orleans por la tubería v3 **sin cambios en F6**: escaleta → guionista → editor; `compara_orleans_v3r.html` con 3 columnas: v2 F5d · v3 pool viejo (F6c) · v3 pool nuevo; métricas del juez al lado; revisor; commit | 2 | PARADA: analista y Omar leen |

Total ≈ 9 h, 2 sesiones (F7a–b, F7c). Commit wip antes de cada compactación; `ESTADO_SESION.md` al día. Modelo: F7a Sonnet; F7b (prompt de extracción y reglas de contaminación) Opus; F7c Sonnet.

## 5. Pruebas
- Unit: parser de `fuentes.json` descarta URLs fuera del grounding; HTML/PDF → txt con muestras fijas; cada ítem extraído tiene `cita_literal` encontrable (`find_literal`); dedupe entre documentos; contaminación por fecha y por lugar (caso Burnley/Trinidad como fixture); `cifras_canonicas` elige la oficial.
- Regresión: `RESEARCH_V3=0` → salida byte-idéntica a hoy para un seed de prueba.
- Integración: pool v3 → `step_4b/4c/4d/4e` sin error → `m01a_escaleta` sin error.

## 6. Riesgos
1. **Paywalls / 403** (prensa de época) → se anota; Wayback Machine (`web.archive.org`) como segundo intento permitido para URLs públicas; si no, se sigue sin esa fuente.
2. **Documentos enormes** (ACLU 566 k) → por mitades con solape de 5 k; costo ≈ US$ 0.5 por documento grande.
3. **Idioma**: la extracción devuelve `texto_original` + `texto_es`; el candado literal de m01b trabaja sobre `texto_es`, así que la traducción se fija en el pool una sola vez (no la rehace el narrador).
4. **Más datos ≠ mejor guion** automáticamente: la escaleta ya filtra (un dato central por beat, humano con ≥ 3 datos). Si el pool crece a 300 ítems, la escaleta recibe un resumen por documento + los ítems de personajes/citas completos (ajuste en `m01a_escaleta` solo si hace falta, como propuesta).
5. **Costo**: 1–2 llamadas R1 + ~10 lecturas R3 ≈ US$ 1.5–2.5. Medir en F7b.

## 7. Después
Si Orleans v3-research sube a 8.5+: siguiente tema nuevo con research v3 desde la semilla; luego Imágenes (ANALISIS_imagenes §0), deuda gfx (BACKLOG §0), primer video completo, merge a `main`.
