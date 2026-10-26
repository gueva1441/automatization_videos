# HANDOFF F30 — Render rápido: el navegador solo pinta bloques

Analista · 2026-10-25 · Para CC. Base: el commit final de F29b A (o `1711e88` si F29b A no corrió). Tres partes A→C; **PARADA al final de C**. API: 0 (todo es ffmpeg y HyperFrames; los planes de gfx se reusan de caché). Banco: Vajont `f8s3-vajont-f29` (plan de v3). **Una variable: dónde se dibuja cada cosa. El video tiene que salir igual.** El rotulista (`gfx_rules.rotulista`) queda **apagado** en esta tanda aunque F29b A ya esté commiteado.

## 0. Diagnóstico (medido en `_fase2b_work/gfx_chNN.log` de v3; detalle en `claude/ANALISIS_render_tiempo_2026-10-25.md`)
- gfx = 59 min de 64. Navegador ≈ **3.5 s por segundo de video cubierto** (1440p, 5 workers); costo fijo por cap ≈ 130 s (plan 45 + re-encode 20 + templater 15 + stitch 50).
- Cobertura del «sparse»: ch01 17 % (50 s) · ch07 26 % (143 s) · **ch02–06 86–100 % (409–593 s)**.
- Causa: `gfx_sparse.event_windows` l.70 `if s.safe: iv.append((s.start, s.end))` → cada escena con rostro/manos (router anti-deformación: PNG + push) entra **entera** al navegador; en caps flux la mitad de las escenas son safe (ch06: 8/16). Más una ventana por **cada transición** (l.75, ~2 s × 15 cortes) y márgenes de 0.5 s → la fusión cubre el cap. ch01/ch07 son híbridos (`is_flux` False) → sin safe → 17–26 %.
- Meta: cobertura = solo bloques (~15 %, lo que ya da ch01). Estimado gfx 59 → ~15–20 min; render 64 → ~25. No es promesa: se mide.

## A. El push «safe» lo hace ffmpeg (tiempo)
Hoy: para una escena safe, HF dibuja el PNG (`public/safe/safe_NN.png`) con `gsap scale 1→1.08 sine.inOut` (push), `translateX` 3 % (pan) o fin en escala 1 (pull/static), tapando el video del base durante toda la escena (`scene.html.tmpl`, `gfx_project._scene_html`). Por eso la escena entera necesita el navegador.
1. **Nuevo paso antes del gfx, en `gfx_layer` (o módulo `gfx_safe_bake.py`):** para cada escena con `s.safe`, ffmpeg genera el tramo de esa escena desde el PNG con el **mismo movimiento** y lo **reemplaza en el base** (`public/base.mp4`, mismo fps/tamaño/GOP del re-encode `-g30`):
   - push: `zoompan` con `z = 1 + (S−1)·(0.5 − 0.5·cos(π·on/N))` (S = `gfx_rules.safe_push_scale` = 1.08, N = cuadros de la escena), centro en `safe.origin` (fracciones de ancho/alto) → `x = ox·iw − iw/zoom·ox`, `y` ídem; `s=2560x1440:fps=30`. Es la misma curva seno que gsap.
   - pan: `crop` con `x` lineal desde 0 hasta `safe_pan_frac·iw`, sobre el PNG escalado 1.04 (hoy `translateX(... ) scale(1.04)`).
   - pull/static: como hoy en HF (termina en escala 1): pull = `zoompan` de 1.08 → 1.00; static = imagen fija.
   - El PNG se rasteriza a 2560×1440·S antes del `zoompan` para no suavizar (el navegador también reescala; medir SSIM, A.4).
2. `gfx_sparse.event_windows`: **quitar** la línea 70 (`if s.safe`). La escena safe ya está cocida en el base; si una ventana de bloque cae encima, HF muestra el **video** del base (no el PNG): en `_scene_html`/`_freeze_img`, una escena safe **cocida** se trata como escena normal (solo `<video>`; sin `safe_NN.png`, sin `gsap scale`). El freeze del saliente sale del base como en las demás.
3. `cut_base`/`stitch` sin cambios (el base ya trae el movimiento; las uniones base↔HF siguen con `XFADE_FRAMES`).
4. **Medida:** por cap, cobertura antes/después y segundos de HF; **SSIM** (`ffmpeg -lavfi ssim`) entre el tramo de 3 escenas safe del `ch06_gfx.mp4` de v3 y el nuevo, ≥ 0.95 (el resto del cap ≥ 0.98); hoja de contactos de esas 3 escenas lado a lado (inicio / mitad / fin de la escena). Si el SSIM baja de 0.95, se compara el centro del push (origen) y la curva, no se acepta «se ve parecido».
5. Tests sin red: `event_windows` con una escena safe no abre ventana; `zoompan` genera N cuadros exactos; el base conserva duración y fps; `--only-cap ch02` sin `--gfx` sigue byte-idéntico (`--sw-encode`; el bake solo corre con `--gfx`).

## B. Las transiciones las hace ffmpeg, en el stitch (tiempo)
Hoy: HF dibuja dissolve (freeze del saliente + fundido 20 f), dip (10 f a negro), flash (3 f) y cut_punch dentro de las ventanas, y `event_windows` l.75 abre una ventana por transición. **Las reglas de qué transición va dónde no cambian** (`gfx_style.identity_transitions` queda intacto; eso es F30b).
1. `gfx_sparse.event_windows`: **quitar** la contribución de l.75 (ventana por transición). Ventanas = bloques (title, rótulos, recortes, sellos, pregunta, reloj, agua, zoom, punch) ± margen, como hoy.
2. **`stitch`** recibe `transitions_of(plan, scenes)` y los cortes de escena (`scenes[i].start`, ya «snapped» a cuadro): el grafo deja de ser «base entre ventanas» y pasa a ser **«tramos entre cortes de escena»**, cada unión con su transición: `cut` → concat seco; `dissolve` → `xfade=fade` de `frames` cuadros; `dip` → `xfade=fadeblack`; `flash` → `xfade=fadewhite` de 3 f; `cut_punch` → concat seco + `zoompan` de 1.0→1.06→1.0 en 10 f sobre el entrante (como lo hace hoy HF; si no es igual, anotar y dejar corte seco). El tramo que cae dentro de una ventana HF viene del render HF, los demás del base; las uniones base↔HF siguen con `XFADE_FRAMES` como hoy.
3. **Transición que cae dentro de una ventana HF** (un bloque cruza un corte, pasa en ch01/ch03/ch06): HF la sigue dibujando como hoy en esa ventana (la ventana ya la contiene) y `stitch` no la aplica dos veces. Regla simple: `stitch` aplica solo las transiciones cuyo instante no está dentro de `[a, b)` de ninguna ventana.
4. El freeze de 0.667 s del saliente (`fz` en `scene_NN.html`) deja de existir fuera de ventanas (el xfade no lo necesita). Dentro de ventanas, como hoy.
5. **Medida:** mismas transiciones, mismos instantes (volcar `transitions_of` antes/después: idéntico); SSIM ≥ 0.95 en ±1 s de 5 cortes de ch06 (1 cut, 2 dissolve, 1 dip, 1 flash) contra v3; cobertura por cap; segundos de HF por cap.
6. Tests sin red: el grafo de `stitch` para un cap de 4 escenas con [cut, dissolve, dip] produce el filter_complex esperado (string); una transición dentro de una ventana no se aplica en `stitch`; duración total del cap exacta a ±1 cuadro.

## C. Chascadas de tiempo (medidas, no supuestas)
1. **Workers 5 → 8** (`GfxRenderSettings.workers`): `--only-cap ch06 --gfx` con 5 y con 8 **después** de A y B, mismo plan; tiempo de HF y RAM libre mínima. Si 8 no baja ≥ 15 % o la RAM libre cae de 6 GB, se queda en 5 y se anota.
2. **`stitch` + grade con NVENC** (`_venc()` de fase2b ya existe): el intermedio `chNN_gfx.mp4` sale con NVENC cq 23 en vez de `libx264 ultrafast crf 16`. Tiempo del stitch por cap antes/después. El candado md5 sin `--gfx` no se toca (`--sw-encode`).
3. **Costura entre caps, solo medir:** a 30 fps, en `_concat_video.ts` y en el mp4 final, los 6 cuadros alrededor de cada frontera de cap: anotar en qué archivo aparece por primera vez el **cuadro gris 50 %** y el flash blanco (`whip_pan_flash` → `fadewhite`, `transition_applier._XFADE_MAP`). **No arreglar** en esta tanda (es F30b); solo decir de dónde salen.

## D. Render de validación (el «antes» limpio de F29b)
`fase2b` sobre `f8s3-vajont-f29` con `--reuse-visuals --gfx --gfx-sparse`, **rotulista apagado**, planes de gfx de v3 reusados de caché (mismos bloques, mismas transiciones): salida `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3b.mp4`. Tabla por cap: cobertura v3 → v3b, HF s, total gfx s, SSIM (A.4, B.5), pared total. **Objetivo medido, no prometido:** gfx ≤ 20 min, pared ≤ 30 min, SSIM ≥ 0.95 donde se midió, bloques y transiciones idénticos en instante y tipo.

## Frenos
- No se toca qué bloques salen ni qué transición va dónde (`gfx_style`, `gfx_director`, realizador, crítico intactos). No se tocan prompts. `gfx_templates`: solo `scene.html.tmpl` para la escena safe cocida.
- Render en fila (F28 C). Sin merge, sin publicar, sin borrar; `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git.
- Un commit por parte (A, B, C). `lab/ESTADO_SESION.md` al final. Suite rápida y amplia verdes.

## Reporte `lab/hyperframes/f30/F30_REPORT.md`
A: diffs, SSIM y hoja de las 3 escenas safe. B: diff, volcado de transiciones antes/después, SSIM de los 5 cortes. C: tabla workers 5/8, stitch antes/después, origen del cuadro gris. D: tabla por cap y total 64 → N. Veredicto íntegro del revisor-handoff. **PARADA.**
