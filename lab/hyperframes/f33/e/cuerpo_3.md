
Programada así, la regla deja el video sin sellos: hace falta el vocabulario de clima (pendiente de Omar) antes de
prenderla.

## E — Verificación
Suite rápida 58 · suite amplia **1003 + 5 previas** (01b_pauses ×3, m03_merge_timing ×2; incluye
`test_constantes_con_origen.py` y `test_module_f33.py`) · md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`)
**`38e5ba14…`** en A, B, C, D y E (`lab/hyperframes/f33/{a,b,c,d,e}/`) · hook de render probado en seco con Vajont: bloquea
(arriba).

## Valores de formato (no del pipeline) que aparecen en hooks, tests y herramientas (§0)
- Timeout de los dos hooks nuevos en `settings.json`: 30 s (el mismo de `guard_git` y `tope_tanda`).
- `simular_regla.py`: 3 ejemplos por defecto (`--ejemplos`), el número que pide el handoff.
- Tests: tamaños de fixtures (dos planes de juguete, 20 ms entre archivos para el orden de mtime, +5 s para un plan «más
  nuevo»); el test de constantes exige > 100 constantes encontradas (hoy 101) para saber que el parser leyó las clases.

## Lecturas de CC (declaradas)
1. **«identidad F3»** = la constante vale lo mismo que el token del perfil `misterio` (la identidad guardada por Omar
   el 2026-10-20 en el lab). Si el perfil la pisa con otro valor, el valor del motor no es la identidad y queda sin
   etiqueta.
2. **Estado en el mapa** = en el camino de producción de hoy (topic con escaleta + `fase2b --gfx --rotulista`, perfil
   misterio; `--plan-only` recorre lo mismo). «Muerto» = en ese camino no aporta al video: nadie lo llama, o se
   llama y su resultado se descarta (lo dice la columna «por qué»); el código sigue (lo usan los topics sin escaleta o
   sin rotulista, o el lab). Además de módulos, el mapa lista **funciones** muertas (el handoff nombra
   `garantizar_pico`, que es una función).
3. **Hook de render**: ve el comando que se escribe en la herramienta (con heredocs fuera, prefijos y `bash -c "…"` por
   dentro); un runner de lab que llama a fase2b por dentro (runpy/subprocess, como `lab/hyperframes/f30b/f30b_vajont.py
   render`) o un script `.ps1`/`.sh` que lo contenga **no pasan por el hook**. Prefiere el falso positivo: cualquier
   comando que no sea de texto y nombre `fase2b.py … --gfx` se mira. `/tanda` lo prohíbe
   igual («no se esquiva con runners»), pero no hay candado técnico para eso.
4. El skill `guion-de-pantalla` dice la regla («el render usa los planes aprobados y no re-decide») y también lo que hoy
   no la cumple: el render vuelve a correr `apply_gfx` y el crítico de los sellos mira el bloque dibujado; el lock de
   planes queda para la tanda de correcciones.

## Lo que queda abierto
1. **66 constantes sin origen** (tabla de A): las tiene que clasificar Omar con el analista; hasta entonces el test
   corre en modo inventario. Cuando estén, `CONSTANTES_ESTRICTO=1` en la suite.
2. **DECISIONES leído por el código** (último pendiente de infraestructura de DECISIONES): no se hizo.
3. **Runners de lab** que llaman a fase2b por dentro no pasan por `guard_render` (lectura 3).
4. **Lock de planes en el render** (el render no re-decide): pendiente para la tanda de correcciones; hoy la compuerta
   asegura que el plan aprobado es el que había al empezar el render, no que el render lo use tal cual.
5. **La página con el flujograma** la hace el analista con `lab/MAPA_MODULOS.json` (`modulos`, `aristas`, `muertos`).
6. Los **muertos** del mapa no se borraron (nada se borra sin decisión de Omar); `data_callout.html.tmpl` y `gfx_fragments`
   todavía sirven a los topics sin escaleta.
7. Lo que dice la ENTRADA y no cuadra (A.1) queda para que el analista lo corrija en su copia.

## C — `/tanda` (pegado)
