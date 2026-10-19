# Íconos de la capa gráfica (F2b §3)

Set propio de 12 íconos, estilo **grabado / etiqueta de veneno 1890 / forense**: tinta blanco hueso (`#e8e0cc`) y un solo
detalle en el rojo del acento (`#c8102e`). Sin texto dentro del ícono. Nunca estilo ícono de interfaz.

## Cómo se producen

- Motor t2i del pipeline: **`fal-ai/flux-2-pro`** (fal), 1024×1024, semillas fijas para todo el set: 1441, 1442, 1443 (candidatos a/b/c).
- Prompt base fijo: `1890 poison label woodcut, single <objeto>, white ink on pure black background, thick irregular engraved strokes, no text, no letters, centered, isolated`.
- Vectorizado: umbral 140 sobre 768 px, banda de borde 6% borrada, `potrace` (port puro `potracer` 0.0.4), turdsize 20; quedan las curvas dentro de la caja del sujeto (caen manchas y rayones). Acento rojo = un hueco chico del sujeto (0.3–6 % del área); si no hay, sin acento.
- Regenerar: `python script_engine/gfx_icons/make_icons.py gen | trace | strip <fondo.jpg>` (cada paso cachea).
- PNG crudos: `lab/hyperframes/f2b/icons_raw/` (fuera de git). Candidatos: `candidates/`. Aprobados: `<clave>.svg` en esta carpeta.
- Respaldo: `lucide/` (lucide-static 0.460.0, licencia ISC incluida), restilizado por código al mismo color y trazo grueso con filtro de tinta. Solo para claves rechazadas dos veces (token `icon_fallback_lucide`).

## Set (prompt y semilla por candidato)

| # | clave | objeto (prompt) | a | b | c |
|---|---|---|---|---|---|
| 1 | `calavera` | human skull | seed 1441 · 255 paths · acento | seed 1442 · 209 paths | seed 1443 · 268 paths |
| 2 | `gota` | drop of liquid | seed 1441 · 100 paths | seed 1442 · 39 paths · acento | seed 1443 · 43 paths |
| 3 | `llama` | flame | seed 1441 · 57 paths · acento | seed 1442 · 46 paths · acento | seed 1443 · 83 paths · acento |
| 4 | `biohazard` | biohazard symbol | seed 1441 · 152 paths · acento | seed 1442 · 129 paths · acento | seed 1443 · 158 paths · acento |
| 5 | `reloj` | pocket watch | seed 1441 · 199 paths · acento | seed 1442 · 104 paths · acento | seed 1443 · 150 paths · acento |
| 6 | `candado` | padlock | seed 1441 · 193 paths · acento | seed 1442 · 156 paths · acento | seed 1443 · 62 paths · acento |
| 7 | `ojo_tachado` | eye crossed out by one diagonal slash | seed 1441 · 106 paths · acento | seed 1442 · 247 paths · acento | seed 1443 · 96 paths · acento |
| 8 | `balanza` | balance scale of justice | seed 1441 · 93 paths · acento | seed 1442 · 182 paths · acento | seed 1443 · 273 paths · acento |
| 9 | `cruz` | grave cross | seed 1441 · 113 paths · acento | seed 1442 · 85 paths · acento | seed 1443 · 77 paths · acento |
| 10 | `persona` | standing human figure | seed 1441 · 147 paths · acento | seed 1442 · 86 paths · acento | seed 1443 · 122 paths · acento |
| 11 | `edificio_ruina` | ruined building | seed 1441 · 571 paths · acento | seed 1442 · 344 paths · acento | seed 1443 · 738 paths · acento |
| 12 | `pregunta` | question mark symbol | seed 1441 · 96 paths · acento | seed 1442 · 110 paths · acento | seed 1443 · 75 paths · acento |

## Elección de Omar (PARADA 2)

Omar eligió (19-oct): **1b, 2a, 3a, 4a, 5b, 6a, 7a, 8b, 9b, 10b, 11b, 12a** → `<clave>.svg` (script `script_engine/gfx_icons/approve.py`).

Acento rojo solo donde significa algo:
- calavera: dos óvalos rojos detrás de la tinta, que se ven por las cuencas de los ojos (ubicados a mano).
- candado: la cerradura (el hueco que marcó el trazado).
- cruz: un clavo rojo en el cruce de los maderos (ubicado a mano; la cruz entera en rojo se leería como "Cruz Roja").
- Los otros 9: sin rojo.
