# 05 — AI & 3D Rendering: The DIY Concept Phase

This is where you actually save real money. You will **not** replace the licensed
architect/engineer, but you *can* show up with polished concept renderings and a
3D massing, so you pay them to engineer and stamp your vision — not to drag a
vague idea through ten billed revisions.

## What AI can and can't do (be honest with yourself)

| Task | AI can do it? |
|------|---------------|
| Photoreal exterior renderings from a photo of your house | ✅ Yes, today |
| "What would a second floor look like here" concept images | ✅ Yes |
| Interior style/mood exploration | ✅ Yes |
| Rough 3D massing model | ✅ Yes (sketch-to-3D tools) |
| Accurate, to-scale construction drawings | ⚠️ Not reliably / not permittable |
| **Signed & sealed permit set, HVHZ structural calcs** | ❌ No — licensed humans only |

## Recommended tools (2026)

**Easiest — render from a photo of your actual house:**
- **MyArchitectAI / ArchitectGPT / similar** — upload a photo of the house, prompt
  "add a modern second story," get photoreal variations. Best for showing family
  and architects "this is the vibe."

**Best image quality (style + detail):**
- **FLUX.1** family (Kontext Pro / Max, FLUX1.1 Pro) — top-rated 2026 models for
  architectural detail. Use via a hosted UI or API.

**Sketch / model → 3D:**
- **Kaedim** — 2D sketch → 3D volumetric model (good for early massing).
- **Archi (AI)** — takes sketches/2D/3D and builds a dimensioned 3D model + render.

**Free / open-source / full control:**
- **Blender** (free, open source) — build a simple 3D massing of the existing
  house + proposed second floor; add the **Dream Textures** / Stable Diffusion
  add-ons for AI texturing and style passes.
- **Stable Diffusion** (open source) — moodboards and style exploration.

## A repeatable workflow (do this in an afternoon)

1. **Capture** — take clear photos of the house: front, both sides, rear, roof.
2. **Massing** — in Blender (or Kaedim from a sketch), block out the existing
   house as simple boxes, then add a second-floor box. Try **full** vs **partial**
   second story to feel the scale against the height cap from [docs/02](docs/02-zoning-permits-miami.md).
3. **Style pass** — feed a front photo into MyArchitectAI/FLUX with prompts like:
   > "Two-story tropical-modern Miami Beach home, white stucco + ipe wood accents,
   > impact glass, flat roof, second story stepped back, lush landscaping, dusk."
4. **Iterate** — generate 5–10 variations, pick 2–3 directions.
5. **Package** — drop the best images + your massing into a short PDF brief.
   That PDF is what you send to the 3 architects.

## Important guardrails

- AI renderings are **inspiration, not dimensions.** Never assume what AI draws
  will fit your setbacks/height/FAR — that's the architect's job to confirm.
- Don't sign a construction contract off AI images. Renderings ≠ buildable plans.
- The money you save: fewer architect design iterations, faster alignment, no
  paying a designer to "explore options" you already explored for free.

---
**Sources:**
- [Best Open-Source Models for Architectural Rendering 2026 (SiliconFlow)](https://www.siliconflow.com/articles/en/best-open-source-models-for-architectural-rendering)
- [10 Best AI Architectural Rendering Software 2026 (MyArchitectAI)](https://www.myarchitectai.com/blog/ai-rendering-software)
- [25 Best AI Architectural Rendering Tools 2026 (illustrarch)](https://illustrarch.com/artificial-intelligence/64787-25-best-ai-architectural-rendering-tools-in-2026.html)
