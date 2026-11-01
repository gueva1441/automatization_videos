# HANDOFF F71b — la persona que el prompt nombra trae su madre (y QA lo puede arreglar)

## Por qué (Omar, 2026-11-01 16:31)
ch01 supp 1 (la mujer con la foto en blanco y negro): la voz habla de Daniel, el prompt dice «An aged black-and-white print of Daniel Écija…», pero la cara de la foto no es Daniel. En QA pidió «que sea Daniel» y no cambió.

## Causa raíz
- El ítem tiene `persona: []` aunque el prompt nombra a Daniel Écija → `_madres_para_item` no le da su madre → el motor inventa la cara.
- QA (`_uris_madres`) solo lee `persona`, que no se edita («casillero persona: no cambia con el pedido») → ningún pedido puede traer la madre.

## Simulación (analista, guion vivo de Wittenoom)
99 ítems (img, supp y fotos de clip). Con nombre del `foto_madre_registry` en el prompt y sin esa persona en `persona`: **1** (ch01 supp 1, Daniel Écija). Agregar por nombre cambia ese 1 y ningún otro. Filtro de era: el ítem es `anio` 2026, Daniel `era` 1962-1963; 2026 no cae en un tramo fuera de era de `condition_by_period` → `persona_aporta_madre` = True (aporta).

## Arreglo (código, sin prompts)
En `asset_manager._madres_para_item` (la REGLA ÚNICA, la usan producción y QA): parámetro nuevo `prompt: str = ""`. Candidatos = `persona` (en orden) + nombres del registry que aparecen en `prompt` y no están en `persona` (nombre completo, gana el más largo: «Daniel Écija hijo» no cuenta como «Daniel Écija»; claves que empiezan con `__` fuera) + `foto_madre_ref`; mismo filtro de era, sin repetir, tope 2 (sin cambios). Todos los llamadores pasan el prompt del ítem (QA: el prompt re-armado). Nada se guarda en `persona`: se deriva cada vez.

## Constantes
Ninguna nueva (tope 2 y filtro de era ya existen, F60 B).

## Módulos
- `asset_manager.py` `_madres_para_item`: hoy persona + refs → también nombres del registry en el prompt.
- Llamadores de `_madres_para_item` (asset_manager y `qa_studio_server._uris_madres`): pasan el prompt.

## Etapas
A. Código + tests (el caso real de ch01 supp 1; «Daniel Écija hijo» no dispara a «Daniel Écija»; filtro de era sigue mandando; tope 2). Salida: tabla de los 99 ítems de Wittenoom con madres antes→después; debe cambiar solo ch01 supp 1.
B. Prueba real, una sola (≈ US$ 0,042 estimado, se reporta): QA `_fix_core` de ch01 supp 1 con el pedido «la foto que sostiene la mujer es de Daniel Écija joven, su cara». Salida: foto antes/después en `lab/hyperframes/f71/`; queda en producción con backup e `_invalidate_baked`.

## Reglas fijas
Cero prompts nuevos (PEDIDO_* byte a byte). Lo viejo a backup. No correr fase2b ni run_pipeline. Revisor-handoff íntegro. Línea en ESTADO_SESION y DECISIONES (Omar 16:31). PARADA: `lab/hyperframes/f71/F71b_REPORT.md`.
