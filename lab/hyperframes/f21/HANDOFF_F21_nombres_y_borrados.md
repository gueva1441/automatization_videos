# HANDOFF F21 — Familias A + B + F de la auditoría: un solo módulo de nombres, fuera el molde de Orleans, los jueces leen la traducción

Analista · 2026-10-24 · Para CC (misma sesión). Base: `08d63d9` (rama `f11-guion-v4`). **Cero llamadas a modelos.** Leé primero `lab/hyperframes/f21/AUDITORIA_fase1_supuestos.md` §1 (familias A, B, F) y los anexos cuando necesités la línea exacta. **PARADA al terminar: el analista valida antes de F22.**

## 0. Por qué
Hoy ningún tema que no sea Orleans pasa la fase 1 entera, por tres cosas que esta tanda arregla:
- **A.** Siete funciones distintas deciden «qué es un nombre» y «cuál es el apellido», todas con regex latina y «apellido = última palabra». Verificado ejecutando: `is_person("V.M. Osetrov") → False`, `person_key("Jürgen Müller") → ("","")`, `is_named_person("Juan de la Cruz") → False`, «Rasputin» → False, cirílico → False; `slugify` de dos títulos rusos → el mismo slug (un documento pisa a otro). Y `norm` (NFD sin marcas) convierte «й» en «и».
- **B.** Vocabulario de Orleans en el código: `SUBJECT_RE_DEFAULT` = «Orleans Parish Prison» para todos los temas (`run_seed` nunca pasa otro), `_OTHER_PLACE` (Hunt, Angola, Jena…), `_OFFICIAL_SAYS` (sheriff), `role_problems` con dos clases preso/guardia (bloqueante (b) del guion: «el teniente Ivanov» + «el sobreviviente Ivanov» → PARADA falsa), `_COMMON_CAPS`, `FORBIDDEN_FILLER` («manto de», «ecos de»), `JUDGMENTS`, `photo_problems` («cámara», «imagen»), `ADMIN_TERMS`, `INSTITUTION`, `verify_quotes` con el tema escrito.
- **F.** La ficha (F19) guarda `texto` original y `traduccion`; la voz dice la traducción; pero `false_quotes`, `role_problems`, `unverified_named` y las métricas comparan contra `pool.citas[].texto` original → en Kyshtym toda cita en español es «cita falsa».

Esta tanda **borra y unifica**. No agrega ningún chequeo, no toca ningún prompt (eso es F22), no cambia umbrales (F23).

## 1. Cambios

### 1.1 Un módulo `script_engine/nombres.py` (A)
Reemplaza a: `research_v3.person_key`, `research_v3.is_named_person`, `research_v3.same_person`, `research_v3.name_terms`, `research_v3._names_in`, `evidence_pool.is_person`, `evidence_pool._person_key`, `evidence._surname`, `guion_v4._surname`, `guion_v4._is_human`, `m01b_guionista._surname`, `verify_quotes._named`, `m01a_columna._tokens/persona_de`, y los `ev.norm(x).split()[-1]` sueltos de `m01a_escaleta` (258-263, 642, 1265) y `ficha_caso` (455). Las funciones viejas quedan como **alias de una línea** al módulo nuevo (para no tocar 40 call sites de golpe) y se marcan `# F21: alias`.

```python
# script_engine/nombres.py — F21. Única fuente de verdad sobre nombres de persona.
import re, unicodedata

PARTICULAS = {"de", "del", "la", "las", "los", "da", "das", "do", "dos", "di", "van", "von", "der", "den", "le",
              "du", "y", "e", "bin", "ibn", "al", "el"}
SUFIJOS = {"jr", "sr", "ii", "iii", "iv", "hijo", "padre"}
TRATAMIENTOS_BASE = {"mr", "mrs", "ms", "dr", "sra", "srta", "don", "dona",
                     "sheriff", "deputy", "alguacil", "sgt", "sergeant", "lieutenant", "lt", "captain", "capt",
                     "capitan", "colonel", "col", "officer", "oficial", "chief", "jefe", "teniente", "sargento",
                     "secretary", "secretario"} | SUFIJOS   # lo que hoy es _TITLES_BASE; los roles del perfil se suman
_tratamientos = set(TRATAMIENTOS_BASE)

def set_tratamientos(extra) -> None:
    """Lo llama research_v3.set_vocabulario con las palabras de roles_testigo/roles_antagonista del perfil."""
    global _tratamientos
    _tratamientos = TRATAMIENTOS_BASE | {norm(w) for w in extra or [] if len(w) >= 3}

_Q = str.maketrans({"«": '"', "»": '"', "“": '"', "”": '"', "„": '"', "‘": "'", "’": "'"})   # = evidence_pool._QUOTES + „

def norm(s) -> str:
    """Minúsculas, comillas unificadas, sin tildes **solo en letras latinas** (ü→u sí; й, ё intactas). Para texto
    latino da exactamente lo mismo que evidence_pool.norm de hoy (probado por el analista con 5 cadenas de Orleans,
    incluida una con «—»); la única diferencia es que „ también se vuelve comilla recta."""
    out = []
    for ch in str(s or "").translate(_Q).lower():
        d = unicodedata.normalize("NFD", ch)
        base = d[0]
        if len(d) > 1 and unicodedata.name(base, "").startswith("LATIN"):
            out.append(base)                      # quita la tilde solo si la base es latina
        else:
            out.append(ch)                        # cirílico: se queda como está (NFC)
    return re.sub(r"\s+", " ", "".join(out)).strip().strip(" .,;:")

def palabras(name) -> list[str]:
    """Las palabras de un nombre, en cualquier alfabeto, con las iniciales separadas: «V.M. Osetrov» → [V, M, Osetrov]."""
    s = re.sub(r"\([^)]*\)", " ", str(name or ""))
    return re.findall(r"[^\W\d_]+", s)

def _mayus(w: str, todo_mayus: bool) -> bool:
    return w[:1].isupper() and (todo_mayus or not w.isupper() or len(w) == 1)

def partes(name) -> list[str]:
    """Nombre y apellido(s) normalizados, sin tratamientos, sin partículas, sin iniciales. «Deputy Renard Reed» →
    [renard, reed]; «Juan de la Cruz» → [juan, cruz]; «Любовь Ладейщикова» → [любовь, ладейщикова]."""
    ws = palabras(name)
    todo = bool(ws) and all(w.isupper() for w in ws if len(w) > 1)      # «MARLIN GUSMAN» (PDF oficial)
    out = []
    for w in ws:
        n = norm(w)
        if len(w) == 1 or n in _tratamientos or n in PARTICULAS or not _mayus(w, todo):
            continue
        out.append(n)
    return out

def iniciales(name) -> list[str]:
    return [norm(w) for w in palabras(name) if len(w) == 1 and w.isupper()]

def clave(name) -> tuple[str, str]:
    """(nombre, apellido). Mononimio → ("", x). Sin partes → ("", "")."""
    p = partes(name)
    if not p:
        return ("", "")
    return (p[0] if len(p) > 1 else "", p[-1])

def apellido(name) -> str:
    return clave(name)[1]

_ORG = {"union", "watch", "departamento", "cuerpo", "oficina", "agencia", "society", "asociacion", "comite",
        "tribunal", "corte", "jurado", "gobierno", "project", "ministerio", "comision", "instituto", "empresa",
        "compania", "company", "committee", "ministry", "institute"}
_GRUPO = re.compile(r"\b(group|grupo|segun|según)\b", re.I)   # lo que queda de _NOT_PERSON: solo grupo/atribución
GRUPOS_BASE = {"officers", "oficiales", "officials", "guards", "guardias", "deputies"}   # formas de grupo, no persona
_grupos = set(GRUPOS_BASE)

def set_grupos(extra) -> None:
    """Lo llama research_v3.set_vocabulario con las formas de grupo (plurales) de los roles del perfil."""
    global _grupos
    _grupos = GRUPOS_BASE | {norm(w) for w in extra or []}

def es_persona(name, mononimo_ok: bool = False) -> bool:
    """Un nombre propio de persona: ≥ 1 apellido de ≥ 2 letras más (otra parte, una inicial o un tratamiento/cargo
    delante: «Deputy Foster»), sin palabras de organización ni de grupo. Con mononimo_ok, basta el apellido
    («Rasputin», un apodo)."""
    raw = palabras(name)
    ws = {norm(w) for w in raw}
    p = partes(name)
    if not p or ws & _ORG or ws & _grupos or _GRUPO.search(str(name or "")):
        return False
    # una palabra en minúscula que no es partícula ni tratamiento es una descripción, no un nombre («un preso de…»)
    if any(w[:1].islower() and norm(w) not in PARTICULAS | _tratamientos for w in raw):
        return False
    cargo = bool(ws & (_tratamientos - SUFIJOS))          # «Deputy Foster», «el teniente Ivanov»
    return len(p) >= 2 or bool(iniciales(name)) or cargo or (mononimo_ok and len(p) == 1)

def misma(a, b) -> bool:
    """Mismo apellido y nombre compatible (igual, uno sin nombre, o las 3 primeras letras iguales)."""
    (fa, la), (fb, lb) = clave(a), clave(b)
    return bool(la) and la == lb and (not fa or not fb or fa[:3] == fb[:3])

def terminos(persona: dict, people: list[dict]) -> list[str]:
    """Cómo buscar a una persona en texto normalizado: «nombre apellido» de cada variante, y el apellido solo si
    nadie más del pool lo comparte."""
    out = []
    for v in [persona.get("nombre")] + list(persona.get("variantes_nombre") or persona.get("variantes") or []):
        f, l = clave(v)
        if f and l:
            out.append(f"{f} {l}")
    sur = apellido(persona.get("nombre"))
    if sur and sum(1 for q in people if apellido(q.get("nombre")) == sur) == 1:
        out.append(sur)
    return list(dict.fromkeys(out))

def menciona(text, termino) -> bool:
    """¿`termino` (ya normalizado) aparece como palabra entera en `text`? Sin \\b (falla en cirílico)."""
    t = norm(text)
    return bool(termino) and re.search(rf"(?<![^\W\d_]){re.escape(termino)}(?![^\W\d_])", t) is not None

def nombra(text, persona: dict, people: list[dict]) -> bool:
    return any(menciona(text, x) for x in terminos(persona, people))
```

**Cómo se conecta (sin cambiar criterios, solo la función que decide):**
- `evidence_pool.norm` → `return nombres.norm(s)` (test: para 500 cadenas latinas del pool de Orleans, byte-idéntico al `norm` viejo; para «Озёрск» no cambia la letra).
- `research_v3.person_key = nombres.clave`; `is_named_person(n) = nombres.es_persona(n)`; `same_person = nombres.misma`; `name_terms = nombres.terminos`; `_names_in(terms, text) = any(nombres.menciona(text, x) for x in terms)`; `presence_v3` usa `menciona` en vez de `\b…\b` sobre `_ascii`. `set_vocabulario` llama `nombres.set_tratamientos(roles)`. En `validate` de personajes (1132-1137): «el apellido está en el documento» → `nombres.menciona(doc, apellido)` **o** cualquier parte del nombre; y se acepta mononimio si el ítem trae `rol` (`mononimo_ok=True`).
- `evidence_pool.is_person = nombres.es_persona`; `_person_key = nombres.clave`.
- `evidence._surname = nombres.apellido`; `_content`: `[a-zñ]{5,}` → `[^\W\d_]{5,}`.
- `guion_v4._surname = nombres.apellido`; `_is_human` → `nombres.misma(author, hum)`; en `unverified_named`, `_named` → `nombres.es_persona` y el `re.search(rf"\b{sur}\b")` → `nombres.menciona`; quitar el `len(sur) > 3` (Li, Wu, Roy).
- `m01b_guionista._surname = nombres.apellido`; `verify_quotes._named = nombres.es_persona`.
- `m01a_columna._tokens(s)` → `nombres.partes(s)` (y `persona_de` compara esas partes).
- `m01a_escaleta` 258-263, 642, 1265: `sur = nombres.apellido(...)` y las comprobaciones por substring → `nombres.menciona`.
- `ficha_caso` 455: `sur = nombres.apellido(nom)` + `menciona`.
- `m05_narrative` 149-157 (`silent_names`), 211-225 (`names_with_role`): usar `terminos`/`menciona`; el patrón «primera y última palabra en mayúscula» de `names_with_role` se reemplaza por `nombres.clave` (métrica, no bloqueante, pero que no mienta).
- `research_v3.slugify` (437): sufijo `-{f["id"]}` siempre (no solo para cirílico). `_path_tokens` (218): `\w+`.
- Los regex `[A-Za-zÁÉÍÓÚÑ…]`/`[a-zñ]+` que queden en los archivos de la fase 1 **se listan en el reporte** con línea y qué deciden; no hace falta cambiarlos todos ahora si no deciden nada (cosmético), pero sí los que deciden (anexos A).

### 1.2 Fuera el molde de Orleans (B) — solo el camino de producción
| dónde | qué | cómo queda |
|---|---|---|
| `research_v3.py:1718-1726` | `SUBJECT_RE_DEFAULT`, `_OTHER_PLACE`, `_OFFICIAL_SAYS` | `subject_re` se arma en `run_seed` desde el perfil: `nombres_lugar` + `nombres_locales` (el mismo `place_re` de F19) + «complejo/planta/edificio/recinto» genéricos **no**: solo los nombres del perfil. `_OTHER_PLACE` **se borra** (si el perfil trae `lugares_excluidos`, se usa; hoy no lo trae: nada). `_OFFICIAL_SAYS` → `oficial(es)?\|official\|registros?\|records?\|autoridad(es)?` + «según (cada rol de `roles_antagonista`)». Sin default de Orleans en ningún lado. |
| `research_v3.py:335-336` | stopwords orleans/parish/prison/katrina/hurricane en `_words` | borrar la resta; `\w+` |
| `research_v3.py:1233` `_NOT_PERSON_BASE` | `del?\|en\|at\|of\|the\|…\|officers\|oficiales` | ya no se usa: `es_persona` filtra con `_GRUPO` (group/grupo/según) y las formas de grupo del perfil (`set_vocabulario` las sigue pasando, ahora a `nombres` como `set_grupos`, mismo mecanismo). Las partículas las maneja `partes`. |
| `research_v3.py:1227` `_TITLES_BASE` | se queda **igual** (F20 lo probó con Reed) pero vive en `nombres.TRATAMIENTOS_BASE`; `_TITLES` = alias. |
| `script_engine/guion_v3_reglas.py:281-301` | `_ROLE_PRESO`, `_ROLE_GUARDIA`, `role_class` preso/guardia | **se borran.** `role_class(text)` devuelve `"testigo"` / `"antagonista"` / `None` según las palabras de `roles_testigo` / `roles_antagonista` del **perfil del seed** (las mismas que lee `research_v3.set_vocabulario`; se exponen como `research_v3.vocabulario()`). Sin perfil → siempre `None` → el bloqueante (b) no dispara y el reporte lo dice («(b) sin perfil: no evaluado»). `_ROLE_BEFORE/_ROLE_AFTER` se arman con esas mismas palabras. El resto de `role_problems` (la lógica de «antes/aposición/intro de cita») **no cambia**; el emparejamiento autor↔persona por `split()[-1]` pasa a `nombres.misma`. |
| `guion_v3_reglas.py:73-93` `JUDGMENTS` | patrones de Orleans/Ycuá («no eran considerados humanos», «como animales», «el sistema los abandonó», «fue una masacre», «esperar un milagro», «caos deliberado», «castig\w*») | se borran esos; quedan solo los **estructurales** (adverbios de intención: «deliberadamente», «a propósito», «sabían que», «a sabiendas»). Es métrica; que mida algo general. |
| `guion_v3_reglas.py:400-411` `photo_problems` | prohíbe foto/fotografía/imagen/cámara/retrato/instantánea | solo `foto\|fotograf\w+\|fotógraf\w+` (lo demás son hechos: «cámara de reacción», «imagen satelital»). |
| `script_engine/evidence.py:312-323` `_COMMON_CAPS` | arrestado, turista, recluso, demandante, sheriff, alcaide, huracán, adjunto, teniente | se borra la lista; `fix_glued_caps` baja a minúscula la palabra pegada solo si es una palabra de **rol del pool** (`rol` de `personajes`, en minúscula) o un tratamiento de `nombres`. |
| `evidence.py:59` | «sheriff» en `_surname` | desaparece con el alias. |
| `script_engine/m05_narrative.py:40-44` `FORBIDDEN_FILLER` | «infierno flotante», «el monstruo», «manto de», «ecos de» | se quitan esas cuatro; el resto de clichés genéricos queda (es métrica). |
| `script_engine/m01a_escaleta.py:85-87` `ADMIN_TERMS` | duro en v1 para la pregunta de pantalla | en v1 pasa a métrica, igual que en v2 (una línea). La lista se queda, es informativa. |
| `script_engine/m01b_guionista.py:40-41` `INSTITUTION` | parish, opp, aclu, fema, sheriff, cuerpo de ingenieros… | la lista se arma desde la ficha: `personas` con rol institucional + `_ORG` de `nombres`; sin ficha, solo `_ORG`. Métrica. |
| `researcher_steps/verify_quotes.py:40` | `TEMA: la Prisión Parroquial de Orleans…` | `TEMA: {seed_title}` (parámetro). Función dormida; igual no puede quedar con el tema escrito. |
| `evidence_pool.py` 154 `_ORG_WORDS`, 233/297 `_NOT_VERB`/`_COMMON_HEADS`, 337-347 `build_prompt`, 579-584 `_OFICIAL`/`_COUNT_NOUN` | Orleans | `_ORG_WORDS` → `nombres._ORG`. Las otras cuatro son del camino v2 (`RESEARCH_V3=0`): **no se tocan**, se listan en el reporte como «v2, dormido». |
| comentarios/docstrings con Gusman, Lewis, Templeman, Katrina en los archivos tocados | J | se neutralizan de pasada **solo en los archivos que esta tanda ya abre**. Nada más. |

### 1.3 Los jueces leen la traducción (F)
Una sola función nueva, un solo lugar donde se aplica:
```python
# guion_v4.py
def pool_con_traducciones(pool: dict, ficha: dict | None) -> dict:
    """F21 (F): copia del pool donde cada cita Q## que la ficha trae con `traduccion` lleva ese texto en `texto`
    (y el original en `texto_original`). Los jueces comparan contra lo que la voz dice. Sin ficha, el pool tal cual."""
```
Se aplica **al entrar** a `bloqueantes()` (`pool_j = pool_con_traducciones(pool, ficha)`) y se pasa `pool_j` a `false_quotes`, `role_problems`, `unverified_named` y a las métricas de `mg.review`/`m05` que reciben el pool. `contamination` e `invented_numbers` reciben el pool original (no miran citas; y una cifra traducida igual tiene que estar en el pool). En `unverified_named`, la búsqueda del texto (`q["texto"][:40]`) usa `texto` **y** `texto_original`. `ficha_caso.id_texts` no cambia.

### 1.4 Nada más
No se tocan: prompts (ni una letra; md5 de los cuatro iguales en el reporte), `pool_gate`, `video_length`, `config`, umbrales, antagonista, ejemplos, `m03*`, `gfx_*`, voz. No se corre ningún modelo.

## 2. Validación sin API: `lab/hyperframes/f21/recheck.py`
Un script que, para **Orleans (`ba6c3cac-f7r3`), Ycuá (`f8s1-ycua-bolanos`) y Kyshtym (`f18-kyshtym-mayak`)**, con lo que ya está en disco:
1. Carga perfil → `set_vocabulario`; re-corre `person_stats`/`verify_pool`-equivalente sobre el pool existente (sin bajar nada) → elegibles con nombres, `n_citas_verificadas`, `n_datos`, `presente_en_evento`; `pool_gate` → color.
2. Ficha existente → `ficha_caso.problems` (cuántos, cuáles).
3. Columna existente → chequeo de la columna.
4. Escaleta existente → `bloqueantes()` de la escaleta.
5. Guion existente (la última narración de cada tema) → `guion_v4.bloqueantes(…, ficha=…)` **y** la lista de métricas.
Se corre **dos veces**: en `08d63d9` (antes; `git stash`/worktree) y con F21. Salida `RECHECK_f21.md`: una tabla por tema, filas = cada medida de 1–5, columnas antes | después | Δ, y debajo las listas con nombres (quién entra/sale de elegibles; qué bloqueante aparece/desaparece y por qué).

**Lo que tiene que pasar** (si no, PARADA y me lo contás antes de tocar nada más):
- Orleans y Ycuá: mismos colores de compuerta; elegibles iguales o más (si alguien sale, nombre y causa); bloqueantes del guion iguales o menos; **ningún bloqueante nuevo**.
- Kyshtym: entran como personas (y como candidatos a elegible según la regla de F20) Osetrov, Komarov, Serov, Ladeyshchikova; el guion de F19 pierde los bloqueantes de «cita falsa» que eran traducciones; (b) no dispara por teniente/sobreviviente.

## 3. Tests (sin red)
- `nombres`: `es_persona` para «V.M. Osetrov» ✔, «Juan de la Cruz» ✔, «Jürgen Müller» ✔, «Любовь Ладейщикова» ✔, «MARLIN GUSMAN» ✔, «Renard Reed» ✔, «Deputy Foster» ✔ (→ clave ("", "foster")), «Rasputin» (False sin `mononimo_ok`, True con), «National Guard Officers» ✗, «Criminal Justice Working Group» ✗, «según la ACLU» ✗, «el Ministerio de Construcción» ✗. `clave("Juan de la Cruz") == ("juan","cruz")`, `clave("Sgt. Bell") == ("","bell")`, `clave("Gonçalves") == ("","goncalves")`, `misma("Marlin Gusman","Martin Gusman")`. `menciona("…Ладейщикова…", "ладейщикова")` ✔ y `menciona("lista", "li")` ✗.
- `norm`: 500 cadenas latinas del pool de Orleans → idéntico al viejo; «Озёрск» → «озёрск» (ё intacta); «“Templeman”» → `"templeman"`.
- `slugify`: dos títulos cirílicos distintos del mismo sitio/año → slugs distintos.
- `role_class` con perfil de Orleans: «deputy» → antagonista si el perfil lo tiene ahí, «preso» → testigo; con perfil de Kyshtym «teniente» → None; sin perfil → None siempre; `role_problems` sobre «el teniente Ivanov… el sobreviviente Ivanov» con perfil Kyshtym → `[]`.
- `pool_con_traducciones`: cita Q01 con `traduccion` en la ficha → `false_quotes` sobre la traducción entre comillas → `[]`; sin ficha → igual que hoy.
- `fix_glued_caps` sin la lista: «el Recluso dijo» con pool cuyo rol es «recluso» → minúscula; «el Huracán Katrina» → no toca.
- `photo_problems`: «la cámara de reacción» → `[]`; «la foto muestra» → problema.
- Suites verdes + las 5 previas; dorado de v3 verde; escaleta sin ficha byte-idéntica; md5 de los 4 prompts sin cambio.

## 4. Frenos
- Cero chequeos nuevos, cero prompts tocados, cero API. Si para que algo pase hace falta una regla nueva, **no**: se anota en el reporte.
- Las funciones viejas quedan como alias; no se borran call sites a mano más allá de lo listado.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`. Borrar `lab/hyperframes/f21/_transfer_tmp/` (basura del analista).
- Actualizar `lab/ESTADO_SESION.md`.

## 5. Reporte `lab/hyperframes/f21/F21_REPORT.md`
1. `RECHECK_f21.md` íntegro (las tres tablas antes | después).
2. Lista de alias creados (función vieja → función nueva) y de regex latinas que quedan en fase 1 con línea y veredicto (decide / no decide).
3. Lo que se borró, archivo:línea, con una línea de qué era.
4. md5 de los 4 prompts (ficha, columna, escaleta, guion v5.1) iguales a los de F20.
5. Veredicto íntegro del revisor-handoff. Costo: US$ 0.00 (confirmado en `cost_history`).

## 6. PARADA
Commit + reporte → PARADA. El analista revisa el diff completo (`git diff 08d63d9..HEAD -- researcher_steps script_engine`), lee `RECHECK_f21.md` y recién después escribe F22 (ejemplos de los prompts + antagonista).
