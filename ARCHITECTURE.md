# ARCHITECTURE — Motor de guion (rediseño SRP)

**Versión:** v1 (2026-05-02)
**Estado:** spec cerrada, lista para implementar módulo por módulo.
**Alcance:** SOLO videos LONG. SHORT mantiene su flujo actual 1-shot.
**Archivos a reescribir:** `topic_researcher.py` + `script_generator.py`. Nada más.

---

## 1. Resumen

Cada llamada Gemini hace UNA destilación. Todo módulo recibe: el pool original etiquetado por bloque-fuente + los outputs de los módulos anteriores, ya cerrados como string fijo. Imposible auto-contradicción. Validación cruzada al final, juez separado del escritor.

---

## 2. Anti-patrones prohibidos

Tomados del diagnóstico del motor actual. Si una propuesta de implementación viola alguno de estos, se rechaza sin discusión:

1. **Single Prompt Overloading** — pedir N tareas en 1 llamada con reglas cruzadas entre ellas.
2. **Reglas que se contradicen en el mismo turno** — pedir "X hereda de Y" cuando ambos se escriben en simultáneo.
3. **Validación tardía como parche** — reescribir output ya generado en vez de prevenirlo en el input. El validador audita, NO reescribe.
4. **Profile assignment ciego** — elegir `art_profile` viendo solo el title del cap, sin bullets/canonical/facts.

---

## 3. Diagrama de flujo

```
niche_discoverer  (intacto)
        ↓ seeds
topic_researcher_light  (1 llamada Pro+grounding por seed; 4 campos)
        ↓ topic_light
topic_validator  (intacto)
        ↓
csv_exporter  →  CSV de selección humana
        ↓                                    ← CHECKPOINT 1 (selección de topics)
        │ (solo topics aprobados)
        ↓
[00] sintetizador
       sub-paso 4a: facts + sources etiquetados  (Flash)
       sub-paso 4b: canonical_subject_description  (Flash)
       sub-paso 4c: meta narrativa                 (Flash)
       sub-paso 4d: research_summary masivo        (Flash)
        ↓ topic completo (deep)
[01a] estructurador     →  skeleton 7 caps (title + bullets)            (1 Flash)
        ↓
[01b] narrador          →  narración cap-por-cap + humanizer phrases    (5 Flash)
        ↓
[03]  extractor visual   →  prompts EN + narration_anchor por imagen     (5 Flash, 1 por cap)
                            (m03 elige art_profile por imagen — image-level desde FASE 1)
        ↓
[04]  sanitizador        →  regex puro + Flash semántico (Veo/Flux)      (regex + 1 Flash)
        ↓
[05]  validador-juez     →  PASS → final_ready_script  |  FAIL → errors[] con retry_step  (1 Flash)
        ↓ (PASS)
fase2a  (intacto — contrato sagrado)
```

**Llamadas Gemini totales por LONG:** 3 (angle queries Pro) + 4 (sub-pasos módulo 00) + 1 (01a) + 5 (01b) + 5 (03) + 1 (04) + 1 (05) = **20 llamadas**.
**Costo estimado:** ~$0.033/video. Casi todas Flash; las 3 Pro son las angle queries con grounding.
**Nota FASE 5:** módulo 02 (asignador de profiles) fue archivado en `script_engine/_archived/m02_profiles.py`. Su responsabilidad pasó a m03 image-level.

---

## 4. Política de persistencia

```
data/scripts/{topic_id}.json                     ← final, contrato sagrado, lo que fase2a consume
data/scripts/_steps/{topic_id}/00_synthesis.json
data/scripts/_steps/{topic_id}/01a_skeleton.json
data/scripts/_steps/{topic_id}/01b_narration.json
data/scripts/_steps/{topic_id}/03_visual.json
data/scripts/_steps/{topic_id}/04_sanitized.json
data/scripts/_steps/{topic_id}/05_validation.json
```

**Decisión clave:** intermedios en directorio sibling `_steps/`, NO dentro de `{topic_id}/`. Razón: mantener `data/scripts/{topic_id}.json` como path canónico y dejar fase2a literalmente sin cambios. (Desviación menor del BACKLOG; reversible si molesta.)

**Reglas:**
- Cada módulo escribe su JSON a disco antes de retornar. Si crashea, el siguiente puede reanudar leyendo del paso anterior.
- Si el módulo 05 falla con `retry_step="03"`, se re-ejecuta el módulo 03 leyendo `01a_skeleton.json` + `01b_narration.json` + el topic completo como input. No hace falta rehacer nada antes.
- `_steps/` es opcional para inspección humana / debugging. La pipeline puede borrarlo después de un PASS exitoso (config flag, default: conservar).

---

## 5. Política de errores

Cuando módulo 05 emite `status="FAIL"`, devuelve `errors[]` con esta forma:

```json
{
  "retry_step": "03",
  "scope": "image",
  "chapter": 4,
  "img_index": 5,
  "reason": "narration_anchor menciona 'Bronwen Duke' pero la narración del cap4 no contiene ese nombre",
  "expected": "narration_anchor debe ser substring exacto de chapters[3].narration",
  "actual": "Bronwen Duke perdió a sus padres..."
}
```

**Campos:**
- `retry_step` — qué módulo re-ejecutar. Valores: `"00"`, `"01a"`, `"01b"`, `"03"`, `"04"`. Nunca `"05"` (no se reintenta a sí mismo). El valor `"02"` quedó deprecado en FASE 5 (módulo 02 archivado).
- `scope` — `"global"` | `"chapter"` | `"image"`. Indica granularidad del problema.
- `chapter` — int 1-7 o null si scope=global.
- `img_index` — int o null. Index dentro de `image_prompts[]` del cap.
- `reason` — humano legible, una línea.
- `expected` — regla violada en términos del contrato.
- `actual` — fragmento del output que la viola (truncado a 200 chars).

**Política de retry:** máximo 2 reintentos del mismo `retry_step`. Tercer fallo → escalación al usuario con todos los `errors[]` acumulados.

---

## 6. Módulos — contratos JSON cerrados

### 6.1. `topic_researcher_light` (pre-checkpoint)

**Propósito:** alimentar el CSV de selección humana sin gastar la deep research. Hoy se gasta ~$0.020/topic; pasa a ~$0.005/topic.

**Implementación:** simplificar `_research_seed` actual (NO de cero). Reusa toda la infra de Pro+grounding y la sanitización de search_keyword.

**INPUT:**
```json
{
  "seed_id": "string",
  "seed_title": "string",
  "seed_description": "string",
  "niche": "string"
}
```

**OUTPUT:**
```json
{
  "topic_id": "uuid",
  "seed_id": "string",
  "video_title": "string (≤62 chars)",
  "hook": "string (1-2 frases impactantes)",
  "angle": "string (técnico|humano|misterio|otro)",
  "virality_score": "int 1-10",
  "search_keyword": "string sanitizada",
  "status": "light_researched"
}
```

**Llamadas Gemini:** 1 (Pro + Google Search grounding).
**Costo:** ~$0.005/topic.
**Criterio de éxito:** los 6 campos no-vacíos, `search_keyword` pasa el sanitizer, `virality_score ∈ [1,10]`.

---

### 6.2. Módulo 00 — sintetizador (deep research)

**Propósito:** generar el topic completo solo para topics aprobados en CSV. Reemplaza `_synthesize_deep_research` monolítico actual.

**Estructura interna:** 3 angle queries existentes (mantienen `_research_angle` + `_build_angle_query_prompt` + `DEEP_RESEARCH_ANGLES`) + 4 sub-pasos secuenciales Flash.

#### 6.2.0. Angle queries (pre-existentes)

**INPUT:** seed + topic_light.
**OUTPUT:** `pool_etiquetado`:
```json
{
  "bloque_tecnico":  "<texto crudo del angle query 1>",
  "bloque_humano":   "<texto crudo del angle query 2>",
  "bloque_misterio": "<texto crudo del angle query 3>"
}
```
**Llamadas Gemini:** 3 (Pro + grounding).

#### 6.2.4a. Sub-paso `sintetizar_facts_y_sources`

**INPUT:** `pool_etiquetado` (todos los bloques).

**OUTPUT:**
```json
{
  "verified_facts": [
    {
      "fact": "Blue-grey crocidolite asbestos tailings piles surrounding Wittenoom Gorge.",
      "source_block": "tecnico"
    }
  ],
  "sources": [
    "Hills B, 1989, Blue Murder. South Melbourne: Sun Books, Macmillan"
  ]
}
```

**REGLA:** cada fact DEBE traer `source_block` indicando de qué bloque angular proviene. Esto rompe el bug 1943↔1937: cada cifra/fecha queda etiquetada con su origen, imposible mezclarlas inadvertidamente.

**Cambio respecto a hoy:** el JSON Wittenoom actual tiene `verified_facts` como list[str]. El nuevo formato es list[dict]. Es un cambio retrocompatible para fase2a (que ignora `verified_facts` — es metadata).

**Llamadas Gemini:** 1 (Flash).

#### 6.2.4b. Sub-paso `sintetizar_canonical`

**INPUT:** `pool_etiquetado` + `verified_facts` (cerrado, como string fijo).

**OUTPUT:**
```json
{
  "canonical_subject_description": "string (200-400 chars, con geo+era literales heredados de verified_facts)"
}
```

**REGLA:** cualquier referencia geográfica o temporal en `canonical_subject_description` DEBE existir literal en algún `verified_fact`. El prompt enumera los facts y prohíbe inventar nuevos.

**Llamadas Gemini:** 1 (Flash).

#### 6.2.4c. Sub-paso `sintetizar_meta_narrativa`

**INPUT:** `pool_etiquetado` + `verified_facts` + `canonical_subject_description` (todo cerrado).

**OUTPUT:**
```json
{
  "video_title": "string (≤62 chars)",
  "hook": "string",
  "mystery": "string",
  "reveal": "string",
  "angle": "string",
  "search_keyword": "string sanitizada",
  "virality_score": "int 1-10"
}
```

**REGLA:** cualquier fecha/cifra que aparezca en `hook` o `mystery` o `reveal` DEBE existir en `verified_facts`. El prompt enumera facts y prohíbe números nuevos.

**Llamadas Gemini:** 1 (Flash).

#### 6.2.4d. Sub-paso `sintetizar_research_summary`

**INPUT:** `pool_etiquetado` + `verified_facts` + `canonical` + meta (todo cerrado).

**OUTPUT:**
```json
{
  "research_summary": "string (1500-3000 chars)"
}
```

**REGLA:** NO redundar facts ya capturados en `verified_facts`. Aporta contexto narrativo, no datos.

**Llamadas Gemini:** 1 (Flash).

#### 6.2.OUTPUT consolidado del módulo 00

```json
{
  "topic_id": "uuid",
  "topic_title": "string",
  "video_title": "string",
  "discovery_mode": "string",
  "verified_facts": [{"fact": "...", "source_block": "..."}],
  "sources": ["..."],
  "canonical_subject_description": "string",
  "hook": "string",
  "mystery": "string",
  "reveal": "string",
  "angle": "string",
  "search_keyword": "string",
  "virality_score": 1,
  "research_summary": "string",
  "_pool_etiquetado": { "bloque_tecnico": "...", "bloque_humano": "...", "bloque_misterio": "..." }
}
```

**Nota:** `_pool_etiquetado` se persiste en `00_synthesis.json` para auditoría pero NO se propaga a módulos posteriores (no lo necesitan).

---

### 6.3. Módulo 01a — estructurador

**Propósito:** generar skeleton de 7 capítulos. SIN narración, SIN profiles. Reemplaza la parte estructural de `_generate_long_outline`.

**INPUT:** output del módulo 00 completo.

**OUTPUT:**
```json
{
  "topic_id": "uuid",
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Gancho",
      "role": "hook",
      "bullets": ["bullet 1", "bullet 2", "..."],
      "duration_seconds": 45,
      "render_engine": "veo"
    },
    {
      "chapter_number": 2,
      "title": "string",
      "role": "development",
      "bullets": ["..."],
      "duration_seconds": 75,
      "render_engine": "flux"
    },
    "// ... caps 3-6 igual que cap2 ...",
    {
      "chapter_number": 7,
      "title": "Revelación + Outro",
      "role": "reveal_outro",
      "bullets": ["..."],
      "duration_seconds": 45,
      "render_engine": "veo"
    }
  ]
}
```

**REGLAS:**
- Exactamente 7 caps. cap1 y cap7 → `render_engine="veo"`. cap2-6 → `render_engine="flux"`.
- `bullets[]`: 4-7 bullets por cap, frases nominales con cifras/fechas concretas tomadas de `verified_facts`.
- `role`: `"hook" | "development" | "reveal_outro"`. cap1=hook, cap7=reveal_outro, resto=development.
- `duration_seconds` indicativo, lo refinará 01b según largo de narración real.

**Llamadas Gemini:** 1 (Flash).

---

### 6.4. Módulo 01b — narrador

**Propósito:** narración cap-por-cap + elección automática de humanizer phrases. Reemplaza la parte narrativa de `_generate_long_outline`.

**INPUT:** output del módulo 00 + skeleton del 01a.

**OUTPUT:**
```json
{
  "topic_id": "uuid",
  "chapters": [
    {
      "chapter_number": 1,
      "narration": "string (300-800 chars)"
    },
    "// ... cap2-6 narration 800-1800 chars ...",
    {
      "chapter_number": 7,
      "narration": "string (400-900 chars)"
    }
  ],
  "humanizer_phrases": ["frase 1", "frase 2", "frase 3"]
}
```

**REGLAS:**
- 5 llamadas Flash separadas, una por cap. cap1 y cap7 con prompts especiales (hook/outro). cap2-6 prompt común.
- Cada llamada recibe: topic completo + skeleton completo + narraciones de caps anteriores ya cerradas como string fijo. Imposible repetir frases.
- `humanizer_phrases`: exactamente 3 frases cortas (≤40 chars), elegidas por una sub-llamada Flash con criterios explícitos: una expresa shock, otra empatía, otra llamado a no olvidar. Se congelan en output.
- Auditoría humana opcional vía CSV final (no bloqueante).

**Llamadas Gemini:** 5 (cap-por-cap) + 1 (humanizer) = 6 totales. Por simplicidad cuento "5 Flash" en el diagrama agrupando humanizer dentro del cap1 si conviene.

---

### 6.5. Módulo 02 — DEPRECADO

**Estado:** archivado en FASE 5 (`script_engine/_archived/m02_profiles.py`).

**Razón:** la responsabilidad de elegir `art_profile` cap-level resultó ser un anti-patrón #4 (profile assignment ciego que m03 después tenía que overridear por imagen). En FASE 1 (chat 15) m03 pasó a elegir `art_profile` por imagen sin defaults. m02 quedó funcionalmente redundante. FASE 5 (chat 16) lo archivó.

**Backward-compat:** topics que tengan `02_profiles.json` en disco siguen funcionando. m05 lo lee defensivo si existe; si no, usa el `art_profile` image-level de m03.

---

### 6.6. Módulo 03 — extractor visual

**Propósito:** generar `image_prompts[]` en inglés con `narration_anchor` explícito. Reemplaza `_generate_image_prompts_for_long_chapter`.

**INPUT:** output del 00 + skeleton + narración. (Desde FASE 5 ya no consume m02.)

**OUTPUT:**
```json
{
  "topic_id": "uuid",
  "chapters": [
    {
      "chapter_number": 1,
      "image_prompt": "A 1960s doctor, middle-aged...",
      "video_prompt": "Slow push in, ambient dust...",
      "subject_ref": "main_subject",
      "narration_anchor": "Más de 2,000 perdieron la vida en Wittenoom..."
    },
    {
      "chapter_number": 2,
      "image_prompts": [
        {
          "prompt": "string (EN, 150-300 chars)",
          "art_profile": "INDUSTRIAL",
          "subject_ref": "main_subject",
          "emotional_rank": "R1",
          "narration_anchor": "string (substring exacto de la narración de este cap)"
        }
      ]
    }
  ]
}
```

**REGLAS DE GENERACIÓN:**
- caps veo (1, 7): 1 `image_prompt` + 1 `video_prompt` + 1 `narration_anchor` global del cap.
- caps flux (2-6): `image_prompts[]` con 7-10 items. Cada item con `narration_anchor` = substring exacto de `chapters[N].narration`.
- `art_profile` se elige por imagen sin defaults cap-level (FASE 1, chat 15). Cada imagen recibe el `art_profile` que mejor ajusta a su `narration_anchor` específico. Anti-patrón #4 ("profile assignment ciego") cerrado.
- `emotional_rank` ∈ `{"R1", "R2", "R3"}`. R1 = pico emocional, R3 = relleno descriptivo.
- 1 llamada Flash por cap (5 totales para caps intermedios + 2 para caps veo si se separan, o 5 totales si se agrupan veo; la decisión queda libre al implementar).

**Llamadas Gemini:** 5 (Flash).

---

### 6.7. Módulo 04 — sanitizador

**Propósito:** limpiar prompts contra blocklist Veo/Flux + leak de metadata. Reemplaza `_auto_fix_blocklist_violations` + `sanitize_metadata_leak`.

**Estrategia dos fases:**

#### 6.7.1. Fase regex (offline, gratis, atrapa ~70%)
- Patrones precompilados contra: nombres propios reales que no son del topic, marcas, IPs de personas vivas, leaks de "as an AI...", "I cannot...", URLs, emails, tags HTML.
- Reemplaza match por placeholder neutro y loguea cada hit.

#### 6.7.2. Fase Flash semántica (atrapa edge cases)
- 1 sola llamada Flash con TODOS los prompts del video como input batch.
- Output: list[{prompt_id, original, sanitized, reason}].
- Solo modifica los prompts que violan blocklist semántica (gore implícito, sexo implícito, copyright). Devuelve los limpios sin tocar.

**INPUT:** output del 03.

**OUTPUT:**
```json
{
  "topic_id": "uuid",
  "chapters": [ "// estructura idéntica al 03 pero con prompts saneados //" ],
  "_sanitization_log": [
    {
      "chapter": 4,
      "img_index": 2,
      "phase": "regex|flash",
      "before": "string (truncado 100 chars)",
      "after": "string (truncado 100 chars)",
      "rule": "blocklist_violence_implicit"
    }
  ]
}
```

**Llamadas Gemini:** 1 (Flash).

---

### 6.8. Módulo 05 — validador-juez

**Propósito:** cross-check final narración↔prompt. Es JUEZ, NO ESCRITOR.

**INPUT:** output del 04.

**REGLAS DE VALIDACIÓN:**
1. **Estructura:** 7 caps, render_engine correcto por cap, todos los campos requeridos del contrato presentes.
2. **narration_anchor:** cada `narration_anchor` debe ser substring exacto de la `narration` del cap correspondiente. Validación determinística pre-Flash, NO se le pide a Gemini.
3. **Coherencia semántica:** cada `prompt` describe escena consistente con su `narration_anchor`. Esto SÍ se pide a Flash, con criterio explícito: si el anchor menciona persona/lugar/objeto X, el prompt debe representar X.
4. **Profile coherente:** `art_profile` por imagen tiene sentido vs `narration_anchor`.
5. **Sin leaks:** prompts en EN puro, sin Spanish, sin metadata leak.

**OUTPUT (caso PASS):**
```json
{
  "status": "PASS",
  "final_ready_script": {
    "topic_id": "uuid",
    "video_type": "long",
    "prompt_protocol_version": "v2",
    "video_title": "string",
    "chapters": [ "// schema exacto de fase2a (ver §7) //" ],
    "humanizer_phrases": ["...", "...", "..."],
    "// metadata trazable (no consumida por fase2a):",
    "verified_facts": [...],
    "sources": [...],
    "research_summary": "string",
    "canonical_subject_description": "string",
    "discovery_mode": "string",
    "word_count": 1234,
    "total_veo_chapters": 2,
    "total_flux_chapters": 5,
    "created_at": "ISO timestamp"
  }
}
```

**OUTPUT (caso FAIL):**
```json
{
  "status": "FAIL",
  "errors": [
    {
      "retry_step": "03",
      "scope": "image",
      "chapter": 4,
      "img_index": 5,
      "reason": "narration_anchor menciona 'Bronwen Duke' pero la narración del cap4 no contiene ese nombre",
      "expected": "narration_anchor debe ser substring exacto de chapters[3].narration",
      "actual": "Bronwen Duke perdió a sus padres..."
    }
  ]
}
```

**Llamadas Gemini:** 1 (Flash) + validaciones determinísticas locales (regex/substring).

**REGLA INVIOLABLE:** módulo 05 NUNCA modifica prompts/narración. Si encuentra problema, emite FAIL y deja que el módulo correspondiente reintente. Cero overrides.

---

## 7. Contrato sagrado de salida → fase2a

Anclado a `fase2a._normalize_long()` (verificado leyendo el código). Estos son los campos que fase2a CONSUME activamente; el resto del JSON es metadata ignorada.

### 7.1. Top-level (consumido)
```json
{
  "topic_id": "uuid",
  "video_type": "long",
  "chapters": [ /* 7 items */ ],
  "humanizer_phrases": ["frase1", "frase2", "frase3"]
}
```

### 7.2. Por chapter — caps veo (1 y 7)
```json
{
  "chapter_number": 1,
  "narration": "string",
  "render_engine": "veo",
  "art_profile": "INTERIOR",
  "image_prompt": "string (EN)",
  "video_prompt": "string (EN, instrucción de cámara)"
}
```

### 7.3. Por chapter — caps flux (2-6)
```json
{
  "chapter_number": 2,
  "narration": "string",
  "render_engine": "flux",
  "art_profile": "INDUSTRIAL",
  "image_prompts": [
    {
      "prompt": "string (EN)",
      "art_profile": "INDUSTRIAL",
      "subject_ref": "main_subject",
      "emotional_rank": "R1",
      "narration_anchor": "string (substring exacto de narration)"
    }
  ]
}
```

### 7.4. Campos metadata (NO consumidos por fase2a, sí persistidos para trazabilidad)
- `prompt_protocol_version`, `video_title`, `topic_title`
- `sources`, `verified_facts`, `research_summary`, `canonical_subject_description`
- `word_count`, `total_veo_chapters`, `total_flux_chapters`, `created_at`, `discovery_mode`
- `bullets_source` (si se decide persistir bullets en el final)

---

## 8. SHORT vs LONG

**SHORT:** mantiene el flujo actual 1-shot. Los 8 módulos NO aplican. Razón: SHORT ya funciona estable, es barato, y la complejidad no justifica el rediseño.

**LONG:** todo lo anterior aplica.

`fase2a.normalize_script()` despacha por `video_type`, no se entera del rediseño.

---

## 9. Funciones reusables del código actual

Estas se mantienen literales o con mínimos ajustes (NO reescribir):

**De `topic_researcher.py`:**
- `_research_angle(seed, angle)`
- `_build_angle_query_prompt(seed, angle)`
- `DEEP_RESEARCH_ANGLES`
- `_sanitize_search_keyword(raw)`
- `_extract_search_keyword_fallback(title, seed_title)`
- `_archive_seed`, `_remove_seed_from_inbox`
- `_load_seeds`, `_load_topics_db`, `_save_topics_db`
- `_get_existing_titles`, `_get_existing_seed_ids`

**A descartar de `topic_researcher.py`:**
- `_build_research_prompt`
- `_build_deep_synthesis_prompt`
- `_synthesize_deep_research`
- `_research_seed` (la versión deep monolítica; `topic_researcher_light` simplifica esta función)

**De `script_generator.py`:** TODO lo que sea `_generate_long_*` se descarta. Si hay helpers utilitarios (parseo de JSON con fallback, retry de Gemini, etc.) se aíslan en un módulo `gemini_helpers.py` reusable por todos los módulos nuevos.

---

## 10. Orden de implementación recomendado

1. **`gemini_helpers.py`** — extraer del `script_generator.py` actual los helpers (parseo, retry, llamada Flash con json mode). ~1h, $0 runtime.
2. **Módulo 00** — sintetizador con sus 4 sub-pasos. Reusa `_research_angle`. ~3h, +$0.001/topic vs hoy.
3. **`topic_researcher_light`** — simplificación de `_research_seed`. ~1h, ahorra $0.015/topic en pre-checkpoint.
4. **Módulo 01a + 01b** — skeleton + narrador. ~3.5h, ~$0.010/video.
5. **Módulo 03** — extractor visual con art_profile image-level. ~3h.
6. **Módulo 04** — sanitizador. ~2h.
7. **Módulo 05** — validador-juez. ~3h.
8. **Integración en `fase1.py`** — wireado del flujo nuevo, mantener SHORT path intacto. ~1h.

**Total:** ~16.5h dev. ~$0.033/video runtime proyectado.

---

## 11. Open questions (no bloquean implementación, decidir antes de prod)

- ¿Persistir `bullets_source` en el JSON final, o solo en `_steps/01a_skeleton.json`? Default propuesto: solo en `_steps/`.
- ¿Borrar `_steps/{topic_id}/` automáticamente tras un PASS exitoso, o conservar para auditoría? Default propuesto: conservar; flag `--purge-steps` opcional.
- ¿Cuántos retries por `retry_step` antes de escalar al usuario? Default propuesto: 2.
- Threshold de `virality_score` para auto-aprobar topics sin checkpoint humano (modo batch nocturno). Default propuesto: no implementar hasta tener datos de calidad post-rediseño.
