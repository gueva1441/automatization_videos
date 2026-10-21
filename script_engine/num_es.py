"""
script_engine/num_es.py — Números en palabras (español), sin dependencias. F5: lo usan las métricas del juez
(«6,500» ↔ «seis mil quinientas») y el normalizer (horas, dólares, porcentajes) para TTS.

    words(n, fem=False)    entero 0–999.999.999 → palabras («quinientas», «veintiuna», «un millón»)
    variants(text_num)     las formas en que la voz puede decir una cifra escrita («6,500» → dígitos y palabras)
    hour_words(h, m, ampm) «6:10 AM» → «seis y diez de la mañana»
"""
from __future__ import annotations

import re

_U = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce",
      "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno",
      "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho",
      "veintinueve"]
_D = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"}
_C = {100: "ciento", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos", 500: "quinientos",
      600: "seiscientos", 700: "setecientos", 800: "ochocientos", 900: "novecientos"}


def _fem(s: str) -> str:
    s = re.sub(r"ientos\b", "ientas", s)
    s = re.sub(r"\bquinientos\b", "quinientas", s)
    s = re.sub(r"\bveintiuno\b", "veintiuna", s)
    return re.sub(r"\buno\b", "una", s)


def _lt1000(n: int) -> str:
    if n < 30:
        return _U[n]
    if n < 100:
        d, u = divmod(n, 10)
        return _D[d * 10] + (f" y {_U[u]}" if u else "")
    if n == 100:
        return "cien"
    c, r = divmod(n, 100)
    return _C[c * 100] + (f" {_lt1000(r)}" if r else "")


def words(n: int, fem: bool = False) -> str:
    if n < 0:
        return "menos " + words(-n, fem)
    if n < 1000:
        s = _lt1000(n)
    elif n < 1_000_000:
        k, r = divmod(n, 1000)
        head = "mil" if k == 1 else re.sub(r"\buno$", "un", _lt1000(k)) + " mil"
        s = head + (f" {_lt1000(r)}" if r else "")
        if fem:                                     # «quinientas mil personas», «seis mil quinientas almas»
            return _fem(s) if k != 1 else "mil" + (f" {_fem(_lt1000(r))}" if r else "")
    else:
        m, r = divmod(n, 1_000_000)
        head = "un millón" if m == 1 else re.sub(r"\buno$", "un", words(m)) + " millones"
        s = head + (f" {words(r, fem)}" if r else "")
        return s
    return _fem(s) if fem else s


def parse_int(text_num: str) -> int | None:
    """«6,500» / «6.500» / «6500» → 6500 (un decimal tipo «4.6» → None)."""
    t = text_num.strip()
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", t) or re.fullmatch(r"\d+", t):
        return int(re.sub(r"[.,]", "", t))
    return None


def variants(text_num: str) -> list[str]:
    """Formas en que la voz puede decir la cifra: dígitos con y sin separador y en palabras (masc. y fem.)."""
    n = parse_int(text_num)
    out = {text_num}
    if n is not None:
        out |= {str(n), f"{n:,}", f"{n:,}".replace(",", "."), words(n), words(n, fem=True)}
        if 1900 <= n <= 2099:                        # años: solo dígitos y palabras masculinas
            out = {str(n), words(n)}
    return [x for x in out if x]


def hour_words(h: int, m: int, ampm: str | None = None) -> str:
    """«6:10 AM» → «seis y diez de la mañana»; «21:00» → «las veintiuna» (sin AM/PM, 24 h documental)."""
    if ampm:
        a = ampm.lower().replace(".", "")
        hh = h % 12 or 12
        if a == "am":
            part = "de la noche" if h % 12 == 0 else "de la mañana"            # 12:xx AM = medianoche
        else:
            part = "del mediodía" if h % 12 == 0 else "de la tarde" if hh < 8 else "de la noche"
        hw = "una" if hh == 1 else words(hh)
        mins = "" if m == 0 else (" y media" if m == 30 else " y cuarto" if m == 15 else f" y {words(m)}")
        return f"{hw}{mins} {part}"
    hw = "una" if h == 1 else ("veintiuna" if h == 21 else words(h))
    if m == 0:
        return f"las {hw}"
    return f"las {hw} y media" if m == 30 else f"las {hw} y {words(m)}"
