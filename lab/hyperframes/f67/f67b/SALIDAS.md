# F67b — salidas

## 1. `papel_falta` y `etapa_de`

Wittenoom hoy (narración sin aprobar):

- `papel_falta` → `papel de otra narración: se re-escribe` (el papel tiene `narracion_md5` = None; narración `778d3e1dcd4ca545453f7a29b6a92bb3`)
- `etapa_de` → `('narracion', 'la narración no está aprobada')`

Sobre una copia, con la narración aprobada:

- aprobada: `778d3e1dcd4ca545453f7a29b6a92bb3`
- `papel_falta` → `papel de otra narración: se re-escribe`
- `etapa_de` → `('papel_nuevo', 'papel de otra narración: se re-escribe')`

## 2. `/papel/aprobar` 409 y botón deshabilitado

POST `/papel/aprobar` con Wittenoom hoy: **409** `{"error": "la narración no está aprobada"}`

Pestaña PAPEL en Chrome headless: botón «Aprobar papel» deshabilitado = **True** · 0 errores de página · aviso: «No se puede aprobar el papel: la narración no está aprobada.» · captura `f67b/papel_bloqueado.png`.

Comienzo de la pestaña:

```
Sin aprobar
el papel no está aprobado
claude-opus-5-5 m01e-7 · US$ 0.9797 · cierre: sin motivos · 0 de 13 fichas revisadas
Aprobar papel
No se puede aprobar el papel: la narración no está aprobada.
⚠ La narración sigue contradiciendo el archivo:
ch01 [1] «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.»: La herida del pie va a cerrar. (D85)
ch01 [9] «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.»: Los residuos de la mina siguen donde los dejaron. (D04, D149)
ch03 [14] «En 19
```

## 3. Normalizado desfasado

Comprobación de solo lectura sobre Wittenoom: caps distintos [1, 2, 3, 4, 5, 6, 7] (7). El archivo real sigue en disco: se borra al correr la voz.

Sobre la copia, `descartar_normalizado` imprime:

```
[normalizado] desfasado: 7 caps distintos, se borra
```

Caps [1, 2, 3, 4, 5, 6, 7]; el archivo sigue: False.

`audio_manager._resolve_text_for_tts`, hoy con el archivo real: lee el texto viejo = **True**. Sin el archivo: normalize_for_tts de la narración actual = **True** (el `exists()` de `audio_manager.py:519`).

`normalizer_gate` lo regenera sobre la copia, sin LLM (`_apply_spans_to_narration` + `_persist_normalized_narration`, lo que corre siempre el gate): desfasado después = [].

## 4. `--criticar`

`python fase1_5.py --help`:

```
--criticar            F67b: juez m05 + crítico (≈ US$ 0,8), sin verificador,
                        sobre la narración ya escrita de --topic; usa la tabla
                        de 01b_verificacion.md que haya en disco y no toca la
                        narración ni su aprobación
```

Corrida en seco sobre una copia, con `post` falso; el POST real, `verificar_caps`, `run_verificacion` y `run_pantalla` explotan: exit 0, 1 llamada(s) al `post` falso: ['claude-opus-5-5 · system md5 fb3e5a9e734ff730a3b5184d88e7f38a']. La narración no cambió: True.

```
[m01f] intento 1: in 1 · out 1 · US$ 0.0000 · JSON
  [m01f] nota 6.5 · 0 DEBERÍA · US$ 0.0000 → C:\Users\Canada\AppData\Local\Temp\tmp_fho2r2x\steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\01f_critico.md
  [narración] narración aprobada por Prueba (2026-10-31), md5 778d3e1d…
```

## Topic real

Archivos de `_steps/<tid>/` que cambiaron: ninguno
