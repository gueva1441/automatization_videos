# Endpoints Nano Banana / Gemini image en fal

Esquemas leídos del OpenAPI de fal el 2026-11-01 (`run_lab.py descubrir`); precios del `llms.txt` de cada modelo y de `api.fal.ai/v1/models/pricing`. Sin gasto.

| Modelo | Tipo | Endpoint | safety_tolerance | enable_safety_checker | 16:9 | Resolución | Precio |
|---|---|---|---|---|---|---|---|
| nb_lite | text-to-image | `google/nano-banana-lite` | sí, 1–6, default 4 | no | sí | fija, 1K según la ficha | tokens: imagen US$ 0,3125/M entrada, 37,50/M salida; texto 0,3125/M y 1,875/M |
| nb_lite | edit | `google/nano-banana-lite/edit` | sí, 1–6, default 4 | no | sí | fija, 1K según la ficha | tokens: imagen US$ 0,3125/M entrada, 37,50/M salida; texto 0,3125/M y 1,875/M |
| nb2_lite | text-to-image | `google/nano-banana-2-lite` | sí, 1–6, default 4 | no | sí | fija, 1K según la ficha | tokens: imagen US$ 0,3125/M entrada, 37,50/M salida; texto 0,3125/M y 1,875/M |
| nb2_lite | edit | `google/nano-banana-2-lite/edit` | sí, 1–6, default 4 | no | sí | fija, 1K según la ficha | tokens: imagen US$ 0,3125/M entrada, 37,50/M salida; texto 0,3125/M y 1,875/M |
| nb2 | text-to-image | `fal-ai/nano-banana-2` | sí, 1–6, default 4 | no | sí | 0.5K, 1K, 2K, 4K (default 1K) | US$ 0,08 por imagen a 1K |
| nb2 | edit | `fal-ai/nano-banana-2/edit` | sí, 1–6, default 4 | no | sí | 0.5K, 1K, 2K, 4K (default 1K) | US$ 0,08 por imagen a 1K |
| nb21 | text-to-image | `google/nano-banana-2.1` | sí, 1–6, default 4 | no | sí | 1K, 2K, 4K (default 1K) | tokens: imagen US$ 1,764/M entrada, 35,294/M salida; texto 1,764/M y 8,823/M |
| nb21 | edit | `google/nano-banana-2.1/edit` | sí, 1–6, default 4 | no | sí | 1K, 2K, 4K (default 1K) | tokens: imagen US$ 1,764/M entrada, 35,294/M salida; texto 1,764/M y 8,823/M |
| nbpro | text-to-image | `fal-ai/nano-banana-pro` | sí, 1–6, default 4 | no | sí | 1K, 2K, 4K (default 1K) | US$ 0,15 por imagen a 1K |
| nbpro | edit | `fal-ai/nano-banana-pro/edit` | sí, 1–6, default 4 | no | sí | 1K, 2K, 4K (default 1K) | US$ 0,15 por imagen a 1K |

Referencia en edit: `image_urls` (lista). Los 5 modelos aceptan la tolerancia 6, ninguno necesitó el máximo alternativo y ninguno queda como control.

## Otros ids del catálogo que no se corren

Ids distintos del mismo nombre o familia; por el nombre parecen alias, no está medido que den lo mismo. Se corre uno por modelo:

- **nb2:** fal-ai/gemini-3.1-flash-image-preview
- **nb21:** fal-ai/nano-banana-2.1
- **nbpro:** google/nano-banana-pro, fal-ai/gemini-3-pro-image-preview
- **Generación anterior, fuera de la lista del handoff:** `fal-ai/nano-banana`, `fal-ai/gemini-25-flash-image` (con sus `/edit`).
