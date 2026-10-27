# HANDOFF F38 — Reintento parcial, tarjeta desde la voz, juez de anclaje, fracciones

Analista · 2026-10-27 00:30 · Para CC. Base: HEAD de F37 (`f39c28f`). **Tanda corta y rápida (ver §Velocidad).** Dos commits: A (código) y B (corrida de Vajont). PARADA al final de B. Sin render, sin aprobar. Reglas que mandan (DECISIONES 22:26 y 22:32): nada hardcode, todo arreglo general, la causa se arregla en el sistema.

## 0. Antes
- ¿Construye sobre código que se reemplaza? No. ¿Cambia el orden? No.
- Módulos: `m01e_pantalla` (reintento, juez) · `voz_datos` (tarjeta) · `voz_utils` (fracciones) · `pantalla_colocar` (tarjeta en el plan). Mapa si cambia un sticker.
- Constantes: ninguna. El juez usa el modelo chico que el proyecto ya tiene configurado: `gemini_model` de `config.py` (hoy `gemini-2.5-flash`), leído de ahí, nunca escrito en el código.

## A. Código (commit A)
**A.1 Reintento parcial.** Causa (F37 abierto 2): el reintento devolvía el papel entero y perdió sin motivo D128, Q14, dos sellos y la tarjeta. Arreglo: el reintento recibe el papel completo **como contexto**, pero su formato de salida es solo `{"cambios": [{"cap","beat","ficha"|null,"sello"|null}]}` **para los beats que tienen motivo**; el código fusiona por (cap, beat); lo demás queda congelado. Un cambio sobre un beat sin motivo se ignora y se anota. Test: con la respuesta de F37, D128/Q14/AVISO/ALARMA del intento 1 sobreviven al reintento.

**A.2 Tarjeta desde la voz, no del autor.** Causa (abierto 1): la tarjeta la elegía el modelo y el reintento la perdió; además el pool tiene dos horas (T72 22:43, T66 22:39). Arreglo en `voz_datos`, sin modelo: fecha = la primera fecha completa que la voz dice en el gancho (ch01); hora = la `hora` de los ítems del pool del beat pico del video (el de la escaleta) **cuyos minutos coinciden con la hora que dice la voz** (parsear horas en letras: «las diez y treinta y nueve»). Si la voz no dice hora, sin hora; si no hay fecha en el gancho, sin tarjeta (nunca se inventa). El autor deja de devolver `tarjeta` (se saca del formato y la línea TARJETA del prompt: **regla que se quita**). Test: Vajont → «9 OCT 1963 · 22:39» (T66 sí, T72 no).

**A.3 Juez de anclaje.** Causa (abierto 5 y 7): «la oración habla de lo mismo» (regla b) y «adelanta un hecho» (regla c) son juicios de sentido; el código solo compara cifras y nombres, y sin listas de palabras no puede más. Arreglo: después de la validación en papel, **una** llamada al modelo chico con todas las fichas del video. Prompt literal (`JUEZ_VERSION = "juez-1"`, md5 en el reporte):
```
Sos el editor de un documental. Te doy, por cada texto que va en pantalla: la oración de la voz donde aparece, la anterior y la siguiente, el dato completo del archivo del que sale, y todo lo que la voz dice después en el video. Respondé, por cada uno, solo JSON:
{"id": …, "mismo_asunto": true|false, "adelanta": true|false, "motivo": "una línea"}
mismo_asunto: la oración donde aparece, o su vecina, habla del mismo hecho que el dato.
adelanta: el dato le cuenta a quien mira algo que la voz recién cuenta más adelante.
```
Las fichas con `mismo_asunto: false` o `adelanta: true` entran como motivos al reintento parcial (A.1) junto con los demás («D131: la oración [1] habla de la presa en pie; el dato es el salto del agua, que la voz cuenta en [15]: elegí otra oración u otro dato»). Lo que siga mal después del reintento sale del papel con el motivo del juez. Tope: dentro del tope del perfil. Tests: con el papel de F37, D131 en [1] da `mismo_asunto: false` o `adelanta: true` (respuesta grabada como caché; el test no llama a la API).

**A.4 Fracciones en letras.** Causa (abierto 6): `voz_utils` no lee «un centímetro y medio» ni «medio centímetro». Arreglo general en el parser: «y medio/media» = +0,5; «medio/media» antes de una unidad = 0,5; «y cuarto» = +0,25; «un tercio» = 1/3. Test: D68 deja de volver por error.

## B. Corrida de Vajont (commit B)
`m01e_pantalla` suelto → `01e_pantalla.md` → `fase2b f8s3-vajont-f30 --plan-only`. Pegar: el papel, los motivos del juez y del reintento, la tabla de lo que queda en pantalla, los chequeos y el costo. Esperado **sin edición a mano**: tarjeta 9 OCT 1963 · 22:39; el gancho en una oración que habla de su dato; D128 y Q14 si estaban en el intento 1 y nadie los cuestionó; ningún beat cambiado sin motivo. Lo que sea gusto se lista para la compuerta de Omar (no se fuerza). `F38_REPORT.md` corto (ver §Velocidad), abierto entero, veredicto del revisor. **PARADA.**

## Velocidad (pedido de Omar: no esperar una hora)
1. Esfuerzo **medium** (tanda chica y especificada).
2. A.1+A.3 (`m01e_pantalla`) y A.2+A.4 (`voz_datos`/`voz_utils`) son independientes: hacerlos **en paralelo con dos subagentes**, y juntarlos en el commit A.
3. Suite amplia en paralelo (`pytest -n auto`; instalar `pytest-xdist` si falta). Suite rápida en cada paso; amplia y md5 de ch02 **una sola vez**, antes del commit A.
4. Reporte **corto**: qué se hizo (una línea por punto), tabla de pantalla, chequeos, costo, abierto, veredicto. Lo largo (papel entero, logs, diffs) va en archivos de `f38/` y el reporte los nombra.
5. Sin simulador aparte: la corrida B es la medición.

## Frenos
Sin render, sin aprobar, sin merge, sin tocar prompts de escaleta/guionista/partición. Cambios de prompt: solo quitar TARJETA del autor (A.2), el formato del reintento (A.1) y el prompt nuevo del juez (A.3), literales. PARADA anticipada si el JSON no parsea dos veces o el tope no alcanza.
