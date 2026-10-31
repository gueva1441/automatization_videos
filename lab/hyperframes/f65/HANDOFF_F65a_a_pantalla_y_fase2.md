# HANDOFF F65a — Cerrar el papel: `a_pantalla` deja de obligar y Fase 2 respeta al verificador

Rama `f11-guion-v4` (HEAD `5225edf`). Modelo para CC: **Opus medium**. Tanda chica, sin llamadas al modelo, sin corrida. Subagentes en paralelo para las pruebas.

## 0. Por qué
- F64 dejó el papel en 13/13 fichas, pero la vuelta **obligó** 5 fichas técnicas (D01, D51, D34, D40, D61) porque «beat sin su `a_pantalla`» es motivo de vuelta (F38c §A.1). El autor las había descartado bien en el intento 1 («cifra técnica»). En el lab, el mejor papel (O2_1, 9/10) las ignoró; el de producción con ellas quedó 7/10.
- F64 borró `juicio` de `pantalla_filtros` y con eso Fase 2 (`pantalla_colocar`, chequeo 5 de `gfx_guion`) volvió a correr `no_dicho`/`spoiler`/`contradicciones` por palabras sobre fichas que el verificador ya juzgó (abierto 1 de `F64_REPORT.md`). Una ficha salvada en el papel puede caer en Fase 2 por la misma palabra.
- Decisiones: DECISIONES 2026-10-31 15:49 (dos líneas).

## 1. Constantes
Ninguna nueva. Nada específico de Wittenoom.

## 2. Módulos
1. `script_engine/m01e_pantalla.py` — `validar`: `a_pantalla_vacios` se sigue calculando y se devuelve (va al JSON, al `.md` como ⚠ «sin su a_pantalla», a `armar`), pero **no** genera motivo, `motivos_beat` ni clave `(a_pantalla, cap, beat)`; se borra el bloque `for a in a_pantalla_vacios` de `motivos` (l.615-620 aprox.) y la clave correspondiente. El dato `a_pantalla` del ítem en la entrada no cambia (el autor lo sigue viendo).
2. `script_engine/pantalla_entrada.py`, `script_engine/pantalla_colocar.py`, `script_engine/gfx_guion.py`, `script_engine/pantalla_filtros.py` — donde en `7b48ebf` se quitó `juicio_autor` (pantalla_entrada l.142, pantalla_colocar l.196, gfx_guion l.275/283/493), entra `juicio_verificador` tal como viene en la ficha del papel (`{regla, motivo, tokens}`); `pantalla_filtros.contradicciones_de/contradicciones/no_dicho/spoiler` vuelven a aceptar `juicio` (la versión de antes de F64, `git show b9979f6:script_engine/pantalla_filtros.py`), pero leyendo `tokens` de `juicio_verificador` por regla: una coincidencia cuyo token (misma normalización que hoy) está en `juicio_verificador.tokens[regla]` **no corta ni pregunta** en Fase 2. Fase 2 nunca llama al verificador: solo respeta lo que el papel ya decidió.
3. Pruebas: `test_module_f38c_papel.py` (la que exige el motivo de `a_pantalla` se borra; la que exige `a_pantalla_vacios` en la salida se queda), `test_module_f40*.py` y `test_module_f37b_colocar.py` (`test_4_fase2_no_dicho…respeta_el_juicio` se reescribe con `juicio_verificador`), `test_module_f64.py` (+1: una ficha con `juicio_verificador.tokens = {"no_dicho": ["Australia"]}` pasa `pantalla_colocar.validar_papel` y el chequeo 5 sin corte; la misma sin juicio corta).

## 3. Etapas (un commit cada una; cada una termina con su salida en texto)
### Etapa A — `a_pantalla` no obliga
Salida: re-validar el papel actual de Wittenoom con el `validar` nuevo en modo solo lectura (`lab/hyperframes/f65/revalida.py`: carga `01e_pantalla.raw.json` → `final`, `validar(final, ent, juez=<caché del raw por pedido_md5>)`, sin llamadas) y mostrar `motivos` y `claves`: deben quedar vacíos (hoy también lo están: la vuelta ya puso los 6) y `a_pantalla_vacios` igual que hoy (`[]`). Además, sobre `lab/hyperframes/f63/a/O2_1.raw.json` (`respuesta`), con el mismo juez de caché de `lab/hyperframes/f64/sim/`: antes 5 motivos `a_pantalla` → ahora 0; los demás motivos iguales. Tabla antes/después.
### Etapa B — Fase 2 respeta al verificador
Salida: el diff de los 4 módulos y la prueba nueva de §2.3 en verde. Además, `python - <<…>` no: escribir `lab/hyperframes/f65/fase2_juicio.py` que toma las 13 fichas del papel actual (`01e_pantalla.json`, `beats[].ficha`) y corre sobre cada una el camino de Fase 2 (`pantalla_colocar.validar_papel` + `contradicciones` del chequeo 5 con la voz del cap) con y sin `juicio_verificador`: tabla ficha · regla que cortaría sin juicio · resultado con juicio. Las 7 que el verificador salvó (D108, Q25, D23, D01 y las de la vuelta) tienen que pasar; ninguna otra cambia.

## 4. Candados
Sin llamadas al modelo (juez = caché del raw; si falta un `pedido_md5`, PARÁ, no llames). Nada de Wittenoom en el código. `main` intacta. Lo viejo se borra con sus tests. Reporte `lab/hyperframes/f65/F65a_REPORT.md` con «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md` actualizado. PARADA al final: el papel sigue sin aprobar.
