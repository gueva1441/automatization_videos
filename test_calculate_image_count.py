"""Test offline de la fórmula adaptativa contra los caps de Pripyat."""
from script_engine.m03_visual import _calculate_image_count

# Esperados con MAX_IMAGES_FLUX=12 (Pripyat, fórmula adaptativa post-handoff)
# Fórmula: base = chars/150 + bonus_position + bonus_long, clamped [6, 12]
caps = [
    (2, 1675, 12),    # base 11 + 1 first_third = 12 (no clampea)
    (3, 1869, 12),    # base 12 + 0 middle + 2 long = 14 → clamped 12
    (4, 1755, 12),    # base 12 + 0 middle = 12 (no clampea)
    (5, 1557, 10),    # base 10 + 0 middle = 10 (no clampea)
    (6, 1927, 12),    # base 13 + 1 last_third + 2 long = 16 → clamped 12
]

print(f"{'cap':<5}{'chars':<8}{'old':<6}{'new':<6}{'esperado':<10}")
print("-" * 35)
for cap_n, chars, expected in caps:
    # Simular un texto de N chars
    text = "a" * chars
    n = _calculate_image_count(text, chapter_number=cap_n, total_chapters=7)
    old = max(7, min(10, round(chars / 200)))
    flag = "OK" if abs(n - expected) <= 1 else "WARN"
    print(f"  {cap_n:<3}{chars:<8}{old:<6}{n:<6}{expected:<10}{flag}")

# Validaciones extra
print()
print("Validaciones:")
# Cap muy corto (chars=600): MIN piso
n_min = _calculate_image_count("a" * 600, chapter_number=4, total_chapters=7)
print(f"  cap corto (600 chars, middle):  {n_min} imgs  (esperado >=6)")
assert n_min >= 6

# Cap muy largo (chars=3000): MAX techo
n_max = _calculate_image_count("a" * 3000, chapter_number=6, total_chapters=7)
print(f"  cap muy largo (3000 chars, last_third): {n_max} imgs  (esperado=12)")
assert n_max == 12

# Sin chapter_number: sin bonus
n_no_pos = _calculate_image_count("a" * 1500)
print(f"  sin chapter_number (1500 chars): {n_no_pos} imgs  (esperado 10, sin bonus)")
assert n_no_pos == 10

print("\nTodos los asserts pasaron.")
