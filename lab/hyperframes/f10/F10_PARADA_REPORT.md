# F10 — hasta la PARADA (§4.3): integración v3 + guion de Ycuá Bolaños

**Rama:** `f10-integracion-v3` (desde `790bec9`). Sin merge, sin producción: **PARADA** hasta el OK de Omar.
**Pedido:** `lab/hyperframes/f10/HANDOFF_F10_integracion_v3.md` §4.1–§4.3. **Decisiones:** `DECISIONES_F10.md` (D1–D18).
**Para leer:** `lab/hyperframes/f10/NARRACION_ycua.md` (por beat, con `narration_tts`), `ESCALETA_ycua.md`, `06_judge_ycua.json`, `costo_guion_ycua.json`.

## 1. §4.1 — Integración (hecho)
- **`fase1_5 --v3`** (o `topic["guion_version"] == 3`, siempre que el topic traiga `evidence_pool`):
  - `m01a` = compuerta del pool + escaleta;
  - `m01b` = guionista → editor → **`m01d_particion`** → juez m05;
  - lo demás (normalizer_gate, audio, m07, m03, assemble) sin cambios;
  - sin el flag, el camino viejo queda igual (test).
- **Nuevo `--from <paso>`:** reanuda la cadena hasta `assemble` (lo va a usar §4.4).
- **`script_engine/m01d_particion.py`:** escribe `01a_skeleton.json` y `01b_narration.json` con el contrato de siempre.
  - Agrega solo `narration_tts` e `ids_usados`.
  - Los títulos de cap salen de una llamada Flash corta, con respaldo determinista.
  - Los campos `bullets`, `pantalla_ids`, `cliffhanger` y `personajes` se derivan de la escaleta.
  - Los largos se miden contra `_len_range(role)` ±15 %: si un cap se pasa, se mueve un párrafo o el editor lo acorta; si queda corto, es aviso.
  - `regenerate_cap` (editor + escaleta + caps vecinos) queda como función.
- **Corrida en seco de Orleans f7r3** (topic de copia; se simula solo lo que cuesta plata o escribe fuera): `seco/seco_chequeos.json`, todo verde.
  - pasaron los 7 pasos hasta `assemble`;
  - skeleton y narración tienen el contrato completo;
  - `narration_tts` llega al audio y el texto de alineado va limpio;
  - m03 v3 queda activo;
  - `assemble` arma 7 caps y `fase2a.normalize_script` los acepta;
  - m02_5 corrió de verdad, en batch.
- **Bug de F7d encontrado y arreglado:** `topic_researcher` perdía el `evidence_pool` al guardar el topic, así que ningún topic de semilla v3 podía correr el guion v3 sin carga a mano (D15).
- **Decisión 2 de Omar (beats de disparo):** aplicada en `m03_imagenes_v3`; el tirador no aparece nunca. Queda una nota de re-hechura en `m03_visual` que el freno no me dejó cambiar (D2).
- **Decisión 3 (temas históricos):** no aplicada todavía (D3).
- **Tests:** `test_module_f10.py` (10). Suite amplia: 572 verdes + las 5 fallas previas.

## 2. §4.2 — Guion de Ycuá Bolaños (hecho; para leer)
- **El topic no existía en `topics_db`:** en F8 solo había corrido `run_seed`. Lo completé con el camino LONG v3 de `topic_researcher` (4a–4e), reusando la carpeta de F8 (US$ 0.99, D14).
  - El pool se rearmó con los arreglos de F8b: 227 datos · 52 citas verificadas · 15 elegibles · 62 eventos, verde.
  - Los ids cambiaron; las notas del analista van con los ids nuevos (D16).
- **Cifra canónica de muertos:** **327 oficiales, además de los desaparecidos** (D192, nota sobre el fallo de la Corte de 2025). La de 400 no se usa (D17). El título que armó 4c dice «400 vidas»: lo decide Omar.
- **Escaleta** (12 beats, 2.º intento; el 1.º lote se rechazó 3 veces, ver D18):
  - humano: **Liz Torres** (sobreviviente, con citas verificadas);
  - antagonista: Juan Pío Paiva;
  - pico: **T21, 11:25, la explosión**;
  - la orden de cerrar las puertas, en el cap 4;
  - la pericia de las 3 puertas, en el cap 6;
  - cierre: las velas y el «Que nunca más».
- **Narración:** 1,235 palabras (82 % de las 1,500). Por cap: 121 · 214 · 214 · 181 · 195 · 214 · 96. Títulos: Lluvia de Cenizas · El Carrito Repleto · La Nube Negra · Manos en el Vidrio · Bola de Fuego · El Mazo del Juez · Velas en las Ruinas.
- **Quedan 20 reglas duras** después del editor (Orleans F7c-3: 21). Lo que más pesa, a mi lectura:
  1. **Largo:** los caps 4, 5 y 7 quedan debajo del mínimo.
  2. **El cierre termina en un resumen** («busca que la memoria no se apague…»), no en la contradicción pericia–testimonios que pidió la nota 4 ni en una cita o pregunta (regla de F8 §2, que es blanda).
  3. **El pico no dice la hora (11:25)** y cierra con un juicio («Fue una masacre»).
  4. **327 suena en la voz (cap 5)**, aunque el plan de pantalla la reservó para verse y no decirse: cuenta como dura.
  5. **Hay párrafos sin dato** en los beats 3, 5 y 9, ids declarados que no suenan literales y una cita del gancho que adelanta un cap.
- **Etiquetas de voz (`narration_tts`):** pausas largas después de cada cita; `[slowly]` en el gancho y el pico; `[whispers]` solo en el golpe del pico (cap 5); `[quietly]` en los caps 4 y 6.
- **Costo del guion:** US$ 0.88 (escaleta 0.51 con el primer lote rechazado, guionista 0.17, editor 0.21, títulos 0.003). Con el research del topic, **US$ 1.87**.

## 3. PARADA
No sigo a producción hasta el OK de Omar. Según §4.3:
- si la nota del analista es menor que 8: una sola corrida de ajuste con sus notas;
- si es 8 o más: producción completa (§4.4).

## 4. Dudas para Omar / el analista
1. ¿El cierre se rehace con nota explícita («terminar en la pericia contra los testimonios, con una pregunta») en la corrida de ajuste?
2. ¿Aceptamos 327 dicho en la voz (es la canónica oficial) o va solo en pantalla?
3. Título del video: dice «400 vidas»; el guion dice 327 oficiales.

## 5. Veredicto del revisor-handoff
(pendiente: se pega íntegro abajo)
