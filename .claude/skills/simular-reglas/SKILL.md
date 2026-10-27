---
name: simular-reglas
description: Correr una regla o un filtro de contenido EN SECO contra el guion de pantalla (GUION_PANTALLA.json) o los planes resueltos antes de programarla, y devolver la tabla propuestos → cortados por esa regla → quedan con 3 ejemplos. Usar siempre que un handoff traiga una regla o filtro nuevo, antes de escribir código.
---
# Simular una regla antes de programarla (F33)

Lección de F29c: las reglas del analista se cancelaron con el material (lectura contra cortes de ~10 s, una por beat,
una por escena) y Vajont salió con 2 textos. Simular primero cuesta segundos.

## Entrada
- La **descripción de la regla** (del handoff, literal).
- El guion del topic de prueba: `output/<topic>/GUION_PANTALLA.json` (si no existe o es viejo: `fase2b <topic>
  --plan-only`). Para reglas sobre lo que el guion no trae, los planes `output/<topic>/_fase2b_work/
  gfx_plan_chNN.resolved.json`.

## Cómo
1. Traducir la regla a un predicado de Python sobre un evento `e` del guion (claves: `cap`, `beat`, `funcion`, `tipo`,
   `etiqueta`, `texto`, `dur`, `lectura_min`, `escena`, `escena_t0`, `escena_t1`, `voz_prev`, `voz_ancla`, `voz_next`,
   `aporta`, `fuente`, `filtro`, `queda`, `t`, `t_mp4`, `pool_id`, `regla`). Verdadero (o un texto con el motivo) = la
   regla lo corta. Hay `re` disponible. Si la regla no se puede expresar con lo que trae el guion, decirlo (y qué falta).
2. Correr:
   ```bash
   python lab/tools/simular_regla.py output/<topic>/GUION_PANTALLA.json --nombre "<regla>" \
       [--tipos sello,ficha] [--sobre quedan|todos] --regla "<predicado>"
   ```
   `--sobre quedan` (default): lo que hoy está en pantalla (¿qué más cortaría?). `--sobre todos`: también lo que ya cortó
   otro filtro (¿se solapa con una regla existente?). Para reglas largas, `--archivo regla.py` con `def regla(e)`.
3. Pegar la salida tal cual en el reporte: total y por cap (propuestos → cortados → quedan) y 3 ejemplos con el minuto,
   el texto y la voz.

## Ejemplo (Vajont, guion de F32): «el sello no repite la voz» (DECISIONES: sello = clima)
```bash
python lab/tools/simular_regla.py output/f8s3-vajont-f30/GUION_PANTALLA.json --nombre "el sello no repite la voz" \
    --tipos sello --regla "re.search(r'(?<!\w)'+re.escape(e['texto'].lower())+r'(?!\w)', e['voz_ancla'].lower()) and 'repite la palabra de la voz'"
```
→ **10 propuestos → 10 cortados → 0 quedan** (fuerza, vida, montaña…): la regla, programada así, deja el video sin
sellos; hace falta el vocabulario de clima antes de prenderla.

## Qué no hace
No toca el código del pipeline ni el guion; no llama a ningún modelo. Si la tabla dice que la regla mata casi todo,
eso va al reporte **antes** de programarla, para que decidan Omar y el analista.
