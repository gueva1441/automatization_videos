# VISION_F50h — puntaje por elemento con Gemini Flash, por letra (F50h etapa 3)

Salida de `python lab/hyperframes/f50h/f50h.py --vision` y `--tabla`. Una llamada por png con el cliente y el modelo de `script_engine/gfx_critic.py` y el prompt exacto del handoff; el modelo no ve la variante, el prompt ni el nombre del archivo. Por letra (A/B/C), **no por variante**: la llave no se abrió.

Puntaje por png = sí / (sí + no); `not_visible` aparte. Por foto y letra: la media de los 2 png.

## Total por letra

| letra | puntaje medio | png medidos | not_visible | invented_text | huecos |
|---|---:|---:|---:|---:|---:|
| A | 0.873 | 39 | 51 | 5 | 1 |
| B | 0.903 | 40 | 47 | 5 | 0 |
| C | 0.887 | 40 | 55 | 4 | 0 |

## Por foto

| foto | A puntaje · nv · inv | B puntaje · nv · inv | C puntaje · nv · inv |
|---|---|---|---|
| 1/2 | 0.688 · 0 · 0 | 0.812 · 0 · 0 | 1.0 · 3 · 0 |
| 1/3 | 0.722 · 0 · 0 | 1.0 · 0 · 0 | 0.945 · 0 · 0 |
| 1/4 | 1.0 · 0 · 0 | 1.0 · 0 · 0 | 1.0 · 0 · 0 |
| 2/9 | 1.0 · 6 · 0 | 0.812 · 3 · 0 | 0.5 · 0 · 0 |
| 2/11 | 1.0 · 1 · 0 | 1.0 · 0 · 0 | 0.857 · 0 · 0 |
| 2/15 | 0.928 · 3 · 0 | 0.833 · 4 · 0 | 0.916 · 4 · 0 |
| 3/3 | 0.873 · 2 · 0 | 0.945 · 2 · 0 | 0.666 · 0 · 0 |
| 3/6 | 1.0 · 4 · 0 | 0.889 · 4 · 0 | 1.0 · 4 · 0 |
| 3/10 | 1.0 · 6 · 0 | 0.938 · 0 · 0 | 0.857 · 2 · 0 |
| 4/1 | 1.0 · 3 · 0 | 0.812 · 3 · 0 | 1.0 · 6 · 0 |
| 4/11 | 1.0 · 4 · 0 · 1 hueco | 0.857 · 2 · 0 | 1.0 · 5 · 0 |
| 4/12 | 0.75 · 1 · 0 | 0.938 · 1 · 0 | 1.0 · 2 · 0 |
| 5/1 | 0.714 · 0 · 2 | 0.857 · 2 · 2 | 0.857 · 3 · 2 |
| 5/8 | 0.688 · 2 · 1 | 0.775 · 7 · 1 | 1.0 · 4 · 0 |
| 5/13 | 0.817 · 5 · 0 | 0.9 · 7 · 0 | 0.857 · 4 · 0 |
| 5/16 | 1.0 · 4 · 0 | 1.0 · 4 · 0 | 0.875 · 7 · 0 |
| 6/5 | 0.544 · 1 · 0 | 0.688 · 0 · 0 | 0.544 · 1 · 0 |
| 6/15 | 1.0 · 1 · 2 | 1.0 · 0 · 2 | 1.0 · 0 · 2 |
| 7/7 | 1.0 · 7 · 0 | 1.0 · 4 · 0 | 1.0 · 8 · 0 |
| 7/9 | 0.803 · 1 · 0 | 1.0 · 4 · 0 | 0.857 · 2 · 0 |
