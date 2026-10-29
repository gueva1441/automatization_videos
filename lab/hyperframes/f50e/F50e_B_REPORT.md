# F50e-B — Las 2 corridas de Opus que faltan en el canon (lab, en texto) · PARADA

Handoff `lab/hyperframes/f50e/HANDOFF_F50e_B_opus_dos_mas.md`, md5 `b6dbe97886db8ec4248afee4dd5b76fe` (verificado). Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Tope US$ 1,00; gastado **US$ 0,7244**. Producción intacta: topics_db y `05_visual_canon.json` dan el mismo md5 antes y después, y no se tocó ningún módulo de producción. No elegí modelo y no corrí D de F50d.

## Qué pasó, en llano
- **Corrieron opus_2 y opus_3, en paralelo.** Fueron directo por el camino sin esquema, así que no hubo ningún intento de 400. El md5 del pedido es `d2568e2a…`, el de F50e-A.
- **Las 3 de Opus cubren 96/96 fotos.** Las 3 traen 4 tramos hasta 2026.
- **Grupos sin años sin ropa:** las 3 corridas de Opus no dejan ninguno.
- **Grupos sin appearance:** Opus deja 2/13, 3/13 y 3/11. Sonnet deja 4/7, 7/10 y 5/8.
- **Costo de Opus:** US$ 0,36 por corrida, en promedio; Sonnet, 0,13.

## Paso 0
- La línea de DECISIONES 23:19 está tal cual.
- `lab/TOPE_TANDA.json` = `{"usd": 1.0, "desde": "2026-10-28T23:20:23"}` (fuera de git).

## Cómo se corrió
- `canon_modelos.py --opus23` corre solo opus_2 y opus_3, en paralelo, con `step_4e.canon_desde_ficha` de producción. El ruteador por hilo le saca el esquema a la llamada de Claude, que es el mismo camino que contestó en opus_1.
- **Frenos:** el script no llama a nada si el md5 del pedido no es `d2568e2a…` o si ya existen `canon_opus_2.json` o `canon_opus_3.json`.
- **Salida:** `CANON_MODELOS_B.json`, en la sesión de cost_tracker `f50e-b-canon-opus`. No pisa nada de F50e-A: git no muestra ningún cambio en `CANON_MODELOS.json` ni en los `canon_*.json` de A.
- **Medida 4a–4g:** se recalcula para las 9 corridas desde sus json, con `canon_modelos.medir`; las 7 de F50e-A se miden sin llamar. **4g** nuevo: grupos con `appearance` vacío.
- `CANON_MODELOS.md` se regeneró con `canon_modelos_md.py`, que junta los dos json.

Salida de las llamadas:
```
{"md5_pedido": "d2568e2a94c5db96f9836451b2f80cd7", "parada": null, "total_usd": 0.7244, "produccion_intacta": {"topics_db": true, "05_visual_canon": true}}
opus_2 96/96 · ['1937-1946', '1947-1966', '1967-1993', '1994-2026'] · grupos 13 0.3877 153.2 ['d2568e2a']
opus_3 96/96 · ['1937-1947', '1948-1966', '1967-1992', '1993-2026'] · grupos 11 0.3367 125.9 ['d2568e2a']
```
La línea del log «tanda 1: US$ 0.7244 (opus 1: 0.0000)» es el resumen del camino viejo de A y no aplica en `--opus23`: el freno de tanda 2 no corre.

## La tabla (de `CANON_MODELOS.md`)
| modelo | corridas medidas | fotos cubiertas mín · máx | grupos (por corrida) | grupos con años sin ropa | grupos sin appearance (por corrida) | years ilegibles | US$ promedio por corrida | fallas |
|---|---|---|---|---|---|---|---:|---|
| flash | 2 de 3 | 61 · 61 de 96 | 22 / 5 | 1 / 0 | 0/22 / 0/5 | ninguno | 0.0255 | flash_2: canon sin periods |
| sonnet | 3 de 3 | 96 · 96 de 96 | 7 / 10 / 8 | 1 / 0 / 1 | 4/7 / 7/10 / 5/8 | ninguno | 0.1287 | — |
| opus | 3 de 3 | 96 · 96 de 96 | 13 / 13 / 11 | 0 / 0 / 0 | 2/13 / 3/13 / 3/11 | ninguno | 0.3569 | — |

| corrida Opus | periods | cubiertas | grupos | sin appearance | US$ | s |
|---|---|---:|---:|---|---:|---:|
| opus_1 (F50e-A) | 1937-1947 · 1948-1966 · 1967-1992 · 1993-2026 | 96/96 | 13 | `airport_police`, `last_residents` | 0.3464 | 130.8 |
| opus_2 | 1937-1946 · 1947-1966 · 1967-1993 · 1994-2026 | 96/96 | 13 | `late_residents`, `airport_police`, `un_rapporteur` | 0.3877 | 153.2 |
| opus_3 | 1937-1947 · 1948-1966 · 1967-1992 · 1993-2026 | 96/96 | 11 | `victims_advocates_and_lawyers`, `late_wittenoom_residents`, `airport_police` | 0.3367 | 125.9 |

Grupos sin appearance de Sonnet (4g):
- sonnet_1: `mine_owners_prospectors_and_company_executives`, `mines_and_health_inspectors`, `government_officials_and_inquiry_leaders`, `asbestos_disease_advocates`;
- sonnet_2: 7, entre ellos `company_management`, `legal_professionals` y `labour_unions_and_arbitration`;
- sonnet_3: 5.

El ejemplo (los `periods` y el grupo con más años de la peor corrida de Opus) está en `CANON_MODELOS.md`. Las 3 corridas de Opus empatan en 96/96. Para desempatar, «peor» es la que tiene más grupos sin appearance (4g): opus_2 (3/13). Se ajustó después del veredicto, punto 14.

## Verificación
- Suite rápida: 55 passed, 3 skipped. La amplia también corrió: 976 passed + las 4 fallas previas.
- ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`, igual. Logs en `lab/hyperframes/f41/f50e_b/`.
- No se tocó ningún archivo de producción, así que el mapa no cambia.

## Lo que queda abierto
1. **Elegir entre Opus y Sonnet es de Omar.** Los dos cubren 96/96 en sus 3 corridas, así que hay que mirar los desempates:
   - años sin ropa: Opus 0/0/0, Sonnet 1/0/1;
   - grupos sin appearance: Opus 2–3 por corrida, Sonnet 4–7;
   - estabilidad del n.º de grupos: Opus 13/13/11, Sonnet 7/10/8;
   - costo: Opus ~US$ 0,36, Sonnet ~0,13 por corrida.
2. **El esquema y Claude:** el esquema del canon tiene 46 campos opcionales y la API de Claude acepta 24. Si se elige un Claude para producción, `step_4e` va a gastar en cada canon un intento que da 400 antes del camino sin esquema, salvo que se cambie el transporte o el esquema. Esa decisión y ese código son de una tanda aparte.
3. **Grupos sin appearance en Opus:** `airport_police` está en las 3 corridas, y los «últimos residentes» en las 3, con otro id cada vez. El pedido dice que se deje vacío si el material no da el origen del grupo, así que puede ser correcto. Para revisar con el analista.
4. **D de F50d** sigue pendiente, para correr con el modelo que se elija. topics_db sigue con el canon de Flash de F50d (corrida 1, tramos hasta 1966).
5. **De F50e-A:** Flash 2 falló (sin periods). Los regex de años de la ficha dan años falsos, así que no hay que usarlos.
6. **De tandas anteriores:**
   - F50d: la verificación de B con un canon nuevo y la regla del más cercano.
   - F50c: los nombres reales por las citas.
   - F50b: las notas F8 viejas y la foto madre en F51.
   - F50: n2, n3, n7, n8, n10 y n12.
   - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
En segundo plano corrieron `canon_modelos.py --opus23` (2 llamadas; exit 0) y `verificar.sh f50e_b` (exit 0). No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Paso 0: md5 del handoff | OK | `md5sum` = b6dbe97886db8ec4248afee4dd5b76fe |
| 2 | Paso 0: línea de DECISIONES tal cual | OK | `git diff HEAD -- DECISIONES.md`: +1 línea, la 23:19 F50e-B; coincide con el handoff |
| 3 | Paso 0: TOPE_TANDA = 1,00 | OK | `{"usd": 1.0, "desde": "2026-10-28T23:20:23"}`; el tope está fuera de git |
| 4 | opus_2 y opus_3 en paralelo, sin esquema, un solo intento | OK | CANON_MODELOS_B.json: 1 intento cada una, `con_esquema:false`, errores `[]`. `canon_modelos.py` usa un ThreadPoolExecutor de 2 y `sin_esquema=True` |
| 5 | md5 del pedido d2568e2a… | OK | CANON_MODELOS_B.json: `md5_pedido` d2568e2a94c5db96f9836451b2f80cd7 en ambos intentos. El script frena si no coincide |
| 6 | Effort high | OK | `EFFORT = "high"` en canon_modelos.py, sin cambios, y se pasa a `claude_helpers.call_json`. No pude verificarlo en el json de salida (no registra el effort) |
| 7 | Costo y tope | OK | cost_history, sesión `f50e-b-canon-opus`: 0,336668 + 0,387688 = 0,7244, menor que 1,00. La sesión de A (0,8093) no se tocó |
| 8 | Las corridas de A no se repiten ni se pisan | OK | `git diff a2ad1c7 --stat -- lab/hyperframes/f50e/` solo muestra CANON_MODELOS.md, canon_modelos.py y canon_modelos_md.py. CANON_MODELOS.json y canon_flash/sonnet/opus_1 no cambiaron. El script frena si ya existen canon_opus_2.json o canon_opus_3.json |
| 9 | Producción intacta | OK | `git diff` de researcher_steps, fase1_5.py, script_engine, step_4e y m03_imagenes_v3 está vacío. md5 de topics_db 2be72528… y de 05_visual_canon 95f2b9f4…, iguales a los de A. El json lo confirma (`produccion_intacta` true/true) |
| 10 | Medida 4a–4f en las 9 corridas, las 7 viejas desde sus json | OK | La tabla por corrida de CANON_MODELOS.md trae 9 filas. El script no llama a ninguna API para las 7 viejas |
| 11 | 4g bien calculado | OK | Recalculé `appearance` vacío desde cada `canon_*.json`: opus_1 2/13, opus_2 3/13 (`late_residents`, `airport_police`, `un_rapporteur`), opus_3 3/11, sonnet 4/7, 7/10, 5/8, flash 0/22 y 0/5. Coincide con el md y con el reporte |
| 12 | CANON_MODELOS.md regenerado, y tabla md = reporte = json | OK | Corrí `canon_modelos_md.py`: el md salió idéntico al que estaba en el repo. La tabla del reporte coincide con el md y los json (fotos 96/96, grupos 13/13/11, años sin ropa 0/0/0, costo promedio de Opus 0,3569) |
| 13 | No se elige modelo, no se corre D de F50d | OK | El reporte lista los criterios como "de Omar" y no recomienda. No hay cambios en el código de F50d |
| 14 | Ejemplo pegado: `periods` y grupo con más años de la peor corrida de Opus | PARCIAL | El md pega el ejemplo bajo "### opus_1 (96/96)". El handoff pide la peor corrida de Opus. Las tres empatan en cobertura y el código toma la primera. Con 4g, la peor sería opus_2 o opus_3 (3 grupos sin appearance contra 2). El reporte lo dice ("el ejemplo es opus_1, la primera de las empatadas"), pero el criterio de "peor" queda débil |
| 15 | Reporte: lo abierto entero, ESTADO, suite rápida, candado ch02, commit | PARCIAL | Suite rápida: 55 passed, 3 skipped. Amplia: 976 passed y 4 fallas previas. ch02 f792f3d483a1fa42daed5f7f0e054f46 en `f41/f50e_b/onlycap_ch02_nogfx.log`. El reporte tiene el marcador `{{VEREDICTO}}` sin reemplazar. No vi ESTADO ni el commit; el commit es posterior, a pedido de Omar |

Observaciones:
- El log de B imprime "tanda 1: US$ 0.7244 (opus 1: 0.0000)". Es cosmético y el reporte ya lo aclara.
- `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log` y `TOPE_TANDA.json` figuran como modificados en el árbol y no corresponden a esta tanda. No los toqué; hay que excluirlos del commit.
- El reporte dice "sonnet_3: 5" y el md da 5/8. Es correcto.

Fuera de alcance: ninguno. Los tracked tocados son DECISIONES.md, canon_modelos.py y canon_modelos_md.py, más los untracked propios de B. No hay cambios en producción.

Riesgos que el contrato no cubre:
- Opus vacía `appearance` en `airport_police` en las 3 corridas y en "los últimos residentes" bajo ids distintos. Las comparaciones de 4g por id entre corridas no sirven.
- El 400 del esquema (46 opcionales contra 24) sigue abierto: si se elige un Claude, cada canon en producción gasta un intento que da 400.
- El effort `high` solo se verifica por el código, no por el json de salida.

### Adenda de CC (después del veredicto)
- **#14:** corregido. `canon_modelos_md.py` desempata la «peor» corrida por 4g, la que tiene más grupos sin appearance. El ejemplo de Opus ahora es opus_2 (3/13); lo dice la línea correspondiente del reporte. Los de Flash (flash_1) y Sonnet (sonnet_2, 7/10) también salen con esta regla.
- **#15:** ESTADO está actualizado y va en el mismo commit, que se hace por rutas explícitas. Quedan fuera `diag_234_cap4.py`, `f28a.log` y `TOPE_TANDA.json`.

