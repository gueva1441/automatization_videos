# Sincronía voz ↔ subtítulo — Orleans v2

Desfase = inicio de la palabra en los timestamps de ElevenLabs (los que usan los subtítulos) − inicio de la misma palabra según faster-whisper (modelo small) sobre el mismo audio. Positivo = el subtítulo llega tarde. Umbral: 150 ms.

| cap | palabras comparadas | mediana | p95 \|desfase\| | máx \|desfase\| | > 150 ms | 1.er Dialogue ASS vs timestamps |
|---|---|---|---|---|---|---|
| ch01 | 38 de 66 | +100 ms | 480 ms | 520 ms | 13 (34 %) | 0.18 s vs 0.18 s |
| ch02 | 102 de 158 | +100 ms | 240 ms | 520 ms | 20 (20 %) | 0.10 s vs 0.10 s |
| ch03 | 126 de 179 | +100 ms | 240 ms | 480 ms | 28 (22 %) | 0.10 s vs 0.10 s |
| ch04 | 134 de 197 | +100 ms | 320 ms | 540 ms | 32 (24 %) | 0.10 s vs 0.10 s |
| ch05 | 137 de 201 | +100 ms | 499 ms | 820 ms | 33 (24 %) | 0.10 s vs 0.10 s |
| ch06 | 133 de 193 | +100 ms | 300 ms | 1040 ms | 30 (23 %) | 0.08 s vs 0.08 s |
| ch07 | 106 de 164 | +100 ms | 420 ms | 740 ms | 25 (24 %) | 0.14 s vs 0.14 s |

## Las 3 palabras con más desfase por cap

- ch01 · «que» @ 27.94 s: +520 ms
- ch01 · «estaba» @ 28.98 s: +500 ms
- ch01 · «fue» @ 17.68 s: +480 ms
- ch02 · «confirmó» @ 9.58 s: +520 ms
- ch02 · «también» @ 66.78 s: +520 ms
- ch02 · «recaía» @ 62.78 s: +440 ms
- ch03 · «cambió» @ 56.46 s: +480 ms
- ch03 · «llegó» @ 61.76 s: +460 ms
- ch03 · «avanzaba» @ 74.94 s: +380 ms
- ch04 · «estaba» @ 79.88 s: +540 ms
- ch04 · «Durante» @ 30.52 s: +520 ms
- ch04 · «¿Dónde» @ 89.50 s: -480 ms
- ch05 · «mil» @ 99.02 s: +820 ms
- ch05 · «Entre» @ 52.82 s: +660 ms
- ch05 · «declaró» @ 69.12 s: +580 ms
- ch06 · «inició» @ 46.80 s: +1040 ms
- ch06 · «Esta» @ 30.62 s: +620 ms
- ch06 · «chocaron» @ 79.62 s: +560 ms
- ch07 · «fue» @ 60.14 s: +740 ms
- ch07 · «Ante» @ 54.08 s: +740 ms
- ch07 · «¿Saldrá» @ 73.66 s: -580 ms
