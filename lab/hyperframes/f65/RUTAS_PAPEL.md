# F65b Etapa B — RUTAS_PAPEL: cada ruta por HTTP (copia del papel actual, 0 llamadas)

Copia temporal de `01e_pantalla.json, 01e_pantalla.md, 01e_pantalla.raw.json`; md5 del papel `cceafae3cf8095e33a224f4eed326ca8`. Lo que se aprueba y se edita acá no llega a producción.

## GET /papel

Cabecera: `estado` {"aprobado": false, "motivo": "el papel no está aprobado"} · md5 `2df09a51ac79ece83e0a1eaf54cda99a` · US$ 1.23091 · claude-opus-5-5 · fichas 13 · revisadas 0 · cierre sin motivos · sin_beat 1 · a_pantalla_vacios 5 · aviso_narracion 1

Descartes atribuidos a algún beat: 56 filas · sin beat: ['Q22']

El beat 1 entero:

```json
{
 "cap": "ch01",
 "beat": 1,
 "funcion": "gancho",
 "pico": true,
 "revisado": false,
 "ficha": {
  "pool_id": "D108",
  "sentence_idx": 6,
  "palabra": "pueblo",
  "palabra_en_oracion": true,
  "etiqueta": "ESE PUEBLO",
  "texto": "Escenario del peor desastre industrial de Australia",
  "respaldo": "La industria de la crocidolita de Wittenoom es considerada el peor desastre industrial en la historia de Australia.",
  "estilo": "normal",
  "aporta": "Dice la escala de lo que pasó en el pueblo de la foto, algo que la voz nunca dice.",
  "oracion": "Esa foto se tomó en un pueblo que hoy no figura en ningún mapa.",
  "caracteres": 61,
  "caben": 71,
  "anio": null,
  "relato": null,
  "juicio_verificador": {
   "regla": [
    "no_dicho"
   ],
   "motivo": "La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra 'Australia'.",
   "tokens": {
    "no_dicho": [
     "Australia"
    ]
   }
  }
 },
 "sello": {
  "palabra": "AMENAZA",
  "sentence_idx": 3,
  "oracion": "Una herida hecha por un pedazo de mineral que no cierra."
 },
 "descartes": [
  {
   "pool_id": "D85",
   "texto": "Daniel Écija padre se hirió el pie con un trozo de amianto y la herida no se cerraba.",
   "tipo": "voz_lo_dice",
   "motivo": "La herida que no cerraba la cuenta la voz en ch01.",
   "quien": "modelo",
   "que": null
  }
 ],
 "a_pantalla_vacio": []
}
```

## POST /papel/revisar

`{cap: ch01, beat: 1, on: true}` → `{"revisados": [["ch01", 1]]}`
- `01e_pantalla.revision.json`: `{
 "revisados": [
  [
   "ch01",
   1
  ]
 ]
}`
- md5 del papel sin cambios: True · revisadas 1

## POST /papel/aprobar (solo en la copia)

`{por: Prueba}` → `{"aprobado": {"por": "Prueba", "fecha": "2026-10-31T17:08", "md5": "2df09a51ac79ece83e0a1eaf54cda99a"}}`
- estado: `{"aprobado": true, "motivo": "papel aprobado por Prueba (2026-10-31T17:08), md5 2df09a51…"}`

## POST /papel/editar con null

`{cap: ch05, beat: 9, ficha: null}` (quitaba D94) → `{"ok": true}`
- ficha ahora: None
- estado antes: `{"aprobado": true, "motivo": "papel aprobado por Prueba (2026-10-31T17:08), md5 2df09a51…"}`
- estado después: `{"aprobado": false, "motivo": "el papel cambió después de la aprobación de Prueba (2026-10-31T17:08): md5 2df09a51… → 23e2caba…"}`
- `01e_pantalla.antes_de_edicion.json` existe: True

## Vuelta atrás (la ficha desde `01e_pantalla.antes_de_edicion.json`)

→ `{"ok": true}` · ficha D94 «EN 1989, CSR PAGÓ · 18,3 millones de dólares australianos a 200 afectados» · juicio_verificador conservado: True · editado: True
- md5 vuelve al original: False (`editar` deja `editado` y `ediciones`: el papel «restaurado» por la ruta tiene otro md5; para volver byte a byte, copiar el `antes_de_edicion`)
- estado: `{"aprobado": false, "motivo": "el papel cambió después de la aprobación de Prueba (2026-10-31T17:08): md5 2df09a51… → 3fa43a8c…"}`

## POST /papel/sugerir

No se llama acá (0 llamadas): ya se midió en la Etapa A. Probada en `test_module_f65b::test_b4` con un `sugerir` falso: hilo, 409 si hay uno en curso, `GET /papel/sugerir_status`.

## Producción intacta

- 01e_pantalla.json: `cceafae3cf8095e33a224f4eed326ca8` · igual: True
- 01e_pantalla.md: `8e800b88921b640704ef3cf7e5da81c1` · igual: True
- 01e_pantalla.raw.json: `22375a5f4ad1bafdc16fd7a1f1a5f175` · igual: True
- `01e_pantalla.revision.json` en producción: False
