# HANDOFF F61b — 10 fotos de los planos medios con persona (¿vivas o posadas?)

Modelo → CC: Opus medium. Las 10 fotos a la vez (tope `FLUX_MAX_WORKERS`); la mirada ciega en un subagente aparte.

## Por qué
F61 bajó el plano general de 75 % a 49 % (en texto). Falta ver si los planos medios con persona salen **vivos** (acción, emoción) o **posados** (foto de carnet, todos a cámara): varios prompts dicen «posing», «everyone facing the camera». Eso solo se ve en fotos. Si salen posadas, la causa está en la acción que escribe m03 y es otra tanda; F61 no se toca acá.

## Constantes
| valor | origen | quién |
|---|---|---|
| 10 fotos | voto del analista, aprobado | Omar 2026-10-30 23:07 |
| ≈ US$ 0,035 por foto | medido en F60 B+C (41 × 0,035) | existente |

## Módulos tocados
- Ninguno de producción. Solo un runner de lab nuevo: `lab/hyperframes/f61/etapa_f61b_fotos.py`.

## Reglas fijas
- Rama `f11-guion-v4`; producción intacta (mismo control de mtimes que `f60/etapa_bc_prueba.py`).
- Prompts **tal cual** salen en `lab/hyperframes/f61/03_visual_f61.json` (no se reescriben); armado y foto con las funciones de producción de F60 (`_madres_para_item`, `persona_aporta_madre`, Seedream `/edit` con las madres, o t2i si no hay madre), **una foto por llamada** (la secuencia no es lo que se mide).
- Madres: las de la prueba F60 B+C (`lab/hyperframes/f60/bc/output/123bbb64-9fca-4395-8bf4-57d60e219ef1/foto_madre/`). No se generan madres nuevas.
- **Chascada:** el runner nuevo llama a `cost_tracker.start_video` con un id de lab (`lab_f61b`), no con el TID de producción, para no ensuciar `data/cost_history.json`. Los runners viejos no se tocan.
- Sin tope de dólares; el costo se informa.

## Las 10 fotos (elegidas por el analista: personas, caps, 1 y 2 personas, y los prompts con «posing»)
| # | ítem en `03_visual_f61.json` | plano | persona | año |
|---|---|---|---|---|
| 1 | `chapters[0].supplemental_image_prompts[0]` | medium | Daniel Écija, María Bernal | 1962 |
| 2 | `chapters[0].supplemental_image_prompts[1]` | medium | Daniel Écija | 1962 |
| 3 | `chapters[1].image_prompts[1]` | medium | Daniel Écija, María Bernal | 1962 |
| 4 | `chapters[1].image_prompts[5]` | medium | Milagros Barroso, Ramón de Juan | 1962 |
| 5 | `chapters[1].image_prompts[7]` | medium | Víctor Calvo | 1962 |
| 6 | `chapters[2].image_prompts[5]` | close | Eric Saint | 1948 |
| 7 | `chapters[3].image_prompts[9]` | medium | Daniel Écija | 1962 |
| 8 | `chapters[3].image_prompts[12]` | medium | María Bernal, Daniel Écija | 1963 |
| 9 | `chapters[4].image_prompts[12]` | medium | Daniel Écija (1991: sin madre por era) | 1991 |
| 10 | `chapters[4].image_prompts[7]` | close | Daniel Écija hijo | 1985 |
Si alguna ruta no existe o el ítem no coincide con plano/persona/año, PARÁ y reportá (no la reemplaces).

## Etapa única
1. Generar las 10 fotos (salidas en `f61/b/`).
2. Hoja `f61/b/hoja_f61b.jpg`: por foto, la(s) madre(s) usadas + la foto + debajo «#, plano pedido, persona, ancla (primeras 12 palabras)».
3. Mirada ciega (subagente que NO lee este handoff ni los prompts, solo la hoja y la lista de planos pedidos), por foto, 1–10 y una línea:
   - **viva o posada** (¿hay una acción o emoción, o es un retrato quieto a cámara?);
   - **plano real** (¿coincide con el pedido?);
   - **cara visible** (sí/no);
   - **parecido a la madre** (si hay madre).
   Íntegra en `f61/b/MIRADA_F61b.md`.
4. En `F61_REPORT.md` §F61b: tabla de las 10 (archivo, madres usadas, segundos, costo), la mirada íntegra, costo total y el veredicto íntegro del revisor-handoff. ESTADO actualizado.

## PARADA
Nada más. El analista mira la hoja con Omar.
