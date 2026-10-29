# SCHEMAS_F52 — schemas y precios leídos de fal antes de llamar

Salida de `python lab/hyperframes/f52/schemas_f52.py` (solo GET: OpenAPI de `fal.ai/api/openapi/queue/openapi.json?endpoint_id=…` y precio de `api.fal.ai/v1/models/pricing?endpoint_id=…`).

## K — `kling/v4/image-to-video`

Schema de entrada `V4ImageToVideoInput`:

| campo | req | tipo | default | enum / rango | descripción |
|---|---|---|---|---|---|
| `multi_prompt` |  | ['array', 'null'] | null |  | Per-shot prompts for multi-shot generation. The video duration is the sum of the shot durations. |
| `resolution` |  | string | "1080p" | ['720p', '1080p'] | Output resolution. |
| `start_image_url` | sí | string | null |  | Image to use as the first frame of the video.

Max file size: 30.0MB, Min width: 300px, Min height: 300px, Min aspect ratio: 0.40, Max aspect ratio: 2.50, Timeo |
| `middle_image_urls` |  | ['array', 'null'] | null |  | Ordered keyframes between the first and last frames (max 8). |
| `duration` |  | integer | 5 | 3–30 | Video duration in seconds (3-30). |
| `end_image_url` |  | ['string', 'null'] | null |  | Image to use as the last frame of the video. |
| `prompt` |  | ['string', 'null'] | null |  | Text prompt. Either prompt or multi_prompt must be provided. |

Precio (HTTP 200): `{"prices": [{"endpoint_id": "kling/v4/image-to-video", "unit_price": 0.157, "unit": "seconds", "currency": "USD"}], "next_cursor": null, "has_more": false}`

## S — `bytedance/seedance-2.5/image-to-video`

Schema de entrada `Seedance25ImageToVideoInput`:

| campo | req | tipo | default | enum / rango | descripción |
|---|---|---|---|---|---|
| `duration` |  | string | "auto" | ['auto', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30'] | Duration of the video in seconds. Supports 4 to 30 seconds, or auto to let the model decide based on the prompt. |
| `resolution` |  | string | "720p" | ['480p', '720p', '1080p'] | Video resolution - 480p for faster generation, 720p for balance, 1080p for high quality. |
| `prompt` |  | ['string', 'null'] | null |  | The text prompt describing the desired motion and action for the video. |
| `aspect_ratio` |  | string | "auto" |  | The aspect ratio of the generated video. Always "auto" for image-to-video |
| `codec` |  | string | "auto" | ['auto', 'H264', 'H265'] | 'auto' retains default video codec behaviour; 'H264' uses H.264; 'H265' uses H.265. |
| `image_url` | sí | string | null |  | The URL of the starting frame image to animate. Supported formats: JPEG, PNG, WebP, BMP, TIFF, GIF, HEIC, HEIF. Max 30 MB. |
| `end_user_id` |  | ['string', 'null'] | null |  | The unique user ID of the end user. |
| `end_image_url` |  | ['string', 'null'] | null |  | The URL of the image to use as the last frame of the video. When provided, the generated video will transition from the starting image to this ending image. Sup |
| `draft` |  | boolean | false |  | Generate a draft preview at 480p, overriding resolution. Returns a draft_id for completing the draft at 1080p within seven days. |
| `bitrate_mode` |  | string | "standard" | ['standard', 'high'] | Output bitrate mode. 'high' requests a higher-quality, larger-file encode from the model; 'standard' uses the default bitrate. |
| `generate_audio` |  | boolean | true |  | Whether to generate synchronized audio for the video, including sound effects, ambient sounds, and lip-synced speech. The cost of video generation is the same r |

Precio (HTTP 200): `{"prices": [{"endpoint_id": "bytedance/seedance-2.5/image-to-video", "unit_price": 0.0214, "unit": "1000 tokens", "currency": "USD"}], "next_cursor": null, "has_more": false}`

## F — `blackforestlabs/flux-3-max/image-to-video`

Schema de entrada `Flux3MaxImageToVideoInput`:

| campo | req | tipo | default | enum / rango | descripción |
|---|---|---|---|---|---|
| `end_image_url` |  | ['string', 'null'] | null |  | Optional URL of the image used as the last frame of the video (PNG, JPEG, or WebP). |
| `aspect_ratio` |  | string | "auto" | ['auto', '21:9', '2:1', '16:9', '4:3', '1:1', '3:4', '9:16'] | Aspect ratio of the generated video. `auto` uses 16:9 for text prompts and follows the first image otherwise. |
| `generate_audio` |  | boolean | true |  | Whether to generate audio for the video. |
| `image_url` | sí | string | null |  | URL of the image the video starts from (PNG, JPEG, or WebP). |
| `seed` |  | ['integer', 'null'] | null |  | The seed to use for the generation. Random when not provided. |
| `resolution` |  | string | "720p" | ['720p', '1080p'] | Resolution of the generated video. |
| `reasoning_level` |  | string | "high" | ['low', 'high'] | How much effort the harness spends reasoning about the given prompt. Higher reasoning effort means slower generation time. |
| `prompt` | sí | string | null |  | The text prompt describing how the video unfolds from the image. |
| `duration` |  | integer | 5 | [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] | Duration of the generated video in seconds. |

Precio (HTTP 200): `{"prices": [{"endpoint_id": "blackforestlabs/flux-3-max/image-to-video", "unit_price": 0.02125, "unit": "seconds", "currency": "USD"}], "next_cursor": null, "has_more": false}`

## G — `google/gemini-omni-flash/v1.1/image-to-video`

Schema de entrada `GeminiOmniFlashV11ImageToVideoInput`:

| campo | req | tipo | default | enum / rango | descripción |
|---|---|---|---|---|---|
| `image_url` | sí | string | null |  | URL of the first frame to animate. |
| `resolution` |  | string | "720p" | ['360p', '720p', '1080p', '4k'] | The resolution of the generated video. |
| `duration` |  | integer | 8 | 3–10 | The duration of the generated video, in seconds. |
| `aspect_ratio` |  | string | "16:9" | ['16:9', '9:16'] | The aspect ratio of the generated video. |
| `prompt` | sí | string | null |  | The text prompt describing how the first image should be animated or interpolated into the optional end image. |
| `end_image_url` |  | ['string', 'null'] | null |  | Optional URL of the end frame. When provided, the model interpolates between the two images in their listed order. |

Precio (HTTP 200): `{"prices": [{"endpoint_id": "google/gemini-omni-flash/v1.1/image-to-video", "unit_price": 0.03, "unit": "seconds", "currency": "USD"}], "next_cursor": null, "has_more": false}`

## seedream — `fal-ai/bytedance/seedream/v5/lite/text-to-image`

Schema de entrada `BytedanceSeedreamV5LiteTextToImageInput`:

| campo | req | tipo | default | enum / rango | descripción |
|---|---|---|---|---|---|
| `output_format` |  | string | "jpeg" | ['jpeg', 'png'] | The file format of the generated images. |
| `enable_safety_checker` |  | boolean | true |  | If set to true, the safety checker will be enabled. Disabling it requires account authorization; unauthorized requests are always checked. |
| `sequential_image_generation` |  | ['string', 'null'] | null | ['auto', 'disabled'] | Generate related images with `auto`, or one image per generation with `disabled`. When omitted, values of `max_images` above one enable `auto`. |
| `max_images` |  | integer | 1 | 1–15 | Maximum images per generation in sequential mode. Ignored when sequential generation is disabled. Combined input references and outputs per generation cannot ex |
| `image_size` |  | [None, 'string'] | "auto_2K" | ['square_hd', 'square', 'portrait_4_3', 'portrait_16_9', 'landscape_4_3', 'landscape_16_9', 'auto_2K', 'auto_3K', 'auto_4K'] | The size of the generated image. Custom dimensions within the provider's pixel and aspect limits are sent unchanged. Other sizes use compatible scaling. The pro |
| `num_images` |  | integer | 1 | 1–6 | Number of separate model generations to be run with the prompt. |
| `return_byteplus_urls` |  | boolean | false |  | If set to true returns seedance-2 trusted URLs. Please note these urls expire in 24 hours. |
| `prompt` | sí | string | null |  | The text prompt used to generate the image |
| `watermark` |  | boolean | false |  | Whether to add the provider's visible watermark. |
| `sync_mode` |  | boolean | false |  | If `True`, the media will be returned as a data URI and the output data won't be available in the request history. |

Precio (HTTP 200): `{"prices": [{"endpoint_id": "fal-ai/bytedance/seedream/v5/lite/text-to-image", "unit_price": 0.035, "unit": "images", "currency": "USD"}], "next_cursor": null, "has_more": false}`

