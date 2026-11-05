# HANDOFF F78b — variantes: «estado visible en el cuerpo» + edad exacta
Rama `f11-guion-v4`, base `b891b75` (F78a B). Analista, 2026-11-04. Aprobado por Omar 19:58 («dale»). Sigue la PARADA de F78a: la Etapa C de F78a NO corre en esta tanda.

## Por qué (lo visto en la Etapa B de F78a, hoja `lab/hyperframes/f78a/b/analista_vista.jpg`)
1. Arcadio: manos tiesas, no deformadas (gancho ch01_supp_05, calculadora ch06_img_14); la voz dice «manos deformadas».
2. Lozano@1981-1981: la variante dibujó la sala de vidrio con niños llorando detrás → contamina sus 3 fotos.
3. Carmen@1992-2000_33: se ve de ~20 años.
Causa (diseño del analista): `_prompt_variante` (foto_madre.py ~l.492) mete la `condition` CRUDA del canon (puede ser un lugar,
una enfermedad abstracta o un hecho no visible) y la edad como rango («early-30s»), que el modelo no lee.

## Constantes (ninguna nueva)
| valor | origen |
|---|---|
| modelo de la llamada de estado = `MODELO_CASILLEROS` con `guion_v4.ESFUERZO[…]`, como `_llamar_rasgos` | existente (F78a) |
| edad = el `edad` que ya calcula `clave_de_foto`, escrita en dígitos | existente (F78a) |
Las claves de variante, cuándo hay variante y la regla única `_madres_para_item` NO cambian.

## Módulo que toca (1): `foto_madre.py` + tests
1. NUEVO `_llamar_estados` + cache `foto_madre/estados.json` (md5 de la entrada), APARTE de `rasgos.json`: los rasgos y las 7
   madres limpias NO se tocan (no cambian de cara).
2. `_prompt_variante` usa `estado_visible` (no la `condition` cruda) y la edad exacta.
3. Si una variante no tiene ni `estado_visible` ni edad → no se genera (la foto usa la madre limpia; ya lo cubre «variante sin
   archivo → madre limpia» de `_madres_para_item`).
Tests: prompt exacto nuevo de la variante; estado vacío y sin edad → sin variante; cache de estados; rasgos.json intacto.

## Llamada de estado — prompt completo (va tal cual)
Entrada: JSON lista de {name, tramo, condition}, una fila por variante que existe (clave con tramo). Salida con schema: lista de
{name (enum), tramo (enum de los tramos de entrada), estado_visible (string, puede ser "")}, una por fila de entrada.
```
Cada fila es una persona real de un documental, con la condición que el material documenta para esos años. Para cada fila escribí
en inglés, en una sola frase, SOLO lo que esa condición deja visible en su cuerpo, en una foto de cintura para arriba con la cara y
las dos manos a la vista: piel, cara, manos, brazos, pelo, postura y contextura, en términos concretos que se puedan fotografiar.
No pongas lugares, otras personas, objetos, ropa, acciones ni sentimientos.
No agregues nada que la condición no diga o no implique.
Si la condición no deja nada visible en el cuerpo, devolvé una cadena vacía.
```
Revisión del analista (a mano, las 6 condiciones de Colza):
- Arcadio «Deformed hands and upper body with disabling chronic pain» → p. ej. «fingers curled and rigid with misshapen
  knuckles, hunched stiff shoulders, thin forearms» (concreto: es lo que faltaba).
- Angela «chronically ill… dragging feet, veins exhausted by transfusions…» → «gaunt sallow face, bruised inner forearms».
- Lozano «hospitalized in a glass-walled room…» → "" o signos en la cara; nunca la sala (la prohíbe «no lugares, no otras personas»).
- Carmen 1981-1982 «…losing more than twenty kilos and visibly emaciated» → «emaciated, hollow cheeks, very thin arms».
- Carmen 1992-2000 «unable to work… disability pension» → "" → la variante lleva solo la edad.
- Mercedes «cramps and insomnia, too weak…» → «dark circles under the eyes, pale tired face» o "".
Simulación real = la Etapa B de esta tanda (barata, con PARADA).

## Prompt nuevo de la variante (completo)
```
The same person as in the reference image: same face, same features, same identity. {si hay edad: "The person is now {edad} years old; show that age in the face, hair and body."} {si hay estado_visible: "<estado_visible>."} Waist-up portrait framed so that the face and both hands are visible, {ROPA_MADRE}, plain mid-grey background, soft even light. {ESTILO_C con anio_estilo} {NO_TEXT}
```
Se borra la frase «Show only what of this would be visible on the body; if nothing is visible, keep the person unchanged» (ya
no hace falta: el estado ya llega solo con lo visible) y el uso de `descriptor_edad` en la variante (sigue para decidir la clave).

## Etapas
A) Código + tests + suite rápida. Salida en texto: `estados.json` NO todavía; la tabla persona/tramo/edad/condición → qué se
   pediría. Commit.
B) Colza: 1 llamada de estado → `estados.json`; mover las 8 variantes actuales (png, _native, .prompt.txt, .llamada.json) a
   `foto_madre/_previas_f78b/`; regenerar las variantes que correspondan; `m06.assemble_final_script`; regenerar 4 fotos de
   control (mover sus 4 archivos a `<cap>/_previas_f78b/`, `process_script`, mismo prompt, sin Opus de m03):
   ch01_supp_05 (Arcadio juicio), ch06_img_14 (Arcadio calculadora), ch04_img_12 (Lozano), ch07_supp_07 (Carmen 2000).
   Hoja `lab/hyperframes/f78a/ETAPA_B2.html`: estados.json, variantes F78a vs F78b, 4 fotos F78a vs F78b con su prompt.
   **PARADA: Omar y el analista miran. La Etapa C de F78a sigue sin correr.**

## Abierto (no entra)
- ch07_supp_07: el prompt de la escena («short practical hair») pisa la trenza de la madre. Si con la edad exacta sigue
  saliendo un muchacho, se arregla en m03 (escritor de prompts) en otra tanda.
- Madre de Mercedes con marco oscuro → «se arregla si se repite».
- `lab/hyperframes/f60/etapa_bc_prueba.py:90` firma vieja de `_clave_lote` (chascada: actualizarla).

## ADENDA (auditoría de subagente, aplicada) — manda sobre lo de arriba
1. Invalidación: cada variante guarda en su `.prompt.txt` / metadatos el md5 de (estado_visible + edad). Si cambia → la variante
   vieja va a `_previas_<tanda>` y se regenera. El skip por archivo existente queda solo cuando el md5 coincide.
2. `_a_previas` recibe la carpeta como parámetro (hoy fija `_previas_f78a`, foto_madre.py:81) y mueve TODOS los archivos de la
   variante (`.png`, `_native.png`, `.prompt.txt`, `.llamada.json`), no solo el `.prompt.txt` (l.484).
3. Entrada de la llamada de estado: una fila por par (name, tramo) ÚNICO sacado de `por_clave` (l.632-636), no de lo que hay en
   disco. Colza = 6 filas. Cruce de la respuesta por (name, tramo); un par que falta o cruzado → "". Si la llamada falla → no se
   mueve ni se genera nada (igual que rasgos, l.574-579).
4. Si ninguna clave tiene tramo → no hay llamada ni `estados.json`.
5. Clave sin estado_visible y sin edad → estado explícito «sin variante: sin estado visible», no entra en `pedidas`; m06 y
   `_madres_para_item` ya caen a la madre limpia. Esperado en Colza: Lozano@1981-1981 (6 años = la madre) sin variante → su foto
   de control ch04_img_12 sale con la madre limpia. Eso es correcto, no falla.
6. Tests: `_llamar_estados` mockeado en las fixtures autouse de test_module_f60_bc.py (l.38-47) y test_module_f78a.py (`_fakes`,
   l.231-248) con un estado NO vacío; reescribir el test de l.186-195 (hoy afirma «Now a early-30s» y «Show only»). Ningún test sale a la red.
7. Etapa B: el mismo preflight de F78a (`b/etapa_b.py:39-59`: si falta otra foto o clip → PARADA). Orden: estados → variantes →
   m06 → mover las 4 → `process_script`. Declarar que las otras fotos de esas variantes quedan con la foto vieja hasta la Etapa C.
8. `<estado_visible>` con `rstrip('.')` antes de agregar el punto. `anio_estilo` sigue siendo el primer año del tramo (Carmen de
   33 con estilo 1992): se declara, no se cambia. Menores con edad pueden caer al respaldo Seedream: se declara.
9. Sin tope de dólares (regla de Omar 2026-10-29): el costo se reporta después.
