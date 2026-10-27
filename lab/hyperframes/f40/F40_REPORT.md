# F40 — Gancho, subtítulos documentales y Kyshtym listo para aprobar — REPORTE

Handoff `lab/hyperframes/f40/HANDOFF_F40_gancho_subs_kyshtym.md` (md5 `d769bb2a666174f86e528abcf5605b82`). Rama `f11-guion-v4`, base `a9eb1fc`. Modelo: Opus 5.5 (medium).

Pedido literal de Omar (palabra por palabra):

> Modelo: Opus medium.
>
> Leé ENTERO lab/hyperframes/f40/HANDOFF_F40_gancho_subs_kyshtym.md (md5 d769bb2a666174f86e528abcf5605b82) y ejecutalo con /tanda, en el orden del handoff:
>
> Paso 0 (en serie): commit de DECISIONES.md (md5 0f5bcfb445fae06c7a48ea7b001eed48, línea 18:30) + el handoff, tal cual.
>
> A y B en paralelo (un subagente cada una):
> - A: borrar gancho_dicho (pantalla_filtros) y dice_voz (m01e_pantalla, pantalla_entrada); la cifra del gancho dicha en otra parte de la voz se le PREGUNTA al autor, citando cap, oración y texto; tabla §3 recalculada por código.
> - B: subtítulos documentales en long-form con las constantes de §1 (Anton 60 px, blanco, borde negro, ≤42 car × 2 renglones, 0,833–7 s, sin amarillo, sin efecto por palabra); karaoke solo para short; hook sin tocar. Salida: eventos del .ass de Vajont ch02, render --only-cap ch02 --gfx --reuse-visuals con 3 fotos PNG (2 renglones · ficha + subtítulo · solo subtítulo), y md5 de ch02 con --no-subs antes y después (deben coincidir).
>
> C después de A: Kyshtym (f39-kyshtym) — «cenás»→«cenas» y «acá»→«aquí» en todos los archivos de Fase 1 con respaldo; los 7 títulos de DECISIONES 18:30; papel regenerado con m01e_pantalla.generar (tope 1,00); D50 en ch04 y «2.000» SOLO si se repiten. 01e_pantalla.md nuevo ENTERO en el reporte.
>
> Tope lab/TOPE_TANDA.json = US$ 1,50. Reglas fijas: cero cambios de prompt; nada de voz, imágenes ni render de Kyshtym; no correr --aprobar-papel; nada fuera de A, B y C; usá todos los subagentes en paralelo que la tanda permita.
>
> Cierre: F40_REPORT.md (paso 0, A, B con las 3 fotos, C, suites, push de la rama, «lo que queda abierto» entero, veredicto íntegro de revisor-handoff), ESTADO actualizado. PARADA.

## Lecturas declaradas
`CLAUDE.md`; `DECISIONES.md` (md5 `0f5bcfb4…`, línea 18:30, más 03:34, 00:30, 22:26, 16:38); el handoff entero; `.claude/commands/tanda.md`; `lab/MAPA_MODULOS.md`; `lab/ESTADO_SESION.md` (cabecera y bloque F39); `fase2b.py` (`--no-subs`, `--plan-edit`, `--gfx-debug`); `script_engine/aprobacion.py`; `m01e_pantalla.editar`; los `01e_pantalla.*` y archivos de Fase 1 de `f39-kyshtym`.

## Paso 0
`md5sum DECISIONES.md` = `0f5bcfb445fae06c7a48ea7b001eed48` ✓ · handoff `d769bb2a666174f86e528abcf5605b82` ✓ → commit **`8669045`** (solo esos 2 archivos, tal cual). No entraron `diag_234_cap4.py` ni `lab/hyperframes/f28/a/f28a.log` (de otras tandas).

## Módulos tocados (sticker de `lab/MAPA_MODULOS.md`; mapa regenerado en A y en B: 35 módulos, 115 aristas, 0 muertos)
| módulo | hoy | después |
|---|---|---|
| `pantalla_filtros` (A) | orden: anclar, **no dicho del gancho** (`gancho_dicho`), candado, no dicho, spoiler, lectura | `gancho_dicho` borrado; la coincidencia del gancho con la voz de todo el video es de `no_dicho` y se le pregunta al autor |
| `m01e_pantalla` (A) | el dato del gancho cae en seco si una cifra suya está en cualquier cap | se le pregunta al autor con cap, número de oración y oración |
| `pantalla_entrada` (A) | el ítem trae `dice_voz` | sin `dice_voz` (solo la marca de gancho) |
| `fase2b` (B) | long-form quema karaoke (Anton 150, 3 palabras, palabra resaltada) | long-form quema subtítulos documentales; karaoke solo para short |
| datos de `f39-kyshtym` (C) | voz con voseo, títulos automáticos, papel de F39 | voz sin voseo, 7 títulos de Omar, papel regenerado (sin código) |

## Constantes
Las de §1, con su origen en la línea (`test_constantes_con_origen` las lista): Anton (`fonts.subs` del perfil); **60 px** de letra a 1080p (`# DECISIONES: Omar, prompt de F40 («Anton 60 px»; voto del analista en F40 §1)`; el subagente lo había anotado con una forma que el test no reconoce y CC lo corrigió); ≤ 42 car. por renglón, ≤ 2 renglones, 0,833–7 s (estándar: Netflix Timed Text Style Guide); blanco con borde negro, sin amarillo, sin resaltar palabra (DECISIONES 03:34); borde 4 y sombra 2 (derivado del `Viral`); `MarginV` 108 (existente); tope US$ 1,50 en `lab/TOPE_TANDA.json`. **Escala:** el video es 2560×1440; los 60/4/2 se escalaron por alto contra 1080 → 80 / 5,33 / 2,67 (derivado: §1 dice «60 px de alto de letra (1080p)»). El `MarginV` 108 queda en píxeles del video, igual que el `Viral` (abierto o2). Ningún número nuevo fuera de §1.

## Cómo se corrió
- Paso 0 en serie. Antes de lanzar B, CC midió el md5 «antes» de ch02 de Orleans con `--no-subs` sobre `8669045` (B.4 c).
- **A y B en paralelo**, un subagente cada una (A: `pantalla_filtros`, `m01e_pantalla`, `pantalla_entrada`; B: `fase2b`); mientras corrían, CC hizo C.1–C.2 (datos, sin código). **C.3 después de A** (el papel se regenera con la regla nueva). Candado en serie al final; revisor al final.
- Commits: **`7ecc26a`** A · **`598c65b`** B · C en el commit del reporte (son datos en `data/`, ignorados por git; las salidas van a `lab/hyperframes/f40/c/`).

## A — El gancho: pregunta, no corte (`7ecc26a`, subagente A)
Archivos: `script_engine/pantalla_filtros.py`, `m01e_pantalla.py`, `pantalla_entrada.py` (CRLF ✓); tests ajustados `test_module_f36c_pantalla.py`, `test_module_f37b_colocar.py`, `test_module_f38e_b.py`; nuevo `test_module_f40_gancho.py`; `lab/hyperframes/f40/a/` (`sim_gancho.py`, `sim_gancho_salida.md`, `A_SALIDA.md`, copias congeladas de Kyshtym y Vajont para los tests).

- **Borrado** (ninguno con otro llamador vivo): `pantalla_filtros.gancho_dicho` y su `regla`, también fuera de `ORDEN` (ahora `[ancla_papel, candado, no_dicho, spoiler, lectura]`); `dice_voz` en `m01e._validar_ficha` (con su clave) y en `pantalla_entrada._item`; el parámetro `voz_txt` de `validar`/`_validar_ficha` y `voz_video` de `_item` (solo los leía `dice_voz`); el import `numero_en` de `pantalla_entrada`. **Quedan:** `no_dicho` (ya sumaba las cifras de todo el video para el gancho), `_donde` (el helper del spoiler), `ev.used_in`/`ev._figures` (los usan `gfx_pool`, `gfx_realizador`, `m05_narrative`, `evidence`).
- **Cómo queda la pregunta:** una cifra del gancho que la voz dice fuera de la oración ancla ± 1 es una pregunta `no_dicho` con `video: True`, escrita con el formato del spoiler. Ejemplo real: «D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo». Lo que el autor mantiene queda en `juicio_autor` y Fase 2 lo respeta.
- **Prompts sin cambio** (md5 antes = después): `PANTALLA_SYSTEM` `7d2ccdd2…` · `FORMATO_SALIDA` `f63ad89a…` · `FORMATO_REINTENTO` `07cd8ad0…` · `REINTENTO_PARCIAL` `29deed05…` · `prompt_md5()` `3b98aef1…`; `PROMPT_VERSION` m01e-6.
- **Tests:** borrados ninguno (no había tests propios de `gancho_dicho` ni `dice_voz`). Ajustados: `test_module_f36c_pantalla.py::test_f_fase2_lee_el_papel_sin_llamar_a_ningun_modelo_de_texto` (el `ORDEN` pierde el primer `no_dicho`, que era `gancho_dicho`); `f36c::test_g_cita_ficha_con_autor_y_sellos_del_papel_nunca_al_mismo_tiempo`, `test_module_f37b_colocar.py::test_b1_q50_corta_se_mueve_a_la_oracion_siguiente_si_no_cabe` y el fixture D47 de `test_module_f38e_b.py` (sale la clave `"dice_voz": False`, que ya nadie lee). Nuevos (9): `test_1_d03_pregunta_con_cap_oracion_y_texto`, `test_1_d03_el_autor_la_mantiene_otro_hecho_queda`, `test_2_mismo_hecho_el_autor_la_saca_sale` (D91 «Más de 5000 personas», la voz lo dice en ch04 [11]), `test_2_sin_preguntar_al_cierre_corta_como_no_dicho`, `test_3_vajont_d195_pasa_sin_pregunta`, `test_4_gancho_dicho_y_dice_voz_borrados`, `test_4_fase2_no_dicho_en_el_gancho_respeta_el_juicio_del_autor`, `test_4_fuera_del_gancho_no_dicho_igual_que_antes`, `test_prompt_no_cambia`. Resultado: 133 passed (los 16 archivos que tocan esos módulos + el nuevo); rápida 58. CC repitió antes del commit: 115 passed (A + papel + rápida).

**Salida en texto (§6.4): la tabla de §3 recalculada por código** (`python lab/hyperframes/f40/a/sim_gancho.py`; «hoy» = HEAD `8669045` vía `git archive` de `script_engine` a una carpeta temporal; «con F40» = el árbol de trabajo; voz = `entrada.caps` del raw de F39; una fila por cada ficha que el autor propuso para el gancho en F39):

| tema | dato del gancho | cifras que encuentra en la voz | hoy | con F40 |
|---|---|---|---|---|
| Kyshtym | D03 «Nivel 6 de 7» (int. 1, [5]) | «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») y «7» en ch04 [14] («A las siete y veinte de la tarde…») | cae no_dicho (gancho) | 4 preguntas → otro hecho → **queda** |
| Kyshtym | D50 «Chernóbil liberó 19 veces más» (int. 2, [5]) | «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.») | cae no_dicho (gancho) | 2 preguntas → otro hecho → **queda** |
| Kyshtym | D03 «6 en una escala de 7» (int. 3, [8]) | 6 y 7, igual que arriba | cae no_dicho (gancho) | cae por `caben` (47 > 31) |
| Kyshtym | D201 «Valia Dronova, 38 años: pulmones de piedra» (int. 4, [4]) | hoy: «20» en ch01 [7] (sale del texto del ítem, «planta 20»); F40: ninguna | cae no_dicho (gancho) | pasa |
| Kyshtym | D03 «NIVEL 6 DE 7 · Escala internacional de accidentes» (int. 5, [1]) | hoy: 6 y 7; F40: ninguna (la cifra está en la etiqueta) | cae no_dicho (gancho) | pasa |
| Vajont v6 | D195 «1.269 de 1.328» (ch01 [2]) | ninguna | pasa | pasa (sin cambio) |

Dos filas difieren de la simulación del analista: D201 «pasa» (la ficha no lleva el 20; el «20» de «planta 20» está en el texto del ítem, y la voz no dice 38) y D03 int. 3 cae igual, pero por `caben`.

## B — Subtítulos documentales (`598c65b`, subagente B)
Archivos: `fase2b.py` (CRLF ✓, +274/−43), `test_constantes_con_origen.py`, `test_module_f30b.py`; nuevo `test_module_f40_subs.py`; `lab/hyperframes/f40/b/` (`gen_ch02_vajont.py`, `ch02_vajont.ass`, `ch02_tabla.md`, `B_SALIDA.md`, las 3 fotos, logs).

- **Constantes** en una clase `SubsDocumentales` (instancia `subs_doc`), cada una con su origen: `alto_ref` 1080, `letra_px` 60, `borde_px` 4, `sombra_px` 2, `margin_v` 108, 42 car. por renglón, 2 renglones, 0,833 s y 7,0 s. Fuente: `fonts.subs` del perfil (`_fuente_subs`; sin ella, `ValueError`).
- **`_build_ass_documental`:** un evento por oración (fin de oración `. ? !`; los puntos suspensivos cuentan como pausa). Si no entra en 2 renglones de 42 o pasa de 7 s, se parte en la pausa más cercana al medio; si no hay pausa, en la palabra más cercana al medio; el renglón se corta con la misma regla. Un evento de menos de 0,833 s se estira dentro del silencio que le sigue; si no alcanza, se junta con el vecino cuando el resultado entra. Tiempos en centésimas (la unidad del .ass). Texto como lo dice la voz, sin `\k`, sin color ni escala por palabra, sin «, » ni …, sin mayúsculas forzadas.
- **Quién elige:** `ChapterPlan.video_type` sale de `_load_script_lookup` (default `"short"`): con `long`, documental; con cualquier otro valor, el karaoke de hoy (`_build_ass_from_words`, sin cambios). El log dice `subs: ON (documental|karaoke)`.
- **Hook:** no se tocó lo que hace; su código se movió a `_ass_header`/`_ass_hook_event`, con salida byte-idéntica (4 casos comparados por md5: plano, con hook, sin comillas, solo hook). En long-form corre solo con `--hook "<texto>"` en modo single, solo en ch01, con el texto del CLI en mayúsculas; en batch, `hook=None`. Los `ch01_subs.ass` de Vajont y Orleans tienen el estilo `Hook` pero ningún `Dialogue` de Hook: en esos renders no corrió.
- **Estilo como queda en el .ass (2560×1440):**
```
Style: Documental,Anton,80,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5.33333,2.66667,2,40,40,108,1
Style: Hook,Anton,128,&H0000FFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,8,5,5,40,40,0,1
```
- **Tests:** nuevo `test_module_f40_subs.py` (17: estilo, escalado, renglones, duraciones con estiramiento, unión y máximo, corte en la pausa, tiempos, pre-pad, sin comillas ni mayúsculas, Hook idéntico, documental con `long` y karaoke con `short`, `video_type` en el lookup). Ajustados: `test_module_f30b.py::test_pre_roll_corre_los_subtitulos_y_la_chascada_saca_las_comillas` (miraba el karaoke con pre-roll en long-form; ahora prueba lo mismo sobre el documental), `test_constantes_con_origen.py::test_inventario_de_constantes` (suma la clase `SubsDocumentales`). 101 passed en los de subtítulos; rápida 58. CC repitió antes del commit: 95 passed.

### B.4 (a) — Eventos del .ass de Vajont ch02 (con el pre-roll de 3 s del title card; 35 eventos, ningún ✗)
| # | inicio | fin | dur (s) | texto (renglones separados por /) | caracteres por renglón | §1 |
|---|---|---|---|---|---|---|
| 1 | 0:00:03.08 | 0:00:05.58 | 2.50 | Longarone está en el fondo / del valle del Piave. | 26 + 20 | ✓ |
| 2 | 0:00:06.30 | 0:00:11.02 | 4.72 | El río pasa por delante del pueblo y, / enfrente, desde una garganta lateral, | 37 + 37 | ✓ |
| 3 | 0:00:11.58 | 0:00:14.92 | 3.34 | baja un torrente que se / llama Vajont y que desemboca | 23 + 28 | ✓ |
| 4 | 0:00:14.94 | 0:00:18.10 | 3.16 | en el Piave justo frente a / Longarone y Castellavazzo. | 26 + 26 | ✓ |
| 5 | 0:00:19.20 | 0:00:21.66 | 2.46 | En mil novecientos cuarenta / y tres se aprobó el | 27 + 19 | ✓ |
| 6 | 0:00:21.68 | 0:00:24.10 | 2.42 | proyecto de cerrar esa / garganta con una presa, | 22 + 23 | ✓ |
| 7 | 0:00:24.64 | 0:00:27.36 | 2.72 | y empezó la compra de / terrenos en Erto y Casso, | 21 + 25 | ✓ |
| 8 | 0:00:27.84 | 0:00:31.12 | 3.28 | los pueblos de arriba, / los que iban a quedar al borde del lago. | 22 + 40 | ✓ |
| 9 | 0:00:31.96 | 0:00:33.50 | 1.54 | La empresa era SADE. | 20 | ✓ |
| 10 | 0:00:34.46 | 0:00:37.66 | 3.20 | El ingeniero que dibujó la / obra se llamaba Carlo Semenza, | 26 + 30 | ✓ |
| 11 | 0:00:38.22 | 0:00:41.02 | 2.80 | y la pensó como un arco / delgado de doble curvatura: | 23 + 27 | ✓ |
| 12 | 0:00:41.70 | 0:00:46.72 | 5.02 | una pared curva, fina para su tamaño, / apoyada en las dos laderas de la garganta. | 37 + 42 | ✓ |
| 13 | 0:00:47.76 | 0:00:49.00 | 1.24 | Cuando empezaron las obras, | 27 | ✓ |
| 14 | 0:00:49.40 | 0:00:52.28 | 2.88 | unos cuatrocientos hombres / colgados de andamios la | 26 + 23 | ✓ |
| 15 | 0:00:52.36 | 0:00:55.16 | 2.80 | fueron levantando hasta tapar / el cielo de la garganta. | 29 + 24 | ✓ |
| 16 | 0:00:56.14 | 0:01:00.06 | 3.92 | Abajo, en Longarone, / la vida siguió con el Piave delante. | 20 + 36 | ✓ |
| 17 | 0:01:01.08 | 0:01:03.00 | 1.92 | Longarone no estaba sobre el embalse. | 37 | ✓ |
| 18 | 0:01:03.58 | 0:01:04.76 | 1.18 | Estaba delante de él. | 21 | ✓ |
| 19 | 0:01:05.58 | 0:01:08.16 | 2.58 | Y la montaña que cerraba / el lago tenía un apodo. | 24 + 23 | ✓ |
| 20 | 0:01:08.94 | 0:01:12.84 | 3.90 | La gente de la zona llamaba al / monte Toc la montaña que camina, | 30 + 32 | ✓ |
| 21 | 0:01:13.40 | 0:01:17.00 | 3.60 | y lo decían los residentes desde / antes de que nadie fuera a medirla. | 32 + 35 | ✓ |
| 22 | 0:01:19.50 | 0:01:20.82 | 1.32 | En la década del cincuenta, | 27 | ✓ |
| 23 | 0:01:21.26 | 0:01:25.60 | 4.34 | el geólogo Leopold Müller detectó / en el Toc un gran desmoronamiento. | 33 + 34 | ✓ |
| 24 | 0:01:26.52 | 0:01:28.84 | 2.32 | Y hubo otro hombre que / caminó esa ladera con un | 22 + 24 | ✓ |
| 25 | 0:01:28.88 | 0:01:31.58 | 2.70 | martillo en la mano y / otra idea en la cabeza: | 21 + 23 | ✓ |
| 26 | 0:01:32.42 | 0:01:38.20 | 5.78 | Edoardo Semenza, geólogo, hijo de Carlo / Semenza, el que había dibujado la presa. | 39 + 40 | ✓ |
| 27 | 0:01:39.26 | 0:01:42.34 | 3.08 | Edoardo buscaba la cicatriz / de un deslizamiento antiguo. | 27 + 28 | ✓ |
| 28 | 0:01:43.22 | 0:01:45.62 | 2.40 | Según una reconstrucción / geológica posterior, | 24 + 20 | ✓ |
| 29 | 0:01:46.12 | 0:01:50.62 | 4.50 | planteó que ese deslizamiento viejo podía / reactivarse cuando el embalse se llenara. | 41 + 41 | ✓ |
| 30 | 0:01:51.60 | 0:01:52.72 | 1.12 | Müller no lo creía: | 19 | ✓ |
| 31 | 0:01:53.48 | 0:01:58.10 | 4.62 | no creía en el deslizamiento antiguo ni / en una capa de arcilla capaz de causarlo. | 39 + 41 | ✓ |
| 32 | 0:01:59.04 | 0:02:02.90 | 3.86 | El hijo del proyectista decía que la / montaña ya se había movido una vez. | 36 + 35 | ✓ |
| 33 | 0:02:03.64 | 0:02:04.98 | 1.34 | El experto decía que no. | 24 | ✓ |
| 34 | 0:02:05.98 | 0:02:08.28 | 2.30 | En marzo de mil novecientos / cincuenta y nueve, | 27 + 18 | ✓ |
| 35 | 0:02:08.70 | 0:02:12.66 | 3.96 | en otro embalse de la misma empresa, / una montaña caminó primero. | 36 + 27 | ✓ |

### B.4 (b) — Render y las 3 fotos
**El render pedido no corrió:** `python fase2b.py f8s3-vajont-f30 --only-cap ch02 --gfx --reuse-visuals` lo frenó el hook, una vez, y no se esquivó (ni `--aprobar-guion`, que es de Omar, ni `--gfx-debug`, que mete un overlay de depuración y cambia la calidad):
```
guard_render: sin guion aprobado no hay render — el guion de f8s3-vajont-f30 no está aprobado (Omar lo aprueba; CC corre `fase2b f8s3-vajont-f30 --aprobar-guion "Omar <fecha>"` solo si su prompt dice «aprobado»)
```
(El guion de Vajont quedó sin aprobar desde el `--plan-only` de F38e B.5.) Las fotos se hicieron lo más fiel posible sin el render gfx (2560×1440, en `lab/hyperframes/f40/b/`):
1. **`foto1_dos_renglones_t41.0.png`**: segundo 41,0 del segmento ch02 de Vajont **sin gfx** con los subtítulos nuevos (`python fase2b.py f8s3-vajont-f30 --only-cap ch02 --reuse-visuals --sw-encode`, rc 0, que el hook deja pasar). Muestra «una pared curva, fina para su tamaño, / apoyada en las dos laderas de la garganta.» (37 + 42, el renglón más largo posible).
2. **`foto2_ficha_y_subtitulo_t90.0.png`** — **sustituto**: segundo 90,0 de la capa gfx ya renderizada `ch02_gfx.mp4` (la de F38e A.4) con el `.ass` nuevo de ch02 quemado encima con el filtro `ass` de ffmpeg (`-copyts`, `fontsdir=script_engine/fonts`), como fase2b quema los subs sobre el clip. Muestra la ficha D47 «FRENTE DEL DESMORONAMIENTO · 2 KM DE FRENTE Y 600 M DE DESARROLLO VERTICAL» a media altura a la izquierda y el subtítulo «martillo en la mano y / otra idea en la cabeza:» abajo al centro: **no se pisan**, queda espacio libre entre los dos. En ese mp4 la ficha está en ≈86,6–91,3 s (el plan de hoy la mueve a 79,6 s: la capa es anterior al `--plan-only` de F38e).
3. **`foto3_solo_subtitulo_t29.7.png`**: mismo segmento sin gfx, segundo 29,7: «La empresa era SADE.» (un renglón).

CC miró las tres: subtítulo blanco con borde negro, sin amarillo ni palabra resaltada, centrado abajo; en la foto 2 la ficha y el subtítulo no se tocan.

Escrituras en `output/`: el `ch02_segment_only.mp4` y el `ch02_subs.ass` de Vajont quedaron pisados por el render sin gfx de las fotos 1 y 3 (respaldo antes en `output/f8s3-vajont-f30/_fase2b_work/_bak_f40/`; el mp4 viejo tenía md5 `ece8f772…`); `ch02_gfx.mp4` no cambió (`2a301589…`). Los de Orleans los pisan las corridas del candado, como siempre.

### B.4 (c) — Candado (Orleans ch02, `--only-cap ch02 --reuse-visuals --sw-encode`, en serie)
| corrida | md5 |
|---|---|
| antes (`8669045`), `--no-subs` (CC) | `98386f8608e86f8099bbfb2d61cf2950` |
| después, `--no-subs` (B) | `98386f8608e86f8099bbfb2d61cf2950` ✓ igual |
| después, con subtítulos | `f792f3d483a1fa42daed5f7f0e054f46` (antes `38e5ba14…`; el cambio es esperado: es el **candado nuevo**, anotado en ESTADO) |
El log de la corrida con subtítulos dice `subs: ON (documental)`.

**Desvío del subagente B (declarado):** antes del render sin gfx **cerró Firefox** (cierre normal, `taskkill` sin `/f`; RAM quedó en 14,5 GB), siguiendo una memoria vieja de CC («Firefox cerrado en todo render») que DECISIONES 2026-10-27 00:30 reemplazó: **CC nunca cierra programas de Omar**, y en `--only-cap` no se mide ni se cierra nada. CC no se lo había prohibido en el brief. La memoria quedó corregida en esta tanda para que no se repita (abierto o1).

## C — Kyshtym (`f39-kyshtym`), después de A
**C.1 Voz sin voseo y C.2 títulos** (CC, sin modelo; `lab/hyperframes/f40/c/c1_c2_voseo_titulos.py`, salida en `C1_C2_salida.txt`), con respaldo `_pre_f40` de cada archivo:
- `01b_narracion_v3.json`: cenás→cenas ×6 · acá→aquí ×3 (md5 `e52926dc…` → `58a232f0…`);
- `01b_narration.json` (`narration` y `narration_tts`): cenás→cenas ×4 · acá→aquí ×2 (`e81d9ac0…` → `1d2fc553…`);
- `01b_guionista_v4.json`: cenás→cenas ×4 · acá→aquí ×2 (`27b10f7d…` → `a9c66678…`);
- `01a_skeleton.json`: los 7 títulos de DECISIONES 18:30, uno por cap (`7c0d64bc…` → `a99ab0b4…`): La luz que no era fuego · La ciudad sin mapa · El tanque catorce · Un domingo de fútbol · La aurora de Cheliábinsk · Los pueblos enterrados · Lo que calló el acta.
- `grep` final en esos cuatro: 0 «cenás», 0 «acá», 0 títulos viejos. Quedan «cenás» solo en `01a_escaleta.json` (la cita de Valevich que la escaleta deja para el cierre, «La víspera cenás con él…»: la escaleta no lleva la narración; no se tocó) y en los `01e_pantalla_f39.*` (el respaldo del papel viejo). El pool y la ficha conservan el texto de la fuente.

**C.3 Papel regenerado** con la regla de A: la misma llamada que hace `fase1_5.run_pantalla` (`f._topic_v3` + `f.run_pantalla("f39-kyshtym", pool, log)`, que llama a `m01e_pantalla.generar` con su costo como paso «pantalla»); sin script nuevo; tope existente US$ 1,00 (respaldo: el perfil no trae `costos.m01e_tope_usd`). Respaldo previo: `01e_pantalla_f39.json/.md/.raw.json` (md5 `17b8237f…` / `763346a6…` / `0ba0d35e…`). Tope de la tanda `lab/TOPE_TANDA.json` = `{"usd": 1.50, "desde": "2026-10-27T18:58:46"}`. Corrida 18:58:46 → 19:01:36 (`lab/hyperframes/f40/c/pantalla.log`):
```
  m01e intento 1: in 48051 · out 21432 · US$ 0.3104 · JSON
  m01e intento 1 validado: fichas fuera 1 · preguntas 7 · vuelven 1 · picos vacíos 0
  m01e intento 2: in 53518 · out 2306 · US$ 0.1301 · JSON
  m01e vuelta 1 validada: fichas fuera 0 · preguntas nuevas 0 · picos vacíos 0
  m01e: 1 motivo(s) sin beat → sin otra vuelta (anotados)
  m01e: 12 fichas · 7 sellos · 6 relojes → …\data\scripts\_steps\f39-kyshtym\01e_pantalla.md
```
**US$ 0,4405** (2 llamadas). 1 vuelta; cierre **«sin beat»** (el único motivo que quedaba no tenía beat que cambiar); cortados al cierre: nada. **El gancho tiene ficha:** D03 «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7» en [5]; las 4 preguntas del gancho (6 y 7, con cap, oración y texto; dos como `no_dicho` del video y dos como spoiler, abierto o3) y la respuesta del autor: **«la mantuvo en ch01 beat 1 [5]: otro hecho»** (`juicio_autor {no_dicho: [6, 7], spoiler: [6, 7]}`). Picos vacíos: ninguno (F39: el gancho). `a_pantalla` vacíos: ninguno (F39: D03).

**C.4 Dos correcciones, solo si se repiten:**
- **ch04 beat 5 con D09 → no se repite.** En el papel nuevo, ch04 beat 5 tiene **D47** «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT» (otro dato, otra estimación), no D09. No se tocó (el handoff: «si no se repiten, no se toca nada y se dice»). Queda para que Omar lo mire en la compuerta (abierto o4).
- **«2000» → «2.000»: se repite** en D83 (ch07 beat 11, «Más de 2000 obreros…»). Se corrigió con **`m01e_pantalla.editar`** (la función de `--plan-edit`): `fase2b --plan-edit` no se pudo usar tal cual porque necesita `data/scripts/f39-kyshtym.json` (el script de Fase 2, que Kyshtym no tiene) e implica `--plan-only`, que necesita voz e imágenes. `editar` no rechazó nada: D83 queda «ENFERMOS ENTRE 1948 Y 1958 · Más de 2.000 obreros con enfermedad por radiación» (`editado: true`, 75 caracteres; el `respaldo` sigue literal del archivo, «más de 2000 trabajadores…»); copia `01e_pantalla.antes_de_edicion.json`; ninguna otra ficha con «2000». Papel final md5 `.md` `0ba9c0ad…` (`lab/hyperframes/f40/c/C4_edicion.txt`).

**Diferencias contra el papel de F39, ficha por ficha** (`lab/hyperframes/f40/c/diff_f39_f40.md`):

| cap · beat | ficha F39 | ficha F40 | sello F39 → F40 | |
|---|---|---|---|---|
| ch01 · 1 | — | D03 «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7» [5] | MEMORIA → MEMORIA | cambia |
| ch02 · 2 | D194 «LAS DOS PRIMERAS PROMOCIONES · Murieron casi por completo» [9] | D194 «LAS DOS PRIMERAS PROMOCIONES · Murieron casi todos» [6] | AMENAZA → CALMA | misma ficha, otro texto |
| ch02 · 3 | D31 «EL CÉSPED ERA CAMUFLAJE · Tierra de 2 metros de espesor» [15] | D31 «EL CÉSPED ERA CAMUFLAJE · Encima, 2 metros de tierra» [15] | CALMA → AMENAZA | misma ficha, otro texto |
| ch03 · 4 | T14 «TANQUES DE ALMACENAMIENTO · Construidos en 1950» [0] | T21 «ESE MISMO AÑO · Se decide dejar de verter residuos en el río Techa» [2] | INMINENTE → INMINENTE | cambia |
| ch04 · 5 | D09 «ESTIMACIONES MODERNAS · Entre 8 y 170 toneladas de TNT» [9] | D47 «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT» [9] | COLAPSO → COLAPSO | cambia |
| ch04 · 6 | D17 «LA ZONA CONTAMINADA · 270.000 habitantes, 217 localidades» [19] | D17 «GENTE EN LA ZONA CONTAMINADA · 270.000 habitantes en 217 localidades» [19] | — → — | misma ficha, otro texto |
| ch05 · 7 | D93 «HABITANTES DE LA CIUDAD · 86.000 personas siguieron ahí» [9] | D93 «VECINOS SIN EVACUAR · 86.000 habitantes» [9] | SILENCIO → RABIA | misma ficha, otro texto |
| ch05 · 8 | D138 «LAS CALLES MÁS CONTAMINADAS · Lenin y Shkolnaya» [16] | P04 «SLAVSKY, MINISTRO · De Construcción de Maquinaria Mediana» [19] | ALARMA → — | cambia |
| ch06 · 9 | D163 «LA GRANJA QUE NO TUMBARON · 50 casas, laboratorio médico» [3] | D20 «TOTAL DE REUBICADOS · 12.763 personas» [6] | RABIA → SILENCIO | cambia |
| ch06 · 10 | D90 «LOS QUE LIMPIARON · Unos 30.000 trabajadores y militares, 1957-1959» [16] | D90 «DOSIS ENTRE 1957 Y 1959 · Unos 30.000 trabajadores y militares con más de 0,25 Sv» [18] | — → — | misma ficha, otro texto |
| ch07 · 11 | D83 «ENFERMOS POR RADIACIÓN · Más de 2000 trabajadores, 1948-1958» [7] | D83 «ENFERMOS ENTRE 1948 Y 1958 · Más de 2.000 obreros con enfermedad por radiación» [7] | — → — | misma ficha, otro texto |
| ch07 · 12 | D149 «LA LEY CAMBIABA · Casi cada año, durante 10 años» [12] | D201 «OTRA MUERTE · Valia, 38 años: pulmones de piedra» [19] | — → — | cambia |

Relojes: 6 y 6, iguales. Fichas 11 → 12; sellos 8 → 7. (La tabla se calculó después de la edición «2.000».)

**C.5 — `01e_pantalla.md` nuevo, ENTERO** (`data/scripts/_steps/f39-kyshtym/01e_pantalla.md`, después de la edición; copia en `lab/hyperframes/f40/c/01e_pantalla.md`):

````markdown
# Guion de pantalla en papel — f39-kyshtym

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 2 intento(s) · US$ 0.4405 · tokens de entrada 48051

Segundos por palabra 0.3459 (mediana de 200 oraciones de 9 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 48051 · out 21432 · US$ 0.3104 · intento 2: in 53518 · out 2306 · US$ 0.1301

Totales: 12 fichas · 7 sellos · 6 relojes · 15 descartados

## ch01 — La luz que no era fuego

- beat 1 · gancho · PICO · ficha **D03** [normal] «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7» en [5] sobre «columna» (41/90 car.) · respaldo: «nivel 6 de 7 en la escala internacional de eventos radiológicos del OIEA» · año — / relato — · juzgado por el autor: otro hecho {'no_dicho': ['6', '7'], 'spoiler': ['6', '7']} · aporta: La voz nunca dice qué tan grave fue el accidente; la pantalla lo pone en una escala. · sello **MEMORIA** en [3]
- relojes: —

## ch02 — La ciudad sin mapa

- beat 2 · planteo · ficha **D194** [normal] «LAS DOS PRIMERAS PROMOCIONES · Murieron casi todos» en [6] sobre «moscas» (47/90 car.) · respaldo: «Las dos primeras promociones de trabajadores de la planta murieron casi por completo.» · año — / relato 1957 · aporta: Confirma con un hecho el rumor de que los obreros morían como moscas; la voz no lo cuenta. · sello **CALMA** en [0]
- beat 3 · planteo · PICO · ficha **D31** [normal] «EL CÉSPED ERA CAMUFLAJE · Encima, 2 metros de tierra» en [15] sobre «césped» (49/90 car.) · respaldo: «capa de tierra de 2 metros de espesor y césped para camuflaje» · año — / relato 1957 · juzgado por el autor: otro hecho {'spoiler': ['2']} · aporta: La voz dice que había tierra y césped; la pantalla da el espesor y para qué estaban. · sello **AMENAZA** en [22]
- relojes: —

## ch03 — El tanque catorce

- beat 4 · escalada · PICO · ficha **T21** [normal] «ESE MISMO AÑO · Se decide dejar de verter residuos en el río Techa» en [2] sobre «esperar» (63/67 car.) · respaldo: «Se toma la decisión de detener el vertido de residuos radiactivos en masas de agua abiertas como el río Techa y el lago Karachai. (fecha 1956)» · año 1956 / relato 1956 · aporta: Muestra que en 1956 ya no se podían tirar los residuos al río, un hecho que la voz no cuenta. · sello **INMINENTE** en [11]
- relojes: 9 MAR 1957 en [6], 10 ABR 1957 en [6]

## ch04 — Un domingo de fútbol

- beat 5 · pico · PICO · ficha **D47** [normal] «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT» en [9] sobre «mucho» (51/90 car.) · respaldo: «Una estimación posterior calculó la potencia de la explosión entre 70 y 100 toneladas de trinitrotolueno.» · año — / relato 1957 · juzgado por el autor: otro hecho {'no_dicho': ['TNT'], 'spoiler': ['100']} · aporta: La voz dice solo «mucho más»; la pantalla pone la cifra de esa otra estimación. · sello **COLAPSO** en [8]
- beat 6 · respiro · ficha **D17** [normal] «GENTE EN LA ZONA CONTAMINADA · 270.000 habitantes en 217 localidades» en [19] sobre «franja» (65/90 car.) · respaldo: «270.000 habitantes en 217 localidades» · año — / relato 1957 · aporta: La voz dice el largo de la franja; la pantalla dice a cuánta gente alcanzó. · sello —
- relojes: 29 SEP 1957 en [0]

## ch05 — La aurora de Cheliábinsk

- beat 7 · giro · PICO · ficha **D93** [normal] «VECINOS SIN EVACUAR · 86.000 habitantes» en [9] sobre «opción» (36/90 car.) · respaldo: «La ciudad de Ozerk, con 86.000 habitantes, no fue evacuada» · año — / relato 1957 · aporta: La voz dice que la ciudad no se evacuó; la pantalla dice cuánta gente se quedó. · sello **RABIA** en [5]
- beat 8 · escalada · ficha **P04** [nombre] «SLAVSKY, MINISTRO · De Construcción de Maquinaria Mediana» en [19] sobre «Slavsky» (54/67 car.) · respaldo: «E. P. Slavsky — Ministro de Construcción de Maquinaria Mediana» · año — / relato 1957 · aporta: La voz solo nombra a Slavsky; la pantalla dice que era un ministro y de qué ministerio. · sello —
- relojes: 6 OCT 1957 en [12]

## ch06 — Los pueblos enterrados

- beat 9 · consecuencia · ficha **D20** [normal] «TOTAL DE REUBICADOS · 12.763 personas» en [6] sobre «localidades» (34/90 car.) · respaldo: «12.763 personas de 23 asentamientos fueron reubicadas por etapas» · año — / relato 1960 · aporta: La voz cuenta las localidades vaciadas; la pantalla dice cuántas personas fueron. · sello **SILENCIO** en [7]
- beat 10 · revelacion · PICO · ficha **D90** [papel] «DOSIS ENTRE 1957 Y 1959 · Unos 30.000 trabajadores y militares con más de 0,25 Sv» en [18] sobre «liquidación» (78/90 car.) · respaldo: «Entre 1957 y 1959, unos 30.000 trabajadores del combinado y militares recibieron dosis de radiación superiores a 0,25 Sv» · año — / relato 1960 · aporta: La voz cuenta el caso de un jefe; la pantalla dice a cuánta gente alcanzó la dosis durante la liquidación. · sello —
- relojes: —

## ch07 — Lo que calló el acta

- beat 11 · revelacion · PICO · ficha **D83** [normal] «ENFERMOS ENTRE 1948 Y 1958 · Más de 2.000 obreros con enfermedad por radiación» en [7] sobre «radiación» (75/90 car.) · respaldo: «Entre 1948 y 1958, más de 2000 trabajadores fueron diagnosticados con enfermedad profesional por radiación.» · aporta: Contrasta en silencio con la declaración de Buldakov con una cifra de diagnósticos que la voz no menciona. · sello —
- beat 12 · cierre · ficha **D201** [normal] «OTRA MUERTE · Valia, 38 años: pulmones de piedra» en [19] sobre «radiación» (45/51 car.) · respaldo: «Valia Dronova, que trabajaba con plutonio metálico, murió a los 38 años porque sus pulmones se habían convertido en piedra» · año — / relato 1998 · aporta: Un caso concreto de una obrera muerta joven, que la voz no cuenta, frente a lo que dice el acta. · sello —
- relojes: 13 ABR 1958 en [0], 16 JUN 1989 en [4]

## Lo que cayó

- (nada)

## Reintento: los motivos que se le mandaron al autor

- P04 (ch05 beat 8) «QUIÉN ERA SLAVSKY · Ministro de Construcción de Maquinaria Mediana»: candado: no están en el texto fuente de P04: ['QUIÉN']
- D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «6» en una oración posterior en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «7» en una oración posterior en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- D31 (ch02 beat 3, oración [15]) «EL CÉSPED ERA CAMUFLAJE · Encima, 2 metros de tierra»: la voz dice «2» en una oración posterior en ch04 [2] («Dos equipos de la ciudad en la cancha, y en las gradas muchachos de la edad de Valevich y de los del comedor.»); ¿es el mismo hecho? si no, mantenelo
- D47 (ch04 beat 5, oración [9]) «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT»: la voz dice «TNT» en la oración ancla o en una vecina en ch04 [9] («La fuerza se calculó después en veinticinco a veintinueve toneladas de TNT; otras fuentes hablan de mucho más.»); ¿es el mismo hecho? si no, mantenelo
- D47 (ch04 beat 5, oración [9]) «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT»: la voz dice «100» en una oración posterior en ch04 [12] («Noventa de cada cien partes cayeron ahí mismo, sobre el combinado.»); ¿es el mismo hecho? si no, mantenelo
- D152: dijiste que la voz lo dice («La voz cuenta los dos juicios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
- el beat 10 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D20 («El total de reasentados no está unificado (12.763 / 10.000-12.000 / unas 10.000); la voz no puede decir tres números, la pantalla sí puede mostrar las tres fuentes.»), D90 («Unos 30.000 trabajadores y militares con más de 0,25 Sv entre 1957 y 1959: cifra de informe, va como texto en pantalla bajo las versiones en disputa.»)

### Preguntas y respuesta del autor

- D03 {'no_dicho': ['6', '7'], 'spoiler': ['6', '7']}: la mantuvo en ch01 beat 1 [5]: otro hecho
- D31 {'spoiler': ['2']}: la mantuvo en ch02 beat 3 [15]: otro hecho
- D47 {'no_dicho': ['TNT'], 'spoiler': ['100']}: la mantuvo en ch04 beat 5 [9]: otro hecho

### Reintento parcial: 1 vuelta(s)

#### Vuelta 1 · US$ 0.1301

- beats que podía cambiar: ch01 beat 1, ch02 beat 3, ch04 beat 5, ch05 beat 8, ch06 beat 10
- motivos:
  - P04 (ch05 beat 8) «QUIÉN ERA SLAVSKY · Ministro de Construcción de Maquinaria Mediana»: candado: no están en el texto fuente de P04: ['QUIÉN']
  - D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
  - D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
  - D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «6» en una oración posterior en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
  - D03 (ch01 beat 1, oración [5]) «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7»: la voz dice «7» en una oración posterior en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
  - D31 (ch02 beat 3, oración [15]) «EL CÉSPED ERA CAMUFLAJE · Encima, 2 metros de tierra»: la voz dice «2» en una oración posterior en ch04 [2] («Dos equipos de la ciudad en la cancha, y en las gradas muchachos de la edad de Valevich y de los del comedor.»); ¿es el mismo hecho? si no, mantenelo
  - D47 (ch04 beat 5, oración [9]) «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT»: la voz dice «TNT» en la oración ancla o en una vecina en ch04 [9] («La fuerza se calculó después en veinticinco a veintinueve toneladas de TNT; otras fuentes hablan de mucho más.»); ¿es el mismo hecho? si no, mantenelo
  - D47 (ch04 beat 5, oración [9]) «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT»: la voz dice «100» en una oración posterior en ch04 [12] («Noventa de cada cien partes cayeron ahí mismo, sobre el combinado.»); ¿es el mismo hecho? si no, mantenelo
  - D152: dijiste que la voz lo dice («La voz cuenta los dos juicios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
  - el beat 10 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D20 («El total de reasentados no está unificado (12.763 / 10.000-12.000 / unas 10.000); la voz no puede decir tres números, la pantalla sí puede mostrar las tres fuentes.»), D90 («Unos 30.000 trabajadores y militares con más de 0,25 Sv entre 1957 y 1959: cifra de informe, va como texto en pantalla bajo las versiones en disputa.»)
- aplicados: ch05 beat 8 (ficha/sello), ch06 beat 10 (ficha/sello)

### Motivos sin beat (no hubo reintento)

- D152: dijiste que la voz lo dice («La voz cuenta los dos juicios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato

## Cierre del reintento

- cerró por: **sin beat** (después de 1 vuelta)
- cortado al cerrar, sin preguntarle al autor: (nada)

## Descartados por el modelo

- Q18 [voz_lo_dice]: La voz cita a Valevich textualmente en la oración 6; sería repetir.
- D153 [voz_lo_dice]: La voz ya dice los cincuenta estudiantes y que Valevich era uno; usé D194, que suma más.
- Q01 [voz_lo_dice]: La voz dice la frase completa en la oración 20.
- T20 [voz_lo_dice]: La voz cuenta las tuberías con fugas desconectadas en 1956.
- T28 [voz_lo_dice]: La voz dice la explosión y la hora (cuatro y veintidós).
- T35 [voz_lo_dice]: La voz cuenta los vidrios rotos y la orden de limpiar sin avisar el nivel.
- Q02 [voz_lo_dice]: La voz cita la nota de la aurora casi literal.
- T43 [voz_lo_dice]: La voz cuenta las casas tumbadas y enterradas en 1958-59.
- Q03 [voz_lo_dice]: La voz parafrasea la declaración de Buldakov.
- D152 [voz_lo_dice]: La voz cuenta los dos juicios de Valevich. — **falso: la voz no dice ['2']**
- D54 [otro]: Para el gancho elegí D03; un beat admite una sola ficha.
- D50 [otro]: La comparación con Chernóbil choca con otras cifras del archivo (D113) y confunde.
- D163 [otro]: No se sabe si ese sovkhoz fue una de las aldeas evacuadas, y contradice lo que cuenta ch06.
- D199 [otro]: No cabe en la oración ancla y podría confundirse con el amigo sin nombre del gancho.
- D90 [otro]: Cifra de informe; D164 se entiende mejor y cabe en la oración.
````

## US$ de la tanda (tope US$ 1,50)
| parte | llamadas | US$ |
|---|---|---|
| A (código y tests) | 0 | 0 |
| B (código, tests, fotos, candados) | 0 | 0 |
| C.3 papel (Sonnet, intento 1 + 1 vuelta) | 2 | 0,4405 |
| **total** | | **0,4405** |

## Frenos
- Nada de voz, imágenes ni render de Kyshtym; **no se corrió `--aprobar-papel`** (el papel de Kyshtym queda sin aprobar: lo aprueba Omar).
- Cero cambios de prompt (md5 en A; `PEDIDO_TITULOS` y la escaleta no se tocaron; los títulos de C son datos).
- Nada fuera de A, B y C: lo de la lista de DECISIONES 18:30 no se tocó (bloqueantes falsos de citas, detector de voseo, títulos automáticos, ficha de relleno en picos, formato de cifras).
- Ningún número nuevo fuera de §1.
- Escrituras en `data/`: `_steps/f39-kyshtym/` (C: los 4 archivos de C.1–C.2 con `_pre_f40`, el papel con `01e_pantalla_f39.*` y `01e_pantalla.antes_de_edicion.json`, `01_v3_costos.json` con el paso «pantalla») y `data/cost_history.json` (ledger de `run_pantalla` y de los `fase2b` de Orleans/Vajont).
- `output/`: los `ch02_segment_only.mp4`/`ch02_subs.ass` de Vajont (respaldo en `_bak_f40/`) y de Orleans (candado).
- **Desvío:** el subagente B cerró Firefox (ver B.4 c). Va contra DECISIONES 00:30.

## Suites y candado (al final de A, B y C; `lab/hyperframes/f40/verificar.sh final`, sobre el árbol con A y B commiteados)
- md5 de ch02 de Orleans **con** subtítulos: `f792f3d483a1fa42daed5f7f0e054f46` (= el de B: reproducible; es el candado nuevo, antes `38e5ba14…`). Sin subtítulos (`--no-subs`): `98386f86…` antes y después (B.4 c).
- Suite rápida: **58 passed**.
- Suite amplia (`-n auto`): **939 passed, 5 failed** = exactamente las 5 previas (`01b_pauses` ×3, `m03_merge_timing` ×2). Cuenta: 913 (F39) + 9 (A) + 17 (B) = 939 ✓.

## Push de la rama
`git push origin f11-guion-v4` después del commit del reporte (`main` no se tocó):
```
To https://github.com/gueva1441/automatization_videos.git
   a67ed45..5b0fa5f  f11-guion-v4 -> f11-guion-v4
```
Sube los commits de F39 (A y reporte) y de F40 (paso 0, A, B y reporte). Este commit, que solo agrega esta salida, se subió con un segundo push.

## Lo que queda abierto (entero)
- o1. **El subagente B cerró Firefox** antes de un `--only-cap` sin gfx, siguiendo una memoria vieja de CC que DECISIONES 00:30 había reemplazado («CC nunca cierra programas de Omar»). La memoria quedó corregida; en los briefs de renders hay que escribir «no cierres ningún programa de Omar».
- o2. **Tamaño de los subtítulos:** §1 dice «60 px (1080p)»; a 2560×1440 se escaló por alto a 80 px (borde 5,33, sombra 2,67). `MarginV` 108 quedó en píxeles del video, igual que el `Viral` (no escalado). Omar confirma o cambia mirando las fotos; cambiar a 60 sin escalar es un solo factor.
- o3. **Preguntas dobles en el gancho:** una cifra del gancho que la voz dice más adelante es a la vez `no_dicho` del video y `spoiler`: D03 recibió 4 preguntas por 2 cifras. Mantener la ficha contesta las dos; duplica motivos. Sería una regla nueva: no se tocó.
- o4. **ch04 beat 5 tiene D47 «Entre 70 y 100 toneladas de TNT»** (D09 no se repitió, así que la corrección a D50 no se aplicó). Es otra estimación de potencia contra los «veinticinco a veintinueve» que dice la voz en [9]; el autor la juzgó «otro hecho» (preguntas por «TNT» y «100»). Para Omar, en la compuerta.
- o5. **`_donde` cita solo la primera oración donde aparece la cifra:** si la voz la dice varias veces, el autor ve una sola (p. ej. con D11 «20 millones de curios» citaría «…veinte años.» de ch01 y no «…veinte millones de curios» de ch04).
- o6. **`no_dicho` mira el dato, no la etiqueta** (desde F36): una cifra de la etiqueta que la voz sí diga no se pregunta.
- o7. **El gancho pierde `used_in`:** `dice_voz` miraba anclas y todas las cifras del texto del ítem; ahora se miran las cifras del dato de la ficha en todo el video y los nombres en la oración ancla ± 1 (lo que pide §2).
- o8. **Texto de motivo cambiado (no pedido):** en `pantalla_filtros.no_dicho`, el motivo del gancho dice «la voz lo dice en otra oración del video (gancho)» cuando la coincidencia está fuera de la ancla ± 1 (antes decía «en la oración ancla o en una vecina», falso para el gancho). Es texto de motivo, no prompt.
- o9. **Dos filas de §3 del handoff no coinciden con el cálculo** (D201 pasa sin pregunta; D03 int. 3 cae por `caben`).
- o10. **El render con `--gfx` de B no corrió** (guion de Vajont sin aprobar); la foto 2 es un sustituto sobre la capa de F38e. No se revisó el sello AMENAZA (120,8–123,3 s, a media altura a la izquierda, con subtítulo a la vez) ni la pregunta de cierre (sin voz). La prueba real es el primer render `--gfx` aprobado.
- o11. **Cortes feos que cumplen §1** («que se / llama», «se aprobó el / proyecto», «andamios la / fueron»): evitarlos pide una lista de palabras o un umbral, que DECISIONES 22:26 y §1 no dejan. Para que Omar los mire.
- o12. **`_segment_hash` no incluye el estilo de los subtítulos:** un `--reassemble` de Orleans o Vajont podría reusar segmentos viejos con karaoke.
- o13. **`_build_ass_from_syllables` se dejó:** sin llamador en producción, pero `test_module_38d_forcealign_integration.py` la importa y la llama; borrarla implica borrar esos tests (decide el analista u Omar).
- o14. **`video_type` por cap:** si un cap no está en el script, cae a `short` (karaoke).
- o15. **«Sin comillas» ahora va siempre en long-form** (antes solo con `--gfx`): el motivo es la fuente (Anton dibuja » como >>).
- o16. **Comentario viejo en `gfx_config.py:452`** («fonts.subs NO se cablea»): sigue cierto para `GfxRules`, pero `fase2b` ahora lee `fonts.subs` del perfil.
- o17. **«2000» → «2.000» se aplicó con `m01e_pantalla.editar`, no con `fase2b --plan-edit`** (que pide el script de Fase 2 y corre `--plan-only`, imposibles sin voz ni imágenes). La ficha editada conserva el `respaldo` literal («2000»), y una ficha editada a mano no pasa por la validación de `respaldo` (c9 de F38e).
- o18. **«cenás» sigue en `01a_escaleta.json`** (la cita de Valevich que la escaleta deja para el cierre) y el pool/la ficha conservan el texto de la fuente: la voz dice «cenas» y la cita de origen «cenás». No se tocó (la escaleta no lleva la narración).
- o19. **Candado nuevo:** `f792f3d4…`, medido con `--sw-encode` como siempre; anotado en ESTADO. No está claro si el `38e5ba14…` original (F4e) era con `--sw-encode`.
- o20. **El papel de Kyshtym está sin aprobar** (`aprobado` ausente): lo aprueba Omar con `python fase1_5.py --topic f39-kyshtym --aprobar-papel "Omar <fecha>"`.
- Lo de la lista de DECISIONES 18:30 sigue fuera: bloqueantes falsos de citas, detector de voseo, títulos automáticos, ficha de relleno en picos, formato de cifras del research. Y los abiertos de F39 (f1–f22) que no cerró esta tanda.

## Procesos (paso 12 de `/tanda`)
Subagentes A, B y el revisor: terminados, ninguno vivo. Shells en segundo plano: el papel de C y el candado (terminados); un armado del reporte que quedó colgado por un `cat` sin entrada se frenó con TaskStop. Ningún proceso de la tanda vivo. **CC no cerró nada de Omar; el subagente B cerró Firefox (o1).**

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | Paso 0: commit de DECISIONES y handoff tal cual, con md5 | OK | `md5sum` da `0f5bcfb4…` y `d769bb2a…`. El commit `8669045` toca solo esos 2 archivos. |
| A1 | Borrar (no apagar) `gancho_dicho` y `dice_voz` | OK | `grep` en `.py` de producción: no queda código vivo, solo un comentario en `pantalla_filtros.py:106,151`. `ORDEN` ya no lo tiene. El test `test_4_gancho_dicho_y_dice_voz_borrados` lo comprueba. |
| A2 | La pregunta cita cap, oración y texto | OK | `01e_pantalla.md`:244: «la voz dice «6» en ch05 [12] («Seis de octubre…»); ¿es el mismo hecho? si no, mantenelo». |
| A3 | Tests D03, mismo hecho y Vajont D195 | OK | `test_module_f40_gancho.py` + `test_module_f40_subs.py`: 26 passed, los corrí yo. |
| A4 | Tabla §3 recalculada por código | OK | Reporte líneas 56–63, desde `sim_gancho.py`. Dos filas difieren del analista (D201 pasa; D03 int. 3 cae por `caben`) y están declaradas (o9). |
| B1 | Constantes §1 | OK, con una escala a juzgar | Estilo `Documental,Anton,80,…,5.33,2.67,…,108`. Es 60/4/2 escalado por alto (1080 a 1440), derivado de «60 px (1080p)». `MarginV` 108 queda sin escalar (o2). Omar lo confirma mirando las fotos. |
| B2 | Eventos del .ass de Vajont ch02, 0 ✗ | OK | 35 eventos, todos ≤42×2 y 0,833–7 s. Las fotos 1 y 2 muestran subtítulo blanco con borde negro, sin amarillo (miré las dos PNG). |
| B3 | Karaoke solo short y Hook intacto | OK | `video_type` elige el estilo. El Hook se movió a `_ass_header`/`_ass_hook_event`; el reporte declara 4 casos byte-idénticos y el diff muestra el código movido. Lo corroboré por diff, no lo reproduje. |
| B4 | Render `--only-cap ch02 --gfx --reuse-visuals` y 3 fotos | PARCIAL | `guard_render` lo frenó (guion sin aprobar) y no se forzó. Las 3 PNG existen. Fotos 1 y 3 son del render sin gfx. Foto 2 es un sustituto: el .ass nuevo quemado sobre `ch02_gfx.mp4` viejo. Ahí la ficha y el subtítulo no se pisan, pero la ficha de esa capa está desfasada respecto del plan actual. |
| B5 | md5 de ch02 con `--no-subs` antes = después | OK | Logs: `98386f86…` antes y después, con subs OFF. Con subs `f792f3d4…` y el log dice `ON (documental)`. |
| C1 | Voseo con respaldo `_pre_f40` | OK | Existen los 3 `_pre_f40`. `grep` en los archivos vivos de narración da 0 «cenás» y 0 «acá». Quedan solo en `01a_escaleta.json`, `01e_pantalla_f39.*` y `01e_pantalla.raw.json` (cita de Valevich de la escaleta); está declarado (o18). |
| C2 | 7 títulos de DECISIONES 18:30 | OK | `01a_skeleton.json` líneas 6–173 coinciden uno a uno con DECISIONES. |
| C3 | Papel regenerado por `m01e_pantalla.generar` con tope 1,00 | OK | Raw y papel con fecha 19:01 (posterior al voseo, 18:44). Respaldo `01e_pantalla_f39.*` presente. US$ 0,4405 de 1,50 (la parte de costo no la verifiqué contra el ledger). |
| C4a | D50 en ch04 solo si se repite | OK | D09 no se repite (ch04 b5 tiene D47) y no se tocó. |
| C4b | «2000»→«2.000» con `plan-edit` | OBSERVACIÓN | La ficha D83 quedó «2.000»; el `.md` lo confirma. Se hizo con `m01e_pantalla.editar` directo y no con la CLI `fase2b --plan-edit`. El handoff nombra ambas en la misma frase y el motivo (la CLI pide script de Fase 2 y voz) es plausible, así que lo juzgo compatible con el pedido, pero es una desviación de forma. Está declarada (o17). |
| C5 | `01e_pantalla.md` ENTERO en el reporte | OK | md5 de `data/…/01e_pantalla.md` = el de la copia en `lab/…/c/` = `0ba9c0ad…`. El bloque pegado en el reporte es idéntico (solo cambia un salto de línea final). |
| F1 | No correr `--aprobar-papel` | OK | El papel no trae `aprobado` (`grep -c` = 0). |
| F2 | Cero cambios de prompt | OK | El md5 del prompt `3b98aef1…` coincide con el papel. Los md5 de A son del reporte. |
| F3 | Nada de voz, imágenes ni render de Kyshtym | OK | No hay evidencia de lo contrario. |
| F4 | Tope US$ 1,50 | OK | `lab/TOPE_TANDA.json` = 1.50; gasto 0,4405. |
| F5 | No cerrar programas de Omar | FALLA, declarada | El subagente B cerró Firefox (reporte líneas 142 y 321, abierto o1), contra DECISIONES 00:30. Está declarada y la memoria quedó corregida. |
| R | Cierre: reporte, ESTADO, push, revisor | PARCIAL | El reporte está completo con «lo que queda abierto» o1–o20 entero. El push y mi veredicto están pendientes de pegar. Mi lectura de ESTADO es el diff sin commitear, que es coherente. |

Fuera de alcance: ninguno. Los archivos sin commitear (`diag_234_cap4.py`, `f28a.log`) son anteriores a la tanda y no son de F40. `TOPE_TANDA.json` y `ESTADO_SESION.md` están dentro del pedido. Las escrituras en `output/` están declaradas, con respaldo de Vajont en `_bak_f40`.

Riesgos que el contrato no cubre:
- El render `--gfx` real, con ficha y subtítulo a la vez, nunca corrió. La foto 2 es un sustituto y queda sin verificar si el sello AMENAZA se pisa con el subtítulo (o10).
- `_segment_hash` no incluye el estilo de subtítulos (o12). Un `--reassemble` puede reusar segmentos con karaoke viejo.
- El gancho de Kyshtym genera preguntas dobles (no_dicho + spoiler): 4 por D03 con solo 2 cifras (o3). Son 4 preguntas para 2 cifras.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Fila B4: el `--gfx` no se forzó a propósito (aprobar el guion de Vajont es de Omar). Cuando Omar apruebe un guion, el primer render `--gfx` es la prueba real de ficha + subtítulo (o10).
- Fila F5: la falla queda como abierto o1; la memoria que la causó se corrigió («CC nunca cierra programas de Omar», DECISIONES 00:30).
- Fila R: este veredicto quedó pegado acá; el push y su salida van en la sección «Push de la rama» de arriba, después del commit final; ESTADO entra en el mismo commit.
