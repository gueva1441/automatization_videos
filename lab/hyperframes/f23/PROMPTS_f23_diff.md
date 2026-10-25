# F23 — md5 y diff de los prompts

## md5

| prompt | archivo (md5 del archivo) | bloque SISTEMA | código | igual |
|---|---|---|---|---|
| ficha v2.2 | PROMPT_FICHA_v2_2.md (`00c134a6f593223b69efcb7e7c19af52`) | `070b75dff58aecfa407fac3d62020ce4` | `070b75dff58aecfa407fac3d62020ce4` | sí |
| guion v5.3 | PROMPT_GUIONISTA_v5_3.md (`35b8e7794bffff8985a83ed968d8ab11`) | `8ca9aa494e3a0b9b4a99f60e6006c5f8` | `8ca9aa494e3a0b9b4a99f60e6006c5f8` | sí |

Sin cambio: escaleta `SYSTEM_V2` (f22-2) `22cfd68b7cee4734e95bb3ee27bb96b2`, columna `SYSTEM` `f294cf6b1220983903ce339f5b21cb27`.

## ficha: f22-1 → f23-1

```diff
--- f22-1
+++ f23-1
@@ -5 +5 @@
-- cronologia: los eventos del día en orden, con la fecha y la hora tal como están en el pool, y sus ids.
+- cronologia: los eventos en orden, con la fecha que el pool tenga (año, mes o día) y la hora si la hay, tal como están en el pool, y sus ids.
@@ -11,2 +11,2 @@
-- escenas (8 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
-- hechos (60 a 80) con un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso; entre 12 y 20), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.
+- escenas (6 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
+- hechos: entre 40 y 80 según lo que el pool dé (nivel 1 entre 10 y 20); con un pool chico, menos hechos buenos valen más que relleno. Cada hecho lleva un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.
@@ -27 +27 @@
-- hechos: entre 60 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
+- hechos: entre 40 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
@@ -29 +29 @@
-- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
+- citas: las mejores 10 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
```

## guion: f22-1 (v5.2) → f23-1 (v5.3)

```diff
--- f22-1 (v5.2)
+++ f23-1 (v5.3)
@@ -37 +37 @@
-Las fechas: la fecha completa una vez, en el cap 2. Después: «ese día», «esa noche», «al día siguiente», «el miércoles».
+Las fechas: cada fecha nueva se dice completa la primera vez. Si todo pasa en un día, después alcanza con «ese día», «esa noche», «al día siguiente», «el miércoles»; si el caso dura años, cada salto de tiempo se dice («En 1960…»).
```
