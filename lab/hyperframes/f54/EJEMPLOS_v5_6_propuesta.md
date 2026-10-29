# F54 B.2 — bloque `<ejemplos>` propuesto para el guionista (PARADA B.0: no entra al código hasta el OK del analista)

Reemplaza el bloque `<ejemplos>` entero del v5.5 (`guion_v4.SYSTEM_V5_5`). Mismo caso ficticio (Puerto Cardal, 1968: Elvira Soto, Bascuñán, el Alborada, el niño, la Dirección de Faros y Balizas). Lo que cambia: el gancho lleva la apuesta (la frase literal del handoff), hay un cierre de cap que deja una deuda con la primera frase del cap siguiente que la paga, un re-gancho a mitad, el pico paga lo que el gancho prometió y el cierre del video vuelve a la imagen del gancho. Se quedan tal cual: la escena con los sentidos, la cita y el silencio, el hecho concreto en vez del juicio y las versiones en disputa. Cero reglas nuevas: los rótulos solo nombran la técnica de cada ejemplo, como antes.

```text
<ejemplos>
Los ejemplos son de un caso que no es el tuyo (una estación de radio y faro en una isla, mil novecientos sesenta y ocho). Copiá la técnica, no el contenido: ninguno de estos nombres, lugares ni cifras está en tus datos.

Gancho (escena en curso, la apuesta, lugar y año, vuelta atrás):
«Una mujer transmite en clave morse a la luz de una vela. La sala huele a querosén quemado. Afuera, el faro sigue encendido. Once personas esperan un barco. Tres de ellas no van a ver la primavera. Puerto Cardal, invierno de mil novecientos sesenta y ocho. Pero tres semanas antes de la vela, llegó un telegrama. Y con él, una orden.»

Cierre de cap que deja una deuda, y la primera frase del cap siguiente que la paga:
el cap 2 termina: «El Alborada tenía que llegar el lunes. No llegó el lunes.»
el cap 3 empieza: «El lunes, el Alborada estaba amarrado en el puerto, con la bodega cargada y el capitán a bordo. Lo que faltaba era un papel.»

Re-gancho a mitad del video (una oración que recuerda la deuda sin pagarla, al cierre de un cap):
«Quedaban nueve días de telegramas sin firma. Para entonces, el niño ya tosía.»

Escena con los sentidos, sin inventar hechos (todo sale de «olor a querosén, ventanas tapadas con mantas, el ruido del generador que se apaga, el silencio después»):
«La noche del catorce, el generador tosió dos veces y se apagó. Por primera vez en tres semanas la estación quedó en silencio. Las ventanas estaban tapadas con mantas para guardar el calor. Olía a querosén. Alguien encendió una vela y la sala apareció, chica, llena de gente que no hablaba.»

Cita y silencio después:
«Teo Marín iba en el Alborada esa mañana. "El capitán leyó el papel y dio la vuelta", dijo Marín. No supo qué decía el papel. Vio la isla a lo lejos. Vio que se alejaba.»

El hecho concreto en vez del juicio (no dice «cruel», «abandono», «inhumano»):
«Elvira pidió el barco siete veces. Las siete respuestas dicen lo mismo: mantener servicio. Ninguna tiene firma.»

Pico (dos frases cortas antes, la más corta después; es la primera de las tres muertes que el gancho prometió):
«Bascuñán mira la silla. La levanta. La rompe contra el piso de la sala de radio y mete las patas en la estufa. Esa noche, mientras la madera arde, Elvira transmite con las baterías del faro. En el cuarto de al lado, el niño deja de toser. Nadie lo dice. Lo saben.»

Versiones en disputa, sin elegir:
«Según los telegramas que Elvira guardó, el Alborada zarpó y recibió orden de volver. El capitán declaró ante la comisión que nunca salió del puerto por el temporal. El barco, esa semana, no llegó.»

Cierre del video (vuelve a la imagen del gancho; la última frase es una cita, sin moraleja):
«La vela se apagó sola, al amanecer del día veintitrés, cuando el Alborada ya se veía desde la torre. Elvira Soto no habla de la comisión. Habla de su libro de telegramas: "Yo mandaba los telegramas. Nadie me dijo que los leyeran".»
</ejemplos>
```

## Qué cambió frente al bloque del v5.4/v5.5, ejemplo por ejemplo
| ejemplo | v5.5 | propuesta |
|---|---|---|
| Gancho | «Once personas esperan un barco que no va a llegar, porque alguien decidió que no llegara.» (sin apuesta: no dice qué se pierde) | «Once personas esperan un barco. Tres de ellas no van a ver la primavera.» (la frase del handoff; primera frase sin cifra, lugar y año, vuelta atrás, igual que antes) |
| Cierre de cap que abre | «Cuando el Alborada entró por fin a la bahía, el padre Quiroga contó… Faltaban dos. Las familias decían que tres.» (solo el cierre; adelantaba el conteo del final) | el cierre del cap 2 («No llegó el lunes.») **y** la primera frase del cap 3 que lo paga («…Lo que faltaba era un papel.») |
| Re-gancho | no había | una oración al cierre de un cap de la mitad que recuerda la deuda («…el niño ya tosía») sin pagarla |
| Pico | igual | igual, y el rótulo dice que paga lo que el gancho prometió (la primera de las tres muertes) |
| Cierre del video | la cita de Soto sola | la vela del gancho se apaga (vuelve a la imagen) y después la cita de Soto, igual que antes |
| Escena con los sentidos · Cita y silencio · Hecho concreto · Versiones en disputa | — | sin cambios |

## Para mirar (analista)
- El conteo: el gancho promete tres muertes; el pico es la primera (el niño); el viejo ejemplo de «faltaban dos, las familias decían que tres» se fue con el cierre de cap, y las versiones en disputa (comisión dos, familias tres) siguen en la escaleta de ejemplo de `m01a`. Si eso molesta, cambio «Tres» por lo que diga el analista: la frase es la del handoff.
- «Quedaban nueve días» es un número del caso ficticio (como los veintitrés días y los siete telegramas del bloque viejo), no una constante del pipeline.
- Se agregan dos nombres de técnica (deuda pagada en la primera frase, re-gancho) que ya existen en `<estructura>` §2 y en `recuerda_loop`: no hay regla nueva, hay ejemplo nuevo.
