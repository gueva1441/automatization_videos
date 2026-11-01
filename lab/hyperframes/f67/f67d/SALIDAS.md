# F67d — salidas

## A. `borrador` sobre una copia de la narración actual de Wittenoom y su `01f_critico.json`

| k | cap | oraciones | tramos | partes | sin decidir (`aplica`) | todos aceptados | aceptar sobre el resultado |
|---|---|---|---|---|---|---|---|
| 1 | ch02 | [9, 16, 17] | 2 | 2 | aplica | aplicado | ya_aplicado |
| 2 | ch03 | [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22] | 1 | 1 | ya_aplicado | ya_aplicado | ya_aplicado |
| 3 | ch04 | [1] | 1 | 1 | aplica | aplicado | ya_aplicado |
| 4 | ch05 | [21] | 1 | 1 | ya_aplicado | ya_aplicado | ya_aplicado |
| 5 | ch06 | [10, 11, 13, 14, 15, 16] | 2 | 1 | no_aplica | no_aplica | no_aplica |
| 6 | ch07 | [1, 7] | 2 | 2 | aplica | aplicado | ya_aplicado |

`pendientes` con todos aceptados: [5] (k=5 no aplica: `1 parte(s) en el texto y 2 tramo(s) en la narración: editar a mano`).

- k=1: la parte «Víctor Calvo, el hijo de Milagros, había hecho esa…» aparece 1 vez/veces con todos aceptados
- k=1: la parte «Del barco, a un avión pequeño. Del avión, a la tie…» aparece 1 vez/veces con todos aceptados
- k=2: la parte «Los informes eran anteriores a la boda, al barco y…» aparece 1 vez/veces con todos aceptados
- k=3: la parte «El hijo cuenta que el primer día de trabajo de su …» aparece 1 vez/veces con todos aceptados
- k=4: la parte «Daniel había estado en Wittenoom diez. Y no fue el…» aparece 1 vez/veces con todos aceptados
- k=5: la parte «Melita Markey, que dirige la Sociedad de Enfermeda…» aparece 0 vez/veces con todos aceptados
- k=6: la parte «En 2023, un relator de la ONU visitó Australia y l…» aparece 1 vez/veces con todos aceptados
- k=6: la parte «Quién sabía está escrito desde 1944: lo escribiero…» aparece 1 vez/veces con todos aceptados

## B. La pestaña en Chrome headless (steps_dir temporal)

### Sin decidir

- Botón «Aprobar narración» apagado = **True** · Falta decidir DEBERÍA 1, 2, 3, 4, 5, 6.
- DEBERÍA 1: sin decidir
- DEBERÍA 2: sin decidir · ya está en el texto
- DEBERÍA 3: sin decidir
- DEBERÍA 4: sin decidir · ya está en el texto
- DEBERÍA 5: sin decidir · no aplica
- DEBERÍA 6: sin decidir

### 1 aceptado (k=1), 1 rechazado (k=5), 4 sin decidir

- Botón «Aprobar narración» apagado = **True** · Falta decidir DEBERÍA 2, 3, 4, 6.
- DEBERÍA 1: ✓ aceptado
- DEBERÍA 2: sin decidir · ya está en el texto
- DEBERÍA 3: sin decidir
- DEBERÍA 4: sin decidir · ya está en el texto
- DEBERÍA 5: ✗ rechazado
- DEBERÍA 6: sin decidir

Sin escribir nada en disco tras esos clics: True.

### Deshacer k=1

- Botón «Aprobar narración» apagado = **True** · Falta decidir DEBERÍA 1, 2, 3, 4, 6.
- DEBERÍA 1: sin decidir
- DEBERÍA 2: sin decidir · ya está en el texto
- DEBERÍA 3: sin decidir
- DEBERÍA 4: sin decidir · ya está en el texto
- DEBERÍA 5: ✗ rechazado
- DEBERÍA 6: sin decidir

### Todo decidido

- Botón «Aprobar narración» apagado = **False** · Al aprobar se aplica todo junto.
- DEBERÍA 1: ✓ aceptado
- DEBERÍA 2: ✓ ya estaba aplicado
- DEBERÍA 3: ✓ aceptado
- DEBERÍA 4: ✓ ya estaba aplicado
- DEBERÍA 5: ✗ rechazado
- DEBERÍA 6: ✗ rechazado

Aprobado sobre la copia: ✓ Aprobada por Omar (2026-10-31T22:55)

Copia después de aprobar: md5 `3f1be0ed9d5bcdf7f9e470e851c4ba48`, `aprobado.md5` igual = True; «Y no fue el único que se llevó Wittenoom adentro.» aparece 1 vez.

Errores de página: 0 []

## Topic real

Archivos de `_steps/<tid>/` que cambiaron: ninguno
