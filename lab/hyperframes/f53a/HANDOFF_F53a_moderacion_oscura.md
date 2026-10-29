# HANDOFF F53a — ¿Gemini Omni Flash aguanta el contenido oscuro del canal? (lab, sin tocar producción)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · solo `lab/hyperframes/f53a/`

## Por qué
En F52 ganó Gemini Omni Flash 1.1 (G) en los dos caps; respaldo: Seedance 2.5 (S). Omar (14:24): G a 1080p. Pero los 8 clips de F52 no tenían contenido fuerte (Wittenoom no trae cadáveres ni muertos), y DECISIONES exige un motor permisivo con el canal (cuerpos, ahorcados). Ningún schema de video trae campo de tolerancia. Antes de pasar G a producción hay que ver si rechaza o modera las fotos más oscuras que el canal ya generó.

## Antes de escribir (método)
- ¿Construye sobre algo a reemplazar? No: lab. Producción (Veo) se toca recién en F53b, con el resultado de esto.
- ¿Cambia el orden? Sí, a favor: va antes de F53b (G a producción).

## Constantes
| constante | valor | origen | quién |
|---|---|---|---|
| fotos | 2, las más fuertes ya generadas por el canal (no se generan nuevas) | derivado: CC las elige buscando en los prompts de los topics de `output/` y `data/scripts/_steps/` (Orleans, Vajont…) los que piden cuerpos, cadáveres, ahorcados o víctimas; lista los candidatos y elige las 2 más explícitas | analista |
| modelos | G y S | F52 (ganador y respaldo) | Omar 14:24 / analista |
| duración | 4 s | mínimo común de los schemas (G 3–10, S 4–30); la moderación no depende del largo | derivado |
| resolución | la más baja del schema (G 360p, S 480p) | la moderación no depende de la resolución; abarata | derivado |
| audio | S `generate_audio` false; G sin campo (se descarta) | F52 | ya en el proyecto |
| prompt de movimiento | el de F52b: `f52/prompts_video.py` (Opus 5.5 high, mira la foto, ficha `f52/guias/{G,S}.md`), con el `video_prompt` vivo del topic si existe; si no existe, «APPROVED MOTION» = «(none)» | F52b | Omar 13:50 |
| tope de la tanda | US$ 4 | derivado: precio leído × multiplicador por resolución desconocido (en 1080p G cobró ×5; peor caso ×5 en las dos: G 2 × 4 s × 0,15 = 1,20; S 2 × ≈ 0,8 = 1,60; Opus ≈ 0,15) ≈ 3,0 + margen | Omar confirma al pegar |

## Módulos
Producción: ninguno. Nuevo en lab: `f53a/moderacion.py` (reusa funciones de `f52/prompts_video.py` y `f52/prueba_video.py` importándolas, sin copiarlas).

## Etapas (paralelo al máximo)
### Etapa 0
`DECISIONES.md`: «2026-10-29 14:24 · **F52 elige:** Gemini Omni Flash 1.1 a 1080p como motor de clips (respaldo Seedance 2.5); costo real G ≈ US$ 0,15/s a 1080p (panel de fal: ×5 sobre 0,03) · Omar · F52» y «2026-10-29 14:30 · **F53a:** prueba de moderación de G y S con las 2 fotos más oscuras ya generadas del canal, 4 s, resolución mínima; solo lab · Omar · F53a». `lab/TOPE_TANDA.json` = 4. md5 del handoff en el commit.
### Etapa 1 — elegir las 2 fotos (US$ 0)
Tabla de candidatos (topic, cap, archivo, prompt recortado a 200 caracteres, por qué es fuerte) y las 2 elegidas. Las fotos se copian a `f53a/fotos/` (sin commitear png).
### Etapa 2 — 4 prompts (≈ US$ 0,15) y 4 clips
4 prompts (2 fotos × G, S) con el camino de F52b; se pegan enteros en el reporte. Sin PARADA intermedia (la prueba es de moderación, no de calidad). Guarda de tope antes de llamar. 4 llamadas en paralelo, foto con tipo leído de los bytes.
Por clip: endpoint, campos enviados, ffprobe, costo (precio leído **y** anotar que el real se confirma en el panel), y **rechazo/moderación con el mensaje literal**; si el clip sale pero el modelo suavizó (tapó el cuerpo, lo borró, cambió la escena), decirlo mirando cuadros a 0/1/2/3/4 s (hoja de contactos `f53a/contactos.png`, skill ver-render).
### Salida
`F53a_REPORT.md`: tabla por clip, lo abierto, veredicto íntegro de `revisor-handoff`. **PARADA: el analista y Omar deciden G o S para F53b.**

## Reglas fijas
No tocar producción. No generar fotos nuevas. No commitear mp4/png.
