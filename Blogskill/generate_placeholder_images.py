"""
Generates placeholder WebP images for a blog post when no AI image-generation
tool is available in the current session. Each placeholder is a clean dark
editorial-style card with the slug, image type, dimensions, and the intended
AI generation prompt printed on it in wrapped text, so it's unmistakably a
placeholder and easy to swap out later with a real generated asset.

Usage: python generate_placeholder_images.py <slug>
Reads prompts from placeholder_prompts_<slug>.json in the same directory
(a simple {"hero": "...", "diagram": "...", "infographic": "..."} file),
writes into ../Blog/<slug>/images/.
"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "Blog"))

SPECS = {
    "hero": (1200, 630),
    "diagram": (900, 500),
    "infographic": (900, 500),
}

BG = (10, 15, 26)          # deep navy
ACCENT = (217, 119, 6)     # warm gold
TEXT = (226, 232, 240)     # near-white
MUTED = (100, 116, 139)    # slate


def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_placeholder(width, height, label, slug, prompt_text, out_path):
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # subtle border
    draw.rectangle([0, 0, width - 1, height - 1], outline=(40, 48, 66), width=2)

    # accent bar
    draw.rectangle([0, 0, width, 8], fill=ACCENT)

    pad = 40
    y = pad

    title_font = load_font(34, bold=True)
    draw.text((pad, y), f"PLACEHOLDER — {label.upper()}", font=title_font, fill=ACCENT)
    y += 48

    slug_font = load_font(18)
    draw.text((pad, y), slug, font=slug_font, fill=MUTED)
    y += 26
    draw.text((pad, y), f"{width}\u00d7{height}px  \u2022  replace before publishing", font=slug_font, fill=MUTED)
    y += 40

    draw.line([(pad, y), (width - pad, y)], fill=(40, 48, 66), width=1)
    y += 24

    prompt_label_font = load_font(16, bold=True)
    draw.text((pad, y), "INTENDED AI PROMPT:", font=prompt_label_font, fill=(148, 163, 184))
    y += 28

    body_font = load_font(16)
    max_chars = max(20, int((width - 2 * pad) / 8.2))
    wrapped = textwrap.wrap(prompt_text, width=max_chars)
    line_height = 22
    max_lines = (height - y - pad) // line_height
    for line in wrapped[:max_lines]:
        draw.text((pad, y), line, font=body_font, fill=TEXT)
        y += line_height
    if len(wrapped) > max_lines:
        draw.text((pad, y), "...", font=body_font, fill=MUTED)

    img.save(out_path, "WEBP", quality=88)
    print(f"Wrote {out_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_placeholder_images.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    prompts_path = os.path.join(SCRIPT_DIR, f"placeholder_prompts_{slug}.json")
    if not os.path.exists(prompts_path):
        print(f"Prompts file not found: {prompts_path}")
        sys.exit(1)

    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    images_dir = os.path.join(BLOG_ROOT, slug, "images")
    os.makedirs(images_dir, exist_ok=True)

    for kind, (w, h) in SPECS.items():
        prompt_text = prompts.get(kind, "")
        out_name = f"{slug}-{kind}-globalaerosols.webp"
        out_path = os.path.join(images_dir, out_name)
        draw_placeholder(w, h, kind, slug, prompt_text, out_path)


if __name__ == "__main__":
    main()
