# HANDOFF F6 — Guion v3: el LLM como guionista, no como redactor por capítulo

**Fecha:** 2026-10-21 · **Analista:** chat proyecto · **Ejecuta:** CC (sesión nueva, Opus para los prompts del guionista/editor) · **Gate:** Omar
**Rama:** `f6-guion-v3` desde `f5-guion-v2` (45c052c). Sin merge a `main`.
**Costo estimado:** ~$2 por intento de guion (Gemini Pro ×3–4 llamadas). Sin imágenes ni render en este handoff.

---

## 0. Por qué (una página)

Orleans v2 (F5d) tiene 41 datos del pool, cifras canónicas, cliffhangers con dato, 2.9 adjetivos/100. Nota del analista: **7/10**. Omar: "aún no siento esas historias tan buenas". Las dos lecturas coinciden: es un buen artículo leído con voz grave.

Causa estructural, no de prompt: `m01b_narrator` escribe **cap por cap** (`_prompt_hook` → 5× `_prompt_development` → `_prompt_outro`), cada uno con "estos ids, 75 segundos, no repitas lo anterior". El LLM nunca ve la historia entera antes de escribir; reparte datos en vez de contar. `m01a_skeleton` reparte el pool por capítulo (`_distribution_plan`, `_evidence_plan`) con bullets de hechos, no con dramaturgia.

Lo que retiene en YouTube (y v2 no tiene):
1. Primeros 30 s con **imagen concreta + promesa**, no contexto.
2. **Un humano con nombre** que seguimos todo el video.
3. **Curva**: cada cap peor que el anterior; v2 caps 3–5 van parejos.
4. **Ritmo**: frases cortas antes del golpe, respiros; v2 tiene todas las frases del mismo largo.
5. **Cierres que obligan**: culpa o consecuencia; no trivia administrativa.
6. **Final humano**: lo que produce like y comentario.

**v3 = el LLM primero decide la historia (escaleta), después la escribe de corrido, después un editor la aprieta. Los validadores duros no cambian. La salida sigue siendo 7 caps con el mismo contrato.**

---

## 1. Principio y criterio de éxito

- **Principio:** el guionista escribe para que el espectador se quede al siguiente segundo. Cada decisión de la escaleta responde a una razón por la que alguien se va (lista de arriba).
- **Criterio de aceptación del piloto:** Omar lee v2 y v3 del **mismo tema** lado a lado (página tipo `compara_orleans.html`) y quiere saber qué pasa después en v3. Si no gana claro, v3 se descarta sin tocar producción.
- **Criterio final (después del primer video publicado con v3):** curva de retención de YouTube Studio contra los últimos 3 videos del canal. Métrica real, no nota del analista.

---

## 2. Arquitectura v3

```
m00 research ──► step_4a_facts ──► evidence_pool (+ [TESTIMONIOS])
                                        │
                              m01a_escaleta  (NUEVO · Pro · 1 llamada)
                                        │  escaleta.json: beats, humano, pico, preguntas, cierre
                              m01b_guionista (REESCRITO · Pro · 1 llamada → narración completa)
                                        │
                              m01c_editor    (NUEVO · Pro · 1 llamada → narración apretada)
                                        │
                              m01d_particion (NUEVO · determinista → 7 caps, contrato actual)
                                        │
                   validadores duros (existentes) ──► m05 juez (sobre el texto completo)
                                        │
                   m02_5 normalizer ──► TTS ──► m03 ──► fase2a/2b (SIN CAMBIOS)
```

### 2.1 m00 / step_4a — una sección más
Agregar al prompt de research y al pool:
- `[TESTIMONIOS]`: citas textuales con nombre y rol de **personas que estuvieron ahí** (presos, guardias, familiares, rescatistas), con fuente. Hoy el pool de Orleans tiene 2 citas y las dos son del sheriff. Sin testigo no hay humano que seguir.
- En `evidence_pool.personajes`: campo `testigo: true/false` y `presente_en: [T05, T08…]` (en qué momentos de la cronología estuvo).
- Si el tema no tiene testigos con nombre → el guionista usa un **personaje colectivo con rostro** ("un preso de Templeman III, 19 años, según HRW") marcado `generado: false, fuente: Dxx`. Nunca un nombre inventado (candado existente).

### 2.2 m01a_escaleta (nuevo; reemplaza el reparto de `m01a_skeleton`)
Una llamada a Pro (`call_pro_json`) con el pool completo + perfil del canal. Devuelve `escaleta.json`:

```json
{
  "humano": {"id": "P04", "nombre": "…", "rol": "…", "por_que": "…"},
  "antagonista": {"id": "P01"},
  "promesa_gancho": "una frase: lo que el espectador va a descubrir",
  "pico": {"beat": 5, "id": "D19", "por_que": "…"},
  "cierre_humano": "la pregunta que se queda",
  "beats": [
    {
      "n": 1, "funcion": "gancho",
      "emocion": "miedo", "intensidad": 3,
      "dato_central": "T05", "datos_apoyo": ["D09"],
      "imagen_sensorial": "agua negra subiendo por la escalera de la celda, un hombre gritando en la oscuridad",
      "pregunta_abierta": "¿por qué nadie vino?",
      "pregunta_pantalla": "¿Quién decidió dejarlos?",
      "cierre": "anticipa: la orden del sheriff",
      "palabras_objetivo": 110,
      "cap": 1
    }
  ]
}
```
Reglas del prompt de escaleta (van como texto, con few-shot de 2 escaletas buenas):
- 7–12 beats, cada uno asignado a un `cap` 1–7 con `palabras_objetivo` que sumen el largo actual por cap (hook 45 s ≈ 110 palabras, desarrollo 75 s ≈ 190, outro 45 s ≈ 110). **El número de caps es 7, fijo.**
- `intensidad` no decreciente hasta el pico; el pico nunca en el último beat; mínimo un beat `intensidad 1` (respiro) después del pico.
- Cada beat tiene **un** `dato_central`; un id aparece en un solo beat (paráfrasis sin cifra permitida después).
- `imagen_sensorial`: algo que se pueda ver, oler o tocar; nunca abstracto. Va a m03 como ancla principal.
- `pregunta_pantalla` con rúbrica dura (§4).
- Reservados para pantalla (`pantalla_ids`) se mantienen: el guionista no los pronuncia, la pantalla los muestra (F5d/F5f).
- Hereda de `m01a_skeleton`: `canonize_figures`, `assign_screen_ids`, `finalize_pool_plan`, `_validate_evidence_plan` (relevancia, ids existentes). `frozen_skeleton` → `frozen_escaleta` con el mismo token.

### 2.3 m01b_guionista (reescritura del núcleo de `m01b_narrator`)
Una llamada a Pro con escaleta + pool + reglas de prosa (`_prose_rules`, lista de relleno prohibido, hard/soft de F5c). Devuelve **la narración completa** en párrafos, cada párrafo marcado `[beat n]`.
- Escribe sabiendo a dónde va: puede plantar en el beat 2 lo que paga en el 6.
- Frase de cierre de cada cap: anticipa algo concreto del cap siguiente (ya existe el chequeo `closing_hits_cliffhanger`).
- Ritmo: ≥1 frase de ≤6 palabras por beat; ninguna frase > 30 palabras; antes del pico, dos frases cortas seguidas.
- Adjetivos 2–4 /100 (piso y techo, F5b).
- Declara `ids_usados` por párrafo (métrica por id, F5b).
- `best_of_n` se mantiene pero sobre el texto completo: n=2 (no 3; cada intento es más largo).

### 2.4 m01c_editor (nuevo)
Segunda llamada a Pro con la narración completa + escaleta. Solo puede: cortar, reordenar frases dentro del beat, acortar, quitar repeticiones y relleno, reforzar el ritmo. **No puede** agregar datos, cifras, nombres ni adjetivos nuevos. Devuelve el texto editado + `cambios[]` (antes/después) para auditoría.
Después del editor corren **todos** los validadores duros otra vez (`invented_numbers`, `contamination`, `non_canonical`, `screen_leaks`, candado literal). Si falla un párrafo, se rechaza el párrafo editado y se conserva el original del guionista; nunca se rechaza el video.

### 2.5 m01d_particion (nuevo, determinista)
Parte la narración en 7 caps por las marcas `[beat n]` → `cap` de la escaleta. Reglas:
- Corta siempre en frontera de párrafo.
- Largo por cap dentro de `_len_range(role)` existente (±15 %). Si un cap se pasa: mueve el último párrafo del beat al cap siguiente **solo si** ese beat no es el pico y la frase de cierre se mantiene; si no, pide al editor acortar ese cap (una llamada corta, misma regla de no agregar).
- Produce exactamente el JSON que hoy produce `generate_narration`: por cap `chapter_number, role, render_engine, duration_seconds, title, narrative_intent, bullets (= imagen_sensorial + dato_central del beat), narration, ids_usados`, más `humanizer_phrases` (se mantiene la llamada Flash existente). **Ningún consumidor río abajo cambia** (fase1_5, fase2a, fase2b, m03, audio_manager, asset_manager, gfx_*).

### 2.6 m05 juez
Se mantiene y se amplía para leer `escaleta.json`:
- Curva: intensidad declarada vs. densidad de léxico sensorial por beat (ya existe `gfx_intensity` como proxy; reusar el léxico).
- Humano: el `humano.nombre` aparece en ≥ 3 caps.
- Pregunta de pantalla: pasa la rúbrica (§4) → si no, se marca y `gfx_question` es respaldo.
- Ritmo: frases cortas por beat, frase más larga.
- Reporte `06_judge_narrative.json` igual + bloque `v3`.

---

## 3. Gancho (cap 1) — regla explícita
Primeras 2 frases: una **imagen** (del beat 1, `imagen_sensorial`) y una **promesa** (`promesa_gancho`). Nada de "En 2005, el huracán Katrina…" hasta la frase 3. Sin cifras en las primeras 2 frases. El validador de hook rechaza si la primera frase contiene año, cifra o nombre de institución.

## 4. Preguntas — rúbrica dura (mata B4 del backlog)
La pregunta de pantalla la escribe el guionista en la escaleta, no `gfx_question` después. Validador:
- ≤ 8 palabras.
- Nombra algo que el espectador **ya conoce** (persona, grupo, lugar u objeto mencionado en este cap o anteriores).
- Implica culpa, consecuencia o destino no resuelto.
- Sin nombres propios nuevos, sin términos administrativos (indemnización, generadores, registros, demanda, informe, autoridades).
- Modelos: "¿Quién apagó las luces?", "¿Por qué nadie abrió las celdas?", "¿Dónde están los 517?".
- Cap 7: no es gancho; es la pregunta humana que se queda ("¿Cuántos siguen sin nombre?").
`gfx_question` queda como respaldo solo si la escaleta no trae una válida.

---

## 5. Lo que NO se toca (FRENOS)
- `m02_5_normalizer_gate`, `tts_normalizer`, audio, `m07`, `m03_visual` (salvo recibir `imagen_sensorial` como ancla, que va en el handoff de Imágenes), `fase2a`, `fase2b`, todo `gfx_*`, `evidence.py`.
- Contrato de `chapters` (campos y 7 caps). `EXPECTED_CHAPTER_COUNT = 7` sigue.
- Candado literal, cifras canónicas, relevancia del pool, reservados para pantalla.
- `regenerate_caps` (reparar un cap suelto) debe seguir funcionando: en v3 regenera el cap llamando al editor con la escaleta y el texto vecino, no al guionista completo.
- Guiones sin `evidence_pool` (topics viejos) siguen por el camino v2 byte-idéntico. Flag `GUION_V3=1` o `topic["guion_version"]=3`.

---

## 6. Fases para CC

| Fase | Qué | Horas | Entrega |
|---|---|---|---|
| F6a | `[TESTIMONIOS]` en step_4a + `testigo/presente_en` en personajes; re-research de Orleans solo para esa sección ($0.50); tests | 1.5 | pool de Orleans con testimonios o constancia de que no existen |
| F6b | `m01a_escaleta` + schema + validadores + few-shot; `frozen_escaleta` | 3 | `escaleta.json` de Orleans legible por Omar |
| F6c | `m01b_guionista` (una llamada, texto completo, best_of_2) + `m01c_editor` + validadores duros post-editor | 3 | narración completa v3 de Orleans + `cambios[]` del editor |
| F6d | `m01d_particion` + contrato 7 caps + `regenerate_caps` v3 + `m05` ampliado | 2 | `01b_narration.json` v3 con el contrato actual; juez v3 |
| F6e | Página `compara_orleans_v3.html` (v2 F5d vs v3, por cap, métricas del juez, escaleta al lado) + revisor + commit | 1 | PARADA: Omar lee |

Total ≈ 10–11 h de CC en 2 sesiones (F6a–b, F6c–e). Commit wip antes de cada compactación; `ESTADO_SESION.md` al día.

**Modelo:** F6a/F6d/F6e mecánicas → Sonnet. F6b/F6c (los prompts del guionista y editor) → Opus.

---

## 7. Pruebas
- Unit: schema de escaleta; intensidad no decreciente hasta el pico; un id por beat; rúbrica de preguntas; partición respeta `_len_range`; editor sin datos nuevos (diff de cifras/nombres antes/después = ∅); hook sin año/cifra en 2 primeras frases.
- Regresión: topic sin pool → salida byte-idéntica a v2 (test existente de m03 sigue).
- Integración: Orleans v3 → `m02_5` → TTS en seco (sin audio real) → `m03` genera prompts con `bullets` nuevos sin error.
- Humano: Omar lee la comparación.

## 8. Riesgos y mitigación
1. **Partir en 7 caps de duración fija** rompe un beat → escaleta asigna `palabras_objetivo` por beat; partición en frontera de párrafo; editor acorta un cap puntual.
2. **El editor "mejora" inventando** → validadores duros después del editor; párrafo rechazado vuelve al original.
3. **Texto largo en una llamada** (≈1,000 palabras) pierde calidad al final → best_of_2; el juez mide por beat; si el último tercio cae, se regenera solo ese tramo con el editor.
4. **Sin testigos en el research** → personaje colectivo con rostro, nunca nombre inventado; beneficio completo en el siguiente tema.
5. **Regresión silenciosa** (perder cliffhangers, reservados) → la escaleta hereda esos campos; la comparación los mide.
6. **Costo** ≈ igual a v2 (3–4 llamadas Pro largas vs 7 cortas + reintentos).
7. **Omar se mete de nuevo a fondo** → v3 se prueba solo en texto, $2; decisión binaria con la comparación; nada de producción hasta que gane.

## 9. Después de v3 (no en este handoff)
Imágenes (ANALISIS_imagenes_orleans_2026-10-21 §0: Seedream 5.0 Lite, estilo al inicio, reglas m03, `imagen_sensorial` como ancla) → deuda gfx B1–B9 (BACKLOG §0) → primer video completo v3 con tema nuevo → decisión de merge a `main`.
