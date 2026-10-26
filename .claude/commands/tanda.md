---
description: Arma y corre una tanda de CC desde un handoff del analista (procedimiento F33): lectura, módulos que toca, una variable, PARADA corta por parte, compuertas, reporte con el revisor y ESTADO.
argument-hint: <ruta del handoff> [autorización de Omar, p. ej. «hacelo entero A → C»]
---
Tanda pedida: $ARGUMENTS

Seguí este orden. No te saltees pasos; si uno no se puede cumplir, frená y decí por qué.

1. **Leer** (enteros, antes de tocar código):
   - `CLAUDE.md`;
   - `DECISIONES.md` (el registro de decisiones de Omar; un número que no esté ahí, en la identidad F3 o en un estándar citado, no entra al código);
   - `lab/ESTADO_SESION.md`: la cabecera y las dos últimas tandas;
   - el handoff indicado arriba, y lo que él mande leer.
2. **Declarar los módulos que toca**, antes de programar: una lista con el nombre y el sticker de `lab/MAPA_MODULOS.md` (qué hace hoy para el video) y qué va a hacer después de la tanda. Si un módulo no está en el mapa, agregarlo al mapa en la misma tanda.
3. **Una variable por etapa.** Si el handoff mezcla dos, separarlas en partes y decirlo.
4. **Constantes solo con origen**: cada número nuevo lleva en su línea `# DECISIONES: …`, `# identidad F3`, `# estándar: …`, `# derivado: …` o `# medido: …` (`test_constantes_con_origen.py` las lista). Sin origen, no entra: se pregunta.
5. **Regla o filtro nuevo → simulador antes del código**: si el handoff trae una regla o un filtro de contenido, invocar al subagente `simulador` (skill `simular-reglas`) contra el `GUION_PANTALLA.json` del topic de prueba **antes de escribir código**, y pegar su tabla (propuestos → cortados por esa regla → quedan, con 3 ejemplos) en el reporte.
6. **Cada parte termina con su salida en texto pegada en el reporte** (el guion, la tabla, el log, lo que el módulo produce) **y PARADA corta**: seguir con la parte siguiente solo si el prompt de Omar lo autoriza expresamente («hacelo entero», «A → E»); si no, esperar.
7. **Nunca `fase2b --gfx` sin guion de pantalla aprobado** (`fase2b <topic> --plan-only` → revisión → Omar dice «aprobado» → `fase2b <topic> --aprobar-guion "Omar <fecha>"`). El hook `guard_render` lo frena igual; no se esquiva con runners.
8. **En cada commit**: suite rápida (`test_module_f25c.py test_module_f24.py test_module_f21.py`) y amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat_windowed, transition_timeout, `test_constantes_con_origen.py`; 5 fallas previas conocidas: 01b_pauses ×3, m03_merge_timing ×2) y el md5 de `fase2b ba6c3cac-a091-41c0-8dad-afd2f4364747 --only-cap ch02 --reuse-visuals --sw-encode` = `38e5ba14…`. Un commit por parte; `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git; sin merge, sin publicar, sin borrar.
9. Si el commit toca `script_engine/gfx_*.py` o `fase2b.py`, actualizar `lab/MAPA_MODULOS.md`/`.json` (el hook `guard_mapa` avisa) o decir en el reporte por qué el mapa no cambió.
10. **Reporte** `lab/hyperframes/fNN/FNN_REPORT.md`: lo hecho por parte con su salida pegada, lecturas declaradas, la sección **«lo que queda abierto» entera** (nada resumido), y el **veredicto íntegro del subagente `revisor-handoff`** (se lo invoca antes de cerrar, con el handoff y el pedido literal de Omar).
11. `lab/ESTADO_SESION.md` actualizado al final (y en cada commit).
12. **Antes de la PARADA, cerrar toda tarea en segundo plano propia**: subagentes y shells lanzados con
    `run_in_background` (que ninguno quede corriendo) y los procesos que la tanda haya dejado vivos (`Get-Process` —
    python, ffmpeg, node, chrome de HyperFrames, `find`/`grep` de un revisor—; cerrar solo los de la tanda, nunca los de
    Omar como su qa_studio o Firefox). Decir en el reporte qué se cerró. **PARADA.**
