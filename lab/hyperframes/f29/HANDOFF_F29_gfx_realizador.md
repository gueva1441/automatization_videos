# HANDOFF F29 — El gfx obedece a la escaleta: realizador en vez de director, sfx nuevos, y Sonnet vs Flash en dos caps

Analista · 2026-10-25 · Para CC. Base: el commit final de F28 (después de C). Cuatro partes A→D; **PARADA al final de D**. Topes: ElevenLabs SFX US$ 3 · Gemini US$ 3 · Claude US$ 2 (solo D). Banco de pruebas: Vajont (`f8s3-vajont`), mismo guion, misma voz, misma música de F28; solo cambia el gfx.

## 0. Diagnóstico (F27, 36 bloques en 7 caps, leídos contra la voz)
- **Spoilers:** cap 6 a los 16 s el recorte dice «murieron 1.910 personas» mientras la voz dice «son las diez y treinta y nueve»; cap 7 a los 8 s «el Tribunal condenó a Montedison», 70 s antes del juicio. La escaleta tenía esos dos ítems en `a_pantalla` con su cap y su beat («junto al recuento», «cifra en liras del fallo»): el gfx no lee la escaleta.
- **El pico sin bloque en 6 de 7 caps** (`pico.block = None`), mientras hay sellos en «fuerza» o «vida».
- **Amontonamiento:** cap 6, 4 bloques en 44 s, nada entre 68 y 111 s, 4 en 26 s. `gap_fill` mete bloques por hueco, no por relato.
- **Recortes por escena, no por frase:** cap 5 a los 9.8 s «Erto y Casso en continua aprensión» mientras la voz dice que el embalse volvió al nivel de seguridad.
- **Sellos léxicos:** 11 en el video; 8 repiten la palabra que la voz dice y el subtítulo escribe; íconos literales (calavera ×2, gota).
- **Preguntas de cierre inventadas** («¿Qué pasó en otro embalse?») cuando cada beat de la escaleta ya trae `cierre`.
- **Crítico desparejo:** 3 citas con veredicto «repite» se dibujaron igual (están `reserved`).
- **Sfx sintetizados** con osciladores (`make_sfx.py`): suenan a juguete y están desparejos (−5 a −18 LUFS).

Principio (acordado con Omar): **el bloque aporta lo que la voz no dice, sobre lo que la voz está contando ahora.** Nunca repite el subtítulo; nunca adelanta un beat posterior.

## A. Qué y cuándo: la escaleta manda (0 API; tests sin red)
1. **Entrada nueva del gfx:** `01a_escaleta.json` del topic (`beats` con `cap`, `n`, `funcion`, `intensidad`, `dato_central`, `datos_apoyo`, `cierre`; `a_pantalla` con `id`, `cap`, `por_que`; `pico`). `gfx_layer` la carga y la pasa a `gfx_pool` y al director. Si no hay escaleta (topics viejos, v3), el camino actual sigue igual, con aviso.
2. **Tramos de beat en el tiempo:** para cada beat del cap, su ventana `[t0, t1]` en la voz: el primer y el último timestamp de las palabras de los párrafos que llevan ese beat (la partición ya sabe qué párrafos van a qué beat; si no, por el orden de los beats y los ids que aparecen). Guardar en `gfx_beats_chNN.json`.
3. **Candidatos del cap** (`gfx_pool`), en este orden y solo estos:
   - **Obligatorios:** los `a_pantalla` del cap, cada uno **dentro de la ventana de su beat** (el beat cuyo `datos_apoyo`/`dato_central` lo contiene; si no está en ninguno, el beat que `por_que` describe; si no se puede decidir, el último beat del cap).
   - **Opcionales:** los `datos_apoyo` y `dato_central` del beat **que la voz no dijo** (el chequeo de «ya dicho» existe en `gfx_pool`: mismo número, mismo nombre o misma cláusula en la voz → fuera). Un ítem solo puede dibujarse dentro de la ventana de su beat.
   - Fuera: cualquier ítem del pool que no esté en los beats del cap. Se acaba la lista `VERIFIED_FACTS` global del cap como fuente de bloques.
4. **Cuántos, por `funcion` del beat:** planteo 0–1 · escalada 1–2 · giro 1–2 (el `dato_central` del giro primero) · pico **1 grande obligatorio** (nivel de agua, zoom de evidencia, recorte o rótulo de cifra) en la frase del pico (`pico.t` de `gfx_peak`) · respiro 0–1 · revelación 1–2 · cierre 0–1. Tope por cap: 5 bloques (sin contar reloj, pregunta y title card). **`gap_fill` apagado** (queda detrás de un flag, por defecto off); `punch_in` solo acompañando un bloque.
5. **Sellos:** máximo 1 por cap, sobre la palabra del pico (`pico.word`) o ninguno; sin ícono, o con ícono abstracto (sello, tinta, prensa). `gfx_intensity` deja de proponer sellos por léxico; se quita el diccionario palabra → ícono para `calavera`, `gota` y todo ícono figurativo (quedan en `gfx_icons` para los rótulos que los pidan por tipo de dato, no por palabra).
6. **Pregunta de cierre = `cierre` del último beat del cap**, literal, con el mismo bloque `chapter_question` (pausa y negro como hoy). `gfx_question` genera solo si el beat no trae `cierre`.
7. **Duración por texto:** `max(2.5, palabras/3 + 1)` s para rótulos, recortes y citas (tope 8 s). Reloj y nivel de agua como hoy.
8. **Crítico parejo:** las citas pierden `reserved` a efectos del crítico; «repite» corta siempre. Como las citas ahora vienen de ítems que la voz no dijo, no deberían repetir; si repiten, es señal de que el chequeo de «ya dicho» falló y se anota.
9. Tests sin red con la escaleta y el sync_map de Vajont: ventanas por beat; D128 cae en el beat 11 (respiro), no antes de `pico.t` del cap 6; D245 en el beat 13; Q50 en el beat 8; ningún bloque fuera de su ventana; ≤ 5 por cap; pico con bloque en los 7 caps; sellos ≤ 1; pregunta = `cierre`.

## B. Sfx con ElevenLabs (tope US$ 3)
1. Los 15 sonidos de `script_engine/sfx/` regenerados con ElevenLabs Sound Effects, mismos nombres y duraciones (`make_sfx.py` conserva la lista; el prompt de cada uno al lado: p. ej. `papel`: «hoja de papel deslizándose sobre una mesa de madera, micrófono cerca, seco, sin reverberación, 0.6 s»; `tic`: «clic suave de mecanismo, seco»; `golpe_grave`: «golpe grave y sordo, lejano, sin cola»; `rumor`: «rumor bajo de tierra, 1.2 s»; `whoosh` corto y suave). Nada metálico, nada de cine de acción.
2. Normalizar todos a **−20 LUFS** integrado antes de la ganancia del perfil; las ganancias por bloque en `gfx_config` quedan como están (se recalibran una vez en el reporte si la mezcla suena distinta: medir LUFS del tramo con y sin sfx en 3 bloques).
3. Los viejos a `script_engine/sfx/_f2_sintetizados/` (se mueven).
4. `make_sfx.py` pasa a ser «regenerar con ElevenLabs» con caché: si el wav existe y el prompt no cambió, no llama.

## C. Vajont con el realizador nuevo (Gemini Flash, como hoy; Gemini ≤ US$ 2)
1. `fase2b` del topic copia `f8s3-vajont-f29` (mismo patrón que F28 C: no pisa nada), **solo la capa gfx**: imágenes, clips, voz, música y mapa de intensidad de F28 se reusan. Render en fila (F28 C ya mostró que 3 en paralelo es peor), con NVENC y 6 workers de clips si F28 C los dejó por defecto.
2. Salida `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3.mp4` + hoja de contactos de **los bloques** (un cuadro por bloque, con segundo, tipo, texto, beat) `BLOQUES_v3.jpg`.
3. Reporte por cap: bloques (segundo, tipo, texto, beat, ventana, ya-dicho sí/no), pico con qué bloque, sellos, pregunta, veredictos del crítico, tiempo de gfx por cap. Comparar contra F27: 36 → N bloques, 11 → N sellos, spoilers 2 → 0, pico con bloque 1/7 → 7/7.

## D. Sonnet vs Flash como realizador, caps 5 y 6 (Claude ≤ US$ 2)
1. El mismo paso de forma (dado el candidato y su ventana: tipo de bloque, lado, duración, texto del rótulo dentro del candado literal) con `claude-sonnet-5-5` vía `claude_helpers` (effort low, JSON sin esquema forzado, cruda guardada), **mismo prompt** que Flash salvo el formato de llamada. Solo los caps 5 (giro + avisos) y 6 (pico).
2. Render de esos dos caps con cada realizador → `ch05_gfx_{flash,sonnet}.mp4`, `ch06_gfx_{flash,sonnet}.mp4` y una hoja de contactos de bloques lado a lado. Costo y tiempo por cap de cada uno.
3. Sin decidir: Omar mira los dos. El reporte solo describe diferencias (bloques distintos, tipos distintos, textos distintos).

## Frenos
- Cero reglas de estilo en prompts de guion/escaleta/ficha. Los prompts de gfx cambian solo donde A lo pide (entrada de beats, cuántos por función, sin sellos léxicos).
- No tocar m03, voz, música ni partición. `gfx_templates`/identidad: solo si un bloque nuevo lo requiere (no debería).
- Sin merge, sin publicar, sin borrar (sfx viejos se mueven). `.env`, `config.py`, `lab/_gpt_probe_analista/` fuera de git.
- Suite rápida y amplia verdes (las 5 previas). Un commit por parte. `lab/ESTADO_SESION.md` al final.

## Reporte `lab/hyperframes/f29/F29_REPORT.md`
A: diffs y tests. B: tabla de los 15 sfx (prompt, LUFS antes/después, créditos). C: tabla por cap y comparación contra F27, ruta del `_v3.mp4`, `BLOQUES_v3.jpg`. D: hoja lado a lado y costos. Veredicto íntegro del revisor-handoff. **PARADA.**
