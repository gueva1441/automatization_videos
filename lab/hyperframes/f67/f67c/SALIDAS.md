# F67c — salidas

## C. `etapa_de` de Wittenoom

- Hoy: `('papel', 'el papel no está aprobado')`
- `assemble_final_script` hoy: no escribe: «m06_assembler: sin papel aprobado vigente: el papel no está aprobado»
- `01b_narration.json` = la narración aprobada, cap por cap: [True, True, True, True, True, True, True]
- Simulando el papel aprobado (monkeypatch de `estado_papel`): `('voz', 'data/scripts/123bbb64-9fca-4395-8bf4-57d60e219ef1.json sin sello')`

Artefactos del 28-oct que ya no pasan:

- script: script sin sello
- manifest: manifest sin sello
- fondos.json: falta fondos.json
- GUION_PANTALLA.json: falta GUION_PANTALLA.json

Archivos de `_steps/<tid>/` que cambiaron: ninguno
