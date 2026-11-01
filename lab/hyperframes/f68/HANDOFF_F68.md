# HANDOFF F68 — Motor de fotos → Nano Banana 2 Lite (una foto por llamada) + respaldo Seedream 4.5; regenerar fotos de Wittenoom para QA

Repo C:\CLAUDE_PROJECTS\automatization_videos, rama f11-guion-v4 (HEAD 00a60b0).

## Por qué
Lab NB-TOL6 (lab/_nb_tol6/): Omar eligió google/nano-banana-2-lite por la cara (hoja_P4). Con safety_tolerance 6 pasa muerte, morgue y edit oscuro con madre; bloquea ahorcados (model_moderated). Seedream 5.0 Lite deforma caras; el modo secuencia es sospechoso adicional.

## ETAPA 0 — Auditoría del handoff (antes de tocar nada)
Subagente revisor-handoff: leer este handoff contra el código real (engine_profiles.py, asset_manager.py, foto_madre.py, script_engine/m03_imagenes_v3.py, config de pipeline image_width/height, tests). Listar contradicciones o supuestos falsos. Corregir solo dentro del alcance; si algo obliga a decidir fuera de alcance → anotar y seguir con la opción más conservadora. Su veredicto va íntegro en el reporte.

## MÓDULOS QUE TOCA
- engine_profiles.py — perfiles de motor de fotos: nuevo PERFIL_NB2_LITE como principal; PERFIL_SEEDREAM pasa a 4.5 y queda solo como respaldo.
- asset_manager.py — llamadas a fal: una foto por llamada con madre (sin secuencia) + respaldo automático.
- foto_madre.py / asset_manager.py — chascada: guardar en disco el prompt de cada madre y el texto exacto de cada llamada de foto.
- Tests del módulo: adaptar los que fijan Seedream/secuencia (reescribir aserciones, no borrar tests).

## CONSTANTES (todas declaradas)
- Motor principal: t2i google/nano-banana-2-lite; edit google/nano-banana-2-lite/edit → elección de Omar 1-11-2026.
- safety_tolerance = "6" → decisión de Omar (máximo del esquema 1–6).
- aspect_ratio = "16:9" → formato del canal.
- Salida nativa fija 1K (1376×768, medido en el lab). Upscale con ffmpeg lanczos a pipeline.image_width×image_height (hoy 2560×1440) para no romper el bake → decisión del analista mientras Omar duerme (fiel, gratis, reversible). Guardar TAMBIÉN el original nativo al lado (*_native.png).
- Costo nb2 lite: por tokens; registrar 0,042 US$/foto (panel de fal, medido por Omar) marcado como estimado.
- Respaldo: Seedream 4.5 (fal-ai/bytedance/seedream/v4.5/text-to-image y /edit, accepts_seed=True, 0,04 US$) → propuesta del analista; anotarlo.
- Workers: máximo paralelo (regla de Omar). Sin tope de dólares; reportar costo al final.

## Reglas
1. Una foto = una llamada. Con persona: edit con su(s) madre(s) en image_urls. Sin persona: text-to-image sin referencia (ninguna escena sin la persona recibe madre — corrige el bug del lote Daniel#1 Image 5).
2. Prompt: el MISMO texto en prosa que hoy arma el pipeline por foto (no cambiar slots, no agregar reglas). Solo en edit, anteponer la frase que funcionó en el lab: «A photograph of the same person shown in the reference image.» (si hay más de una madre: «A photograph of the same people shown in the reference images.»).
3. Respaldo automático: si nb2 lite devuelve content_policy_violation o no_media_generated → misma foto, mismo prompt, mismas madres, por Seedream 4.5 (edit o t2i). Marcar en el manifest motor=seedream45_respaldo con el mensaje exacto. Si el respaldo también rechaza → camino de falla que ya existe (no inventar otro).
4. Cola de fal con request_id guardado ANTES de esperar (como F60); reanudar sin re-pedir.
5. El camino de secuencia (_llamar_secuencia) queda sin uso con el perfil nuevo; NO borrarlo.
6. Chascada: escribir en disco el prompt de cada madre (foto_madre.py hoy lo descarta) y el texto exacto + modelo + parámetros de cada llamada de foto, junto a la foto.

## ETAPA 1 — Código + tests
Implementar con diff mínimo; suite rápida verde.

## ETAPA 2 — Prueba chica antes de gastar todo
3 fotos reales de Wittenoom: una de Daniel con madre, una de grupo con persona, una sin persona. Verificar: nativo 1376×768 + versión 2560×1440, manifest, prompt guardado en disco. Probar el respaldo forzando un rechazo con el prompt P1 (ahorcado) de lab/_nb_tol6/run_lab.py. Si algo falla → arreglar y repetir; si no se puede → PARADA.

## ETAPA 3 — Regenerar TODAS las fotos de Wittenoom (video 123bbb64-9fca-4395-8bf4-57d60e219ef1)
- Las fotos actuales (Seedream 5.0 Lite) se MUEVEN a output/<topic>/_archivo_seedream5lite/ (no se borran).
- Correr el paso normal de imágenes del pipeline para que QA Studio las muestre como siempre.
- Clips (Gemini Omni): NO regenerar. Listar cuáles usan una foto de arranque que cambió.

## ETAPA 4 — Reporte (lab/hyperframes/f68/F68_REPORT.md + lab/ESTADO_SESION.md)
Lectura tomada · tabla por foto (motor, respaldo sí/no y motivo, segundos, US$) · número de respaldos · clips afectados · costo total · veredicto íntegro de revisor-handoff · «lo que queda abierto». Commit + push.

PARADA al terminar la Etapa 4. No tocar main, guion, papel, voz, gfx ni render.

---

# ADENDA F68 — Omar duerme y quiere ver TODAS las fotos nuevas en QA Studio al levantarse. Esto manda sobre el handoff:

1. AUTONOMÍA TOTAL: no preguntes nada a nadie. El subagente revisor-handoff audita (Etapa 0) y VOS aplicás sus correcciones directamente, sin esperar aprobación. Anotá cada corrección en el reporte.
2. SIN PARADAS por problemas arreglables: si algo falla en la Etapa 2 o 3 (tests, una foto, un endpoint, tamaño, manifest), diagnosticá la causa, arreglala y seguí. Repetí las veces que haga falta. Solo parás si es IMPOSIBLE generar fotos (fal caído o clave sin saldo); en ese caso dejá todo lo hecho guardado y el motivo en el reporte.
3. REGENERAR TODAS las fotos de Wittenoom, sin excepción (con y sin persona). El costo no importa (decisión de Omar); solo reportalo al final.
4. Si una foto falla en Nano Banana Y en el respaldo Seedream 4.5, reintentá 2 veces más; si sigue fallando, dejala marcada en el manifest y seguí con las demás. No frenes el lote por una foto.
5. El resultado final obligatorio: QA Studio abre Wittenoom y muestra las fotos nuevas. Verificalo vos (que QA Studio las lea) antes de cerrar. Si no las muestra, arreglalo.
6. Commit + push y reporte al final, como dice la Etapa 4.
