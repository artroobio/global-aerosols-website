import os
import boto3
from botocore.client import Config
from PIL import Image, ImageDraw, ImageFont

# Config
ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

base_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"
slug = "metered-dose-valve-engineering-dose-accuracy"

blog_images_dir = os.path.join(base_dir, "Blog", slug, "images")
public_images_dir = os.path.join(base_dir, "public", "images", "blog")
os.makedirs(blog_images_dir, exist_ok=True)
os.makedirs(public_images_dir, exist_ok=True)

# Brand colors (RGB)
NAVY = (10, 22, 40)         # #0a1628
NAVY_LIGHT = (15, 32, 58)   # #0f203a
GOLD = (201, 168, 76)       # #c9a84c
WHITE = (255, 255, 255)     # #ffffff
GRAY_TEXT = (148, 163, 184) # #94a3b8
CYAN = (34, 211, 238)       # #22d3ee
AMBER = (245, 158, 11)      # #f59e0b

font_path_bold = r"C:\Windows\Fonts\georgiab.ttf"
font_path_reg = r"C:\Windows\Fonts\georgia.ttf"
font_path_sans = r"C:\Windows\Fonts\arial.ttf"
font_path_sans_bold = r"C:\Windows\Fonts\arialbd.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

font_title = get_font(font_path_bold, 32)
font_header = get_font(font_path_bold, 22)
font_table_hdr = get_font(font_path_sans_bold, 13)
font_table_cell = get_font(font_path_sans, 12)
font_watermark = get_font(font_path_sans, 14)
font_body_bold = get_font(font_path_sans_bold, 14)
font_body = get_font(font_path_sans, 13)

def add_watermark(draw, width, height):
    text = "globalaerosols.com"
    try:
        bbox = draw.textbbox((0, 0), text, font=font_watermark)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        w, h = 160, 14
    draw.text((width - w - 24, height - h - 24), text, fill=GOLD, font=font_watermark)

# 1. HERO IMAGE PROCESS (convert PNG artifact to WEBP)
hero_png_path = r"C:\Users\atind\.gemini\antigravity-ide\brain\7b54e643-a7c6-4913-bdc5-d7ad807a6f06\mdv_hero_img_1785760289265.png"

hero_filename = f"{slug}-hero-globalaerosols.webp"
hero_dest1 = os.path.join(blog_images_dir, hero_filename)
hero_dest2 = os.path.join(public_images_dir, hero_filename)

if os.path.exists(hero_png_path):
    print("Processing Hero image from generated PNG...")
    hero_img = Image.open(hero_png_path).convert("RGB")
    # Resize to exact 1200x630
    hero_img = hero_img.resize((1200, 630), Image.Resampling.LANCZOS)
    hero_img.save(hero_dest1, "WEBP", quality=92)
    hero_img.save(hero_dest2, "WEBP", quality=92)
    print(f"Saved hero WEBP to {hero_dest1}")

# 2. DIAGRAM IMAGE (900x500)
print("Rendering Diagram Image...")
w, h = 900, 500
img = Image.new("RGBA", (w, h), NAVY)

overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([30, 20, 870, 70], fill=(10, 22, 40, 220), outline=GOLD, width=1)
img = Image.alpha_composite(img, overlay).convert("RGB")

draw = ImageDraw.Draw(img)
draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
draw.text((45, 32), "Metered Dose Valve: Actuation Cycle & Chamber Mechanics", fill=GOLD, font=font_header)

steps = [
    ("1. Rest Position", "Metering chamber fills via inlet orifice under internal propellant vapor pressure.", CYAN),
    ("2. Downstroke Actuation", "Valve stem depresses; inlet gasket seals chamber from bulk canister.", WHITE),
    ("3. Metered Discharge", "Stem outlet port aligns, expelling exact chamber volume under expansion.", GOLD),
    ("4. Upstroke Return", "Internal spring returns stem; outlet closes & inlet re-opens to refill.", AMBER)
]

for idx, (title, desc, color) in enumerate(steps):
    sy = 85 + (idx * 95)
    # Box
    draw.rectangle([40, sy, 260, sy + 80], fill=NAVY_LIGHT, outline=color, width=2)
    draw.text((55, sy + 15), f"PHASE {idx+1}", fill=color, font=font_body_bold)
    draw.text((55, sy + 42), title.split(". ")[1], fill=WHITE, font=font_table_cell)
    
    # Detail Panel
    draw.rectangle([280, sy, 850, sy + 80], fill=(10, 22, 40, 200), outline=GOLD, width=1)
    draw.text((300, sy + 18), title, fill=color, font=font_table_hdr)
    draw.text((300, sy + 44), desc, fill=GRAY_TEXT, font=font_body)
    
    # Connecting Arrow
    if idx < 3:
        draw.line([(150, sy + 80), (150, sy + 95)], fill=CYAN, width=2)
        draw.polygon([(145, sy + 90), (155, sy + 90), (150, sy + 95)], fill=CYAN)

add_watermark(draw, w, h)

diag_filename = f"{slug}-diagram-globalaerosols.webp"
diag_dest1 = os.path.join(blog_images_dir, diag_filename)
diag_dest2 = os.path.join(public_images_dir, diag_filename)
img.save(diag_dest1, "WEBP", quality=90)
img.save(diag_dest2, "WEBP", quality=90)
print(f"Saved diagram WEBP to {diag_dest1}")

# 3. INFOGRAPHIC IMAGE (900x500)
print("Rendering Infographic Image...")
w, h = 900, 500
img = Image.new("RGBA", (w, h), NAVY)

overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([30, 20, 870, 70], fill=(10, 22, 40, 220), outline=GOLD, width=1)
img = Image.alpha_composite(img, overlay).convert("RGB")

draw = ImageDraw.Draw(img)
draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
draw.text((45, 32), "MDV Engineering Specifications & Performance Criteria", fill=GOLD, font=font_header)

tx, ty = 40, 90
row_h = 90
col_w = [180, 210, 220, 200]

headers = ["Engineering Domain", "Performance Parameter", "Industry Standard / Limit", "Key Quality Factor"]
draw.rectangle([tx, ty, tx + sum(col_w), ty + 35], fill=(15, 32, 58), outline=GOLD, width=1)

cx = tx
for i, head in enumerate(headers):
    draw.text((cx + 12, ty + 10), head, fill=GOLD, font=font_table_hdr)
    cx += col_w[i]

rows = [
    ["Dose Accuracy", "Volumetric Tolerance\n(25 uL to 100 uL range)", "±2% to ±5% target delivery\nper USP <601> / Ph.Eur.", "Stem travel & chamber bore\ndimensional tolerance"],
    ["Leak Integrity", "Canister Seal & Valve Leak\nRate under pressure", "<0.5 mg/day shelf-life limit\n(ASTM D3925 / ICH Q1A)", "Gasket swell & crimp pressure\non valve cup seat"],
    ["Dose Uniformity", "Shot-to-Shot Consistency\nthrough canister life", "Minimum 9 out of 10 within\n85% - 115% nominal dose", "Rapid refilling flow & vapor\npressure balance"],
    ["Material Quality", "Elastomer Extractables &\nLeachables Profile", "FDA / EMA pharmaceutical\nqualification standards", "EPDM / Nitrile grade selection\n& propellant compatibility"]
]

for r_idx, row in enumerate(rows):
    cy = ty + 35 + (r_idx * row_h)
    
    row_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ro_draw = ImageDraw.Draw(row_overlay)
    ro_draw.rectangle([tx, cy, tx + sum(col_w), cy + row_h], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img.convert("RGBA"), row_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    cx = tx
    for c_idx, val in enumerate(row):
        font_to_use = font_table_hdr if c_idx == 0 else font_table_cell
        fill_color = WHITE if c_idx == 0 else GRAY_TEXT
        
        lines = val.split('\n')
        line_offset = 0
        for line in lines:
            draw.text((cx + 12, cy + 18 + line_offset), line, fill=fill_color, font=font_to_use)
            line_offset += 16
        cx += col_w[c_idx]

add_watermark(draw, w, h)

info_filename = f"{slug}-infographic-globalaerosols.webp"
info_dest1 = os.path.join(blog_images_dir, info_filename)
info_dest2 = os.path.join(public_images_dir, info_filename)
img.save(info_dest1, "WEBP", quality=90)
img.save(info_dest2, "WEBP", quality=90)
print(f"Saved infographic WEBP to {info_dest1}")

# 4. UPLOAD ALL THREE TO CLOUDFLARE R2
print("Uploading images to Cloudflare R2...")
s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

for fname, fpath in [(hero_filename, hero_dest1), (diag_filename, diag_dest1), (info_filename, info_dest1)]:
    r2_key = f"images/{slug}/{fname}"
    print(f"Uploading {fname} -> {BUCKET_NAME}/{r2_key}")
    try:
        s3.upload_file(
            Filename=fpath,
            Bucket=BUCKET_NAME,
            Key=r2_key,
            ExtraArgs={'ContentType': 'image/webp'}
        )
        print(f"SUCCESS: Uploaded {fname} to R2!")
    except Exception as e:
        print(f"ERROR uploading {fname}: {e}")

print("MDV IMAGE GENERATION & R2 UPLOAD COMPLETE!")
