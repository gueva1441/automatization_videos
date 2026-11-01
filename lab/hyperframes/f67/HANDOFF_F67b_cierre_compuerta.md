# HANDOFF F67b — Cierre de la compuerta: el papel no pasa sin narración aprobada · normalizado viejo fuera · `--criticar` solo

Modelo → CC: Opus medium. Decisión de Omar 2026-10-31 20:09 (DECISIONES.md). Tanda chica, 3 arreglos generales, sin prompts nuevos (sin auditoría de subagente; sí `revisor-handoff`). Subagentes en paralelo donde convenga. Sin topes en dólares. Nada de producción se corre salvo lo que dice §3 (`--criticar` **no** se corre en esta tanda: lo corre Omar después de aprobar).

## 0. Orden re-derivado
- ¿Construye sobre algo que ya decidimos reemplazar? No: cierra los abiertos 9, 10 y el pendiente «volver a criticar» de `F67_REPORT.md` con lo que F67 dejó (`estado_narracion`, `papel_falta`, `run_papel_aprobado`, `reconstruir`, `m01f_critico.generar`).
- ¿Cambia el orden? No. Antes de que Omar apruebe la narración y el papel se re-escriba.

## 1. Constantes
| valor | origen | quién |
|---|---|---|
| `--criticar`: juez m05 (código) + `m01f_critico.generar` (Opus 5.5 medium, 1 llamada, ≈ US$ 0,8), **sin** verificador; usa la tabla de `01b_verificacion.md` que haya en disco (si no hay, `verificacion` = «sin verificación en disco») | DECISIONES 20:09; F67 B (0,72 medido) | Omar |
| papel desfasado = `01e_pantalla.json` sin `narracion_md5` o con `narracion_md5` ≠ `md5_narracion` actual, **aprobado o no** | DECISIONES 20:09 (se borra la excepción de F67 §2) | Omar |
| normalizado desfasado = `01b_narration_normalized.json` cuyo `narration_original` de algún cap ≠ `01b_narration.json.chapters[].narration` actual (misma comparación que hace `normalizer_gate` para decidir si re-normaliza; CC la cita) | F67_REPORT abierto 10 / riesgo 2 del revisor | analista |

## 2. Módulos tocados (hoy → después)
| archivo | hoy | después |
|---|---|---|
| `fase1_5.py` | `papel_falta` respeta un papel aprobado sin `narracion_md5`; `--verificar-narracion` = juez + verificador + crítico | `papel_falta` sin esa excepción (desfasado ⇒ se re-escribe, aprobado o no, y lo dice en el log: «papel de otra narración: se re-escribe»); nuevo `--criticar` (§1); antes de la voz (`normalizer_gate`) y en `--from audio`: si el normalizado está desfasado se borra y se avisa en el log (el gate lo regenera) |
| `qa_studio_server.py` | POST `/papel/aprobar` aprueba siempre | POST `/papel/aprobar` responde 409 «la narración no está aprobada» o «el papel es de otra narración» (`estado_narracion` + `papel_falta`); la pestaña PAPEL muestra ese motivo y deshabilita el botón |
| `run_pipeline.py` `etapa_de` | `papel_nuevo` respeta papel aprobado sin `narracion_md5` | `papel_nuevo` = papel desfasado, aprobado o no (misma `papel_falta`) |
| tests | `tests/test_m01f_compuerta.py` | + casos: papel aprobado sin `narracion_md5` → `papel_nuevo`; `/papel/aprobar` 409 sin narración aprobada; normalizado desfasado se borra antes de la voz |

## 3. Etapas (cada una termina con su salida en texto)
1. **`papel_falta` y `etapa_de`**: sacar la excepción; test. Salida: `python -c` que imprime `papel_falta` y `etapa_de` para Wittenoom (debe dar «papel de otra narración» / `papel_nuevo` cuando la narración esté aprobada; hoy, con la narración sin aprobar, `narracion`).
2. **`/papel/aprobar` 409 + botón deshabilitado**: salida: respuesta del POST con Wittenoom hoy (409, motivo) y captura a texto de la pestaña PAPEL (Chrome headless como F66b).
3. **Normalizado desfasado**: borrado antes de la voz; salida: log de la comprobación sobre Wittenoom (debe decir «desfasado: 7 caps distintos, se borra»); **no** se corre la voz. Confirmar que `audio_manager.py:493` no lo lee cuando no existe y que `normalizer_gate` lo regenera.
4. **`--criticar`**: flag en `fase1_5`; salida: `--help` y una corrida en seco (`post` falso en test) que muestra que no llama al verificador. **No** se corre contra la API en esta tanda.
5. Reporte `lab/hyperframes/f67/F67b_REPORT.md` (salidas, diff, tests, veredicto íntegro de `revisor-handoff`), ESTADO_SESION cabecera, commit en `f11-guion-v4` (incluye la línea 20:09 de DECISIONES.md sin commitear). Copia de este handoff con md5.

## 4. Lo que se borra
- La excepción «papel aprobado sin `narracion_md5` se respeta» en `papel_falta` y `etapa_de`, con su test.

## 5. PARADA
Nada más se corre: ni voz, ni fotos, ni papel, ni `--criticar`. Avisar «CC terminó».
