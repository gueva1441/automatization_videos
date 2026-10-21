# DECISIONES F4e — Marca de esquina apagada, crítico visual (6b), hoja de contactos

Pedido de Omar (2026-10-20), sobre F4d (`b23b0ae`).

## 1 · Marca
- **I1** `channel_bug.corner.enabled = false` en el perfil. `gfx_bug.config()` lo expone como `corner_enabled`. El cosido del render disperso ya tenía el interruptor (`bug["corner"]`) y `burn_on_clip` ahora lo respeta. El cierre del video (encapuchado al centro + negro) queda igual. El log del cap dice «esquina apagada».

## 2 · Crítico visual — `script_engine/gfx_critic.py`, paso 6b
- **I2 (dónde)** Corre en `gfx_layer.apply_gfx` después de todo el plan: reglas duras, pico, identidad, íconos, pregunta y pausa. Va antes de guardar el plan resuelto, de los SFX y del render, así los SFX y los cues reflejan solo lo que pasó. Token `visual_critic` (OFF en el motor, ON en misterio).
- **I3 (qué juzga)** Sello, ícono (énfasis con `icon_callout`), recorte, dato, contador, nivel de agua y zoom. El contador no estaba en la lista de Omar; lo sumé porque es un dato en pantalla. No juzga el título, la pregunta de cierre, los golpes de zoom ni las transiciones: no son bloques de contenido.
- **I4 (qué recibe)** (a) El cuadro REAL de la foto: `base.mp4`, sin gráficos, 1280 px de ancho, en el instante en que el bloque ya entró (inicio + min(1 s, mitad de la duración)). (b) La frase de la voz en ese instante: la oración que lo contiene, o ±2 s si cae en un silencio. (c) El bloque descripto en texto: qué es, qué dice, dónde va y cuánto ocupa, porque en el cuadro todavía no está dibujado.
- **I5 (criterios)** Los tres de Omar en el prompt: el ícono no dibuja lo que la foto ya muestra; el texto no repite la voz de ese instante; nada tapa un rostro ni una zona clara. Agregué una aclaración: un sello de UNA palabra que dice la voz es énfasis, no repetición. Si no, todo sello caía en «repite», porque por diseño el sello es una palabra de la voz (R3/R4).
- **I6 (few-shot)** `gfx_profiles/misterio_critico_fewshot.json`: 5 bloques del plan dorado de ch02 aprobados por Omar (recorte de Katrina, nivel de agua 4.6 m, dato 6,500 personas, zoom «ahogaba», recorte de las celdas). Cada uno va con la frase de la voz (tomada de los subtítulos de ch02) y veredicto «suma». Van solo en texto, sin imagen, para no multiplicar el costo por bloque. Lo genera `armar_fewshot_critico.py`.
- **I7 (veredicto)** JSON con esquema: `veredicto` ∈ suma | repite | estorba, y `motivo`. Solo pasan los «suma». El crítico solo quita: nunca agrega ni reescribe. Si quita el bloque del pico (nivel de agua o zoom), el pico queda con su palabra y se anota.
- **I8 (error)** Si Gemini falla o responde inválido, el veredicto es «error», el bloque **queda** y no se cachea. Así una caída de Gemini no vacía el cap, y se reintenta en la próxima corrida.
- **I9 (caché y log)** `work_dir/gfx_critic_<cap>.json` por (hash del cuadro, bloque, voz, versión del prompt). Cada veredicto va a `gfx_<cap>.log` («crítico: t bloque «texto» → VEREDICTO — motivo»), más la cuenta final «N/M bloques pasan».
- **I10 (modelo)** `api.gemini_model` con temperatura 0, el mismo cliente que `gfx_vision`. El costo se registra con `cost_tracker.track_gemini_vision`: 7 llamadas en ch02 y 8 en ch05.

## 3 · Hoja de contactos
- **I11** `hoja_contactos_<cap>.jpg` en `work_dir`, copiada en `lab/hyperframes/f4e/`. Lleva un cuadro por bloque que pasó, del render de la capa gfx (sin subtítulos), 0.4 s después del cuadro que vio el crítico, para que el bloque ya esté dibujado. Cada cuadro tiene el tiempo, el bloque, el veredicto y el motivo. «Un cuadro 1:1 por bloque» lo leí como un cuadro por cada bloque. Los cuadros van a 640 px para que la hoja se pueda mirar entera; no son recortes sin escalar.

## Lo que la hoja mostró y el crítico no ve
- **I12 (defecto, sin arreglar)** ch02 1:00.7: el recorte «días en celdas inundadas con agua contaminada con aguas residuales» (10 palabras, la cláusula completa de F4d) no entra en la tarjeta y se corta en «…AGUA CONTAMINADA CO». «aguas residuales», lo que el recorte tenía que sumar, no se ve. El crítico dio «suma» porque juzga el texto propuesto y no lo ve dibujado. Arreglo posible: que la tarjeta achique la letra o crezca hasta que entre el titular, o bajar el tope de la cláusula a 8 palabras.
- **I13 (defecto, sin arreglar)** ch02 1:17.9: el recuadro del zoom «Pies del hombre» cae a la izquierda de los pies, sobre la zona vacía. La caja viene de la caché de visión de F4b. El crítico recibe la caja como coordenadas y no la valida. Arreglo posible: mandarle al crítico el recorte de la caja, como ya hace `verify_crop`, o pasar el zoom por `verify_crop` también fuera del pico.
- **I14** El nivel de agua se ve a mitad de subida («2 m») porque el cuadro de la hoja cae durante la animación (2.5 s de subida).
