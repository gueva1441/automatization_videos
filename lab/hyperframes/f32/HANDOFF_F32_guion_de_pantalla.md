# HANDOFF F32 — El guion de pantalla: todo lo que se verá, en texto, antes de renderizar

Analista · 2026-10-26 · Para CC. Base: `0253672` (F31). Tres partes A→C; **PARADA al final de C, sin render de video.** API: Claude ≤ US$ 1 (rotulista, 7 llamadas) · Gemini ≤ US$ 0.5. Banco: `f8s3-vajont-f30`. **Esta tanda no produce un mp4.** Produce el guion de pantalla de Vajont, que el analista y Omar leen; el render se pide después, aparte, cuando el guion esté aprobado. Desde ahora este es el orden fijo del pipeline.

## Flujograma (dónde se mete el paso nuevo)
```
voz final + sync map ─┐
escaleta (beats)      ├─► director (Flash): escenas, movimientos, sellos, punches, reloj, agua, lupa
pool (ítems)          ├─► rotulista (Sonnet): textos por beat, anclados a palabra
                      │
                      ▼
            reglas (código) + crítico (Flash, sobre foto)
                      │
                      ▼
   ┌──────────────────────────────────────────────┐
   │  GUION DE PANTALLA (texto + json)             │  ← fase2b --plan-only  (~5 min, sin navegador)
   │  línea por evento · resumen por beat ·        │
   │  qué cortó cada filtro · chequeos automáticos │
   └──────────────────────────────────────────────┘
                      │
          analista lee (a)(b)(c) + propone «DEBERÍA» por línea
                      │
               Omar: «render» / «cambiá X»  ──► cambios = edición del plan (sin re-llamar al modelo si no hace falta)
                      │
                      ▼
              fase2b --gfx (render, ~35 min)  ──► hoja de cuadros (solo forma)
```

## 0. Constantes y origen
| constante | valor | origen |
|---|---|---|
| velocidad de lectura | 15 cps | estándar de subtitulado (ya en F29c) |
| textos por beat | 1; gancho 0–1 | decisión de Omar (26-10) |
| `a_pantalla` en el mismo beat | **pueden salir 2 si van en escenas distintas** | decisión de Omar pendiente — voto del analista: sí; si Omar no dice lo contrario antes de correr, va así y queda anotado |
| texto en el beat `pico` | **solo `a_pantalla`** (lo puso la escaleta); lo demás 0 | ídem (voto del analista: sí) |
| pre-roll del title card | `title_dur` (3 s, identidad); **ch01 sin pre-roll** (ya tiene intro de 2.5 s); **la música del cap arranca con el title card** | ídem (voto: sí a los tres) |
| pregunta de cierre | dura `caracteres ÷ 15 cps`; la pausa de negro que sigue, como hoy (`pause`, F2) | derivado + valor existente |
| ficha, tamaño | dato = `question_px` (tamaño de la pregunta de cierre); etiqueta = `tc_kicker_px` **con la placa que ya usa `.co-text.stamp`** | valores existentes del perfil; decisión de Omar (26-10: «los rótulos siguen grandes»; etiqueta roja 1.2:1 medida en F31) |
| sello | por **tema** de la oración (catálogo: muerte, agua, veneno…), tamaño y placa según lo que Omar elija de F31 (hasta entonces, el de hoy) | decisión de Omar (catálogo, 25-10) |
| punch de zoom | solo en el pico (ya lo hace el zoom_punch de F30b); los `punch_in` del director **fuera** (duplican) | derivado de F30b |

## A. El guion de pantalla (`script_engine/gfx_guion.py`, nuevo; `fase2b --plan-only` lo escribe siempre)
Salida por topic: `output/<topic>/GUION_PANTALLA.md` + `GUION_PANTALLA.json` (misma información; el json es lo que la hoja de cuadros y los chequeos leen después).
### A.1 Línea por evento, en orden del mp4 final (con pre-roll e intro ya sumados)
`mm:ss · chNN · beat n (función) · tipo · «etiqueta | texto» · dura X s (lectura mínima Y s) · escena k (de t a t) · voz −1: … · voz ancla: … · voz +1: … · aporta: … · fuente: id · filtro: pasó / quién lo cortó y por qué`
Tipos: title card, ficha, recorte, cita, persona, lupa, sello, reloj, nivel de agua, contador, punch, pregunta de cierre, **transición** (tipo + razón + escena saliente/entrante), **costura** (negro → title → voz, con los segundos de cada tramo), **silencio de voz** (todo hueco entre palabras mayor que la pausa más larga del propio guion en ese cap: se calcula, no se fija).
### A.2 Resumen por beat
Por beat: función, ventana, escenas que abarca, **propuestos** (director: sellos/punches/reloj/agua/lupa; rotulista: textos), **cortados** por cada regla (cantidad, lectura, no dicho, spoiler, coherencia, zona, candado, crítico) con motivo, **quedan**. Beat vacío de todo → `⚠ BEAT VACÍO`. Cap con 0 textos → `⚠ CAP SIN TEXTO`.
### A.3 Chequeos automáticos (cada uno una línea `✓`/`✗` con el dato)
dos bloques en la misma escena · bloque que cruza corte · texto sin lectura · pregunta de cierre sin lectura · cifra que contradice la voz · `a_pantalla` faltantes (con motivo) · costuras con cuadro no negro (se calcula sobre la mezcla de audio y los tiempos del plan; el video no existe todavía) · **inicio de voz por cap**: segundo esperado vs. segundo medido en la **mezcla de audio** (A.4) y si conserva la rampa (los 100 ms previos al pico no pueden saltar de silencio a −18 dB).
### A.4 Mezcla de audio sin video
`--plan-only` también produce `output/<topic>/_fase2b_work/mezcla_preview.wav` (voz + música + sfx con pre-roll e intro, sin video: segundos de ffmpeg) para medir A.3 y para que Omar pueda **oír** los silencios y las costuras sin render.
### A.5 Cambios a mano
`fase2b --plan-edit <archivo.json>` aplica ediciones al plan (texto, etiqueta, `word_idx`, escena, borrar, agregar un bloque de un ítem del pool) y **regenera el guion sin volver a llamar al rotulista**; el crítico solo corre sobre lo editado. Así el «DEBERÍA» del analista se aplica en minutos.
### A.6 Tests sin red
Guion de un cap de fixture con los tipos cubiertos; beat vacío marcado; cap sin texto marcado; silencio calculado contra la pausa máxima del guion; inicio de voz con rampa pasa y sin rampa falla (fixture con el audio de v5 ch01: tiene que dar `✗ 5.65 s medido vs 5.55 esperado, sin rampa`); `--plan-edit` reemplaza un texto y el guion lo refleja.

## B. Arreglos (cada uno su commit; se verifican en el guion, no en video)
1. **Pre-roll:** la voz se desplaza exactamente `title_dur` **sin perder su ataque** (hoy pierde ~100 ms: en v5 el «Hay» de ch01 arranca en −18 dB a 5.65 s; en v3b subía −28 → −23 → −16 desde 2.55). ch01 sin pre-roll. La música del cap arranca con el title card. Medida: A.3 inicio de voz ✓ en los 7 caps.
2. **Pregunta de cierre:** duración por cps; la pausa como hoy. Medida: A.3.
3. **Lectura contra corte:** si no cabe antes del corte, el bloque **arranca en el primer cuadro de la escena siguiente** (misma oración o la siguiente); solo si tampoco cabe ahí, «sin tiempo de lectura». Medida: en Vajont, D117 vuelve (escena 4 de ch02).
4. **`a_pantalla` documento** (`por_que` dice carta/acta/informe/documento) → tipo `documento` forzado (recorte con kicker real), aunque el modelo lo devuelva como cita. Medida: Q50 sale.
5. **2 `a_pantalla` por beat** en escenas distintas; **`a_pantalla` permitido en el pico**. Medida: D128 y D192 los dos en ch06.
6. **Sellos por tema**: `gfx_intensity`/realizador dejan de cortar «por léxico»; el sello se propone por tema de la oración (tabla chica tema → palabra del mood, código) y el filtro es el catálogo (1 por beat, nunca sobre un texto, nunca dos en la misma escena). `punch_in` del director fuera (el zoom_punch del pico ya está).
7. **Agua / contador / lupa** vuelven por el rotulista: `cifra` con `unidad` ∈ {metros, personas, m³, liras} y la escaleta/pool con `kind` de nivel → `water_level`; cantidad de personas o dinero → `count_up`; `lupa` → `evidence_zoom`. El prompt del rotulista suma **una línea** al tipo `cifra`: «devolvé `unidad` (metros, personas, m³, liras u otra) y `valor` numérico». Nada más cambia en el prompt (md5 nuevo en el reporte).
8. **Ficha un escalón más chica** y etiqueta con placa (§0). Se ve en la hoja de cuadros después; aquí solo se commitea.

## C. Guion de Vajont (sin render)
`fase2b f8s3-vajont-f30 --plan-only --rotulista` → `GUION_PANTALLA.md/.json` + `mezcla_preview.wav`. Copiar a `lab/hyperframes/f32/`. Reporte: la tabla de A.2 completa, los chequeos A.3, costos, tiempo del `--plan-only` (objetivo: minutos, se mide). **No renderizar.** El analista lee el guion y entrega a Omar el semáforo por cap y las líneas con «DEBERÍA»; Omar dice «render» y ahí va otro prompt.

## Frenos
- Prompts de guion/escaleta/ficha intactos. El del rotulista cambia solo por la línea de B.7 (md5 en el reporte). Sin números nuevos fuera de §0. Un commit por parte. Sin merge, sin publicar, sin borrar. `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git. Suite rápida y amplia verdes; `--only-cap ch02` sin `--gfx` byte-idéntico (`--sw-encode`). `lab/ESTADO_SESION.md` al final.

## Reporte `lab/hyperframes/f32/F32_REPORT.md`
A: diffs, ejemplo del guion (un cap entero pegado), tests. B: cada arreglo con su medida en el guion. C: ruta del guion y del wav, tabla A.2, chequeos A.3, costos, tiempo. Veredicto íntegro del revisor-handoff. **PARADA.**
