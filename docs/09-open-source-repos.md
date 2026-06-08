# 09 — The Open-Source Repos (and how to run them FREE, no GPU)

You asked for "the repo that does it." Here are the real open-source repos that
edit a photo of your house to add a second floor — and, more importantly, the
**free hosted versions** so you don't need a GPU or any setup.

> ⚠️ This Claude sandbox has **no GPU** (4 CPUs / 15 GB RAM), so these can't run
> *here*. They run great on the free hosted demos below, or on a free GPU (Colab).

## The repos (open source)

| Repo | What it is | Link |
|------|-----------|------|
| **Qwen-Image-Edit** (2511) | Free, open-source instruction image editor; "geometric reasoning" — best open rival to Nano Banana | https://github.com/QwenLM/Qwen-Image · weights: https://huggingface.co/Qwen/Qwen-Image-Edit-2511 |
| **FLUX.1 Kontext [dev]** | 12B open-weight image editor by Black Forest Labs | https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev |
| **ComfyUI** | Node-based UI that runs both of the above with ready workflows | https://github.com/comfyanonymous/ComfyUI |

## ✅ Easiest: run the repo FREE in your browser (no GPU, no install)

These are the actual open-source models hosted as free demos — upload your photo,
type the instruction, get the edit:

1. **Qwen-Image-Edit 2511 (free):** https://huggingface.co/spaces/Qwen/Qwen-Image-Edit-2511
2. **Qwen-Image-Edit Fast (free):** https://huggingface.co/spaces/multimodalart/Qwen-Image-Edit-Fast
3. **Qwen Chat (free):** https://chat.qwen.ai — attach photo, ask for the edit.
4. **Google "Nano Banana" / Gemini (free):** https://gemini.google.com (closed-source but the strongest free option).

**Steps:** open a link → upload your front photo → paste a prompt from
[docs/08](08-photoreal-render-howto.md) → download the result → iterate.

## Run it yourself on a FREE GPU (Google Colab)

If you want to batch many variations or use the open weights directly:

1. Open Google Colab → Runtime → **change runtime to a free T4 GPU**.
2. Install + run FLUX.1 Kontext via 🤗 diffusers:

```python
# Colab (free T4 GPU). FLUX.1-Kontext-dev is gated: accept the license on its
# HF page and run `huggingface-cli login` with your free token first.
!pip -q install -U diffusers transformers accelerate sentencepiece
import torch
from diffusers import FluxKontextPipeline
from diffusers.utils import load_image

pipe = FluxKontextPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-Kontext-dev", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()          # fits in free-tier VRAM

img = load_image("my_house_front.jpg")   # upload your photo to the Colab files
prompt = ("Add a realistic second floor on top of the existing flat roof, set "
          "back ~8-10 ft from the front, same white-stucco modern style, "
          "black-framed glass, thin flat roof, wood accent, glass-railed balcony. "
          "Keep the ground floor, driveway, landscaping and camera angle unchanged. "
          "Photorealistic architectural photo, natural light.")
out = pipe(image=img, prompt=prompt, guidance_scale=2.5,
           num_inference_steps=28).images[0]
out.save("house_two_story.png")
```

(For **Qwen-Image-Edit**, the QwenLM/Qwen-Image GitHub README has an equivalent
`diffusers` snippet; it's not gated, but the 20B model wants ~24 GB VRAM, so the
hosted Space above is the easier route.)

## Pay-per-image API (cheapest "just works", cents per render)
- **Replicate — FLUX Kontext:** https://replicate.com/black-forest-labs/flux-kontext-pro
- **fal.ai — FLUX Kontext:** https://fal.ai/flux-kontext

## Recommendation
Start with the **Qwen-Image-Edit 2511 free Space** or **Gemini**. Zero setup,
free, and it's the same tech as the repos. Only move to Colab/Replicate if you
want bulk variations or scripted control.
