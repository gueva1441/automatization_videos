# ENTRADA_ANALISTA 2026-10-30f — F60 A2/A3/B+C cerradas en lab · decidir madres de niños y madres parecidas · después anacronismos

Arrancá con `arranque-analista-pipeline` (formato §0, semáforo con %) y `handoff-analista`. Conectá `C:\CLAUDE_PROJECTS\automatization_videos` (rama `f11-guion-v4`). Reemplaza a la ENTRADA 2026-10-30e.

## 0. Lo que Omar quiere
Solo CONSTRUIR; producir Wittenoom lo decide él. Estimaciones honestas y cortas. Aprobó todo lo de hoy («dale a todo» 20:29).

## 1. Hecho (commits)
- `9f4d121` A2: fuera «or if unsure» → no alcanzó. Causa: el canon de persona mezclaba estado («pie vendado») y el casillero pedía «same age and condition».
- `99a0834` A3: `documented_people[].appearance_canon` = solo aspecto fijo (edad aparente en los años de era + nacionalidad/etnia + contextura si documentada); estado → `condition_by_period` (m03 lo ve como dato; el armado no lo pega); ejemplos del pedido cambiados; `TEXTO_PERSONA` «at the age the canon describes». Daniel 7/9 escenas (antes 1 y 0), venda solo 1962-63, 0 falsos positivos. Efecto declarado: todo tema rehace su canon en su próxima corrida.
- `8e6f7e4` B+C: madre por persona (≥ 2 fotos que aportan), Seedream t2i por la cola con `ROPA_MADRE`; regla única de madres (persona en orden + foto_madre_ref, tope 2) en todos los caminos y QA; filtro de edad `persona_aporta_madre` (sin madre si el año cae fuera de la era Y dentro de un `condition_by_period` que no se cruza con la era → Daniel 1991); pre-paso de secuencia una vez antes de los caps, lotes de 6 por persona, `pedidos.json` reanudable; `_clip_poll` → `_fal_queue_poll`; caps con clip (supps al pre-paso, foto inicial por una foto); contrato nuevo `foto_madre_personas` (m06 → fase2a → asset_manager). 30 tests, suites verdes. Prueba en lab US$ 1,435: 8 madres, 3 lotes 8/8, producción intacta. Código revisado por el analista: limpio.
- Etapa X (lab, US$ 0,105): 3/3 anacronismos se van nombrando el objeto concreto (DC-3 de MMA con fuente SLWA; reloj de acero con correa de cuero; ranura de latón sin portero ni buzón). Seedream v5 Lite `/edit` NO acepta `seed`.

## 2. Abiertos de B+C (SALIDA_BC §4) con etiqueta propuesta
1. **Madres de niños → frena** (Víctor Calvo 6 fotos, Mercedes 2): «a young Spanish boy/girl» rinde ≈ 13-15 años; las escenas piden ≈ 8-10 (mirada 2: 5,3 y 4,0). Causa: la tabla de edades del BLOQUE 2 empieza en 20; con `age_at_event` null el modelo pone «young». Propuesta del analista: decidir con Omar entre (a) que la edad aparente de menores salga como número del material, (b) sin madre para menores, (c) aceptar.
2. **Madres del mismo tipo se confunden → frena** (María/Milagros «young adult Spanish woman»; Daniel/Ramón). La regla del pedido prohíbe rasgos específicos, así que dos personas del mismo grupo salen iguales. Propuesta: prueba barata (≈ US$ 0,3): generar las madres de un mismo grupo en UNA llamada de secuencia («cada una una persona distinta», texto en código, no LLM) y regenerar 3 fotos de 2 personas. Alternativa: en fotos con 2 personas del mismo grupo, solo la madre principal.
3. Secuencia solo toma 8/33 (las de 2 personas van por una foto con 2 madres) → se queda (mismo precio).
4. «Fuera de la era» = sin intersección → se queda.
5. Venda sale como yeso en 3 fotos; anacronismos de escena (avión, aire acondicionado, camión) → tanda de anacronismos (§3).
6. `foto_madre_personas` en el contrato → se queda. 7. `etapa0b_secuencia.py` roto por el rename → se queda (no se re-corre).

## 3. Después: anacronismos (patrón `persona`)
X probó que el nombre concreto del objeto lo corrige. Tanda: el canon (Opus) lista objetos de época por período desde research/ficha (+ búsqueda con fuente cuando la ficha no los trae), m03 rutea `objetos`, el código pega la descripción. Diseñar con simulación sobre los 3 casos de X + los 3 de la prueba B+C.

## 4. Lista «se arregla si se repite / aparte» (sigue de la 30e §5)
Look 1962; rótulos inventados; mancha roja de venda → rechazo de clips; miniatura 03 gris; «Flux-PRO»; planos cerrados; `has_nsfw_concepts` ausente; «Court» en revisar; anclas de m03 inestables entre corridas; guion nuevo en `_steps` de Wittenoom (29-oct 20:55) → al producir, primero voz nueva y después m03; carpeta temporal `lab/hyperframes/f60/_aud/` (borrar a mano).
