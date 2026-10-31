# HANDOFF F60 Etapa A3 — el canon de cada persona documentada separa aspecto fijo de estado (como F51b con los grupos)

Rama `f11-guion-v4`. `main` no se toca. Usá tantos subagentes en paralelo como el trabajo permita.

## Por qué (diagnóstico de A2, verificado por el analista)
- `TEXTO_PERSONA` pide la persona «at the same age and condition the canon describes».
- El canon de `Daniel Écija` dice «a young adult Spanish migrant miner in work clothes, one foot visibly bandaged» → Opus solo lo pone donde hay venda (10/10).
- Mismo defecto en `María Bernal` («hopeful yet physically weakened») y `Daniel Écija hijo` (una acción: «presenting travel documents at an airport checkpoint»).
- Origen: el BLOQUE 2 del pedido del canon pide hoy en `appearance_canon` «rol + atuendo de época», y sus ejemplos llevan oficio y ánimo. F51b separó fijo/estado solo en `people_groups`.

## Módulos que toca (y para qué es cada uno)
1. `researcher_steps/step_4e_visual_canon.py` — arma el pedido del canon visual (Opus) y limpia su respuesta.
2. `script_engine/m03_visual.py` — llena los casilleros de cada foto (Opus); le muestra el canon.
3. Tests nuevos (abajo). Ningún test existente tiene estos textos literales (f50b usa `m3.TEXTO_PERSONA` por referencia): no hay byte a byte que adaptar; si encontrás alguno, declaralo.
Nada más de producción. `armar`, foto madre, `asset_manager`, m05, m06, gfx: NO se tocan.

## Efectos declarados (no son fallas)
- `marca_canon` hace md5 del texto del pedido → el cambio del BLOQUE 2 invalida `canon_ficha_md5` en TODOS los temas: la próxima corrida de producción de cualquier tema rehace su canon con Opus (≈ US$ 1 c/u) y reescribe topics_db y `05_visual_canon.json`. Esperado.
- m05_judge (l.~430) y m06 (l.~147) reciben `documented_people` entero: verán `condition_by_period` y un `appearance_canon` más corto. No se rompe nada.
- `name_matching` / `detect_name_leakage`: solo usan `name`.

## Constantes
Ninguna constante ni lista nueva.

## Etapa A3.1 — código
### 1. Pedido del canon, BLOQUE 2 (`step_4e_visual_canon.py`)
**1a.** Sustitución exacta (l.~250-253), ANTES:
```
- appearance_canon: 1-2 frases EN describiendo aspecto físico genérico
  (edad aparente + nacionalidad/etnia + rol + atuendo de época). PROHIBIDO
  mencionar el nombre real. PROHIBIDO mencionar rasgos específicos como
  "tall", "blue eyes", "scar" — solo descriptores ampliamente verificables.
```
DESPUÉS:
```
- appearance_canon: 1 frase EN con solo el aspecto físico fijo de la persona
  (edad aparente en los años de era + nacionalidad/etnia + contextura si el
  material la documenta). Nada que cambie según dónde esté, qué haga o qué
  le pase (ropa, oficio, heridas, enfermedad, ánimo, acción): el oficio va
  en role, la ropa en era_visual_canon y el estado físico documentado en
  condition_by_period. PROHIBIDO mencionar el nombre real. PROHIBIDO
  mencionar rasgos específicos como "tall", "blue eyes", "scar" — solo
  descriptores ampliamente verificables.
- condition_by_period: una entrada por cada tramo de años en que el material
  documenta un estado físico de esa persona (heridas, enfermedad, desgaste);
  years "AAAA-AAAA" y condition (EN, una frase). Si el material no documenta
  ningún estado, lista vacía.
```
**1b.** Ejemplos (l.~284 y l.~293-295). Sustituciones exactas:
- `   ✓ BIEN: "a mid-30s American naval officer with focused demeanor"` → `   ✓ BIEN: "a mid-30s American man of medium build"`
- las 4 líneas desde `✓ BIEN appearance_canon: "a mid-30s American naval officer with focused` hasta `la era se infiere del era_visual_canon del topic)` → 
```
✓ BIEN appearance_canon: "a mid-30s American man of medium build"
                           (solo edad + nacionalidad + contextura, sin era;
                           el oficio va en role, la ropa en era_visual_canon)
```
Los ✗ MAL quedan como están.
**1c.** JSON de ejemplo (l.~403, está dentro de un f-string con `{{ }}`; `[]` no lleva llaves): `"appearance_canon": "a mid-30s American naval officer with focused authoritative demeanor"` → `"appearance_canon": "a mid-30s American man of medium build",` y en la línea siguiente `      "condition_by_period": []`.
**1d.** Docstring del esquema (l.~56-58): agregar `"condition_by_period": [{"years": str, "condition": str}]` tras `"appearance_canon": str`.

### 2. Limpieza (`_clean_person`) — limpieza NUEVA y determinista
- Devolver también `condition_by_period`: lista de `{years, condition}` (strings, strip), descartando entradas que no sean dict o con `years`/`condition` vacíos; ausente o no-lista → `[]`. (El test `test_f51b_condition_by_period_sobrevive_la_limpieza` sirve solo de patrón: `people_groups` pasa crudo, no hay criterio previo que copiar.)
- Cada `condition` pasa por el mismo strip de nombre por tokens que hoy se aplica a `appearance`. El strip C5 de era (`_strip_era_from_appearance`) NO se aplica a `condition`.
- `_PERSON_REQUIRED_KEYS` no cambia (el campo es opcional).

### 3. m03 ve el estado como DATO (`m03_visual.py`, bloque PERSONAS DOCUMENTADAS ~l.461)
Tras la línea `    appearance_canon: …` de cada persona, por cada entrada de su `condition_by_period`:
```
    condition {years}: {condition}
```
Misma sangría (4 espacios). Sin texto de regla nuevo. Lista vacía → bloque idéntico al de hoy.
`people_groups[].condition_by_period` NO se muestra (decisión F51b; fuera de alcance).

### 4. `TEXTO_PERSONA` (l.~283)
ANTES: `... (even from behind), at the same age and condition the canon describes — the main one first, ...`
DESPUÉS: `... (even from behind), at the age the canon describes — the main one first, ...`
Resto byte a byte igual.

### 5. Tests + suites
Tests nuevos: `condition_by_period` sobrevive `_clean_person` (y descarta entradas rotas; nombre quitado de `condition`); el bloque de m03 imprime la línea `condition` y con lista vacía queda idéntico. Suites: ch02 `--only-cap` en candado (confirmá que el md5 no depende del SI de m03 antes de afirmar `f792f3d4…`), rápida, amplia (+ las 4 previas).

## Etapa A3.2 — prueba en lab (copia `lab/hyperframes/f60/base`; NUNCA el topics_db real ni `_steps` reales)
1. **Canon nuevo** de Wittenoom con Opus: `ficha = fc.load(TID, <copia>/data/scripts/_steps)`; topic leído sin `asegurar_canon` (NO usarlo: escribe topics_db con `save_db`); `s4e.canon_desde_ficha(topic, ficha)` envuelto en `cost_tracker`. Guardar en `a3/05_visual_canon_a3.json`.
   - **PARÁ** si Daniel sale sin `condition_by_period` con la herida, o si algún `appearance_canon` sigue trayendo oficio, ropa, herida, ánimo o acción (comparación leída a mano, sin lista de palabras). Reportá y no sigas a m03.
2. **m03 los 7 caps** (runner nuevo `etapa_a3_m03.py` desde `etapa_a2_m03.py`, `CAPS = range(1, 8)`, sin el filtro de caps parciales), mismas entradas que la corrida 2 de A (f54/antes + pool f44/B). Workers al máximo.
   - El canon nuevo entra al `topic`: `topic = {**topic, **{k: canon_a3[k] for k in fase1_5.CANON_KEYS}}` antes de `assign_visual_prompts`. NO copiar el `05_visual_canon.json` de producción a la copia. Verificá en el log que el bloque PERSONAS que recibe Opus es el nuevo.
   - Anclas fijas: envolver `m3._plan_anchors` en el runner para que devuelva las anclas de `a/03_visual_despues.json` (flux: `{"anchors":[{anchor,pos,end}]}` con `pos/end` por búsqueda en la narración; veo caps 1 y 7: `veo_anchor` + `supplementals`). Si `_reconcile_anchor_timing` las mueve, emparejá por ancla como en A2 y declaralo.
3. Cero fotos.

## Salida (`SALIDA_A3.md`) — en este orden
- a) Canon: por persona, `appearance_canon` antes → después y su `condition_by_period`. Grupos, props, era: tabla igual / cambia (con texto) / nuevo / desaparece.
- b) Tabla de verdad de SALIDA_A (las ≈ 9 escenas de Daniel): resultado A, A2, A3 por ancla.
- c) Falsos positivos: Daniel en fotos de la familia Calvo, Milagros/Ramón, etc.
- d) Venda: cada foto con Daniel → `year`, ¿prompt con venda/cojera? Esperado: venda solo en el tramo de la herida del canon.
- e) María, Daniel hijo y confusiones de edad: ¿padre/hijo confundidos?, ¿Daniel en la escena de 1991 (55 años)?, ¿Víctor Calvo adulto?
- f) Control de nombres (regla 19:35): 2+ palabras → PARÁ; 1 palabra → «revisar».
- g) Prompt de video del cap 1: ¿conserva el pie vendado?
- h) Costo real (canon + m03).

## DECISIONES.md (CRLF, tal cual, al final)
```
- 2026-10-30 20:00 · **F60 A3:** en el pedido del canon, `documented_people[].appearance_canon` pasa a ser solo el aspecto fijo (edad aparente en los años de era, nacionalidad/etnia, contextura si el material la documenta); ropa, oficio, heridas, enfermedad, ánimo y acción salen (oficio → role, ropa → era_visual_canon); el estado físico documentado va a `condition_by_period` (years + condition), que m03 ve como dato y el armado no pega en la foto; los ejemplos del pedido se cambian a juego · Omar · F60
- 2026-10-30 20:00 · **F60 A3:** en el casillero `persona`, «at the same age and condition the canon describes» → «at the age the canon describes» · Omar · F60
```

## PARADA A3
Commit, ESTADO, F60_REPORT §Etapa A3 con el veredicto íntegro del `revisor-handoff`. No se pasa a la Etapa B sin OK del analista y de Omar.
