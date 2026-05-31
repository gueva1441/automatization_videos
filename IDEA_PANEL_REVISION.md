# IDEA_PANEL_REVISION.md — Panel de revisión pre-ensamblado

**Estado:** EN HOLD. No arrancar hasta publicar el video del Nyos + cerrar los
fixes de raíz de chat 33 (#234, HH:MM, m05 falsos mismatch).
**Origen:** brainstorm chat 33 (2026-05-29). Capturado para no perderlo.
**Por qué está escrito acá y no en memoria de Claude:** la memoria se borra y
es de Claude, no del proyecto. Esto vive en el repo = fuente de verdad.

---

## 1. QUÉ ES (en una frase)

Un panel visual que muestra TODA la película en borrador ANTES de gastar el
render final, donde Omar revisa imagen por imagen / anchor por anchor, y puede
accionar correcciones sin re-correr toda la cadena.

El dolor que ataca: hoy el pipeline es a ciegas hasta el MP4 final. Bugs como
"imagen no concuerda con narración" o "#234 anchor cae a uniforme" se descubren
mirando el video terminado. Este panel los caza ANTES de ensamblar, de forma
visual (donde el ojo de Omar es fuerte), reemplazando/complementando el menú de
texto de m06.

---

## 2. ARQUITECTURA DECIDIDA

**Camino A — TODO LOCAL.** Decidido en chat 33.

- Panel (HTML/frontend) + backend chico (FastAPI sugerido) corren en la
  máquina Windows local, donde YA está todo el pipeline: módulos m00-m07,
  Flux, Veo, ElevenLabs, DepthFlow, las venvs, los assets en C:\CLAUDE_PROJECTS\.
- Se abre en `localhost`. Solo para la compu de Omar (por ahora).
- El dominio Hetzner + n8n NO participan en fase 1.

**Por qué local y no Hetzner (razón técnica, no preferencia):**
- DepthFlow necesita GPU + venv local (`.venv-depthflow`). El Hetzner
  (salvo plan GPU) no la tiene → DepthFlow no corre o va lentísimo.
- Workarounds atados a Windows: `loudnorm.pyd` (lazy import por política WDAC),
  Whisper (mismo tema WDAC). Son código que existe PORQUE es Windows.
- Las APIs puras (Flux, Veo, ElevenLabs, Gemini) sí podrían correr desde
  cualquier lado (son HTTP a la nube), pero DepthFlow ata todo a local.
- Conclusión: con todo local, DepthFlow deja de ser problema. Lo factible y lo
  mejor coinciden.

**Migración futura a acceso remoto (si algún día se quiere abrir desde el celu):**
FastAPI es el mismo código corra donde corra. Se migra a un esquema híbrido
sin tirar nada. NO es necesario para el panel de revisión.

**Dato de contexto:** Omar ya tiene un proyecto con trigger de Telegram corriendo
Python en el Hetzner. O sea el patrón "servicio que escucha → dispara Python →
responde" ya lo ejecutó. No parte de cero el día que quiera fase remota.

---

## 3. FEATURES — Por anchor / por capítulo

Línea de tiempo del ancho del video, partida por capítulos. Cada anchor es un
cuadrito dinámico sobre la línea, mostrando:

- **La imagen real de Flux** generada para ese anchor (la que se revisa de verdad).
- **El texto de narración** de ese tramo.
- **El movimiento de DepthFlow asignado** por Gemini (horizontal / vertical /
  orbital) como badge/etiqueta.
- **Muestra de movimiento (ayuda visual):** un clip/GIF PRE-GRABADO y guardado,
  uno por cada movimiento. FIJO, no varía nunca. Es una chuleta visual de "así
  se mueve orbital", NO la animación real de esta foto. Se generan UNA vez con
  DepthFlow sobre una imagen de prueba (3 clips) y se guardan. Trivial.
  → CLAVE: esto evita renderizar DepthFlow sobre las 100+ imágenes antes de
    aprobar. Sin esta separación, el panel sería lento y caro.
- **La música que suena en ese tramo** (con play para escucharla).

---

## 4. FEATURES ACCIONABLES — Las 3 grandes (A / B / C)

Pesos honestos: A es la joya, B es el músculo, C es el lujo. Orden de
construcción natural: A → B → C. A solo ya cambia el juego.

### A — Director de video conversacional (LA JOYA)
LLM (Gemini) como director creativo con el que se charla en lenguaje natural.
- Omar: "este Veo no retiene, dame 3 ideas habladas para este anchor".
- Gemini tira 3 conceptos EN TEXTO, sin generar nada (barato).
- Omar elige uno → RECIÉN AHÍ Gemini construye el prompt → dispara generación.
- Por qué es lo más fuerte: separa la conversación creativa (barata, texto) de
  la generación (cara, imagen/video). Es la evolución natural de m05
  ("LLM as teacher" → "LLM as director"). Encaja con la filosofía "opciones
  habladas + confirmación antes de gastar plata".

### B — Regeneración selectiva por anchor (EL MÚSCULO)
- Se aprueba una opción → genera prompt → Flux/Veo crea la imagen → aparece en
  el panel SIN re-correr toda la cadena.
- Requiere que el panel pueda DISPARAR el pipeline (botón → script de regen de
  UN anchor). Es plomería, no concepto. Factible con backend local.
- Aplica también a audio: si la música no gusta, mostrar qué OTROS audios ya
  grabados están disponibles y poder cambiar el asignado.

### C — Probar efecto DepthFlow real en UNA imagen (EL LUJO)
- Botón → renderiza DepthFlow sobre esa única imagen → play → aprobar.
- ⚠️ DECISIÓN CERRADA A REVISAR: el roadmap ELIMINÓ zoom_in/zoom_out/dolly y se
  quedó con 3 movimientos (chat 21). Omar mencionó querer "los 5" acá. ANTES de
  reabrir: recordar POR QUÉ se sacaron (se veían casi estáticos sin los kwargs
  isometric/depth; inventario reducido a horizontal/vertical/orbital validado).
- ⚠️ Es la ÚNICA parte que renderiza DepthFlow on-demand (cuesta cómputo).
  Rompe un poco la premisa "panel barato que no renderiza". Posible (DepthFlow
  sobre 1 img es rápido) pero va al final. Es premium.

---

## 5. FEATURES BARATAS DE VERDAD (solo leen JSON que ya se produce)

Cero riesgo, cero gasto. Solo display de datos existentes. Buen punto de arranque.

- **Semáforo de salud del video (LA MÁS FUERTE de las baratas).** Una pantalla
  rojo/verde antes de aprobar: ¿algún anchor cayó a uniforme (#234)? ¿algún cap
  sin música? ¿alguna imagen 3/3 en m05? Es el checklist de "¿listo para
  ensamblar?" automatizado. Lee sync_map + music_map + issues m05. Ataca el
  dolor más viejo y repetido: descubrir bugs mirando el MP4 final. #234 mordió
  en chat 31 Y 32 justamente porque cae en SILENCIO.
- **Lectura del guion corrido** (los 7 caps seguidos, limpio, como lo escucha
  el espectador). Detectar baches de retención LEYENDO, antes de gastar.
- **Diff visual entre regeneraciones** ("cap 4 backup vs ahora": qué prompts
  cambiaron, qué imágenes se rehicieron). Saca la duda "¿mejoré o la cagué?".
- **Menú de m06 como semáforos** en vez de texto (cohorts 3/3, 2/3, 1/3 ya
  existen → solo mostrarlos como colores).

---

## 6. TRAMPAS DESCARTADAS (suenan simples, esconden proceso caro)

Omar las descartó en chat 33 tras verlas. Documentadas para no re-proponerlas:

- **Slider de volumen de música en el panel.** TRAMPA: el `mixing` config se
  HORNEA en el sync_map al generar el audio (backlog: olor arquitectónico).
  Mover el slider re-dispararía ElevenLabs (~2 min + gasto) + regen m07. No es
  "mover slider y listo".
- **Previsualizar voz de Bill en un anchor** → llamada ElevenLabs, gasta.
- (Nota: "cambiar a otro audio YA grabado" SÍ se queda — eso es feature B, no
  trampa, porque no regenera, solo reasigna uno existente.)

---

## 7. ADVERTENCIA META (lección #91 + #7 de chat 32)

Esta idea creció rápido en el brainstorm: de "panel para revisar imágenes" a
"IDE con director conversacional + regen selectiva + 5 movimientos + sliders +
dashboards". Cada cosa suena "simple de agregar" — ESA sensación es la trampa
del patrón #91 (si todo parece "agregar item N", capaz hay que repensar el
alcance, no sumar features).

Disciplina al retomar:
1. Publicar el video del Nyos primero. Cerrar fixes de chat 33.
2. Arrancar por las features BARATAS (sección 5) — semáforo de salud primero.
   Dan valor inmediato sin gasto ni backend complejo.
3. Después A (director conversacional). Necesita backend FastAPI local.
4. Después B (regen selectiva).
5. C (DepthFlow on-demand) al final, si todavía se quiere.

NO arrancar por C ni por los sliders. NO mezclar las baratas con las caras en
la misma primera versión.

---

## 8. STACK SUGERIDO (para cuando se arranque)

- **Frontend:** HTML + JS (o un framework liviano). Lee los JSON, dibuja el
  timeline, muestra PNGs desde disco.
- **Backend:** FastAPI local (Python, lo que ya domina el pipeline). Recibe
  clics del panel y corre los scripts de regen / llamadas a Gemini.
- **Cómo se sirve:** `python -m http.server` o el propio FastAPI sirviendo el
  HTML. Se abre en `localhost`.
- **Quién lo construye:** Claude Code (es código, no diagnóstico). Claude (chat)
  arma el handoff de diseño. Mismo two-layer de siempre.
- **Cómo se valida:** con el mecanismo push_id de chat 33. Claude Code escribe →
  Omar pushea + refresh → Claude (chat) revisa leyendo el repo. Estreno real
  del VERSION.json.
- **OJO gitignore:** el panel es código → va a GitHub. Pero los PNG/MP4/JSON de
  output están gitignored → Claude NO los ve por el repo. Para validar que el
  panel LEE bien esos datos, Omar pega outputs por PowerShell como siempre.

---

## 9. NOTA SOBRE VIRALIZACIÓN — leer al retomar

El panel es un ACELERADOR DE ITERACIÓN, no un DETECTOR DE FÓRMULA. Distinguir
esto evita sobre-invertir esperando algo que el panel no hace.

- **Lo que el panel SÍ da:** velocidad. Probar más variantes (hook, imagen,
  ritmo) por unidad de tiempo, viendo y corrigiendo ANTES de ensamblar. El loop
  probar→ajustar→repetir se vuelve más rápido y barato.
- **Lo que el panel NO da:** la fórmula misma. La retención real (la que define
  si viraliza) NO se ve en pre-ensamblado — se ve en los datos de YouTube/TikTok
  DESPUÉS de publicar: curva de retención, % que pasa los primeros 3s, dónde
  abandonan. Esa señal viene de la plataforma, no del pipeline.
- **Dónde está de verdad la fórmula:** publicando volumen y leyendo retención
  real. Ej. ya sabido del nicho: voz clonada Bill = factor #1 retención dark
  history (eso salió del nicho/datos, no de un panel).
- **Idea futura SEPARADA del panel:** cuando Omar tenga varios videos
  publicados, lo más valioso para "buscar fórmula" probablemente NO es el panel
  sino una herramienta chica que lea la retención de los videos YA publicados y
  detecte patrones ("los que arrancan con pregunta retienen X% más que los que
  arrancan con dato"). El panel produce mejor; el análisis post-publicación
  descubre qué funciona. Son dos cosas distintas, ambas útiles.

---

## FIN IDEA_PANEL_REVISION.md
