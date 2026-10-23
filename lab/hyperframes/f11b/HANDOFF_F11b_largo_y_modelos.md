# HANDOFF F11b — v4 con largo + comparación de modelos (Ycuá)

Analista · 2026-10-23 · Para CC. Base: `6264058` (rama `f11-guion-v4`; seguir en la misma rama). **SOLO narración.** Nada de imágenes, voz, audio, m03, assemble, fase2a/2b, render, QA Studio ni producción.

## 0. Por qué (leído del disco)
- F11 funcionó en estructura: ningún cap vacío, A y B difieren en 1 bloqueante, prompt de 7.9 k a 3.4 k tokens.
- F11 falló en largo (450–790 palabras contra ≈ 1,500). Hay dos causas y **las dos son del handoff F11, no del enfoque**:
  1. el prompt no pide largo: «CAP n · 250 palabras» es solo una etiqueta, y no hay total;
  2. la regeneración de caps cortos lleva la guardia léxica completa, que prohíbe prosa nueva (pasaron 5 de 26).
- Lectura del analista: Gemini v4 A tiene la mejor voz de todas las versiones (frases cortas, escena, sin juicios), pero está escrito como un resumen. Notas: Ycuá 6.5 y Orleans 5.5, contra 8 y 8.5 de v3.
- Prueba del analista (`lab/_gpt_probe_analista/`): `gpt-6.1-sol` en esfuerzo medio, con un prompt v4 que **sí** decía «unas 1,500 palabras en total», dio 1,456 palabras y 0 bloqueantes. La voz quedó plana, de analista («Los datos disponibles no permiten explicar…»). Nota 7. No es una comparación limpia: el prompt era otro.
- Ids calculados después del texto: hay falsos positivos (Orleans beat 8 con 24 ids; D80, D81 y D97 salen en casi todos los párrafos). m03 y gfx los leen.

## 1. Cambios (ninguna regla nueva)
1. **Línea de largo en el prompt v4** (se devuelve una instrucción que ya tenía v3; no es nueva). Al final del prompt: «Cada cap tiene que tener cerca de las palabras que dice su encabezado: es su largo, no un máximo. El video completo ≈ {total} palabras.» En el encabezado de cada cap: «≈ N palabras».
2. **Regeneración de cap corto** (bloqueante c): la guardia aplica solo a **cifras, nombres propios y citas nuevas**. Se permiten adjetivos y prosa nueva. Va como parámetro de la guardia en el llamado desde `guion_v4.py`; el comportamiento de m01c y de v3 no cambia (el test dorado de v3 sigue verde).
3. **Modelo enchufable.** Con `--modelo gemini-pro | gpt-6.1-sol | gpt-6-astra`, toda la cadena v4 de esa corrida (guionista + regeneración + edición de oración) usa ese modelo.
   - El **juez** sigue siendo el mismo de siempre para las tres.
   - El helper nuevo es `gpt_helpers.py`: chat completions, JSON y `reasoning_effort`.
   - La llave se lee de `OPENAI_API_KEY` en `.env`. Nunca va en logs, reportes ni git. Verificá que `.env` esté en `.gitignore`.
   - Costo: `usage` × precio (Sol US$ 2 / 10 y Astra US$ 10 / 50 por millón de tokens de entrada / salida). Anotá la fuente del precio en el reporte.
   - Si un modelo no existe o falla, se reporta. No se reemplaza por otro.
4. **Chascada — ids después del texto.**
   - Los ids de un párrafo pasan a ser `used_items(texto) ∩ ids de su beat`: dato central, apoyos y lo asignado a su cap.
   - Se reporta, por versión, el promedio de ids por párrafo antes y después.
   - Encontrá por qué D80, D81 y D97 matchean en todo: decilo en el reporte y no lo parchees con listas.

## 2. Corridas (solo Ycuá `f8s1-ycua-bolanos`, escaleta `01a_escaleta_v1.json`, md5 `e1ba1a48…`, sin notas)
| corrida | modelo | esfuerzo |
|---|---|---|
| `_v4b_gem` | Gemini Pro (el de siempre) | — |
| `_v4b_sol` | `gpt-6.1-sol` | `high` |
| `_v4b_astra` | `gpt-6-astra` | por defecto |
- Una corrida por modelo, con el **mismo prompt exacto**. Guardá ese prompt una sola vez como `prompt_ycua_v4b.txt`.
- Salidas `NARRACION_ycua_v4b_<modelo>.md` y `guion_ycua_v4b_<modelo>.json` en `lab/hyperframes/f11b/`. No se pisa nada de F11, de v1 ni de `_ajuste`, y no se escribe en `topics_db`.
- **`lab/hyperframes/f11b/compara_f11b.html`**, legible en el teléfono:
  - Arriba, una tabla resumen con una fila por versión: v3 (v1), Gemini v4 A (F11), GPT Sol medio (la prueba del analista, `lab/_gpt_probe_analista/ycua_gpt.json`), gem, sol y astra.
  - Columnas de la tabla: palabras, palabras por cap / objetivo, bloqueantes, duras v3 re-medidas, cierre, ids por párrafo, costo, segundos.
  - Por cap: pestañas o desplegables por versión, con el texto, sus bloqueantes y la frase marcada en color (fecha repetida, juicio de lista, eco, tráiler).
- **Tope de costo: US$ 2.00.** Si se pasa, PARADA.

**Criterio (lo mide el reporte; decide Omar con el analista):** bloqueantes ≤ 2 y entre 1,350 y 1,700 palabras, sin caps vacíos. La nota de lectura la da el analista.

## 3. Frenos
- Igual que F11 §3: solo narración, **cero reglas nuevas** (ninguna regex ni lista que rechace), los archivos prohibidos no se tocan, sin merge, no correr `f10_quirurgico_ycua.py`.
- No commitear `.env`, ni `lab/_gpt_probe_analista/` (es del analista), ni los modificados de siempre.
- Tests: test dorado de v3 verde; tests nuevos para la guardia de la regeneración, el modelo enchufable (con `call` falso, sin red) y los ids por beat. Suites verdes + las 5 fallas previas.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f11b/F11b_REPORT.md`
1. Tabla resumen (la del html).
2. Qué hizo la ronda de reparación en cada corrida.
3. Ids antes y después, y la causa de D80/D81/D97.
4. Lo que el v4 sigue sin ver.
5. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista lee las tres narraciones y le da a Omar nota y comparación antes de que Omar las lea. Nada de producción.
