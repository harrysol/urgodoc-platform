# 08 — How to Get a REALISTIC Second-Floor Render (the right way)

Box/massing models (matplotlib, Blender) show *volume*, not realism. To get an
image that looks like a real photo of **your** house with a second floor, edit
the **actual photo** with an AI image model. This is what works in 2025–26.

## Best tools (in order)

1. **Google "Nano Banana" (Gemini 3 Pro Image)** — best for editing a real house
   photo. **Free** in the [Gemini app](https://gemini.google.com) or
   [Google AI Studio](https://aistudio.google.com). Keeps your real house, adds
   the second story photorealistically.
2. **ChatGPT (image editing)** — upload photo + prompt; very easy.
3. **Stable Diffusion + ControlNet (img2img)** — most control; locks the existing
   structure via depth/canny. Power-user route (r/StableDiffusion).

## Step-by-step (Nano Banana / Gemini — free)

1. Go to the Gemini app or AI Studio. Start an image chat.
2. **Upload your front photo** (the clean straight-on front shot of the house).
3. Paste the **prompt below**.
4. Generate. Then refine with follow-ups ("make the second floor lower",
   "more glass on the front", "show it at sunset", "add a rooftop terbalcony").
5. Repeat for the **bay/rear view** photo with the second prompt.

## Paste-ready prompt — FRONT view

> Using this photo of my single-story white house, add a realistic **second
> floor on top of the existing flat roof**. Keep the existing ground floor, white
> stucco walls, black-framed windows, the column-screen entry, circular paver
> driveway, landscaping, sky and the exact camera angle and perspective unchanged.
> The new second story should sit on the flat roof, **set back about 8–10 ft from
> the front facade**, in the same modern tropical white-stucco style: floor-to-
> ceiling black-framed impact windows, a thin flat roof with a slim dark fascia,
> a warm wood-accent panel, and a glass-railed balcony. Match the daylight,
> shadows and perspective so it looks like a real photograph. Photorealistic,
> architectural photography, natural lighting, high detail.

## Paste-ready prompt — BAY / REAR view (the money shot)

> Using this waterfront photo, add a realistic **second floor** to the house that
> opens toward the bay. Keep the pool, deck, seawall, water, palms and camera
> angle unchanged. The second story should have a large **west-facing primary-
> suite terrace with a glass railing** and floor-to-ceiling black-framed glass to
> capture the open-bay sunset views, in the same white-stucco modern style with a
> thin flat roof and a wood accent. Golden-hour lighting, photorealistic,
> architectural photography.

## Tips that matter (from people who do this)

- **One change at a time.** Add the second floor first; *then* refine details in
  follow-up prompts. Big multi-change prompts drift.
- **Feed it a clean, straight-on, well-lit photo.** Better input = better output.
- **Lock identity:** tell it explicitly to keep the ground floor, driveway,
  windows and angle "unchanged." That's what keeps it looking like *your* house.
- **Iterate cheaply.** Generate 5–10, keep the 2 best. It's free in Gemini.
- **Optional pro step:** if you want exact proportions, feed a SketchUp/Blender
  3D screenshot into the same tool as a guide image ("match this massing, make it
  photorealistic"). That's the only place a 3D model helps here.

## Then what
Take the 2–3 best images to the architect ([docs/04](04-architect-shortlist.md))
as your concept. They turn it into the **signed/sealed permit set** — the part AI
cannot do. See [docs/05](05-ai-3d-rendering-guide.md) and [docs/06](06-budget-timeline-process.md).
