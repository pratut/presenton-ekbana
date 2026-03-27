# PPTX Cost Calculation

This document explains how presentation generation cost is calculated and shown in the UI.

## What Is Measured

The backend tracks provider usage for:

- LLM text generation (outlines, structure, slide content)
- Image generation (when image providers are used)

The tracked fields are returned as `usage_cost` in presentation APIs and used by frontend UI.

## Data Source (Basis of Calculation)

Cost is calculated from **provider-reported usage** where available:

- OpenAI: token usage from API responses/stream usage
- Anthropic: token usage from message usage
- Google: token usage from `usage_metadata`
- Codex: usage in response completion events (if provided)
- Image providers: image generation count per request

The backend does not estimate tokens from text length; it uses provider usage payloads.

## Pricing Source

Pricing is defined in backend code:

- `servers/fastapi/utils/usage_cost.py`
  - `LLM_PRICING` (USD per 1K input/output tokens)
  - `IMAGE_PRICING` (USD per generated image)

If a provider/model does not have a pricing entry, it falls back to `default` (often `0.0`).

## Formula

### LLM Cost

For each LLM usage item:

`item_cost = (input_tokens / 1000 * input_price_per_1k) + (output_tokens / 1000 * output_price_per_1k)`

### Image Cost

For each image usage item:

`item_cost = images_generated * price_per_image`

### Total Cost

`total_cost = sum(all_llm_item_costs) + sum(all_image_item_costs)`

## Aggregates Returned

The backend returns a summary object with:

- `total_amount`
- `llm_amount`
- `image_amount`
- `total_input_tokens`
- `total_output_tokens`
- `total_tokens`
- `total_images_generated`
- `items[]` (detailed usage entries)

## Per-Slide Cost Attribution

For slide-level display, usage items are tagged with metadata:

- `metadata.slide_index`
- `metadata.phase` (for example: `slide_content`, `slide_assets`)

Frontend groups items by `slide_index` to show per-slide cost and per-slide tokens.

Notes:

- Some usage is global (outline/structure generation) and may not map to a single slide.
- Per-slide UI reflects items that include `slide_index`.

## Where It Is Displayed

Current UI display is in:

- `servers/nextjs/app/(presentation-generator)/presentation/components/PresentationHeader.tsx`

It shows:

- Total cost
- LLM vs image breakdown
- Total token usage (input/output/total)
- Per-slide summary (when slide metadata is present)

## How To Change Pricing

To update cost numbers:

1. Edit `LLM_PRICING` and/or `IMAGE_PRICING` in `servers/fastapi/utils/usage_cost.py`.
2. Regenerate a presentation so new usage records use updated prices.

Existing stored `usage_cost` values on old presentations are not recalculated automatically.
