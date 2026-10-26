Leé `lab/ESTADO_SESION.md` y después, en este orden, `lab/hyperframes/f29b/HANDOFF_F29b_rotulista.md` y `lab/hyperframes/f30/HANDOFF_F30_render_rapido.md`. Base: `1711e88` en `f11-guion-v4`.

La tanda tiene tres etapas, en este orden exacto, y una sola PARADA al final:

1. **F29b parte A** (el rotulista: módulo, prompt, candados, pico único, crítico después, tests sin red). Commit. **No renderices nada todavía** y dejá `gfx_rules.rotulista = False` por defecto hasta la etapa 3.

2. **F30 completo, A → B → C → D** (push safe a ffmpeg, transiciones en el stitch, workers/NVENC medidos, costura solo medida, y el render de validación `_v3b.mp4` con el rotulista apagado y los planes de v3 de caché). Un commit por parte. Si el SSIM o las transiciones no dan lo que pide el handoff, frená ahí, escribí el reporte de F30 con lo que hay y no pasés a la etapa 3.

3. **F29b parte B** (hoja de bloques con la voz al lado y miniatura de celular, planes de los 7 caps con `gfx_rules.rotulista = True`, render `--only-cap ch03` y `--only-cap ch06`), ya con el render rápido. Commit.

Reglas de siempre: una variable por etapa (F30 no cambia qué bloques ni qué transiciones; F29b no toca forma ni velocidad), cero cambios en prompts de guion/escaleta/ficha, workers al máximo donde haya paralelo (las 7 llamadas del rotulista en paralelo; el render gfx en fila), topes de costo de cada handoff, nada de `.env`/`config.py`/`lab/_gpt_probe_analista/`/`gfx_profiles/*` en git, sin merge, sin publicar, sin borrar. Suite rápida y amplia verdes en cada commit; `--only-cap ch02` sin `--gfx` byte-idéntico con `--sw-encode`.

Reportes: `lab/hyperframes/f29b/F29b_REPORT.md` y `lab/hyperframes/f30/F30_REPORT.md`, cada uno con el veredicto íntegro del revisor-handoff. `lab/ESTADO_SESION.md` al final con las tres etapas. **PARADA.**
