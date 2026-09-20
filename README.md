# LTX Video API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/lightricks/ltx-2.5-pro?utm_source=github&utm_medium=ugc&utm_campaign=ltx-video&utm_content=readme-badge&utm_term=tier-a)

LTX Video is Lightricks' family of diffusion-transformer video models, and LTX-2.5 Pro is the current generation: it animates a still image into a clip with synchronised audio, optional camera moves and a chosen duration, resolution and frame rate. This package is a Python client for the LTX API hosted on Synexa, so `pip install` and one `run()` call turn an image URL and a prompt into a finished video file.

The client gives you a blocking `run()` that returns when the clip is ready, a submit-and-poll mode for long renders, webhook delivery on completion, and typed errors for failed or timed-out predictions. Its only dependency is `httpx`. It is built for product teams, content pipelines and researchers who want LTX output in a service without running a video-generation stack themselves.

> **Try it now:** [https://synexa.ai/explore/lightricks/ltx-2.5-pro](https://synexa.ai/explore/lightricks/ltx-2.5-pro?utm_source=github&utm_medium=ugc&utm_campaign=ltx-video&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About LTX Video](#about-ltx-video)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **Video models do not fit on ordinary GPUs.** The LTX-2 generation is far larger than the original 2B LTX-Video and needs tens of gigabytes of VRAM at production resolutions. The hosted endpoint runs on datacenter cards; you never touch CUDA.
- **No pipeline assembly.** Self-hosting means the DiT checkpoint, text encoder, VAE, audio components and a compatible PyTorch build, kept in sync across upgrades. Here the whole setup is `pip install` and an API key.
- **No cold start.** Loading a multi-gigabyte video model takes minutes on a fresh instance; the hosted model stays resident.
- **Per-clip pricing.** Image-to-video is $0.12 per run and audio-to-video is $0.17 per run, with no hourly GPU charge, so a project that renders ten clips a day pays for ten clips.

## Installation

```bash
pip install git+https://github.com/ltx-video/ltx-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=ltx-video&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import ltx_api

output = ltx_api.run({
    "image_url": "https://example.com/input.png",
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from ltx_api import Client

client = Client(api_key="sk-...")
output = client.run({"image_url": "https://example.com/input.png", "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`lightricks/ltx-2.5-pro`](https://synexa.ai/explore/lightricks/ltx-2.5-pro?utm_source=github&utm_medium=ugc&utm_campaign=ltx-video&utm_content=readme-models&utm_term=tier-a) | image-to-video | LTX-2.5 Pro animates a still image into video with synchronised audio and optional camera moves. | $0.12 |
| [`lightricks/ltx-2.5-audio-to-video`](https://synexa.ai/explore/lightricks/ltx-2.5-audio-to-video?utm_source=github&utm_medium=ugc&utm_campaign=ltx-video&utm_content=readme-models&utm_term=tier-a) | audio-to-video | LTX-2.5 Pro generates video timed to a supplied audio track, optionally starting from an image. | $0.17 |

The default model is **`lightricks/ltx-2.5-pro`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `lightricks/ltx-2.5-pro`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | First frame of the video (.jpg/.png/.webp) |
| `end_image_url` | file | no | — | — | Optional last frame (.jpg/.png/.webp). When set, the clip becomes a transition between the two frames |
| `prompt` | string | yes | `The subject turns slowly toward the came…` | — | The prompt to use for the generated video |
| `duration` | string | no | `auto` | 6, 8, 10, auto | The duration of the generated video in seconds. Set to 'auto' to let the model choose the duration automatically. |
| `resolution` | string | no | `1080p` | 720p, 1080p | The resolution of the generated video. |
| `aspect_ratio` | string | no | `auto` | auto, 16:9, 9:16 | The aspect ratio of the generated video. If 'auto', the aspect ratio will be determined automatically based on the input image. |
| `fps` | integer | no | `25` | 24, 25, 50 | The frames per second of the generated video. One of: 24, 25, 50 |
| `generate_audio` | boolean | no | `True` | — | Whether to generate audio for the generated video |
| `camera_motion` | string | no | — | dolly_in, dolly_out, dolly_left, dolly_right, jib_up, jib… | Optional camera motion applied to the generated video. |

### `lightricks/ltx-2.5-audio-to-video`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `audio_url` | file | yes | — | — | Audio that sets the timing (.mp3/.wav/.flac/.m4a/.ogg). 2-20 seconds; the Pro tier caps it at 10 |
| `image_url` | file | no | — | — | Optional first frame (.jpg/.png/.webp). Without it, prompt is required |
| `prompt` | string | no | — | — | Text description of how the video should be generated. Required if image_url is not provided. When image_url is provided, this describes how the image should be animated. |
| `guidance_scale` | number | no | — | 1, 50 | Guidance scale for video generation. Higher values make the output more closely follow the prompt. Defaults to 5 for text-to-video, or 9 when providing an image. |
| `aspect_ratio` | string | no | `auto` | auto, 16:9, 9:16 | The aspect ratio of the generated video. If 'auto', the aspect ratio will be determined automatically based on the input image, or defaults to 16:9 if no image is provided. |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from ltx_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About LTX Video

LTX Video (LTX-Video) is a family of open video generation models from Lightricks, the company behind Facetune and Videoleap. The first release, in November 2024, was a 2-billion-parameter diffusion transformer that generated video faster than real time on a single datacenter GPU by working in a heavily compressed spatiotemporal latent space, with a VAE that both decodes latents and performs the final denoising step. Code and weights are published in the [Lightricks/LTX-Video](https://github.com/Lightricks/LTX-Video) repository under an open licence.

LTX-2, released in late 2025, moved the family to a much larger model that generates video and audio jointly rather than bolting sound on afterwards, which is why lip movement, footsteps and ambient sound line up with the picture. LTX-2.5 continues that line. The Pro tier served here supports text-guided image-to-video, first-and-last-frame transitions, a choice of 24, 25 or 50 fps, several output resolutions and aspect ratios (or `auto` to follow the input image), an optional camera-motion preset, and a `generate_audio` switch.

Two hosted endpoints are available through this client. `lightricks/ltx-2.5-pro` (the default) animates an `image_url` according to a `prompt`, optionally towards an `end_image_url`. `lightricks/ltx-2.5-audio-to-video` times the video to an `audio_url` of 2–20 seconds (10 on the Pro tier), starting from an optional image. Both return a video URL. Clips are short by design (seconds, not minutes), and the model works best when the prompt describes motion and camera behaviour rather than restating what is already visible in the input frame.

The endpoints used by this client are `lightricks/ltx-2.5-pro` and `lightricks/ltx-2.5-audio-to-video`, which are Lightricks' own LTX-2.5 Pro model served on Synexa. The open LTX-Video and LTX-2 weights, and the reference inference code, are available in the official repository if you want to self-host an earlier generation.

**Official project:** https://github.com/Lightricks/LTX-Video

## Use cases

- **Animate product photos for ads** — call `run({"image_url": hero_shot, "prompt": "slow push-in, soft studio lighting", "camera_motion": ...})` and get a five-second clip with ambient sound for each SKU.
- **Transitions between two keyframes** — pass `image_url` and `end_image_url` and the model renders the motion between them, useful for storyboard-to-animatic workflows.
- **Music-driven visuals** — send a 10-second `audio_url` to `lightricks/ltx-2.5-audio-to-video` with a prompt describing the scene and the cuts and motion follow the beat.
- **Talking-head or voiceover clips** — combine a portrait `image_url` with a speech `audio_url` on the audio-to-video endpoint so mouth movement is timed to the track.
- **Social-media batch rendering** — loop over a folder of stills, submit each with `wait=False` and a `webhook`, and let your server collect the URLs as they finish.
- **Previsualisation in film and game pipelines** — turn concept frames into moving shots at 24 fps and try several `camera_motion` presets to settle the camera language before committing to a full render.

## FAQ

**Is there an LTX Video API?**

Lightricks publishes LTX-Video as open weights and offers its own hosted products; this package is an independent Python client for the `lightricks/ltx-2.5-pro` and `lightricks/ltx-2.5-audio-to-video` endpoints hosted on Synexa, which serve LTX-2.5 Pro behind an HTTPS API.

**How much does the LTX Video API cost?**

Image-to-video with `lightricks/ltx-2.5-pro` is $0.12 per run; audio-to-video with `lightricks/ltx-2.5-audio-to-video` is $0.17 per run. Billing is per prediction with no idle charge. New Synexa accounts get a free trial credit.

**Can I run LTX Video without a GPU?**

Yes. This client sends the request to Synexa's GPUs and returns a video URL; your machine needs only Python 3.8+ and `httpx`. Running LTX-2 locally requires a high-memory CUDA GPU and the full inference stack from the official repository.

**Does this client work with the Lightricks/LTX-Video repo or ComfyUI?**

No. It does not load local checkpoints or ComfyUI graphs. It is a thin HTTP client for the hosted endpoints; if you need the LTX-Video ComfyUI nodes, LoRAs or offline inference, use the official repository.

**What input formats does it accept?**

`image_url` and `end_image_url` accept publicly reachable `.jpg`, `.png` or `.webp` URLs. `audio_url` accepts `.mp3`, `.wav`, `.flac`, `.m4a` or `.ogg` of 2–20 seconds (10 seconds on the Pro tier). `prompt` is a string, `duration` is seconds or `auto`, `fps` is 24, 25 or 50. Output is a URL to an MP4.

**Is this the official LTX Video SDK?**

No. This is an independent, MIT-licensed client and is not affiliated with Lightricks. The official project is at https://github.com/Lightricks/LTX-Video.

## Related

- [Lightricks/LTX-Video](https://github.com/Lightricks/LTX-Video) — official open weights, inference code and ComfyUI integration.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client for every model on the platform.
- [lightricks/ltx-2.5-audio-to-video](https://synexa.ai/explore/lightricks/ltx-2.5-audio-to-video) — the audio-timed sibling endpoint, also supported by this client.
- [zsxkib/mmaudio](https://synexa.ai/explore/zsxkib/mmaudio) — add a synthesised soundtrack to a video that was rendered without audio.
- [bytedance/seedvr2-upscale](https://synexa.ai/explore/bytedance/seedvr2-upscale) — upscale the first frame before animating it.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of LTX Video. Model weights and trademarks belong to their respective owners.
