# HANDOFF F4 — De la identidad del lab a producción

**Fecha:** 2026-10-20 01:30 · **Analista:** chat proyecto · **Ejecutor:** CC (sesión nueva) · **Gate:** Omar (2 paradas, desde el celular)
**Base:** `f3-lab-identidad` @ último commit (≥ `9d36be7`). Misma rama hasta el merge. `main` intacta hasta la PARADA 2.
**Leer antes:** `lab/ESTADO_SESION.md`, `CLAUDE.md`, `lab/hyperframes/f3/F3_REPORT.md`, `DECISIONES_F3.md`, `HANDOFF_F3_laboratorio_identidad.md`, `HANDOFF_F3b_lab_foto_por_foto.md`, `DOC_MAESTRO_HyperFrames.md`, y los tres archivos que generó el lab: `gfx_profiles/misterio.json`, `gfx_profiles/misterio_golden_ch02.json`, `IDENTIDAD_misterio.md` (2026-10-20 01:20).

---

## 0. Qué pasó y qué sigue
Omar recorrió los 15 tramos de ch02 en el lab y guardó la identidad (01:20). **Esa identidad es el contrato de estilo del canal.** F4 hace que el director la aplique solo en todos los caps y videos, cierra lo pendiente, y lleva la capa gfx a `main`.

## 1. Lectura de la identidad (lo que el analista ve en `IDENTIDAD_misterio.md`)

### 1.1 Formas aprobadas (van al perfil como default; el director no las cambia)
| Elemento | Forma |
|---|---|
| Movimiento de foto | **acercar** por defecto (11/15); alejar en apertura/cierre de escena; 3D en paisajes; paneo en planos anchos; **nunca quieta** salvo documentos |
| Transición entre tramos | **fundido cruzado 20 f como default** (12/15); corte en ritmo rápido; fundido a negro 1 vez; flash solo en impacto (2/15 máx) |
| Golpe de zoom | **suave** (1.015), 400 ms |
| Dato | M; cifras entran con **sello**, nombres con **cascada**; sin caja; salida fade |
| Recorte | periódico, cascada, −2°, 30 %, sin cinta; **variante "con ícono"** cuando la categoría tiene |
| Sello rojo | **S** (84 px), −3°, con borde, entrada sello |
| Mood | baja, 2.5 s, letterbox en muerte, SFX según mood; agua = **solo sombra que sube** (sin cáusticas) |
| Ícono | bloque L (360 px @2560) + sello + fuente; entrada **tinta** para gota/agua, **sello** para candado/encierro, prensa opcional; hold respirar + pulso; salida tinta seca |
| Nivel de agua | 1 por video, en el pico de agua con cifra |
| Reloj | solo si ≥ 2 horas verificadas; si no, no sale |
| Título | persiana, 3 s, con "CAPÍTULO N · título" |
| Pregunta de cierre | 70 %, persiana, **pausa 3 s**, drone; después **corte a negro 0.75–1 s** |
| Look | viñeta 0.15, grano 0, acento `#c2302f` |

### 1.2 Correcciones del analista a lo marcado (aplicar como regla, no como veto)
1. **Golpe de zoom: 8 en 2 min es demasiado.** Omar aprobó la *forma* (suave), no la *cantidad*. Regla: máx **4 por cap**, nunca dos en la misma frase, nunca dentro de ±5 s del pico. El director elige los 4 de palabras con más peso.
2. **Fundido cruzado como default** cambia el ritmo del canal (hoy era corte). Se acepta, con regla: corte obligatorio cuando la siguiente foto es del mismo lugar en otro momento (evita "slideshow"); el director alterna al menos 1 corte cada 3 transiciones.
3. **Sello S** quedó más chico que el callout; se acepta. Pero el sello dentro del bloque de ícono sigue en M para que se lea junto al ícono L.
4. **Pregunta manual** «Quien fue el culpable?» → el generador debe producir preguntas **de ese tipo**: concretas, ≤ 8 palabras, con sujeto reconocible. El contrato concreto de F3 (prohibidas abstractas) se mantiene; agregar como ejemplos few-shot las de Omar.
5. **Preguntas abiertas del resumen** (subtítulos, color de acento, alejar, paneo, 3D sin ✔): quedan en el valor actual. No preguntarle a Omar.

### 1.3 Dedupe y límites por video (ya existen, se confirman)
Una cifra se anima como contador una sola vez · un fact = un bloque · titulares no se repiten entre caps · nivel de agua 1 · matriz de figuras 1 · flash ≤ 2 por cap.

## 2. Trabajo de CC

### §1 Pendientes que no se cerraron en F3 (verificar primero si ya están; si no, hacerlos)
- 1.1 Mood agua sin cáusticas (solo sombra que sube 1/3 + leve oscurecimiento de bordes). Revisar los otros 3 moods por patrones repetidos visibles.
- 1.2 Pregunta de cierre concreta: contrato F3 + few-shot con «¿Quién fue el culpable?», «¿Qué pasó con los presos del tercer piso?», «¿Por qué nadie abrió las celdas?». Regenerar ch02 y ch05; pegar en el reporte.
- 1.3 Video completo con pausas (música + unión) una vez; confirmar duración = suma de caps + pausas, sin saltos en fronteras.

### §2 El director aplica la identidad (lo central de F4)
- 2.1 `gfx_director.py` lee `misterio.json` (formas + `enabled`) y `misterio_golden_ch02.json` como **few-shot**: en el prompt va el plan dorado resumido (t · palabra · elemento · variante) como "así se arma un capítulo de este canal".
- 2.2 El validador aplica §1.1 y §1.2 como reglas duras (cantidades, alternancia de transiciones, pico, dedupe). El LLM nunca elige formas; solo *dónde* y *qué*.
- 2.3 Transiciones: el director ahora propone la transición por tramo (default fundido cruzado, con la regla de alternancia); `transition_config`/fase2b la respeta solo con `--gfx`.
- 2.4 Prueba: **ch05** desde cero con identidad, sin tocar nada a mano → render looks + página de revisión + cues. Reporte: qué formas usó, cuántos de cada bloque, pico elegido, pregunta generada.
- **PARADA 1 — Omar mira ch05.** Pregunta única: "¿se parece a lo que armé en ch02?" Si no, Omar dice qué no, y se ajusta regla, no el cap.

### §3 Golpe de zoom / empuje / corte+golpe sobre clips de video
Hoy escalan solo fotos fijas. Hacer que escalen también el clip (DepthFlow/Veo) sin congelar el movimiento: transformar el contenedor del video (`scale` en el wrapper, no freeze). Verificar en ch01 (Veo) y ch04 (3D). Tests.

### §4 Render completo de Orleans con identidad
- `looks`, disperso, `--hw-encode` si PSNR OK. `AB_{id}_f4.mp4` (sin gfx | con gfx). Cues de los 7 caps, página de revisión, `F4_REPORT.md` con: bloques por cap, formas usadas, picos, preguntas, tiempos (gfx, concat+música, total, incremental), Gemini, veredictos íntegros.
- Pasar `IDENTIDAD_misterio.md` a `gfx_profiles/IDENTIDAD_misterio.md` versionado (es documentación del canal).
- **PARADA 2 — Omar mira el completo** y decide el merge.

### §5 Merge (solo con OK explícito de Omar en PARADA 2)
- `f3-lab-identidad` → `main` (trae F1, F2, F2b, F3). Sin `--gfx`, segmentos byte-idénticos (md5 `38e5ba14…` en ch02); el final cambia por el concat sin re-encode (ya aceptado: PSNR luma ≥ 50 dB contra fuente).
- Actualizar `REPO_MAP.md`, `ARCHITECTURE.md`, `DOC_MAESTRO_HyperFrames.md` (v1.2: identidad, lab, F4), `CLAUDE.md` (regla: "todo cambio de forma gfx pasa por el lab, no por código").
- Default de producción: `--gfx` **activado** en el flujo del siguiente video, con `--gfx-sparse` y `looks`.

## 3. Deudas que quedan anotadas (no bloquean el merge)
m01b: `cliffhanger`, `timeline` (fecha+hora por evento), coordenadas para mapa v2 · match cut · dominó entre bloques · incremental ≤ 6 min (re-render por ventanas) · vigilante mensual de palabras sin ícono · reloj con horas reales · Shorts.

## 4. Candados
Lock literal (excepción `generated:true` solo para pregunta) · sin shaders · sin rembg · `main` intacta hasta PARADA 2 · tests verdes y revisor por commit · formas solo desde el perfil, nunca desde el LLM · Gemini tope $2 para toda F4.

## 5. Orden
§1 → §2 → **PARADA 1 (ch05)** → §3 → §4 → **PARADA 2 (completo)** → §5 merge. Estimación: §1 2 h · §2 4 h · §3 2 h · §4 2 h · §5 1 h ≈ **11 h de CC**, 2 miradas de Omar (~15 min).

---

## Anexo — MODO NOCTURNO (pedido de Omar al lanzar F4)
Trabajás solo hasta que yo vuelva, sin preguntarme nada. Reglas (las mismas del HANDOFF_F2_nocturno §2):
- Ante una decisión sin regla escrita, elegí lo más conservador, anotalo en DECISIONES_F4.md y seguí.
- Las dos PARADAS del handoff NO paran el trabajo: en PARADA 1 dejás ch05 renderizado con su página de revisión y seguís con §3 y §4; en PARADA 2 dejás el video completo listo y te detenés ahí. Lo único que no hacés sin mí es el merge a main (§5).
- Un render completo máximo. Renders parciales solo --only-cap.
- Gemini tope $2. Si el revisor dice NO CUMPLE dos veces en la misma sección, la dejás sin commit, la anotás y pasás a la siguiente.
- Antes del render completo: RAM libre > 14 GB, Firefox cerrado.
- Al terminar: RESUMEN_NOCHE_F4.md (≤ 40 líneas): qué cerró con commit, qué no y por qué, decisiones por defecto, gasto, tiempos, y máximo 3 preguntas para mí con la opción que ya aplicaste.
