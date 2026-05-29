"""
transition_profiles.py — Reglas duras de transiciones por art_profile + posición.

Funciona como guard-rail anti-alucinación + sistema de defaults estáticos:
  - whitelist            : transiciones preferidas (sugerencia para director futuro)
  - blacklist            : transiciones PROHIBIDAS por nicho
  - default_by_position  : transición estática por unión narrativa cuando
                           no hay director, o cuando el director falla

POSICIONES NARRATIVAS soportadas:
  - "hook_to_body"     : ch01→ch02 (entrada al misterio)
  - "body_to_body"     : capítulos del cuerpo entre sí (ch02→ch03, ch03→ch04, etc.)
  - "body_to_climax"   : mid-point narrativo (típicamente ch04→ch05 en LONG)
  - "body_to_reveal"   : última transición del cuerpo a la revelación (ch07→ch08)
  - "intra_chapter"    : foto→foto DENTRO del mismo capítulo Flux

NO contiene parámetros de render (eso vive en transition_config.py).
NO contiene la lógica de aplicación FFmpeg (eso vive en parallax_animator_v2.py
o en un futuro modules/transition_applier.py).
"""
from __future__ import annotations

from dataclasses import dataclass

from transition_config import (
    DEFAULT_TRANSITION,
    VALID_TRANSITIONS,
    is_valid,
)


# ═══════════════════════════════════════════════════════════════
#  TIPOS
# ═══════════════════════════════════════════════════════════════

# Las posiciones narrativas son strings cerrados.
# No usamos Literal para no atar a Python 3.11+ aunque ya está el tipo.
NARRATIVE_POSITIONS: frozenset[str] = frozenset({
    "hook_to_body",
    "body_to_body",
    "body_to_climax",
    "body_to_reveal",
    "intra_chapter",
})


# ═══════════════════════════════════════════════════════════════
#  REGLAS POR art_profile
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionProfileRules:
    whitelist: frozenset[str]                   # transiciones preferidas
    blacklist: frozenset[str]                   # transiciones PROHIBIDAS
    default_by_position: dict[str, str]         # posición → nombre transición


TRANSITION_PROFILES: dict[str, TransitionProfileRules] = {
    # ─── SUBMARINE: profundidad, abismo, criaturas marinas ───
    # Permite TODO. La estética submarina aguanta drama agresivo.
    "SUBMARINE": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_black",
        }),
        blacklist=frozenset({"fade_to_white"}),  # no encaja la estética purificadora
        default_by_position={
            "hook_to_body":   "whip_pan_flash",  # ← GANADORA: entrada dramática al abismo
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",  # giro narrativo
            "body_to_reveal": "zoom_punch",      # caída hacia revelación
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── INTERIOR: caras frontales, espacios cerrados ───
    # NO whip_pan agresivo en caras (motion blur destroza rasgos).
    # Prefiere zoom_punch y crossfade.
    "INTERIOR": TransitionProfileRules(
        whitelist=frozenset({
            "zoom_punch", "crossfade", "crossfade_micro",
            "fade_to_black", "whip_pan_flash",
        }),
        blacklist=frozenset({"fade_to_white"}),
        default_by_position={
            "hook_to_body":   "zoom_punch",      # caída en el rostro, no whip (rasgos)
            "body_to_body":   "crossfade",
            "body_to_climax": "zoom_punch",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── POLAR: hielo, expediciones, paisajes amplios ───
    # Aguanta drama agresivo. Whip pan sobre paisajes amplios = ASMR viral.
    "POLAR": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_white", "fade_to_black",
        }),
        blacklist=frozenset(),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",  # ← GANADORA
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── MARITIME_EXTERIOR: horizontes, mares, costa ───
    # Mismo perfil que POLAR (paisajes amplios aguantan whip).
    "MARITIME_EXTERIOR": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_white", "fade_to_black",
        }),
        blacklist=frozenset(),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",  # ← GANADORA
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── DESERT: paisajes áridos amplios, dunas, outback ───
    # Paisaje exterior. Aguanta whip pan sobre horizontes.
    "DESERT": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_white", "fade_to_black",
        }),
        blacklist=frozenset(),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── JUNGLE: vegetación densa, drama orgánico ───
    # Drama denso. fade_to_white rompe la oscuridad selvática.
    "JUNGLE": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_black",
        }),
        blacklist=frozenset({"fade_to_white"}),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── WILDERNESS: naturaleza salvaje, bosques, paisajes amplios ───
    # Tipo POLAR. Todo permitido.
    "WILDERNESS": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_white", "fade_to_black",
        }),
        blacklist=frozenset(),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── URBAN: ciudades, calles, figuras humanas ───
    # Tipo INTERIOR. Whip agresivo destroza rasgos en cierres cortos.
    "URBAN": TransitionProfileRules(
        whitelist=frozenset({
            "zoom_punch", "crossfade", "crossfade_micro",
            "fade_to_black", "whip_pan_flash",
        }),
        blacklist=frozenset({"fade_to_white"}),
        default_by_position={
            "hook_to_body":   "zoom_punch",
            "body_to_body":   "crossfade",
            "body_to_climax": "zoom_punch",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── INDUSTRIAL: fábricas, refinerías, maquinaria ───
    # Drama agresivo OK. fade_to_white rompe la atmósfera contaminada.
    "INDUSTRIAL": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_black",
        }),
        blacklist=frozenset({"fade_to_white"}),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── UNDERGROUND: cuevas, túneles, abismal ───
    # Tipo SUBMARINE. fade_to_white incompatible con oscuridad subterránea.
    "UNDERGROUND": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_black",
        }),
        blacklist=frozenset({"fade_to_white"}),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── AERIAL: tomas desde el aire, escala panorámica ───
    # Tipo POLAR. Paisaje amplio aguanta todo.
    "AERIAL": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_white", "fade_to_black",
        }),
        blacklist=frozenset(),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── SPACE: cosmos, planetas, vacío estelar ───
    # Tipo SUBMARINE. fade_to_white rompe la negrura cósmica.
    "SPACE": TransitionProfileRules(
        whitelist=frozenset({
            "whip_pan_flash", "zoom_punch", "crossfade",
            "crossfade_micro", "fade_to_black",
        }),
        blacklist=frozenset({"fade_to_white"}),
        default_by_position={
            "hook_to_body":   "whip_pan_flash",
            "body_to_body":   "crossfade",
            "body_to_climax": "whip_pan_flash",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),

    # ─── HISTORICAL: escenas de época, pinturas, archivos ───
    # Tipo INTERIOR conservador. Sin whip agresivo (rasgos / detalles).
    "HISTORICAL": TransitionProfileRules(
        whitelist=frozenset({
            "zoom_punch", "crossfade", "crossfade_micro",
            "fade_to_black",
        }),
        blacklist=frozenset({"fade_to_white", "whip_pan_flash"}),
        default_by_position={
            "hook_to_body":   "zoom_punch",
            "body_to_body":   "crossfade",
            "body_to_climax": "zoom_punch",
            "body_to_reveal": "zoom_punch",
            "intra_chapter":  "crossfade_micro",
        },
    ),
}


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def get_rules(art_profile: str) -> TransitionProfileRules:
    """Devuelve las reglas de transición para un art_profile. KeyError si no existe."""
    if art_profile not in TRANSITION_PROFILES:
        raise KeyError(f"art_profile sin reglas de transición: '{art_profile}'")
    return TRANSITION_PROFILES[art_profile]


def is_allowed(art_profile: str, transition_name: str) -> bool:
    """¿Esta transición está permitida para este art_profile?"""
    if not is_valid(transition_name):
        return False
    rules = get_rules(art_profile)
    return transition_name not in rules.blacklist


def get_default_transition(art_profile: str, position: str) -> str:
    """
    Devuelve el nombre de transición default para (art_profile, posición narrativa).

    Cascada de fallbacks:
      1. default_by_position del profile
      2. DEFAULT_TRANSITION global ("whip_pan_flash")
      3. "hard_cut" si todo falla (no debería pasar nunca)
    """
    if position not in NARRATIVE_POSITIONS:
        # Posición desconocida → usa default global si está permitido,
        # si no, hard_cut.
        rules = get_rules(art_profile)
        if DEFAULT_TRANSITION not in rules.blacklist:
            return DEFAULT_TRANSITION
        return "hard_cut"

    rules = get_rules(art_profile)
    candidate = rules.default_by_position.get(position)
    if candidate and is_valid(candidate) and candidate not in rules.blacklist:
        return candidate

    # Fallback al default global si está permitido
    if DEFAULT_TRANSITION not in rules.blacklist and is_valid(DEFAULT_TRANSITION):
        return DEFAULT_TRANSITION

    # Último recurso
    return "hard_cut"


def render_constraints_for_prompt(art_profile: str) -> str:
    """Texto plano con whitelist/blacklist para inyectar en user prompt (director futuro)."""
    rules = get_rules(art_profile)
    parts = [f"art_profile activo: {art_profile}"]
    if rules.whitelist:
        parts.append("Preferidas: " + ", ".join(sorted(rules.whitelist)))
    if rules.blacklist:
        parts.append("PROHIBIDAS (no devolver): " + ", ".join(sorted(rules.blacklist)))
    return " | ".join(parts)