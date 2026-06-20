import os
import json
import boto3
from botocore.client import Config
from PIL import Image, ImageDraw, ImageFont

# Configuration
ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

# Paths
base_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"
slug = "aerosol-particle-size-distribution-measurement"
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

# Fonts
font_path_bold = r"C:\Windows\Fonts\georgiab.ttf"
font_path_reg = r"C:\Windows\Fonts\georgia.ttf"
font_path_sans = r"C:\Windows\Fonts\arial.ttf"
font_path_sans_bold = r"C:\Windows\Fonts\arialbd.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

font_title = get_font(font_path_bold, 34)
font_subtitle = get_font(font_path_reg, 18)
font_header = get_font(font_path_bold, 24)
font_table_hdr = get_font(font_path_sans_bold, 13)
font_table_cell = get_font(font_path_sans, 12)
font_watermark = get_font(font_path_sans, 14)
font_body_bold = get_font(font_path_bold, 14)
font_body = get_font(font_path_reg, 14)

def add_watermark(draw, width, height):
    text = "globalaerosols.com"
    try:
        bbox = draw.textbbox((0, 0), text, font=font_watermark)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        w, h = 160, 14
    draw.text((width - w - 24, height - h - 24), text, fill=GOLD, font=font_watermark)

# Initialize Boto3 S3 Client for Cloudflare R2
s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def upload_to_r2(local_filepath, filename):
    r2_key = f"images/{slug}/{filename}"
    print(f"Uploading {filename} to {BUCKET_NAME}/{r2_key}...")
    try:
        s3.upload_file(
            Filename=local_filepath,
            Bucket=BUCKET_NAME,
            Key=r2_key,
            ExtraArgs={'ContentType': 'image/webp'}
        )
        print(f"SUCCESS: Uploaded {filename}!")
        return True
    except Exception as e:
        print(f"ERROR: Failed to upload {filename}: {e}")
        return False

# 1. RENDER HERO (1200x630)
print("Rendering Hero Image...")
w, h = 1200, 630
img = Image.new("RGBA", (w, h), NAVY)

# Translucent panel on the left
overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([30, 30, 490, h-30], fill=(10, 22, 40, 185), outline=GOLD, width=1)
img = Image.alpha_composite(img, overlay).convert("RGB")

draw = ImageDraw.Draw(img)
draw.rectangle([20, 20, w-20, h-20], outline=GOLD, width=3)
draw.rectangle([25, 25, w-25, h-25], outline=GOLD, width=1)

# Titles inside left panel
draw.text((70, 90), "Aerosol Particle", fill=GOLD, font=font_title)
draw.text((70, 140), "Size Distribution:", fill=WHITE, font=font_title)
draw.text((70, 190), "Measurement & Specs", fill=WHITE, font=font_title)
draw.line([(70, 255), (450, 255)], fill=GOLD, width=2)
draw.text((70, 275), "A technical overview of sizing methods,", fill=GRAY_TEXT, font=font_subtitle)
draw.text((70, 300), "diffraction dynamics and MMAD kinetics", fill=GRAY_TEXT, font=font_subtitle)

# Technical metadata box inside left panel
draw.rectangle([70, 440, 450, 520], fill=NAVY_LIGHT, outline=GOLD, width=1)
draw.text((90, 455), "Focus: MMAD, Laser Sizing, Impactor Stages", fill=WHITE, font=font_body_bold)
draw.text((90, 485), "Domain: Aerosol Physics & Spray Science", fill=GRAY_TEXT, font=font_body)

# Laser / droplet cloud visualization on the right
# Draw laser source box
draw.rectangle([580, 280, 640, 350], fill=NAVY_LIGHT, outline=CYAN, width=2)
draw.text((595, 308), "LASER", fill=CYAN, font=font_body_bold)

# Draw laser beam line passing through plume
draw.line([(640, 315), (1050, 315)], fill=(255, 50, 50), width=4) # Red laser beam line

# Draw spray nozzle on top right spraying downwards into laser beam
draw.rectangle([780, 100, 840, 150], fill=GRAY_TEXT, outline=GOLD, width=1)
draw.line([(810, 150), (810, 170)], fill=WHITE, width=6) # nozzle tip

# Draw translucent spray plume intersecting the laser beam
plume_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
plume_draw = ImageDraw.Draw(plume_overlay)
# Plume cone
plume_draw.polygon([(810, 170), (700, 400), (950, 400)], fill=(34, 211, 238, 50), outline=(34, 211, 238, 120))
# Individual dots for droplets
import random
random.seed(42)
for _ in range(150):
    px = random.randint(700, 920)
    py = random.randint(180, 400)
    # Check if inside triangle
    # simple bounding check for density
    if abs(px - 810) < (py - 170) * 0.6:
        size = random.randint(2, 6)
        color = CYAN if random.random() > 0.3 else GOLD
        plume_draw.ellipse([px-size, py-size, px+size, py+size], fill=color + (180,))

img = Image.alpha_composite(img.convert("RGBA"), plume_overlay).convert("RGB")
draw = ImageDraw.Draw(img)

# Labels for right-side diagram
draw.text((790, 75), "NOZZLE", fill=WHITE, font=font_body_bold)
draw.text((880, 220), "SPRAY PLUME", fill=CYAN, font=font_body_bold)
draw.text((940, 330), "LASER DIFFRACTION\nINTERSECTION", fill=GOLD, font=font_body_bold)

add_watermark(draw, w, h)

hero_dest1 = os.path.join(blog_images_dir, f"{slug}-hero-globalaerosols.webp")
hero_dest2 = os.path.join(public_images_dir, f"{slug}-hero-globalaerosols.webp")
img.save(hero_dest1, "WEBP", quality=90)
img.save(hero_dest2, "WEBP", quality=90)
upload_to_r2(hero_dest1, f"{slug}-hero-globalaerosols.webp")

# 2. RENDER DIAGRAM (900x500)
print("Rendering Diagram Image...")
w, h = 900, 500
img = Image.new("RGBA", (w, h), NAVY)

# Header
overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
img = Image.alpha_composite(img, overlay).convert("RGB")

draw = ImageDraw.Draw(img)
draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
draw.text((45, 35), "Cascade Impactor: Inertial Sizing Stages", fill=GOLD, font=font_header)

# Drawing stages stacked vertically
# We draw 4 stages
stage_colors = [CYAN, WHITE, GOLD, AMBER]
stage_labels = [
    "Stage 1: Cut-off Diameter > 10.0 microns",
    "Stage 2: Cut-off Diameter 5.0 - 10.0 microns",
    "Stage 3: Cut-off Diameter 2.0 - 5.0 microns",
    "Stage 4: Cut-off Diameter < 2.0 microns"
]
stage_explanations = [
    "Coarse fraction impacts on upper collection plate.",
    "Medium fraction impacts; lighter particles stay in stream.",
    "Fine respirable fraction impacts on stage 3 collection plate.",
    "Sub-micron particles captured on back-up filter stage."
]

for idx in range(4):
    sy = 100 + (idx * 85)
    # Stage box
    draw.rectangle([40, sy, 300, sy + 70], fill=NAVY_LIGHT, outline=stage_colors[idx], width=1)
    # Text inside box
    draw.text((55, sy + 15), f"STAGE {idx+1}", fill=stage_colors[idx], font=font_body_bold)
    draw.text((55, sy + 38), f"Impaction Plate #{idx+1}", fill=WHITE, font=font_table_cell)
    
    # Description lines next to stage
    draw.rectangle([320, sy, 850, sy + 70], fill=(10, 22, 40, 180), outline=GOLD, width=1)
    draw.text((340, sy + 15), stage_labels[idx], fill=WHITE, font=font_table_hdr)
    draw.text((340, sy + 38), stage_explanations[idx], fill=GRAY_TEXT, font=font_table_cell)
    
    # Flow arrow linking stages
    if idx < 3:
        # Draw small down arrow
        draw.line([(170, sy + 70), (170, sy + 85)], fill=CYAN, width=2)
        draw.polygon([(165, sy + 80), (175, sy + 80), (170, sy + 85)], fill=CYAN)

add_watermark(draw, w, h)

diag_dest1 = os.path.join(blog_images_dir, f"{slug}-diagram-globalaerosols.webp")
diag_dest2 = os.path.join(public_images_dir, f"{slug}-diagram-globalaerosols.webp")
img.save(diag_dest1, "WEBP", quality=90)
img.save(diag_dest2, "WEBP", quality=90)
upload_to_r2(diag_dest1, f"{slug}-diagram-globalaerosols.webp")

# 3. RENDER INFOGRAPHIC (900x500)
print("Rendering Infographic Image...")
w, h = 900, 500
img = Image.new("RGBA", (w, h), NAVY)

# Header
overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
img = Image.alpha_composite(img, overlay).convert("RGB")

draw = ImageDraw.Draw(img)
draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
draw.text((45, 35), "Droplet Sizing Methods: Technical Performance Comparison", fill=GOLD, font=font_header)

# Comparison table parameters
tx, ty = 40, 100
row_h = 75
col_w = [180, 220, 210, 210]

headers = ["Sizing Method", "Operating Principle", "Key Advantages", "Limitations"]
draw.rectangle([tx, ty, tx + sum(col_w), ty + 40], fill=(15, 32, 58), outline=GOLD, width=1)

cx = tx
for i, head in enumerate(headers):
    draw.text((cx + 15, ty + 12), head, fill=GOLD, font=font_table_hdr)
    cx += col_w[i]

rows = [
    ["Laser Diffraction", "Measures angular light scattering\nintensity from droplet cloud.", "Extremely fast, high throughput,\ncovers broad dynamic range.", "Cannot differentiate phase;\nsensitive to high density."],
    ["Cascade Impaction", "Separates particles inertially based\non aerodynamic diameter.", "Collects physical samples;\nallows chemical analysis.", "Time-consuming; prone to evaporation\nissues during high airflow."],
    ["Phase Doppler (PDPA)", "Laser Doppler interferometry measuring\nindividual droplet velocities.", "Simultaneous size & velocity data;\nexcellent spatial resolution.", "Requires diluting dense sprays;\nhighly expensive setup."],
    ["Optical Counter (OPC)", "Measures single-particle light\nscattering in flow cell.", "Highly sensitive for low-concentration\nor sterile aerosol rooms.", "Coincidence errors at high concentration;\nsmall sizing limit."]
]

for r_idx, row in enumerate(rows):
    cy = ty + 40 + (r_idx * row_h)
    
    row_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ro_draw = ImageDraw.Draw(row_overlay)
    ro_draw.rectangle([tx, cy, tx + sum(col_w), cy + row_h], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img.convert("RGBA"), row_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    cx = tx
    for c_idx, val in enumerate(row):
        font_to_use = font_table_hdr if c_idx == 0 else font_table_cell
        fill_color = WHITE if c_idx == 0 else GRAY_TEXT
        
        # Draw multiline text
        lines = val.split('\n')
        line_offset = 0
        for line in lines:
            draw.text((cx + 15, cy + 18 + line_offset), line, fill=fill_color, font=font_to_use)
            line_offset += 16
        cx += col_w[c_idx]

add_watermark(draw, w, h)

info_dest1 = os.path.join(blog_images_dir, f"{slug}-infographic-globalaerosols.webp")
info_dest2 = os.path.join(public_images_dir, f"{slug}-infographic-globalaerosols.webp")
img.save(info_dest1, "WEBP", quality=90)
img.save(info_dest2, "WEBP", quality=90)
upload_to_r2(info_dest1, f"{slug}-infographic-globalaerosols.webp")

print("ALL TOPIC 3 ASSETS SUCCESSFULLY GENERATED AND UPLOADED!")
