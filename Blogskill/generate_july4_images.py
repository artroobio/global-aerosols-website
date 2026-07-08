import os
import boto3
from botocore.client import Config
from PIL import Image, ImageDraw, ImageFont

ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

base_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"

NAVY       = (10, 22, 40)
NAVY_LIGHT = (15, 32, 58)
NAVY_MID   = (12, 28, 52)
GOLD       = (201, 168, 76)
WHITE      = (255, 255, 255)
GRAY_TEXT  = (148, 163, 184)
CYAN       = (34, 211, 238)
AMBER      = (245, 158, 11)
ROSE       = (244, 114, 182)
STEEL      = (100, 116, 139)

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

font_title      = get_font(r"C:\Windows\Fonts\georgiab.ttf", 36)
font_subtitle   = get_font(r"C:\Windows\Fonts\georgia.ttf", 18)
font_body       = get_font(r"C:\Windows\Fonts\georgia.ttf", 14)
font_body_bold  = get_font(r"C:\Windows\Fonts\georgiab.ttf", 14)
font_watermark  = get_font(r"C:\Windows\Fonts\arial.ttf", 14)
font_header     = get_font(r"C:\Windows\Fonts\georgiab.ttf", 22)
font_table_hdr  = get_font(r"C:\Windows\Fonts\arialbd.ttf", 13)
font_table_cell = get_font(r"C:\Windows\Fonts\arial.ttf", 12)
font_small      = get_font(r"C:\Windows\Fonts\arial.ttf", 11)

def add_watermark(draw, width, height):
    text = "globalaerosols.com"
    try:
        bbox = draw.textbbox((0, 0), text, font=font_watermark)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except Exception:
        w, h = 160, 14
    draw.text((width - w - 24, height - h - 24), text, fill=GOLD, font=font_watermark)

s3 = boto3.client(
    service_name="s3",
    endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="auto"
)

def upload_to_r2(slug, filename, local_filepath):
    r2_key = f"images/{slug}/{filename}"
    print(f"  Uploading -> {r2_key} ...")
    try:
        s3.upload_file(
            Filename=local_filepath,
            Bucket=BUCKET_NAME,
            Key=r2_key,
            ExtraArgs={"ContentType": "image/webp"}
        )
        print(f"  SUCCESS: {filename}")
    except Exception as e:
        print(f"  ERROR: {e}")

def save_and_upload(img, slug, filename, images_dir):
    path = os.path.join(images_dir, filename)
    img.save(path, "WEBP", quality=90)
    print(f"  Saved: {path}")
    upload_to_r2(slug, filename, path)


# =====================================================================
# POST 1: Aerosol Body Mist vs Fine Fragrance Spray
# =====================================================================
def render_body_mist():
    slug = "aerosol-body-mist-vs-fragrance-spray-alcohol"
    d = os.path.join(base_dir, "Blogskill", slug, "images")
    os.makedirs(d, exist_ok=True)

    # HERO 1200x630
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), NAVY)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ovd = ImageDraw.Draw(ov)
    ovd.polygon([(0, 0), (w, 0), (w, 400), (0, 600)], fill=(15, 32, 58, 200))
    ovd.rectangle([30, 30, 500, h - 30], fill=(10, 22, 40, 190), outline=GOLD, width=1)
    img = Image.alpha_composite(img, ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, w-20, h-20], outline=GOLD, width=3)
    draw.rectangle([25, 25, w-25, h-25], outline=GOLD, width=1)
    draw.text((70, 80), "Aerosol Body Mist", fill=GOLD, font=font_title)
    draw.text((70, 130), "vs Fine Fragrance", fill=WHITE, font=font_title)
    draw.text((70, 180), "Spray", fill=WHITE, font=font_title)
    draw.line([(70, 240), (450, 240)], fill=GOLD, width=2)
    draw.text((70, 258), "Alcohol concentration, projection &", fill=GRAY_TEXT, font=font_subtitle)
    draw.text((70, 285), "stability formulation guide", fill=GRAY_TEXT, font=font_subtitle)
    draw.rectangle([70, 420, 460, 510], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.text((90, 433), "Personal Care & Cosmetic Aerosols", fill=WHITE, font=font_body_bold)
    draw.text((90, 455), "EtOH concentration, LPG/DME propellants,", fill=GRAY_TEXT, font=font_body)
    draw.text((90, 473), "droplet size engineering, stability testing", fill=GRAY_TEXT, font=font_body)
    # Mist cone + bottle right side
    cx2, cy2 = 860, 315
    draw.polygon([(cx2-10, cy2-80), (cx2+10, cy2-80), (cx2+130, cy2+110), (cx2-130, cy2+110)],
                 fill=NAVY_MID, outline=CYAN)
    for rx, ry, r in [(760,200,4),(810,180,3),(870,160,5),(720,240,3),(920,200,4),
                      (790,260,3),(850,280,5),(770,310,4),(910,310,3),(830,350,3)]:
        draw.ellipse([rx-r, ry-r, rx+r, ry+r], fill=CYAN)
    draw.rectangle([840, 240, 880, 400], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.ellipse([830, 220, 890, 255], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.rectangle([850, 205, 870, 225], fill=GOLD)
    draw.text((700, 425), "FINE MIST ATOMIZATION", fill=CYAN, font=font_body_bold)
    draw.text((720, 445), "LPG / DME Propellant System", fill=GRAY_TEXT, font=font_body)
    add_watermark(draw, w, h)
    save_and_upload(img, slug, f"{slug}-hero-globalaerosols.webp", d)

    # DIAGRAM 900x500
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ovd = ImageDraw.Draw(ov)
    ovd.rectangle([30, 25, 870, 72], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    ovd.rectangle([40, 110, 310, 462], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    ovd.rectangle([590, 110, 860, 462], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img, ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 36), "Body Mist vs Fine Fragrance: Formulation Ratios", fill=GOLD, font=font_header)
    draw.text((55, 122), "BODY MIST", fill=CYAN, font=font_body_bold)
    draw.text((55, 143), "(Eau Fraiche / Cologne Tier)", fill=GRAY_TEXT, font=font_small)
    draw.line([(55, 163), (295, 163)], fill=GOLD, width=1)
    mist_rows = [
        ("Denatured Ethanol", "60-75%"),
        ("Water", "15-30%"),
        ("Fragrance Oil Load", "1-5%"),
        ("Solubilizer (PS-20)", "1-3%"),
        ("LPG Propellant", "10-15%"),
    ]
    for i, (lb, vl) in enumerate(mist_rows):
        y = 175 + i*50
        draw.rectangle([55, y, 295, y+35], fill=NAVY_LIGHT, outline=STEEL, width=1)
        draw.text((65, y+5), lb, fill=WHITE, font=font_body_bold)
        draw.text((65, y+20), vl, fill=GOLD, font=font_body)
    draw.text((598, 122), "FINE FRAGRANCE AEROSOL", fill=AMBER, font=font_body_bold)
    draw.text((598, 143), "(EDT / EDP Tier)", fill=GRAY_TEXT, font=font_small)
    draw.line([(598, 163), (845, 163)], fill=GOLD, width=1)
    frag_rows = [
        ("Denatured Ethanol", "75-90%"),
        ("Water", "0-5%"),
        ("Fragrance Oil Load", "8-20%"),
        ("Solubilizer", "Optional"),
        ("LPG / N2 Propellant", "8-12%"),
    ]
    for i, (lb, vl) in enumerate(frag_rows):
        y = 175 + i*50
        draw.rectangle([598, y, 845, y+35], fill=NAVY_LIGHT, outline=STEEL, width=1)
        draw.text((608, y+5), lb, fill=WHITE, font=font_body_bold)
        draw.text((608, y+20), vl, fill=AMBER, font=font_body)
    draw.text((418, 200), "vs", fill=GOLD, font=font_title)
    draw.line([(445, 170), (445, 450)], fill=GOLD, width=1)
    add_watermark(draw, w, h)
    save_and_upload(img, slug, f"{slug}-diagram-globalaerosols.webp", d)

    # INFOGRAPHIC 900x500
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ovd = ImageDraw.Draw(ov)
    ovd.rectangle([30, 25, 870, 72], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img, ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 36), "Fragrance Aerosol: Stability, Droplet & Safety Summary", fill=GOLD, font=font_header)
    tx, ty, row_h = 40, 100, 65
    col_w = [230, 280, 280]
    headers = ["Parameter", "Body Mist Aerosol", "Fine Fragrance Aerosol"]
    draw.rectangle([tx, ty, tx+sum(col_w), ty+40], fill=(15, 32, 58), outline=GOLD, width=1)
    cx3 = tx
    for hd in headers:
        draw.text((cx3+12, ty+12), hd, fill=GOLD, font=font_table_hdr)
        cx3 += col_w[headers.index(hd)]
    rows = [
        ("Stability Risk", "High (water-induced phase sep.)", "Low (alcohol solubilizes oil)"),
        ("Stability Remedy", "Polysorbate-20 solubilizer", "High-proof EtOH base"),
        ("Droplet Size Target", "Fine/diffuse - all-over mist", "Coarser/directed - pulse pts"),
        ("Flammability Class", "Flammable (GHS Cat. 1)", "Extremely Flammable (GHS)"),
    ]
    for r_idx, row in enumerate(rows):
        cy3 = ty + 40 + r_idx*row_h
        ro = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        rod = ImageDraw.Draw(ro)
        rod.rectangle([tx, cy3, tx+sum(col_w), cy3+row_h], fill=(10, 22, 40, 220), outline=GOLD, width=1)
        img = Image.alpha_composite(img.convert("RGBA"), ro).convert("RGB")
        draw = ImageDraw.Draw(img)
        cx3 = tx
        for c_idx, val in enumerate(row):
            draw.text((cx3+12, cy3+22), val,
                      fill=(WHITE if c_idx == 0 else GRAY_TEXT),
                      font=(font_table_hdr if c_idx == 0 else font_table_cell))
            cx3 += col_w[c_idx]
    add_watermark(draw, w, h)
    save_and_upload(img, slug, f"{slug}-infographic-globalaerosols.webp", d)


# =====================================================================
# POST 2: EU Aerosol Dispensers Directive 75/324/EEC
# =====================================================================
def render_eu_directive():
    slug = "eu-aerosol-dispensers-directive-testing-labeling"
    d = os.path.join(base_dir, "Blogskill", slug, "images")
    os.makedirs(d, exist_ok=True)

    # HERO 1200x630
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), NAVY)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ovd = ImageDraw.Draw(ov)
    ovd.polygon([(0, 0), (w, 0), (w, 350), (0, 580)], fill=(15, 32, 58, 180))
    ovd.rectangle([30, 30, 500, h-30], fill=(10, 22, 40, 190), outline=GOLD, width=1)
    img = Image.alpha_composite(img, ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, w-20, h-20], outline=GOLD, width=3)
    draw.rectangle([25, 25, w-25, h-25], outline=GOLD, width=1)
    draw.text((70, 75), "EU Aerosol Dispensers", fill=GOLD, font=font_title)
    draw.text((70, 125), "Directive 75/324/EEC", fill=WHITE, font=font_title)
    draw.line([(70, 185), (450, 185)], fill=GOLD, width=2)
    draw.text((70, 203), "Pressure testing, labeling &", fill=GRAY_TEXT, font=font_subtitle)
    draw.text((70, 230), "conformity marking guide", fill=GRAY_TEXT, font=font_subtitle)
    draw.rectangle([70, 380, 460, 485], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.text((90, 393), "Category: Aerosol Regulatory & Safety", fill=WHITE, font=font_body_bold)
    draw.text((90, 416), "Focus: Hot water bath test,", fill=GRAY_TEXT, font=font_body)
    draw.text((90, 436), "        reversed-e symbol, CLP, flammability tiers", fill=GRAY_TEXT, font=font_body)
    # Annotated can
    cx2, cy2 = 780, 130
    draw.rounded_rectangle([cx2, cy2, cx2+120, cy2+330], radius=12, fill=NAVY_LIGHT, outline=GOLD, width=2)
    draw.ellipse([cx2, cy2-20, cx2+120, cy2+40], fill=STEEL, outline=GOLD, width=1)
    draw.rectangle([cx2+45, cy2-35, cx2+75, cy2-10], fill=GOLD)
    draw.rectangle([cx2+10, cy2+80, cx2+110, cy2+280], fill=NAVY_MID, outline=CYAN, width=1)
    draw.text((cx2+18, cy2+90), "e  (conformity)", fill=CYAN, font=font_body_bold)
    draw.line([(cx2+15, cy2+115), (cx2+105, cy2+115)], fill=GOLD, width=1)
    draw.text((cx2+15, cy2+125), "PRESSURIZED", fill=AMBER, font=font_small)
    draw.text((cx2+15, cy2+143), "FLAMMABLE", fill=AMBER, font=font_small)
    draw.text((cx2+15, cy2+163), "Net: 150 mL", fill=GRAY_TEXT, font=font_small)
    draw.text((cx2+15, cy2+181), "Max 50 deg C", fill=GRAY_TEXT, font=font_small)
    draw.text((940, 165), "Reversed-e Mark", fill=CYAN, font=font_body_bold)
    draw.text((940, 185), "(Conformity Symbol)", fill=GRAY_TEXT, font=font_body)
    draw.line([(935, 178), (cx2+122, cy2+100)], fill=CYAN, width=1)
    draw.text((940, 265), "CLP Hazard", fill=AMBER, font=font_body_bold)
    draw.text((940, 285), "Pictograms + Codes", fill=GRAY_TEXT, font=font_body)
    draw.line([(935, 278), (cx2+122, cy2+143)], fill=AMBER, width=1)
    add_watermark(draw, w, h)
    save_and_upload(img, slug, f"{slug}-hero-globalaerosols.webp", d)

    # DIAGRAM 900x500
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ovd = ImageDraw.Draw(ov)
    ovd.rectangle([30, 25, 870, 72], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    ovd.rectangle([40, 110, 430, 465], fill=(10, 22, 40, 200), outline=GOLD, width=1)
    ovd.rectangle([460, 110, 860, 465], fill=(10, 22, 40, 200), outline=GOLD, width=1)
    img = Image.alpha_composite(img, ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 36), "75/324/EEC: Pressure Testing & Compliance Checklist", fill=GOLD, font=font_header)
    draw.text((60, 122), "Hot Water Bath Test (50 deg C)", fill=CYAN, font=font_body_bold)
    draw.line([(60, 142), (410, 142)], fill=GOLD, width=1)
    bx, by = 80, 165
    draw.rectangle([bx, by+60, bx+280, by+200], fill=(10, 28, 50), outline=CYAN, width=2)
    draw.rectangle([bx+4, by+80, bx+276, by+196], fill=(15, 40, 70))
    draw.text((bx+5, by+62), "50 deg C Water Bath", fill=CYAN, font=font_body_bold)
    draw.rounded_rectangle([bx+105, by+90, bx+175, by+192], radius=6, fill=NAVY_LIGHT, outline=GOLD, width=1)
    for bpx, bpy in [(bx+60, by+150), (bx+200, by+130), (bx+240, by+160)]:
        draw.ellipse([bpx-5, bpy-5, bpx+5, bpy+5], outline=CYAN, width=1)
    steps = [
        "Fill can to required level",
        "Submerge at 50 deg C defined period",
        "No leakage / distortion / burst",
        "Verify internal pressure within limit",
        "100% lot or statistical QC inspection",
    ]
    for i, s in enumerate(steps):
        draw.text((60, by+215+i*22), f"- {s}", fill=WHITE, font=font_body)
    draw.text((480, 122), "Compliance Checklist", fill=AMBER, font=font_body_bold)
    draw.line([(480, 142), (840, 142)], fill=GOLD, width=1)
    checklist = [
        "Container Design & Materials",
        "Fill Ratio Verification",
        "Hot Water Bath (50 deg C) Test",
        "Internal Pressure @ 50 deg C Limit",
        "Reversed-e Symbol on Label",
        "CLP Flammability Classification",
        "Precautionary Statements (P-codes)",
        "Technical Documentation Retained",
    ]
    for i, item in enumerate(checklist):
        y = 158 + i*36
        draw.rectangle([480, y, 840, y+28], fill=NAVY_LIGHT, outline=STEEL, width=1)
        draw.text((490, y+6), f"[OK]  {item}", fill=GOLD, font=font_body)
    add_watermark(draw, w, h)
    save_and_upload(img, slug, f"{slug}-diagram-globalaerosols.webp", d)

    # INFOGRAPHIC 900x500
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ovd = ImageDraw.Draw(ov)
    ovd.rectangle([30, 25, 870, 72], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img, ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 36), "EU Aerosol: Flammability Classes & Label Requirements", fill=GOLD, font=font_header)
    tx, ty, row_h = 40, 100, 65
    col_w = [185, 220, 225, 185]
    headers = ["Flammability Class", "Test Criterion", "Label Elements", "GHS Signal"]
    draw.rectangle([tx, ty, tx+sum(col_w), ty+40], fill=(15, 32, 58), outline=GOLD, width=1)
    cx4 = tx
    for hd in headers:
        draw.text((cx4+8, ty+12), hd, fill=GOLD, font=font_table_hdr)
        cx4 += col_w[headers.index(hd)]
    rows = [
        ("Non-Flammable", "Flame proj. < 15 cm", "! Pressurized + P-codes", "No GHS02"),
        ("Flammable", "Proj. >=15 cm; FP >23C", "Flame picto + WARNING", "GHS02 Flame"),
        ("Extremely Flammable", "Proj. >=75 cm; FP <=23C", "Flame + DANGER + H222", "GHS02 Bold"),
        ("All Categories", "Any aerosol per directive", "Reversed-e + net content", "e conformity"),
    ]
    row_colors = [CYAN, AMBER, ROSE, GOLD]
    for r_idx, (row, rc) in enumerate(zip(rows, row_colors)):
        cy4 = ty + 40 + r_idx*row_h
        ro = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        rod = ImageDraw.Draw(ro)
        rod.rectangle([tx, cy4, tx+sum(col_w), cy4+row_h], fill=(10, 22, 40, 210), outline=GOLD, width=1)
        img = Image.alpha_composite(img.convert("RGBA"), ro).convert("RGB")
        draw = ImageDraw.Draw(img)
        cx4 = tx
        for c_idx, val in enumerate(row):
            draw.text((cx4+8, cy4+18), val,
                      fill=(rc if c_idx == 0 else GRAY_TEXT),
                      font=(font_table_hdr if c_idx == 0 else font_table_cell))
            cx4 += col_w[c_idx]
    add_watermark(draw, w, h)
    save_and_upload(img, slug, f"{slug}-infographic-globalaerosols.webp", d)


if __name__ == "__main__":
    print("=== POST 1: Body Mist vs Fine Fragrance Spray ===")
    render_body_mist()
    print()
    print("=== POST 2: EU Aerosol Dispensers Directive ===")
    render_eu_directive()
    print()
    print("ALL DONE - 6 images generated and uploaded to R2!")
