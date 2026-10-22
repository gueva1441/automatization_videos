# HANDOFF F8 — Imágenes v3 + cierre de parámetros de guion + 3 semillas por la compuerta

**Fecha:** 2026-10-22 · **Analista:** chat proyecto · **Ejecuta:** CC, sesión nueva, **modo autónomo 8 h** (Omar fuera) · **Gate:** Omar al volver
**Rama:** `f8-imagenes-v3` desde `f7-research-v3` (560dcf7). Sin merge a `main`.
**Leer antes:** este archivo; `claude/ANALISIS_imagenes_orleans_2026-10-21.md` §0 (está también en el proyecto; si no está en disco, la sección 1 de abajo lo resume completo); `lab/hyperframes/f7/HANDOFF_F7_research_v3.md` §8–9 (parámetros y reglas vigentes).

**Reglas del modo autónomo:** no preguntar; **si el contexto pasa de ~80 %, commit wip + ESTADO_SESION.md + abrir una sesión nueva con el prompt de §7 y seguir desde el último punto del §4** (CC puede abrir sesiones; no esperar a Omar); decidir, anotar la decisión en `lab/hyperframes/f8/DECISIONES_F8.md` y seguir. Commit wip antes de cada compactación + `ESTADO_SESION.md`. Nada de render completo, nada de QA Studio, nada de merge. Si algo bloquea más de 30 min, se anota y se pasa al siguiente punto.

---

## 0. Por qué
Guion v3 está cerrado en 8.5/10 (F7c-3). La siguiente pérdida de calidad está en las fotos: Orleans v2 tuvo manos manchadas, cara asiática, ojos verdes, 12 pasillos iguales, y motivos que no venían de la historia sino de una frase suelta. Con v3 el guionista ya decide **qué se ve** en cada beat (`imagen_sensorial`); m03 tiene que usarlo. Y el motor cambia a Seedream 5.0 Lite (probado por Omar: 10/12 y 9/12 en obediencia, acepta el contenido del canal, $0.035).

---

## 1. Cambios en imágenes (A–G)

### A. Motor → Seedream 5.0 Lite
- `engine_profiles.PERFIL_SEEDREAM.model_id` → `bytedance/seedream/v5/lite/text-to-image`; el `/edit` de la foto madre → `bytedance/seedream/v5/lite/edit` (verificar que acepte `image_urls`; si no, dejar el /edit en v4.5 y anotarlo).
- `config` costo `seedream_per_image` 0.04 → 0.035. `image_size` fijo 2560×1440 (no "auto 2K").
- `FLUX_MAX_WORKERS` → `fal_concurrency` en config (default 20) + reintento con backoff exponencial en 429/503 (3 intentos). El límite de fal baja a 10 si no se compran $100 en 4 semanas.
- Telemetría: `endpoint` real en el manifest (ya existe), más `ms` por imagen.

### B. Ancla principal = `imagen_sensorial` del beat
- m03 recibe por cap los beats de la escaleta (`escaleta.json` → `cap`, `imagen_sensorial`, `emocion`, `intensidad`, `dato_central`). Para cada imagen del cap, el ancla narrativa se elige como hoy (plan de anclas, **freno**), pero el **sujeto visual** sale de la `imagen_sensorial` del beat al que pertenece el tramo; la narración aporta lugar/época/detalle.
- Si el cap tiene N imágenes y M beats, cada beat recibe ≥1 imagen; la del **pico** (intensidad 5) recibe 2 y una de ellas es la más cerrada del cap.
- `bullets` del cap (ya = imagen_sensorial + dato_central desde F6d) alimentan el prompt como contexto; no se tocan `_validate_anchor_substring`, `_reconcile_anchor_timing`, fluidificador, candado, `foto_madre_ref`, `hard_fact_ids`.
- Guiones sin escaleta (v2) → camino actual byte-idéntico.

### C. Estilo al inicio y al final del prompt
El bloque de estilo/paleta/grano (hoy cola: "documentary photographic realism, dark-history, faceless…") va **primero** en el prompt ("Grainy 35mm documentary photograph, <año>, dark-history realism, muted colors, visible film grain, slightly underexposed.") y se repite abreviado al final. Probado: con estilo en cola, Seedream devuelve set de película limpio.

### D. Reglas de composición (validador determinista sobre el prompt generado + instrucción a Flash)
1. **Dedupe de motivos por video**: lista acumulada (pasillo, podio/sheriff, manos en barrotes, generador, calendario, documento en escritorio, puerta cerrada). Cada motivo máx. 2 veces por video salvo que el beat lo exija (`imagen_sensorial` lo nombra).
2. **Manos**: nunca en primer plano ni como sujeto; solo en plano medio o fuera de foco. Prohibido "close shot of hands", "knuckles", "fingers gripping".
3. **Caras**: sin macro facial; emoción por postura, luz y acción. Prohibidos los clichés: "jaw clenched", "lips pressed thin", "pupils dilated", "whites of his eyes", "knuckles white", "trembling".
4. **Nada de conteos exactos ni izquierda/derecha** como requisito (Seedream falla ahí): posiciones como referencia absoluta ("hacia la ventana", "junto al podio").
5. Proporción: ≤25 % de las imágenes del video con humano en plano medio; ≥1 establecimiento/exterior por cap.

### E. Contenido sensible (YouTube)
- Cuerpos: siempre parcialmente ocultos (agua, sombra, distancia), nunca rostro ni plano cerrado; **≤2 por video**, nunca en cap 1, nunca candidata a miniatura.
- Prohibido en prompts: blood, wound, gore, mutilated, dismembered, rope around neck (ahorcados solo por sombra o pies), child + any harm.
- Menores: solo si el pool los documenta y nunca en situación de daño físico explícito; preferir objetos (zapatos, bandeja) a cuerpos.
- Flag por imagen `sensible: true/false` en el manifest (para futuro híbrido de motores).

### F. Tope de fotos y re-encuadre
- `max_images_per_video = 90` ya aplicado (F7c-2) → ~16 por cap de 105 s, 8–9 s por foto.
- **Re-encuadre**: cuando `_calculate_image_count` pide más de lo que el tope permite, m03 marca imágenes `reencuadre_de: <idx>`; fase2a genera el clip desde la misma foto con otro recorte (zoom 1.3–1.6 sobre el tercio opuesto) y otro movimiento. Cuenta como plano, no como foto. Solo si fase2a lo permite sin tocar el fluidificador; si no, anotar como propuesta.

### G. Corrida de humo (sin render completo)
- 12 prompts de Orleans f7r3 (los 12 beats más fuertes, incluidos pico y gancho) con las reglas nuevas → 12 imágenes con Seedream 5.0 Lite → `lab/hyperframes/f8/humo/` + hoja de contactos + tabla: prompt viejo vs nuevo, endpoint, ms, costo, flags.
- Comparar con las 12 equivalentes de v2 (misma posición) en una página `compara_imagenes_f8.html` (antes/después).
- Costo ≈ $0.45.

---

## 2. Cierre de parámetros de guion (chascada, 30 min)
1. Escaleta: **mínimo 2 beats por cap de desarrollo** (total 10–12 beats). Amarillo de la compuerta: 7–8 beats (como dejó CC).
2. Regla soft al editor: la **última frase del video** es cita o pregunta, nunca resumen ("Cientos de familias nunca supieron…" → termina en la cita de Reed).
3. No re-correr Orleans por esto; se verifica en las semillas nuevas (§3).

---

## 3. Tres semillas por research v3 + compuerta (noche, ≈ $8)
Crear 3 seeds en el inbox (formato del `topic_researcher`, `seed_title` en español, `geo` e `idioma_local`) y correr **solo** research v3 + compuerta (`POOL_GATE.md`), **sin** escaleta ni guion ni imágenes:

| # | Semilla | Por qué debería dar verde | Idiomas de búsqueda |
|---|---|---|---|
| S1 | **Ycuá Bolaños, Asunción, 1 de agosto de 2004** — el supermercado donde cerraron las puertas durante el incendio; ~400 muertos | Juicio con sentencia, informes de bomberos y fiscalía, cientos de testimonios en español, sobrevivientes con nombre, cronología minuto a minuto | es, (gn) |
| S2 | **Cromañón, Buenos Aires, 30 de diciembre de 2004** — 194 muertos en un boliche con salidas de emergencia encadenadas | Causa judicial enorme, informe de la Legislatura, testimonios, cronología, antagonistas con nombre | es |
| S3 | **Vajont, Italia, 9 de octubre de 1963** — la represa cuya ola borró Longarone; ~2,000 muertos; los ingenieros sabían | Proceso judicial, informes técnicos, prensa de época, testimonios; prueba la búsqueda en **otro idioma** | it, en, es |

Por semilla: `fuentes.json`, `manifest`, `00_pool_v3.json`, `POOL_GATE.md`, y una ficha de 10 líneas: color, humanos elegibles (nombre, rol, nº citas), pico probable, antagonista, riesgo de contenido sensible (S1 y S2 tienen menores entre las víctimas: anotar). **No** elegir; Omar elige al volver.
Si una semilla da rojo, no reintentar: anotar qué faltó.

---

## 4. Orden de trabajo (8 h) y entregas
1. (0:00–0:30) Rama, leer, §2 chascada, tests, commit wip.
2. (0:30–4:30) §1 A–F con tests (`test_module_f8.py`): perfil v5, concurrencia/429, estilo al inicio, validador de motivos/manos/clichés/sensible, ancla por beat, tope/re-encuadre. Commit wip.
3. (4:30–5:30) §1 G corrida de humo + `compara_imagenes_f8.html` + hoja de contactos. Commit.
4. (5:30–7:30) §3 tres semillas en paralelo (research v3 + compuerta). Fichas. Commit (los pools viven en `data/`, fuera de git: copiar `POOL_GATE.md` y fichas a `lab/hyperframes/f8/semillas/`).
5. (7:30–8:00) `F8_REPORT.md`: qué se hizo, qué no, costos medidos, decisiones tomadas solo, dudas para Omar; revisor; commit final; `ESTADO_SESION.md`.

## 5. FRENOS
- m03: solo los puntos B, C, D, E, F de arriba; no tocar plan de anclas, fluidificador, candado, `foto_madre_ref`, `hard_fact_ids`, rangos 120–400.
- fase2a: solo el re-encuadre, y solo si no toca el fluidificador.
- No tocar guion v3 salvo §2. No tocar gfx_*. No validador de visión (decisión de Omar).
- No render completo, no QA Studio, no regenerar fotos de Orleans fuera de la corrida de humo.

## 6. Riesgos
1. `/edit` de v5 Lite con otro contrato → dejar foto madre en v4.5 y anotar.
2. Seedream 5.0 Lite más lento (33–60 s): con 20 concurrentes son ~5 min por video; medir en la corrida de humo.
3. Re-encuadre puede chocar con DepthFlow (mismo mapa de profundidad): si choca, la imagen reencuadrada usa Ken Burns plano.
4. Semillas: Vajont puede dar amarillo por idioma (fuentes en italiano); es a propósito, mide el research multilingüe.
5. Presupuesto de la noche: ≈ $0.5 humo + $8 semillas + $0.3 tests = < $10.

## 7. Prompt de continuación (para la sesión nueva si esta se satura)
```
Continuación F8 (modo autónomo, Omar fuera). Leé lab/hyperframes/f8/HANDOFF_F8_imagenes_v3.md completo y lab/ESTADO_SESION.md. Rama f8-imagenes-v3. Retomá desde el último punto del §4 que ESTADO_SESION marque como pendiente, con las mismas reglas: no preguntar, decidir y anotar en DECISIONES_F8.md, commit wip antes de compactar, sin render completo, sin QA Studio, sin merge. Si volvés a pasar de ~80 % de contexto, repetí este mismo procedimiento. Al terminar todo: F8_REPORT.md, revisor, commit final.
```
