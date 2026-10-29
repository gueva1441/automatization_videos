# MEDIDAS_CLIPS — los 8 clips de F52 medidos con ffmpeg (por modelo: NO es la hoja ciega)

Salida de `python lab/hyperframes/f52/medidas_clips.py`.

- **SSIM 1.º vs foto:** el primer cuadro contra la foto de arranque, en gris a 1280×720; 1 = idénticos.
- **SSIM último vs 1.º:** cuánto cambió la toma en 8 s; más bajo, más cambio.
- **Cortes:** cuadros con cambio de escena mayor a 0,4.
- **Congelados:** tramos de 0,5 s o más sin cambio.
- **Movimiento:** media y máximo de la diferencia entre cuadros seguidos, en escala 0–255.

| clip | modelo | SSIM 1.º vs foto | SSIM último vs 1.º | cortes (s) | congelados | mov. medio | mov. máx | audio |
|---|---|---|---|---|---|---|---|---|
| cap01_K | K Kling 4.0 | 0.9315 | 0.5258 | — | — | 0.72 | 1.45 | sí (se descarta) |
| cap01_S | S Seedance 2.5 | 0.5243 | 0.5103 | — | — | 1.92 | 2.89 | no |
| cap01_F | F FLUX 3 Max | 0.5149 | 0.5242 | — | — | 0.61 | 2.26 | no |
| cap01_G | G Gemini Omni Flash 1.1 | 0.8542 | 0.4508 | — | — | 2.69 | 5.09 | sí (se descarta) |
| cap07_K | K Kling 4.0 | 0.8687 | 0.3125 | — | — | 2.61 | 3.51 | sí (se descarta) |
| cap07_S | S Seedance 2.5 | 0.2721 | 0.206 | — | — | 3.92 | 5.47 | no |
| cap07_F | F FLUX 3 Max | 0.3255 | 0.1773 | — | — | 4.52 | 9.06 | no |
| cap07_G | G Gemini Omni Flash 1.1 | 0.6662 | 0.14 | — | — | 12.38 | 15.32 | sí (se descarta) |
