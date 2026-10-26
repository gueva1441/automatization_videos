Abrí una sesión nueva para esta tanda, como en F25c, con el contexto cargado desde cero: leé `CLAUDE.md`, `lab/ESTADO_SESION.md` y después, en este orden, `lab/hyperframes/f29c/HANDOFF_F29c_rotulista_por_beat.md`, `lab/hyperframes/f30b/HANDOFF_F30b_transiciones_por_relato.md` y `lab/hyperframes/f31/HANDOFF_F31_lab_forma.md`. Pensamiento en high. Base: `d7fac3c` en `f11-guion-v4`. Omar duerme: la tanda corre entera sin preguntar; lo que no se pueda decidir se anota como «pendiente de Omar» y se sigue.

Tres etapas, en este orden, una PARADA al final:

1. **F29c completo** (A → B): reglas por beat, ficha = title card, prompt nuevo tal cual está en A.5 (md5 en el reporte), arreglos de B, render completo **v4** y hoja. Si alguna medida de B.4 no da, se anota y **se sigue igual** a la etapa 2 (son independientes).

2. **F30b completo** (A → C): transiciones por relato, costura sin gris ni blanco, title card con aire (pre-roll de `title_dur`), chascada `«»` en el `.ass`, render completo **v5** y hoja de costuras. Si el pre-roll no se puede hacer sin tocar el `.wav` de voz o sin romper el md5 de ch02 sin `--gfx`, **no lo forcés**: dejá el pre-roll fuera, anotalo como pendiente, y rendericé v5 con el resto.

3. **F31** (una parte): los 11 renders `--only-cap ch06` con las variantes detrás de flags, la hoja `VARIANTES_ch06.jpg` a 360 px y las medidas. **Nada queda como default.**

Reglas de siempre: una variable por etapa, cero cambios en prompts de guion/escaleta/ficha, ningún número nuevo que no esté en la tabla §0 de cada handoff (si hace falta uno, «pendiente de Omar» y el valor que ya exista), workers al máximo donde haya paralelo y el render gfx en fila, Firefox cerrado (cierre normal) antes de cada render, topes de costo de cada handoff (Claude ≤ 2 en total en la tanda), nada de `.env`/`config.py`/`lab/_gpt_probe_analista/`/`gfx_profiles/*` en git, sin merge, sin publicar, sin borrar. Un commit por parte. Suite rápida y amplia verdes en cada commit; `--only-cap ch02` sin `--gfx` byte-idéntico con `--sw-encode`.

Reportes: `F29c_REPORT.md`, `F30b_REPORT.md`, `F31_REPORT.md`, cada uno con el veredicto íntegro del revisor-handoff. `lab/ESTADO_SESION.md` al final con las tres etapas y, arriba de todo, **una lista de qué tiene que mirar Omar al despertar: `_v4.mp4`, `_v5.mp4`, `BLOQUES_v4.jpg`, `COSTURAS_v5.jpg`, `VARIANTES_ch06.jpg`**. **PARADA.**
