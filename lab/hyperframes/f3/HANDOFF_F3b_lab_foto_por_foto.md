# HANDOFF F3b — Lab de identidad, UI v2: foto por foto

**Fecha:** 2026-10-19 22:40 · **Analista:** chat proyecto · **Ejecutor:** CC · **Gate:** Omar
**Base:** `f3-lab-identidad` @ `04a6025` (§A–§C cerrados). Misma rama. `main` intacta. F2b sin merge.
**Qué cambia:** solo la **pantalla** (`index.html`, `lab.js`, CSS). El servidor, el preview, el candado, las sugerencias, el resumen y Guardar identidad **se quedan como están**. Se reordena cómo se presentan.

---

## 0. Por qué

Omar abrió el lab y lo encontró confuso: tres columnas, 43 piezas en pestañas, atributos técnicos, sugerencias en una lista larga. Lo que él quiere es **recorrer el capítulo foto por foto**: en cada foto ver los objetos que van encima, lo que la IA sugiere para cada uno, probarlo con un botón, elegir entre pocas formas, marcar "se queda", pasar a la siguiente. Al terminar las 15, **ver el capítulo completo corrido**.

## 1. Pantalla (una sola vista, dos columnas)

```
┌──────────────────────────────────────────────────┬──────────────────────────────┐
│ FOTO 3 de 15 · 0:15.7–0:21.7      ◀ Anterior  Siguiente ▶ │ OBJETOS DE ESTA FOTO         │
│                                                  │                              │
│  [ escena 16:9 grande · ▶ Play esta foto ]       │ ① Movimiento de la foto      │
│                                                  │    IA: acercamiento lento    │
│  La voz dice aquí:                               │    hacia la cara             │
│  "…sus diques cedieron ante la embestida         │    [▶ Probar]   ☐ Se queda   │
│   colosal del agua. Rápidamente…"                │    Otras formas:             │
│  (palabras del léxico en color)                  │    ◉ acercar ○ alejar ○ paneo│
│                                                  │    ○ 3D  ○ quieta            │
│  ● ● ● ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  (progreso 3/15)   │                              │
│                                                  │ ② Sello rojo "AGUA"  (0:19.2)│
│                                                  │    IA: no ponerlo; "agua" es │
│                                                  │    palabra común (peso 1)    │
│                                                  │    [▶ Probar]   ☐ Se queda   │
│                                                  │    Otras formas:             │
│                                                  │    ◉ sello ○ golpe ○ sin sello│
│                                                  │                              │
│                                                  │ ③ Mood agua  (0:19.2)        │
│                                                  │    IA: sí, 2.5 s, suave      │
│                                                  │    [▶ Probar]   ☑ Se queda   │
│                                                  │    Intensidad: ◉ suave ○ media│
│                                                  │                              │
│                                                  │ ④ Salida hacia la foto 4     │
│                                                  │    IA: corte seco            │
│                                                  │    [▶ Probar]   ☐ Se queda   │
│                                                  │    ◉ corte ○ fundido negro   │
│                                                  │    ○ flash ○ tinta ○ zoom    │
│                                                  │                              │
│                                                  │ + Agregar algo a esta foto ▾ │
├──────────────────────────────────────────────────┴──────────────────────────────┤
│ ▶ Ver capítulo completo   🎬 Render mp4   💾 Guardar identidad   📄 Resumen   ↶ ↷ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Reglas
1. **Una foto a la vez.** `Anterior / Siguiente` y la fila de puntos para saltar. El estado se guarda solo.
2. **Lista de objetos de ESA foto, nada más.** Se construye automáticamente desde el plan + sugerencias: todo lo que cae en el rango de tiempo de la foto. Normalmente 3–6 objetos. Siempre están ① movimiento de la foto y el último "salida hacia la foto N+1". En medio: títulos, datos, contador, sellos, moods, íconos, recortes, fuente, pregunta de cierre (solo en la última foto).
3. **Cada objeto es una tarjeta igual:** nombre en español + momento · **"IA:" una frase** (qué sugiere y por qué, ≤ 15 palabras) · botón **▶ Probar** · casilla **☐ Se queda** · fila **"Otras formas"** con botones redondos (máx 6). Nada más visible. Un enlace pequeño "más opciones" despliega tamaño S/M/L, posición (9 zonas) y duración; lo demás no se muestra.
4. **▶ Probar** = salta la escena 1 s antes del objeto, reproduce hasta 1 s después de que termina, con el audio. Si cambia la forma (○), se regenera y se reproduce de nuevo solo. Sin recargar nada a mano.
5. **☐ Se queda** marcado = aprobado (va al resumen e identidad). Sin marcar al pasar a la siguiente foto = pendiente (el resumen lo lista). Botón pequeño **✖ Nunca** dentro de "más opciones" para los rechazos definitivos.
6. **"Otras formas"** son las variantes de animación de ese tipo de objeto, con nombres cortos: p. ej. sello → `sello · golpe · sin sello`; recorte → `periódico · post-it · ficha · carpeta`; ícono → `tinta · prensa · sello` y debajo `respira · deriva · pulso · quieto`; texto → `cascada · persiana · máquina · sello · fade`; movimiento → `acercar · alejar · paneo · 3D · golpe · quieta`; salida → `corte · fundido negro · flash · fundido cruzado · tinta · zoom`. La forma sugerida por la IA aparece preseleccionada (◉).
7. **La columna izquierda** muestra el texto que dice la voz durante esa foto (palabras del léxico en color, clic = salta ahí). No se muestra el capítulo entero.
8. **+ Agregar algo a esta foto** abre una lista corta en español (Dato · Sello · Ícono · Recorte · Contador · Mood · Cita · Tercio inferior · Pregunta de cierre). Al elegir, el lab propone dónde (palabra) y con qué forma, y lo mete como tarjeta nueva.
9. **▶ Ver capítulo completo**: reproduce las 15 fotos seguidas en la escena con audio, con todo lo aprobado y lo pendiente (lo rechazado no). Es el "ya junto" de Omar. Se puede pausar y, al pausar, el lab salta a la tarjeta de esa foto.
10. **🎬 Render mp4** (llega en §D): mismo plan → `fase2b --only-cap ch02`.

### 1.2 Lo que desaparece de la pantalla
Pestañas del catálogo, panel "Aquí", tira de 15 miniaturas permanente, lista larga de sugerencias, atributos técnicos a la vista, nombres de ids. **No se borra código**: el catálogo sigue siendo la fuente de las tarjetas y las "otras formas"; solo cambia la presentación.

### 1.3 Textos de la IA en las tarjetas
Vienen del `hint` del catálogo + la sugerencia específica de ch02. Formato fijo: **"IA: <qué> — <por qué en 5 palabras>"**. Ejemplos: "IA: acercar lento hacia la cara — es un retrato", "IA: no poner sello — palabra común", "IA: fundido a negro — termina el capítulo".

## 2. Implementación
- `lab.js`: nuevo modo `foto` (default). Deriva `objetos[fotoIdx]` del plan/sugerencias por rango de tiempo; `Probar` usa el seek+play existente con ventana [t−1, tFin+1]; `Otras formas` mapea a los `mutate()` ya existentes; `Ver capítulo completo` = play desde 0 con el plan actual.
- `index.html`/CSS: dos columnas + barra inferior. Tarjetas uniformes. Botones ○/◉ grandes (mínimo 36 px), fuente 15 px.
- Nada nuevo en servidor salvo, si hace falta, `GET /objetos?foto=N` para no calcular en el cliente.
- El modo viejo queda accesible en `?modo=experto` por si el analista lo necesita; no se linkea desde la UI.

## 3. Prueba antes de parar
CC recorre las 15 fotos con el navegador: cada una muestra 3–6 tarjetas, cada ▶ Probar reproduce la ventana correcta con audio, cambiar ○ regenera y reproduce, ☑ aparece en el resumen, ▶ Ver capítulo completo corre de 0 a 1:37 sin cortes. Captura de la foto 1 y de la última (con la tarjeta de pregunta de cierre) en el reporte.

## 4. Orden
§F (esta UI, ~3 h) → **PARADA: Omar recorre las 15 fotos** → §D (plantillas nuevas, pausa de cierre, Render, regenerar ícono) → §E (director con identidad).

## 5. Candados
Los de F3. Ningún cambio en `gfx_project.py`, `fase2b.py`, `gfx_config.py` en §F.
