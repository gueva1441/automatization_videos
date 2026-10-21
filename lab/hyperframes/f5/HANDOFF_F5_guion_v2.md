# HANDOFF F5 — Guion v2: el research completo llega al guion y a la pantalla

**Fecha:** 2026-10-20 22:20 · **Analista:** chat proyecto · **Ejecutor:** CC · **Gate:** Omar (una parada: comparar v1 vs v2 de Orleans)
**Base:** `f3-lab-identidad` tras F4f. Rama nueva `f5-guion-v2` desde ahí. `main` intacta.
**Leer:** `CLAUDE.md`, `lab/ESTADO_SESION.md`, `researcher_steps/step_4a_facts.py`, `script_engine/m01a_skeleton.py`, `m01b_narrator.py`, `m02_5_normalizer_gate.py`, el juez (`m05_PROMPT_v1.txt` y su módulo), `script_engine/gfx_literal_lock.py`, `gfx_director.py`, `gfx_fragments.py`, y `data/scripts/_steps/ba6c3cac-…/00_pool_etiquetado.json`.

---

## 0. Diagnóstico (verificado en disco por el analista)
- El pool del research de Orleans (`00_pool_etiquetado.json`, 3 bloques) tiene **~45 datos duros, una cronología de 12 fechas, 5 lugares con nombre, 3 citas textuales del Sheriff Gusman** y contradicciones oficiales (6,375 vs 8,000; "nadie escapó" vs 14 órdenes de arresto; 517 no contabilizados; 1,300 testimonios).
- `step_4a_facts` lo reduce a **10 facts** ("entre 6 y 12, al menos 3 visuales"). `m01a_skeleton` reparte esos 10 entre 7 caps (cap 6 recibe 1). `m01b_narrator` prohíbe cualquier cifra/fecha/nombre fuera de esos facts y exige 1,200+ caracteres por cap.
- Resultado medido en la narración de Orleans: "6,500" en 5/7 caps, "hasta el pecho" en 5/7, "29 de agosto" en 4/7, "500 desaparecidos" en 4/7; el Sheriff Gusman **no aparece**; caps 3 y 4 cuentan lo mismo; cap 7 es resumen. La prosa rellena con adjetivos porque no tiene datos.
- Aguas abajo, el director de gráficos solo puede mostrar esos mismos 10 facts, y el candado literal rechaza todo lo demás. Por eso los recortes repiten la voz.

**Una causa, dos síntomas (guion flaco y post-its vacíos). Se arregla una vez, aguas arriba.**

## 1. Cambios río arriba (motor de guion)

### 1.1 `step_4a_facts` → además emite `evidence_pool`
Sin tocar los 6–12 `verified_facts` (los usan las imágenes), agregar una segunda extracción sobre los mismos bloques, **sin tope**, con este esquema:
```json
"evidence_pool": {
  "datos":      [{"id":"D01","texto":"Katrina tocó tierra como huracán de categoría 3","tipo":"magnitud|cifra|fecha|nombre|lugar|cita|contradiccion","valor":"categoría 3","fecha":"2005-08-29","bloque":"humano","fuente":"ACLU 2006"}],
  "cronologia": [{"id":"T01","fecha":"2005-08-26","hora":null,"evento":"Cortan los teléfonos a los reclusos","bloque":"misterio","fuente":"ACLU 2006"}],
  "lugares":    [{"id":"L01","nombre":"Orleans Parish Prison, Tulane Avenue, New Orleans","rol":"escenario principal"}],
  "citas":      [{"id":"Q01","texto":"permanecerán donde pertenecen","autor":"Sheriff Marlin N. Gusman","fecha":"2005-08-28","fuente":"ACLU 2006"}],
  "personajes": [{"id":"P01","nombre":"Marlin N. Gusman","rol":"Sheriff de Orleans Parish; decidió no evacuar","antagonista":true}]
}
```
Reglas: todo literal del pool (nada inferido); cada ítem con `bloque` y `fuente` (la fuente se toma de la lista `[FUENTES CONSULTADAS]` del bloque; si el bloque no la ata a un dato, `fuente: null`, nunca inventada). Geocodificar `lugares` una vez (Nominatim, gratis) → `lat/lon` si resuelve; si no, `null`.

### 1.2 `m01a_skeleton`
- Recibe `evidence_pool`. Reparte **datos, no facts**, por cap, siguiendo la cronología cuando existe (Orleans: 26 ago → 2 sep → 2006 → 2009 → 2010).
- Cada cap recibe **≥ 3 datos nuevos** (no usados en caps anteriores) + a lo sumo 1 repetido como puente.
- Define `personajes` del video (antagonista obligatorio si el pool lo tiene) y en qué cap entra cada uno.
- Campo nuevo por cap: `cliffhanger`: **el dato concreto** (id del pool) que el cap siguiente va a revelar. Es la pregunta de cierre.

### 1.3 `m01b_narrator`
- Lista blanca numérica = `verified_facts` ∪ `evidence_pool` (regla 6 de PROSE_RULES).
- Reglas nuevas en el prompt y en `_validate_narration`:
  1. Usar los ≥ 3 datos asignados; cada uno aparece literal (cifra/fecha/nombre).
  2. Ningún dato del video aparece en más de **2 caps** (el validador cuenta contra las narraciones previas).
  3. Nombrar a las personas del skeleton por nombre y cargo la primera vez.
  4. Si el cap tiene ≥ 2 fechas de la cronología, narrar **en orden** y decir las fechas.
  5. Citas: entre comillas, con autor, literales del pool.
  6. Lista de relleno prohibido (rechaza): "imaginen", "una eternidad de", "cámara de tortura", "coloso de", "manto oscuro", "infierno personal", "eco fantasmal", "sombra inalcanzable", "tragedia íntima", y toda frase que califique sin dato en oraciones consecutivas (> 2 seguidas).
  7. El cierre anticipa el `cliffhanger` del skeleton (puede ser pregunta o afirmación incompleta), nunca retórica genérica ("¿cuánto podrían resistir?").
- `LEN_*` se mantiene; con más datos la longitud se llena sola.

### 1.4 `m02_5_normalizer_gate`
Cubrir para TTS: horas ("6:10 AM" → "seis y diez de la mañana"), dólares ("$223 millones"), porcentajes, citas (sin leer las comillas), siglas (ACLU, HRW, DOJ, FEMA → deletreo o nombre).

### 1.5 Juez (`m05`)
Métricas nuevas con umbral, por cap y por video:
- **densidad**: datos literales por 100 palabras ≥ 2.0 (Orleans v1 ≈ 0.7).
- **repetición**: ningún dato en > 2 caps; índice de 3-gramas repetidos entre caps < 5 %.
- **adjetivación**: adjetivos calificativos por 100 palabras ≤ 8 (v1 ≈ 14).
- **antagonista**: nombrado si existe en el pool.
- **cliffhanger**: el cierre contiene el dato o entidad del `cliffhanger` del skeleton.
Falla → reintento con feedback dirigido (ya existe el mecanismo `_call_with_length_retry`).

### 1.6 `m03_visual` (opcional, si el tiempo alcanza)
Los prompts de imagen pueden pedir lugares/objetos del pool (paso elevado de Broad St sobre la I-10; torre de 10 pisos de la House of Detention; teléfonos cortados). No cambia la arquitectura; cambia la especificidad.

## 2. Cambios río abajo (producción)
- **Candado literal** (`gfx_literal_lock`): texto permitido = narración ∪ `evidence_pool` (datos, citas, cronología, lugares). Un recorte que diga lo que la voz **no** dice es ahora el caso deseado, no un rechazo.
- **Director / fragmentos**: candidatos de recorte y dato salen del `evidence_pool` del cap (y de los caps vecinos ±1), nunca de la narración. Kicker = `fuente` del dato; sin fuente → `fecha`; sin ninguna → sin recorte. Dedupe por `id`.
- **Ícono de recorte/dato por contenido** (decisión de Omar, escena 1): el ícono lo decide el `tipo`/tema del dato (huracán → espiral; generadores → rayo tachado; cifras de personas → sin ícono), nunca la palabra de la voz que disparó el bloque. Espiral de huracán y rayo tachado se generan una vez con el pipeline de los 12 (mismo prompt base).
- **Pregunta de cierre**: del `cliffhanger` del skeleton (reemplaza al generador de F3; queda como fallback).
- **Reloj**: de `cronologia` (hora si hay; si no, fecha; si el cap no avanza de fecha, no sale).
- **Mapa** (prepara F6): `lugares` con lat/lon quedan en el guion; no se renderiza todavía.
- Sin cambios: TTS, fase1_5, fase2a, DepthFlow, plantillas HyperFrames, lab de identidad, concat.
- Compatibilidad: guiones sin `evidence_pool` siguen funcionando con `verified_facts` (todo detrás de `if pool`).

## 3. Prueba sobre Orleans (sin imágenes, sin render)
1. Regenerar solo el guion de Orleans en un `topic_id` nuevo (copia del research: reusar `00_pool_etiquetado.json`, no volver a investigar): 4a → skeleton → narración → normalizer → juez.
2. **Página de comparación** `lab/guion/compara_orleans.html` (estática): v1 y v2 lado a lado por cap, con las métricas de §1.5 por cap y por video, y debajo el `evidence_pool` con marca de qué dato usó cada versión. Sin servidor; un HTML que CC genera con un script.
3. **Simulación del director sobre v2** sin render: correr `gfx_director` + fragmentos + crítico visual en modo plan (sin HyperFrames) para los 7 caps de v2 usando las fotos de v1 como proxy → `gfx_cues_v2_chNN.md`. Es para que el analista valide que los recortes ahora salen del pool con fuente.
4. Costo estimado: Flash ≈ $0.30 (guion + juez + director). **Cero imágenes, cero render.**
5. Entregables: `F5_REPORT.md` (métricas v1/v2, decisiones, veredictos), la página de comparación, los cues simulados.

## 4. PARADA — validación del analista (antes de que Omar decida)
El analista lee del disco y responde por escrito, en `VALIDACION_F5.md`, estas preguntas con evidencia:
1. ¿v2 usa ≥ 3 datos nuevos por cap y nombra a Gusman? (del juez + lectura)
2. ¿Bajó la repetición? ("6,500", "pecho", "29 de agosto" ≤ 2 caps)
3. ¿La prosa cambió de adjetivos a hechos? (adjetivos/100 antes vs después, y 3 pares de frases)
4. ¿Los cierres anticipan algo concreto? (los 6 cliffhangers listados)
5. **¿Mejora todo lo demás?** Con los cues simulados: cuántos recortes salen del pool con fuente vs v1; cuántos "repite" marca el crítico en v2 vs v1; si el reloj y la pregunta de cierre ya se alimentan del pool; si queda alguna palabra de peso 3 sin material.
6. Riesgos nuevos: narraciones más largas para TTS, nombres propios mal pronunciados, datos contradictorios del pool (6,375 vs 6,500) elegidos sin criterio.
Solo si 1–5 son sí, Omar lee la página de comparación y decide **rehacer el video de Orleans con v2** (imágenes nuevas: costo de un video) o aplicarlo directamente al **siguiente video**.

## 5. Candados
No inventar datos (todo literal del pool, con fuente o `null`) · `verified_facts` e imágenes de v1 intactos · `main` intacta · tests verdes y revisor por módulo · guiones viejos siguen corriendo · sin render completo en F5.

## 6. Orden y estimación
§1.1 (2 h) → §1.2 (2 h) → §1.3 + §1.4 (3 h) → §1.5 (2 h) → §2 (3 h) → §3 (2 h) → **PARADA**. ≈ 14 h de CC, autónomo, decisiones conservadoras en `DECISIONES_F5.md`.
