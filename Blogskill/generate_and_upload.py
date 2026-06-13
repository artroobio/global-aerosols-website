import os
import boto3
from botocore.client import Config
from PIL import Image, ImageDraw, ImageFont

# Configuration
ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

# Directory paths
base_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"
public_images_dir = os.path.join(base_dir, "public", "images", "blog")
os.makedirs(public_images_dir, exist_ok=True)

# Brand colors (RGB)
NAVY = (10, 22, 40)         # #0a1628
NAVY_LIGHT = (15, 32, 58)   # #0f203a
GOLD = (201, 168, 76)       # #c9a84c
WHITE = (255, 255, 255)     # #ffffff
GRAY_TEXT = (148, 163, 184) # #94a3b8
CYAN = (34, 211, 238)       # #22d3ee
AMBER = (245, 158, 11)      # #f59e0b

# Load system fonts
font_path_bold = r"C:\Windows\Fonts\georgiab.ttf"
font_path_reg = r"C:\Windows\Fonts\georgia.ttf"
font_path_sans = r"C:\Windows\Fonts\arial.ttf"
font_path_sans_bold = r"C:\Windows\Fonts\arialbd.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

font_title = get_font(font_path_bold, 36)
font_subtitle = get_font(font_path_reg, 18)
font_body = get_font(font_path_reg, 14)
font_body_bold = get_font(font_path_bold, 14)
font_watermark = get_font(font_path_sans, 14)
font_header = get_font(font_path_bold, 24)
font_table_hdr = get_font(font_path_sans_bold, 13)
font_table_cell = get_font(font_path_sans, 12)

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

def upload_to_r2(slug, filename, local_filepath):
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

# =====================================================================
# RENDER: Hair Conditioner
# =====================================================================
def render_hair_conditioner():
    slug = "hair-conditioner-formulation-cationic-surfactants"
    blog_images_dir = os.path.join(base_dir, "blogskill", slug, "images")
    os.makedirs(blog_images_dir, exist_ok=True)
    
    # 1. HERO (1200x630)
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), NAVY)
    
    # Sleek translucent left panel
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([30, 30, 480, h-30], fill=(10, 22, 40, 175), outline=GOLD, width=1)
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    # Gold decorative border
    draw.rectangle([20, 20, w-20, h-20], outline=GOLD, width=3)
    draw.rectangle([25, 25, w-25, h-25], outline=GOLD, width=1)
    
    # Text inside panel
    draw.text((70, 100), "Hair Conditioner", fill=GOLD, font=font_title)
    draw.text((70, 150), "Formulation:", fill=WHITE, font=font_title)
    draw.text((70, 200), "Cationic Surfactants", fill=WHITE, font=font_title)
    draw.line([(70, 265), (420, 265)], fill=GOLD, width=2)
    draw.text((70, 285), "A technical guide to cationic emulsification", fill=GRAY_TEXT, font=font_subtitle)
    draw.text((70, 310), "and electrostatic adsorption kinetics", fill=GRAY_TEXT, font=font_subtitle)
    
    # Technical Metadata Box
    draw.rectangle([70, 440, 440, 520], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.text((90, 455), "Domain: Cosmetics & Personal Care", fill=WHITE, font=font_body_bold)
    draw.text((90, 485), "Focus: BTMS-50, Fatty Alcohols, Emulsions", fill=GRAY_TEXT, font=font_body)
    
    # Sleek render on the right: Frosted jar and beakers schematic
    draw.ellipse([650, 150, 950, 450], outline=GOLD, width=2)
    draw.ellipse([670, 170, 930, 430], outline=GOLD, width=1)
    draw.line([(800, 150), (800, 450)], fill=GOLD, width=1)
    draw.line([(650, 300), (950, 300)], fill=GOLD, width=1)
    draw.text((720, 240), "CREAMY EMULSION\n  MATRIX", fill=CYAN, font=font_body_bold)
    draw.text((735, 330), "BTMS-50 / CETYL\n GEL NETWORK", fill=GOLD, font=font_body_bold)
    
    add_watermark(draw, w, h)
    
    filename = f"{slug}-hero-globalaerosols.webp"
    local_path = os.path.join(blog_images_dir, filename)
    public_path = os.path.join(public_images_dir, filename)
    img.save(local_path, "WEBP", quality=90)
    img.save(public_path, "WEBP", quality=90)
    upload_to_r2(slug, filename, local_path)

    # 2. DIAGRAM (900x500)
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    
    # Header bar
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    
    # Technical annotations boxes
    overlay_draw.rectangle([50, 120, 320, 240], fill=(10, 22, 40, 230), outline=GOLD, width=1)
    overlay_draw.rectangle([580, 120, 850, 240], fill=(10, 22, 40, 230), outline=GOLD, width=1)
    overlay_draw.rectangle([250, 390, 650, 465], fill=(10, 22, 40, 230), outline=GOLD, width=1)
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 35), "Cationic Surfactant Adsorption on Hair Cuticle", fill=GOLD, font=font_header)
    
    # Left box
    draw.text((70, 135), "Negatively Charged Cuticle (-)", fill=CYAN, font=font_body_bold)
    draw.text((70, 160), "- Damaged hair exhibits high\n  negative charge density\n- Exposed cysteic acid groups\n- Electrostatic attraction target", fill=WHITE, font=font_body)
    
    # Right box
    draw.text((600, 135), "Cationic Adsorption (+)", fill=GOLD, font=font_body_bold)
    draw.text((600, 160), "- BTMS-50 cationic heads bind\n  firmly to cuticle surface\n- Resists water rinsing\n- Monomolecular protective film", fill=WHITE, font=font_body)
    
    # Bottom box
    draw.text((270, 400), "Result: Friction & Static Elimination", fill=WHITE, font=font_body_bold)
    draw.text((270, 422), "Aligned cuticle layers reduce coefficient of friction by 40-60%,\npreventing flyaways and restoring premium cosmetic shine.", fill=GRAY_TEXT, font=font_body)
    
    # Stylized hair strand with charge symbols in center
    draw.rectangle([350, 150, 550, 360], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.text((370, 160), "HAIR CUTICLE CORE", fill=WHITE, font=font_body_bold)
    
    # Draw minus charges inside hair
    for y in range(200, 340, 30):
        draw.text((380, y), "[-] Carboxylate", fill=CYAN, font=font_body)
        draw.text((470, y), "[+] Cationic", fill=GOLD, font=font_body)
        draw.line([(440, y+8), (465, y+8)], fill=GOLD, width=1)
        
    add_watermark(draw, w, h)
    
    filename = f"{slug}-diagram-globalaerosols.webp"
    local_path = os.path.join(blog_images_dir, filename)
    public_path = os.path.join(public_images_dir, filename)
    img.save(local_path, "WEBP", quality=90)
    img.save(public_path, "WEBP", quality=90)
    upload_to_r2(slug, filename, local_path)

    # 3. INFOGRAPHIC (900x500)
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    
    # Header bar
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 35), "Rinse-Off vs Leave-In Formulation Parameters", fill=GOLD, font=font_header)
    
    # Table Comparison
    tx, ty = 40, 100
    row_h = 65
    col_w = [220, 290, 290]
    
    headers = ["Parameter", "Rinse-Off Formulation", "Leave-In Formulation"]
    draw.rectangle([tx, ty, tx + sum(col_w), ty + 40], fill=(15, 32, 58), outline=GOLD, width=1)
    
    cx = tx
    for i, head in enumerate(headers):
        draw.text((cx + 15, ty + 12), head, fill=GOLD, font=font_table_hdr)
        cx += col_w[i]
        
    rows = [
        ["BTMS-50 Concentration", "3.0% – 6.0% w/w (High deposition)", "1.0% – 3.0% w/w (Avoid build-up)"],
        ["Fatty Alcohol Co-emulsifiers", "2.0% – 5.0% w/w (Thick cream network)", "0.5% – 1.5% w/w (Light fluid lotion)"],
        ["Target Viscosity Range", "8,000 – 20,000 cP (Rich emulsion)", "500 – 3,000 cP (Pourable/sprayable)"],
        ["Preservative System", "Standard phenoxyethanol + EDTA", "High demand (continuous scalp exposure)"]
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
            draw.text((cx + 15, cy + 24), val, fill=fill_color, font=font_to_use)
            cx += col_w[c_idx]
            
    add_watermark(draw, w, h)
    
    filename = f"{slug}-infographic-globalaerosols.webp"
    local_path = os.path.join(blog_images_dir, filename)
    public_path = os.path.join(public_images_dir, filename)
    img.save(local_path, "WEBP", quality=90)
    img.save(public_path, "WEBP", quality=90)
    upload_to_r2(slug, filename, local_path)

# =====================================================================
# RENDER: PSA Adhesives
# =====================================================================
def render_psa_adhesives():
    slug = "pressure-sensitive-adhesives-acrylic-vs-rubber"
    blog_images_dir = os.path.join(base_dir, "blogskill", slug, "images")
    os.makedirs(blog_images_dir, exist_ok=True)
    
    # 1. HERO (1200x630)
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), NAVY)
    
    # Sleek translucent left panel
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([30, 30, 480, h-30], fill=(10, 22, 40, 175), outline=GOLD, width=1)
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    # Gold decorative border
    draw.rectangle([20, 20, w-20, h-20], outline=GOLD, width=3)
    draw.rectangle([25, 25, w-25, h-25], outline=GOLD, width=1)
    
    # Text inside panel
    draw.text((70, 100), "Pressure Sensitive", fill=GOLD, font=font_title)
    draw.text((70, 150), "Adhesives:", fill=WHITE, font=font_title)
    draw.text((70, 200), "Acrylics vs Rubber", fill=WHITE, font=font_title)
    draw.line([(70, 265), (420, 265)], fill=GOLD, width=2)
    draw.text((70, 285), "Explore the tack-peel-shear triangle", fill=GRAY_TEXT, font=font_subtitle)
    draw.text((70, 310), "and viscoelastic coating chemistry", fill=GRAY_TEXT, font=font_subtitle)
    
    # Technical Metadata Box
    draw.rectangle([70, 440, 440, 520], fill=NAVY_LIGHT, outline=GOLD, width=1)
    draw.text((90, 455), "Domain: Adhesives & Polymer Care", fill=WHITE, font=font_body_bold)
    draw.text((90, 485), "Focus: PSA, viscoelasticity, monomers", fill=GRAY_TEXT, font=font_body)
    
    # Sleek render on the right: Peel angle schematic
    draw.line([(650, 420), (980, 420)], fill=GRAY_TEXT, width=4) # substrate
    draw.rectangle([720, 200, 800, 416], fill=NAVY_LIGHT, outline=GOLD, width=1) # tape being peeled
    draw.line([(800, 420), (920, 300)], fill=AMBER, width=6) # peeled tape
    draw.text((660, 435), "POLISHED STEEL TEST SUBSTRATE", fill=CYAN, font=font_body_bold)
    draw.text((820, 260), "90° PEEL ANGLE", fill=GOLD, font=font_body_bold)
    
    add_watermark(draw, w, h)
    
    filename = f"{slug}-hero-globalaerosols.webp"
    local_path = os.path.join(blog_images_dir, filename)
    public_path = os.path.join(public_images_dir, filename)
    img.save(local_path, "WEBP", quality=90)
    img.save(public_path, "WEBP", quality=90)
    upload_to_r2(slug, filename, local_path)

    # 2. DIAGRAM (900x500)
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    
    # Header bar
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    
    # Technical annotations boxes
    overlay_draw.rectangle([50, 120, 320, 240], fill=(10, 22, 40, 230), outline=GOLD, width=1)
    overlay_draw.rectangle([580, 120, 850, 240], fill=(10, 22, 40, 230), outline=GOLD, width=1)
    overlay_draw.rectangle([250, 390, 650, 465], fill=(10, 22, 40, 230), outline=GOLD, width=1)
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 35), "Adhesive Peel Mechanics & Viscoelastic Stretching", fill=GOLD, font=font_header)
    
    # Left box
    draw.text((70, 135), "Peel Force Dynamics", fill=CYAN, font=font_body_bold)
    draw.text((70, 160), "- Tensile stress concentration\n  at the peel front\n- Viscoelastic shear strain\n- Polymer chain slippage", fill=WHITE, font=font_body)
    
    # Right box
    draw.text((600, 135), "Fibril Stretching", fill=GOLD, font=font_body_bold)
    draw.text((600, 160), "- Cavitation & void growth\n- Rapid filament drawing\n- High energy dissipation\n- Cohesive vs adhesive failure", fill=WHITE, font=font_body)
    
    # Bottom box
    draw.text((270, 400), "Dahlquist Criterion for Contact", fill=WHITE, font=font_body_bold)
    draw.text((270, 422), "Viscoelastic adhesive elastic modulus must be below 0.3 MPa\nat application frequency to establish immediate molecular contact.", fill=GRAY_TEXT, font=font_body)
    
    # Center visualization
    draw.line([(350, 340), (550, 340)], fill=WHITE, width=4) # substrate
    draw.line([(350, 340), (450, 340)], fill=CYAN, width=6) # tape backing on substrate
    draw.line([(450, 340), (520, 220)], fill=AMBER, width=6) # tape being peeled
    
    # Draw vertical stretching fibrils in the peel zone
    for x in range(450, 480, 5):
        draw.line([(x, 340), (x + 8, 340 - (x - 445)*3)], fill=GOLD, width=1)
        
    add_watermark(draw, w, h)
    
    filename = f"{slug}-diagram-globalaerosols.webp"
    local_path = os.path.join(blog_images_dir, filename)
    public_path = os.path.join(public_images_dir, filename)
    img.save(local_path, "WEBP", quality=90)
    img.save(public_path, "WEBP", quality=90)
    upload_to_r2(slug, filename, local_path)

    # 3. INFOGRAPHIC (900x500)
    w, h = 900, 500
    img = Image.new("RGBA", (w, h), NAVY)
    
    # Header bar
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([30, 25, 870, 75], fill=(10, 22, 40, 220), outline=GOLD, width=1)
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, w-15, h-15], outline=GOLD, width=2)
    draw.text((45, 35), "Acrylic vs Rubber-Based PSA Comparison Matrix", fill=GOLD, font=font_header)
    
    # Table Comparison
    tx, ty = 40, 100
    row_h = 65
    col_w = [220, 290, 290]
    
    headers = ["Parameter", "Acrylic-Based PSAs", "Rubber-Based PSAs"]
    draw.rectangle([tx, ty, tx + sum(col_w), ty + 40], fill=(15, 32, 58), outline=GOLD, width=1)
    
    cx = tx
    for i, head in enumerate(headers):
        draw.text((cx + 15, ty + 12), head, fill=GOLD, font=font_table_hdr)
        cx += col_w[i]
        
    rows = [
        ["Polymer Base Chemistry", "Polyacrylates (2-EHA, BA, AA)", "SIS / SBS block copolymers"],
        ["Tackifying Resin Demand", "Self-tacky (optional resin added)", "Mandatory (rosin/terpene resins)"],
        ["UV & Thermal Stability", "Excellent (fully saturated backbones)", "Poor (prone to oxidative cracking)"],
        ["Application Strengths", "High-temperature & outdoor mounting", "Packaging tapes & low-energy surfaces"]
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
            draw.text((cx + 15, cy + 24), val, fill=fill_color, font=font_to_use)
            cx += col_w[c_idx]
            
    add_watermark(draw, w, h)
    
    filename = f"{slug}-infographic-globalaerosols.webp"
    local_path = os.path.join(blog_images_dir, filename)
    public_path = os.path.join(public_images_dir, filename)
    img.save(local_path, "WEBP", quality=90)
    img.save(public_path, "WEBP", quality=90)
    upload_to_r2(slug, filename, local_path)

if __name__ == "__main__":
    print("Generating Hair Conditioner Formulation images...")
    render_hair_conditioner()
    
    print("\nGenerating Pressure Sensitive Adhesives images...")
    render_psa_adhesives()
    
    print("\nALL IMAGE GENERATION AND UPLOAD STEPS COMPLETED!")
