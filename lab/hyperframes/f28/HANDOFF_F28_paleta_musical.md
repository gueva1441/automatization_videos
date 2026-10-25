# HANDOFF F28 — Paleta musical del canal (30 pistas → 12), mapa de intensidad, re-mezcla de Vajont, y render más rápido

Analista · 2026-10-25 · Para CC. Base: `4e18e8a` (rama `f11-guion-v4`). Tres partes. **A termina en PARADA** (el analista elige las 12). B y C van después de esa PARADA, con un prompt nuevo. Topes: ElevenLabs Music según §A.0 · Gemini US$ 3 · Claude 0.

## 0. Por qué
- Las 4 pistas `*_curated` son loops de 60 s del chat 36. Vajont F27: `rising_tension` dio 9 vueltas seguidas en los caps 2–5; costura cada minuto; LRA 16.7 LU (sube y baja sin relación con la voz); tonalidades que chocan en los cortes (Re m → Sol# m → Fa# m → Re m). La mezcla está bien (−24.3 LUFS con música vs −24.6 solo voz): el problema es la unidad, no el volumen.
- m07 nunca generó una pista nueva en producción: el matcher siempre reusa las curated. El `composition_plan` existe solo en `test_music_director_pripyat.py`.
- Omar no quiere oír 30 pistas. Decisión: **medidas (CC) → oído (Gemini) → elección (analista)**. Una vez. Después, el matcher elige de la paleta y nadie genera música por video.

## El sonido del canal (lo que Gemini juzga; lo que los prompts piden)
Misterios Sepultados suena **grave, quieto y paciente**. Un fondo que está debajo de la voz y nunca compite con ella: drones de cello y contrabajo, sub-grave, piano lejano con mucha reverberación, cuerdas sostenidas sin tremolo. **Sin melodía que se recuerde, sin pulso, sin batería, sin voces, sin subidas de tráiler.** Todo en **Re menor** (o Fa mayor / La menor, sus relativas), 55–65 BPM de sensación aunque no haya ritmo. La tensión se construye con densidad y con silencio, no con volumen. Una pista buena se puede escuchar diez veces seguidas sin notar dónde empieza o termina. Referencia de sensación, no de copia: el fondo de los documentales de historia oscura con narrador único.

## A. Paleta: 30 pistas → medidas → Gemini → PARADA (el analista elige 12)
0. **Antes de generar:** una pista de prueba de 3 min. Anotar los créditos que descontó ElevenLabs (panel o cabecera de la respuesta) y traducirlo a US$ con el plan de Omar. Si 30 pistas de 3 min pasan de **US$ 25**, bajar a 20 pistas; si pasan de US$ 40, PARADA y preguntar. Comprobar en la documentación el máximo de `music_length_ms` del endpoint; si no llega a 180000, usar el máximo.
1. **Generar 30 pistas de ~180 s** con ElevenLabs Music, endpoint `detailed` con `composition_plan`, **5 por intent** para hook, setup, rising_tension, shock, consequences, outro (resolution se cubre con outro/consequences). El plan lo escribe Gemini Flash (la función del test de Pripyat, movida a `m07` como `plan_composicion(intent, descripcion_del_canal, largo_ms)`), con 3–5 secciones y estas reglas fijas en el plan: tonalidad Re menor en `positive_global_styles`; `NEGATIVE_GLOBAL_STYLES` de `music_config`; sin fade-in ni fade-out (para loop); primera y última sección con la misma densidad. Cada pista guardada en `audio_library/_paleta_f28/<intent>_<nn>.mp3` + `.json` (prompt, plan, créditos, duración). **No pasan por el gate ni a la librería todavía.** Modo no interactivo.
2. **Medidas (CC, 0 API)** por pista, en `PALETA_medidas.json` y tabla en el reporte:
   - `ffmpeg ebur128`: I (LUFS), LRA (LU), pico.
   - **Pulso:** autocorrelación de la envolvente (o `librosa.beat.beat_track` si se instala): fuerza del pulso 0–1. Más de 0.35 = tiene ritmo.
   - **Melodía:** cromagrama (librosa) → entropía de la distribución de notas por ventana de 2 s; una nota dominante que cambia cada 1–2 s = melodía.
   - **Tonalidad:** perfil Krumhansl sobre el cromagrama → tono y modo estimados.
   - **Brillo en la banda de la voz:** energía 1–4 kHz / energía total, y centroide espectral.
   - **Costura:** correlación entre los últimos 2 s y los primeros 2 s; RMS de ambos (fade).
   - **Parecido:** distancia coseno entre los MFCC medios de cada par de pistas del mismo intent.
   Reglas de poda (CC aplica y marca, no borra): fuera si pulso > 0.35, o tonalidad ≠ Re m / Fa M / La m, o LRA > 12, o banda-voz > 0.30, o fade en costura. Si un intent queda con < 3, decirlo.
3. **Gemini escucha** (Gemini 2.5 Pro con el mp3 como entrada; una llamada por pista, las 30, tope US$ 3): devuelve JSON `{descripcion: 2–3 frases de qué se oye, instrumentos, tiene_melodia, tiene_pulso, suena_a_trailer, compite_con_voz, nota_canal 1–10 contra «El sonido del canal», mejor_intent}`. El prompt lleva el párrafo del sonido del canal literal. Guardar crudo.
4. **Reporte `lab/hyperframes/f28/F28A_REPORT.md`:** tabla de 30 filas (id, intent, medidas, poda, nota Gemini, descripción corta), créditos y US$ gastados, lo que se rompió. Hoja de 30 espectrogramas (`PALETA_espectros.jpg`, 6×5) para el analista. **PARADA.** El analista elige 12 (2 por intent) y las nombra.

## B. (después de la PARADA) Paleta a producción + mapa de intensidad + re-mezcla de Vajont
1. Las 12 elegidas → `audio_library/<intent>_f28_<a|b>.mp3` + `.json` con `music_volume`/`floor` calibrados como las curated (mismo método del chat 40, LUFS objetivo igual). Las `*_curated` quedan en `audio_library/_retiradas/` (se mueven, no se borran). El matcher elige entre las 2 de cada intent; `MUSIC_LENGTH_MS` → 180000 solo informa duración.
2. **Mapa de intensidad por cap** (nuevo, chico): desde los beats de la escaleta del cap (`01a_escaleta.json` + timestamps de la voz), el director marca tramos `silencio | fondo | sube | golpe` con tiempos; `fase2b` los aplica como envolvente de volumen sobre la música (ganancias relativas: silencio −∞ con 1.5 s de fade, fondo = `music_volume`, sube +3 dB, golpe +5 dB y vuelta a fondo en 4 s). Reglas fijas: silencio solo antes del pico del cap y en citas de testigo; nunca más de 2 silencios por cap; `golpe` solo en el beat de pico. Es un mapa de niveles, no audio nuevo. Sin gate.
3. **Re-mezcla de Vajont:** `fase2b` solo audio + stitch (sin tocar imágenes, clips ni gfx) con `--hw-encode` → `output/f8s3-vajont/f8s3-vajont_final_gfx_v2.mp4`. Reportar: pista por cap, mapa de intensidad por cap, LUFS por cap con/sin música, tiempo del pase.
4. Tests sin red: poda sobre medidas sintéticas; mapa de intensidad sobre una escaleta de prueba; envolvente aplicada = ganancias esperadas.

## C. Render más rápido (0 API; variables separadas, medir cada una)
1. `--hw-encode` por defecto en `fase2b` (NVENC p5 cq19, ya medido en F2: PSNR 48.7 dB). Tiempo del pase de segmento y mezcla antes/después.
2. gfx de los caps **en paralelo, 3 a la vez** (`ThreadPool` sobre lo que hoy va en fila en `fase2b`; cada cap su carpeta `gfx_chNN`, ya separadas). RAM y VRAM medidas durante la corrida (32 GB RAM, 3080 Ti 16 GB). Si un cap falla por memoria, bajar a 2.
3. Clips animados `max_workers` 4 → 6.
4. Prueba: re-render completo de Vajont desde los assets (sin regenerar imágenes) con las tres variables; pared total contra los 128 min de F27. Reportar cada variable por separado si se puede (pase por pase).

## Frenos
- Cero reglas de estilo en prompts de guion; esto es audio y render.
- Sin merge, sin publicar, sin borrar (las curated se mueven). `.env`, `config.py`, `lab/_gpt_probe_analista/` no se commitean.
- Topes de §0 y §A.0. `lab/ESTADO_SESION.md` al final de cada parte.

## Reportes
`lab/hyperframes/f28/F28A_REPORT.md` (PARADA para elegir) · después `F28_REPORT.md` con B y C, veredicto íntegro del revisor-handoff. **PARADA.**
