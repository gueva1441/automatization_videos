# HANDOFF F47b — ¿Qué modelo llena mejor los casilleros de foto? Opus 5.5 y Sonnet 5.5 contra Fable y Pro (lab, solo texto)

Analista, 2026-10-28 03:22. Pedido de Omar (03:19): «si dale» a medir Opus 5.5 y Sonnet 5.5 con la misma prueba en texto de F47. Fable (D de F47) lo había elegido el analista sin acordarlo; esta tanda mide las alternativas más baratas antes de decidir el modelo.
Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`. Base: `lab/hyperframes/f47/` (`f47_corridas.py`, crudos de C2 y D).

## Qué mostró F47 (medido por el analista)
- D (Fable) contra C2 (Pro), 60 fotos: lugar en la prosa 34 vs 22; origen y aspecto de la gente dicho 37/39 vs 24/35; frases sacadas por F8 0 vs 6.
- Defectos de D: año repetido en el setting 47/60; negaciones en el setting («no people») 5/12 en el cap 7; ~170 palabras vs ~130; costo ~7× Pro (US$ 0,60–1,07 por cap).

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Caps 2, 5, 6, 7 | los mismos de D en F47 (comparación directa) | analista |
| E = `claude-opus-5-5`, F = `claude-sonnet-5-5` | Omar 03:19 | Omar |
| effort **high** en E y F | el mismo de D en F47: así solo cambia el modelo | analista (una variable) |
| Canon `f46b/canon_C.json`, expedientes y pedidos de F47 | existentes | — |
| Fotos: 0 | Omar 02:55 «solo en texto» (vigente) | Omar |
| Tope **US$ 4,00** | Opus ≈ 0,33–0,45/cap y Sonnet ≈ 0,17–0,25/cap con los tokens medidos de D en F47 (20–27 k entrada, 8–17 k salida) y `claude_helpers.PRICES` → ≈ 2,8 para 8 llamadas + margen | Omar confirma al pegar |

## Variantes (una variable cada una: el modelo)
| Variante | Modelo | Caps | Contra qué |
|---|---|---|---|
| **E** | `claude-opus-5-5`, effort high | 2, 5, 6, 7 | D y C2 de F47 (no se re-corren) |
| **F** | `claude-sonnet-5-5`, effort high | 2, 5, 6, 7 | D y C2 de F47 |
Mismo system, mismo user-prompt, mismo esquema, misma validación y mismo ajuste de transporte (array en la raíz → `{"image_prompts": …}`) que D. Ningún texto nuevo para los LLM. Negativa o JSON roto → se reporta tal cual, sin retocar el prompt.

## Chequeos por código (por foto; columnas C2 | D | E | F, con C2 y D leídos de `PROMPTS_F47.json`)
Los 8 de F47, tal cual, más dos:
9. **año del setting distinto del año del código:** años de 4 cifras (y décadas «1980s») que el `setting` crudo trae, contra el año de la foto;
10. **negaciones en el setting:** frases «no + palabra» en el `setting` crudo (se listan enteras).
Y por variante: llamadas ok/intentos, segundos, tokens y US$ por cap.

## Módulos
Producción: **ninguno se edita**. Se reusa `lab/hyperframes/f47/f47_corridas.py` (ruteador por hilo de `m03.call_pro_json`) con los modelos E y F; si hace falta un archivo nuevo, `lab/hyperframes/f47/f47b_corridas.py` que lo importe.

## Paso 0
`DECISIONES.md`, tal cual: «2026-10-28 03:19 · F47b: la misma prueba en texto de F47 con Claude Opus 5.5 (E) y Sonnet 5.5 (F) llenando los casilleros, caps 2, 5, 6, 7, effort high como D; después fotos solo del ganador contra Pro. Fable (D) lo había elegido el analista sin acordarlo · Omar · F47b».

## Parte única — prompts en texto
1. 8 llamadas (E y F × 4 caps) **todas en paralelo**; freno antes de cada una; costos con `cost_tracker` en `f47b-lab`.
2. Armado por código + F8 igual que F47.
3. Salida `PROMPTS_F47b.md`: por cap y foto → ancla, año (fuente), grupos C2 | D | E | F, los prompts enteros de E y F (C2 y D por referencia a `PROMPTS_F47.md`), palabras. Después la tabla de los 10 chequeos con totales por cap y por variante, y la tabla de costos por cap y variante.
4. Crudos `slots_E_chNN.json`, `slots_F_chNN.json`, `pedidos/` (verificar md5 del pedido igual a D en cada cap).
5. Costos reales de `cost_history` (`f47b-lab`).

## Reglas fijas
- Nada en `data/` (salvo `cost_history`), `output/` ni `topics_db`. Ningún archivo de producción editado. Cero fotos, cero llamadas a fal.
- Paralelo al máximo (subagentes y workers).
- Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque.
- Reporte `F47b_REPORT.md` con «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md`; commit.

## PARADA al terminar la parte única. No se elige modelo ni se toca producción.
