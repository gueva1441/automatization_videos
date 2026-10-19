# HANDOFF F2b — Director v2 (énfasis, íconos, recortes de verdad) + concat sin re-encode

**Fecha:** 2026-10-19 · **Analista:** chat proyecto · **Ejecutor:** CC · **Gate:** Omar (al final, un video)
**Base:** `f2-gfx-director` @ `0cc1997` (F2 nocturno cerrado). Trabajar en la misma rama. `main` intacta hasta el OK de Omar.
**Docs:** `DOC_MAESTRO_HyperFrames.md` v1.1, `F2_REPORT.md`, `RESUMEN_NOCHE.md`, `DECISIONES_F2_nocturno.md`.
**Modo:** autónomo como el nocturno (mismas reglas de §2 del `HANDOFF_F2_nocturno.md`): no preguntar, decidir conservador y anotar, un commit por sección con revisor, tope Gemini **$2**, un solo render completo al final en `looks`. Omar mira **una tira de íconos** (2 min) y **el video final**.

---

## 0. Diagnóstico que motiva F2b (feedback de Omar al AB de F2)
- **0 recortes** en todo el video: el LLM parafrasea el titular y el candado los tira (33/33).
- **Zoom fuera del detalle narrado** (la herida): `zoom_judge` busca "lo interesante", no lo que dice la voz.
- **Preguntas de cierre malas** ("¿El agua subió hasta el nivel del pecho?"): bullets convertidos en sí/no.
- **Pocas animaciones por cap** (3–4 en 2 min): la regla de 35 s es laxa y el director solo sabe buscar cifras/nombres; no reacciona a palabras con carga (veneno, putrefacción, cadáveres).
- **Tiempo:** concat + música re-encodean el video entero (~15 min); es lo que rompe los dos objetivos.
- CC metió grano FFmpeg en el disperso; el look aprobado es **grano 0, viñeta 0.15**.

## 1. Correcciones al director v1 (→ v1.5)
| # | Cambio | Spec |
|---|---|---|
| 1.1 | **Titular determinista** | El LLM devuelve `fact_idx` + `scene_idx`. El validador construye `headline` = primeras ≤ 8 palabras del fact hasta la primera coma/punto; si el fact tiene cifra, la cláusula con la cifra. `kicker` = fuente del fact o año. Pasa el candado por construcción. Objetivo: 1–2 recortes por cap |
| 1.2 | **Zoom guiado por narración** | A `zoom_judge` se le pasa la frase del anchor ("la herida en la mano") y devuelve el box **de eso** o `null`. Si `null` → sin zoom. Umbral de confianza explícito |
| 1.3 | **`chapter_question` OFF** | Default off en el perfil. Queda el código. Se reactiva cuando m01b emita `cliffhanger` por cap (anotar como deuda de guion en el reporte) |
| 1.4 | **Densidad** | Intervalo máximo sin bloque: **18 s** (antes 35). El relleno del validador usa, en este orden: énfasis de palabra (§2), callout de fact, punch_in |
| 1.5 | **Visión para retratos, filtrada** | `zoom_judge` solo sobre imágenes cuyo `image_prompt` menciona persona/rostro/retrato/manos/cuerpo. Resultado alimenta el router (`high` si retrato/primer plano) |
| 1.6 | **Grano 0** en el disperso; viñeta 0.15. Quitar la desviación D21 |

## 2. Léxico de moods + énfasis de palabra (nuevo)
- `gfx_profiles/misterio.json` gana `moods`: **4 categorías** activas, cada una con lista de disparadores en español (sinónimos y flexiones; ≥ 25 palabras por categoría) y un preset de capa:

| Categoría | Disparadores (ejemplos) | Capa (1–3 s, intensidad baja, nunca toca píxeles) |
|---|---|---|
| `veneno_enfermedad` | veneno, arsénico, cianuro, gas, tóxico, putrefacción, infección, contaminado, enfermos… | viraje verde-amarillo en sombras 1 s · partículas oscuras derivando · viñeta se cierra 10 % |
| `agua` | agua, inundación, se ahogaban, crecida, sumergidos, marea… | cáusticas de luz sutiles · sombra oscura que sube desde abajo hasta 1/3 |
| `muerte` | cadáveres, muertos, murieron, cuerpos, fallecidos, restos… | desaturación 80 % en 1.5 s · push-in lentísimo · letterbox 2 s · viñeta cerrada |
| `oscuridad_encierro` | oscuridad, sin luz, atrapados, encerrados, celda, a oscuras… | oscuridad entra desde bordes · haz tipo linterna que deriva 2–3° · parpadeo de luz 2 veces |

- Reserva (en el JSON, inactivas): `fuego`, `caos_gritos`, `radiacion_quimico`, `frio_abandono`, `silencio`.
- **Bloque `keyword_emphasis`:** el director marca por cap las 3–5 palabras de más carga que estén en el léxico (literal por construcción). Cada una dispara: capa de mood + (opcional) sello rojo con la palabra + ícono (§3) si la categoría tiene. Máx 1 por frase, mín 20 s entre moods de la misma categoría. SFX asociado (tic sordo).
- Regla de identidad: un mood es un **momento**, no un filtro; si en un cap hay > 5 disparadores, el validador se queda con los 5 de palabras más raras (menor frecuencia en la narración completa).

## 3. Íconos (nuevo)
- **Set propio: 12 íconos SVG**, estilo **grabado / etiqueta de veneno 1890 / forense**: trazo de tinta irregular, blanco hueso, rojo de acento en un solo detalle. **Nunca** estilo ícono de interfaz. Lista: calavera, gota, llama, biohazard, reloj, candado, ojo tachado, balanza, cruz, persona, edificio en ruina, signo de pregunta.
- **Cómo se producen (rápido, ~1–1.5 h, ≤ $1):** generarlos con el motor t2i del pipeline (`engine_profiles`, Seedream o Flux) con un prompt base fijo para todo el set — *"1890 poison label woodcut, single <objeto>, white ink on pure black background, thick irregular engraved strokes, no text, no letters, centered, isolated"* — mismo seed/estilo, 3 tiradas por ícono. Umbralizar a blanco/negro y **vectorizar con `potrace`** → SVG con paths reales (necesarios para `engrave` e `ink_bleed`). Limpiar paths diminutos. Registrar prompt, seed y motor por ícono en `gfx_profiles/icons/README.md`. Prohibido: texto dentro del ícono, dibujar SVG a mano más de 15 min por ícono.
- Entregar **`tira_iconos_12.jpg`** (3 candidatos por ícono, sobre fondo de ch02, con la animación `engrave` a mitad en una segunda fila) → **Omar elige por número (2 min)**. Rechazados: una tirada más; si sigue mal, respaldo Lucide para ese ícono.
- **Respaldo:** paquete local de Lucide o Tabler (MIT), restilizado por CSS al mismo trazo/color. El director elige de una **lista blanca** de nombres mapeados por categoría; nunca inventa SVG.
- **Si nada aplica → sin ícono** (texto solo). Nunca ícono equivocado.
- **Bloques:** `icon_callout` (ícono + palabra/cifra, reemplaza al callout de texto cuando la categoría tiene ícono; máx 3/cap) e `icon_array` (cifra = N figuras dibujándose en filas de 10, las víctimas en rojo; solo cifras ≤ 500 con relación total/afectados en facts; máx 1/cap).
- **Animaciones del ícono (3):** `ink_bleed` (tinta que se expande, 0.7 s; moods veneno/muerte), `engrave` (trazo a trazo, contorno y luego rayado, 0.8 s; evidencia/mapas/planos), `stamp` (ya existe). Salida única: fade con grano "tinta que se seca". Lint 0 errores.
- **Crecimiento:** el reporte de cada video lista palabras de énfasis **sin ícono**; entra al vigilante mensual.

## 4. Concat + música sin re-encode (fase2b + transition_applier — autorizado)
- Los xfade inter-cap re-encodean solo **±1 s alrededor de cada frontera** (6 ventanas); el resto de los segmentos se concatena con `-c copy` (todos los segmentos ya salen con los mismos parámetros de encode; verificar y, si no, normalizar en `_build_chapter_segment`).
- La música se mezcla como **audio solo** y se remuxa con `-c:v copy`.
- `--hw-encode` para las ventanas de frontera si está disponible.
- Objetivo: concat + música ≤ 2.5 min; incremental ≤ 6 min; corrida completa extra ≤ 22 min.
- Tests: salida sin `--gfx` sigue byte-idéntica **en los segmentos**; el final cambia de hash por construcción (ya no se re-encodea) → el test de "igual que hoy" pasa a comparar PSNR ≥ 50 dB y duración ±1 frame, y se anota en el doc maestro.

## 5. Entregables
1. Commits por sección: §1, §2, §3 (íconos: commit solo tras aprobación de Omar de la tira), §4.
2. **`tira_iconos_12.jpg`** → punto de parada único para Omar.
3. Render completo de Orleans (`looks`, disperso, `--hw-encode` si pasó PSNR): `AB_{id}_f2b.mp4` + cues de los 7 caps + página de revisión.
4. `F2b_REPORT.md`: bloques por cap (incluidos moods e íconos usados), recortes que salieron, zooms con/sin box, densidad (s promedio entre bloques), tiempos (gfx, concat+música, total, incremental), palabras de énfasis sin ícono, PSNR, Gemini.
5. Prueba incremental: cambiar un callout de ch04 → tiempo total.
6. Veredictos del revisor íntegros.

## 6. Candados
Lock literal · sin `--gfx` segmentos byte-idénticos · sin shaders · sin rembg · `main` intacta · tests verdes por commit · ningún texto ni ícono inventado por el LLM.

## 7. Estimación
§1 ~3 h · §2 ~2.5 h (detección por regex, sin LLM; 4 capas CSS) · §3 ~2.5 h (íconos por t2i + potrace, 3 animaciones, respaldo Lucide) · §4 ~3 h · render + reporte 1.5 h → **~12 h de CC**.

## 8. Orden y paradas de Omar
§1 → §2 → render ch02 looks (`--only-cap`) → **PARADA 1** (página de revisión de ch02) → §3 → **PARADA 2** (tira de íconos) → §4 → render completo → AB → reporte. Dos paradas, ~10 min de Omar en total.
