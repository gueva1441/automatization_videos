# Sincronía voz ↔ subtítulo — Orleans v2

Desfase = inicio de la palabra en los timestamps de ElevenLabs (los que usan los subtítulos) − inicio de la misma palabra según faster-whisper (modelo small) sobre el mismo audio. Positivo = el subtítulo llega tarde. Umbral: 150 ms.

| cap | palabras comparadas | mediana | p95 \|desfase\| | máx \|desfase\| | > 150 ms | 1.er Dialogue ASS vs timestamps |
|---|---|---|---|---|---|---|
| ch01 | 55 de 145 | +139 ms | 200 ms | 359 ms | 18 (33 %) | 0.12 s vs 0.12 s |
| ch02 | 7 de 409 | +79 ms | 60220 ms | 76060 ms | 2 (29 %) | 0.08 s vs 0.08 s |
| ch03 | 224 de 631 | +80 ms | 240 ms | 580 ms | 40 (18 %) | 0.10 s vs 0.10 s |
| ch04 | 152 de 449 | +80 ms | 190 ms | 560 ms | 26 (17 %) | 0.10 s vs 0.10 s |
| ch05 | 156 de 459 | +100 ms | 500 ms | 660 ms | 51 (33 %) | 0.08 s vs 0.08 s |
| ch06 | 144 de 389 | +139 ms | 319 ms | 679 ms | 51 (35 %) | 0.08 s vs 0.08 s |
| ch07 | 110 de 309 | +120 ms | 319 ms | 639 ms | 37 (34 %) | 0.08 s vs 0.08 s |

## Las 3 palabras con más desfase por cap

- ch01 · «Atrapados» @ 2.78 s: +359 ms
- ch01 · «quiso» @ 34.88 s: +260 ms
- ch01 · «nadie» @ 34.42 s: +219 ms
- ch02 · «del» @ 20.52 s: -76060 ms
- ch02 · «una» @ 2.74 s: -60220 ms
- ch02 · «desastre?» @ 96.82 s: +79 ms
- ch03 · «pero» @ 135.88 s: +580 ms
- ch03 · «hasta» @ 81.10 s: +480 ms
- ch03 · «apenas» @ 138.72 s: +460 ms
- ch04 · «presenciaron» @ 69.92 s: +560 ms
- ch04 · «hasta» @ 19.58 s: +500 ms
- ch04 · «con» @ 33.12 s: +440 ms
- ch05 · «abrió» @ 39.14 s: +660 ms
- ch05 · «los» @ 53.78 s: +660 ms
- ch05 · «terminaron» @ 96.16 s: +620 ms
- ch06 · «puede» @ 86.26 s: +679 ms
- ch06 · «les» @ 22.56 s: +599 ms
- ch06 · «son» @ 67.78 s: +539 ms
- ch07 · «resuenan» @ 48.72 s: +639 ms
- ch07 · «que» @ 68.08 s: +580 ms
- ch07 · «que» @ 16.88 s: +519 ms
