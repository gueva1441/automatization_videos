# F50 C — prueba del clip Veo (1 llamada, 4 s)

- Endpoint: `https://queue.fal.run/fal-ai/veo3.1/lite/image-to-video`.
- Imagen: `output\123bbb64-9fca-4395-8bf4-57d60e219ef1\assets\ch01_veo\ch01_img_01.png` (el primer cuadro de hoy del cap 1).
- Payload (sin la imagen): `{"prompt": "The camera performs a very slow, subtle push-in, drawing closer to the unsettling details of the bandaged foot. As fine particles of red and grey dust drift across the ground, a single loose thread on the crude bandage flutters gently in a faint, imperceptible breeze.", "image_url": "data:image/png;base64,/9j/4AAQSkZJRgABAQ…", "negative_prompt": "text, subtitles, captions, watermark, logo, morphing faces, distorted hands, extra limbs, people entering the frame, sudden lighting change, camera shake, fast cuts, cartoon, CGI look", "duration": "4s", "generate_audio": false, "resolution": "1080p"}`.
- Respuesta del envío: HTTP 200 `{"status":"IN_QUEUE","request_id":"01a1833c-5ab1-7cd2-8e90-c3f62a78cbf7","response_url":"https://queue.fal.run/fal-ai/veo3.1/requests/01a1833c-5ab1-7cd2-8e90-c3…` · 32 consultas de estado.
- Resultado: HTTP 200 `{"video":{"url":"https://v3b.fal.media/files/b/0ab03607/1hiZ_mWaocMUAsGs8MOiA_c0ffd7add7c14b4dbcb34e2f73d302e0.mp4","content_type":"video/mp4","file_name":"c0ffd7add7c14b4dbcb34e2f73d302e0.mp4","file_`.
- Estado: **ok** en 157.2 s. fal aceptó `negative_prompt` y `duration`.
- ffprobe de `veo_prueba.mp4`: duración **4.000000 s**, h264 1920×1080.
- Costo: US$ 0.24 en `cost_tracker` (video_id `f50-veo-prueba`; `track_fal` cobra la tarifa fija por clip de config, no mira la duración: el precio real de fal por un clip de 4 s no está medido).
