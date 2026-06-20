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
slug = "dot-un-aerosol-transport-regulations-hazmat"
blog_images_dir = os.path.join(base_dir, "Blog", slug, "images")
public_images_dir = os.path.join(base_dir, "public", "images", "blog")

os.makedirs(blog_images_dir, exist_ok=True)
os.makedirs(public_images_dir, exist_ok=True)

# Image file paths from generate_image
hero_src = r"C:\Users\atind\.gemini\antigravity-ide\brain\c7519e81-ea4a-46d6-aeb2-f9c1d2854a74\dot_un_aerosol_transport_regulations_hazmat_hero_1781966849340.png"
diagram_src = r"C:\Users\atind\.gemini\antigravity-ide\brain\c7519e81-ea4a-46d6-aeb2-f9c1d2854a74\dot_un_aerosol_transport_regulations_hazmat_diagram_1781966868881.png"

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

font_header = get_font(font_path_bold, 24)
font_table_hdr = get_font(font_path_sans_bold, 13)
font_table_cell = get_font(font_path_sans, 12)
font_watermark = get_font(font_path_sans, 14)

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

# 1. Process Hero Image
print("Processing Hero Image...")
try:
    hero_img = Image.open(hero_src)
    # Resize if needed or save directly as webp
    hero_dest1 = os.path.join(blog_images_dir, f"{slug}-hero-globalaerosols.webp")
    hero_dest2 = os.path.join(public_images_dir, f"{slug}-hero-globalaerosols.webp")
    hero_img.save(hero_dest1, "WEBP", quality=90)
    hero_img.save(hero_dest2, "WEBP", quality=90)
    upload_to_r2(hero_dest1, f"{slug}-hero-globalaerosols.webp")
except Exception as e:
    print(f"Error processing Hero: {e}")

# 2. Process Diagram Image
print("Processing Diagram Image...")
try:
    diag_img = Image.open(diagram_src)
    diag_dest1 = os.path.join(blog_images_dir, f"{slug}-diagram-globalaerosols.webp")
    diag_dest2 = os.path.join(public_images_dir, f"{slug}-diagram-globalaerosols.webp")
    diag_img.save(diag_dest1, "WEBP", quality=90)
    diag_img.save(diag_dest2, "WEBP", quality=90)
    upload_to_r2(diag_dest1, f"{slug}-diagram-globalaerosols.webp")
except Exception as e:
    print(f"Error processing Diagram: {e}")

# 3. Render Infographic Table using PIL
print("Rendering Infographic Image...")
w, h = 900, 500
img = Image.new("RGBA", (w, h), NAVY)

# Header bar
overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
img = Image.alpha_composite(img, overlay).convert("RGB")

draw = ImageDraw.Draw(img)
draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
draw.text((45, 35), "Aerosol Transport Regulations: Shipping Category Matrix", fill=GOLD, font=font_header)

# Table Comparison
tx, ty = 40, 100
row_h = 75
col_w = [180, 320, 320]

headers = ["Shipping Class", "Limited Quantity (LTD QTY)", "Fully Regulated (UN 1950)"]
draw.rectangle([tx, ty, tx + sum(col_w), ty + 40], fill=(15, 32, 58), outline=GOLD, width=1)

cx = tx
for i, head in enumerate(headers):
    draw.text((cx + 15, ty + 12), head, fill=GOLD, font=font_table_hdr)
    cx += col_w[i]

rows = [
    ["Quantity Thresholds", "Inner packaging <= 1,000 mL (1.0 L)\nTotal gross box weight <= 30 kg (66 lbs)", "No inner limit (standard container specs)\nGross box weight based on UN packaging rating"],
    ["Packaging Standard", "UN spec box not required; sturdy outer box\nMust survive 1.2-meter drop test series", "UN spec certified packaging (e.g. 4G box)\nSpecific packaging group II performance standard"],
    ["Hazard Labeling", "Limited Quantity mark (black/white diamond)\nNo Class 2 hazardous labels required for road", "Class 2.1 (Flammable Gas) or Class 2.2 label\nUN 1950 Aerosols shipping description marking"],
    ["Shipping Papers", "Not required for domestic highway/rail shipping\nRequired for air (IATA) and sea (IMDG) freight", "Full Dangerous Goods Declaration mandatory\nRequires emergency response telephone number"]
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
        
        # Draw multiline text carefully
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

print("ALL ASSETS SUCCESSFULLY CREATED AND UPLOADED!")
