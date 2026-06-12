import os
import shutil
import boto3
from botocore.client import Config
from PIL import Image

# Configuration
ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"
CDN_PREFIX = "https://cdn.globalaerosols.com"

# Directories
PROJECT_ROOT = r"C:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
BACKUP_DIR = os.path.join(PUBLIC_DIR, "original_backups")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Initialize Boto3 S3 Client for Cloudflare R2
s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

# Relative paths in public/
images_to_process = [
    # (relative path in public, is_landing)
    ("global-aerosols-2.png", True),
    ("images/aerosol_consultancy.png", False),
    ("images/aerosol_formulation.png", False),
    ("images/aerosol_manufacturing.png", False),
    ("images/aerosol_raw_materials.png", False),
    ("images/household_category.png", False),
    ("images/paints_category.png", False),
    ("images/artscrafts_category.png", False),
    ("images/automotive_category.png", False),
    ("images/industrial_category.png", False),
    ("images/adhesives_category.png", False),
    ("images/personalcare_category.png", False),
    ("images/cosmetics_category.png", False),
    ("images/pharma_category.png", False),
    ("images/aerosols/aerosols_hero.webp", False),
    ("images/home/team-synergy.jpg", False),
    ("images/home/process_consultation.webp", False),
    ("images/home/process_research.webp", False),
    ("images/home/process_development.webp", False),
    ("images/home/process_optimization.webp", False),
    ("images/home/process_delivery.webp", False),
    ("images/service-laboratory.webp", False),
    ("images/service-engineering.webp", False),
    ("images/service-scaleup.webp", False)
]

def get_webp_rel_path(rel_path):
    base, _ = os.path.splitext(rel_path)
    return base + ".webp"

def compress_image(src_path, dest_path, is_landing):
    img = Image.open(src_path)
    # Convert RGBA/P to RGB if needed to save as WebP cleanly
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        alpha = img.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=alpha)
        img = bg.convert('RGB')
    else:
        img = img.convert('RGB')

    if is_landing:
        # Maintain 100% quality (lossless)
        img.save(dest_path, "WEBP", quality=100, lossless=True)
        print(f"Compressed landing image (lossless): {dest_path} (Size: {os.path.getsize(dest_path) / 1024:.2f} KB)")
        return True

    # Iterative compression logic to stay under 100KB
    quality = 90
    while quality >= 20:
        img.save(dest_path, "WEBP", quality=quality)
        file_size = os.path.getsize(dest_path)
        if file_size <= 100 * 1024:
            print(f"Compressed {src_path} at quality {quality} (Size: {file_size / 1024:.2f} KB)")
            return True
        quality -= 5

    # If still not under 100KB, resize the image down and compress again
    width, height = img.size
    scale = 0.8
    while scale >= 0.2:
        new_size = (int(width * scale), int(height * scale))
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        quality = 70
        while quality >= 30:
            resized_img.save(dest_path, "WEBP", quality=quality)
            file_size = os.path.getsize(dest_path)
            if file_size <= 100 * 1024:
                print(f"Resized & Compressed {src_path} at scale {scale} and quality {quality} (Size: {file_size / 1024:.2f} KB)")
                return True
            quality -= 10
        scale -= 0.1

    print(f"WARNING: Could not compress {src_path} under 100KB even after resizing!")
    return False

def upload_to_r2(local_path, r2_key):
    print(f"Uploading {local_path} to R2 bucket {BUCKET_NAME} with key '{r2_key}'...")
    try:
        s3.upload_file(
            Filename=local_path,
            Bucket=BUCKET_NAME,
            Key=r2_key,
            ExtraArgs={'ContentType': 'image/webp'}
        )
        print(f"SUCCESS: Uploaded '{r2_key}'!")
        return True
    except Exception as e:
        print(f"ERROR: Failed to upload '{r2_key}': {e}")
        return False

def update_code_references(replacements):
    print("\nUpdating image references in Astro source code...")
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if not file.endswith('.astro') and not file.endswith('.js') and not file.endswith('.mjs') and not file.endswith('.css'):
                continue
            
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            modified = False
            for orig, new in replacements.items():
                if orig in content:
                    content = content.replace(orig, new)
                    modified = True
                    print(f"Replaced reference: {orig} -> {new} in {file}")

            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

def main():
    replacements = {}
    
    for rel_path, is_landing in images_to_process:
        src_abs_path = os.path.join(PUBLIC_DIR, rel_path)
        if not os.path.exists(src_abs_path):
            print(f"SKIPPING: File {src_abs_path} does not exist.")
            continue

        # 1. Back up original file
        backup_dest = os.path.join(BACKUP_DIR, rel_path)
        os.makedirs(os.path.dirname(backup_dest), exist_ok=True)
        shutil.copy2(src_abs_path, backup_dest)
        print(f"Backed up: {rel_path} -> original_backups/{rel_path}")

        # 2. Compress to WebP
        webp_rel_path = get_webp_rel_path(rel_path)
        webp_abs_path = os.path.join(PUBLIC_DIR, webp_rel_path)
        
        success = compress_image(src_abs_path, webp_abs_path, is_landing)
        if not success:
            continue

        # 3. Delete original file (only if it has a different extension than .webp)
        _, ext = os.path.splitext(rel_path)
        if ext.lower() != '.webp':
            os.remove(src_abs_path)
            print(f"Deleted original local file: {rel_path}")

        # 4. Upload to Cloudflare R2
        r2_key = webp_rel_path.replace("\\", "/")
        upload_to_r2(webp_abs_path, r2_key)

        # 5. Record replacement patterns
        # Replace absolute links like /images/... or /global-aerosols-2.png
        orig_ref = "/" + rel_path.replace("\\", "/")
        new_ref = f"{CDN_PREFIX}/{r2_key}"
        replacements[orig_ref] = new_ref
        
        # Also replace relative or other forms if found, e.g. without leading slash in configs
        orig_ref_no_slash = rel_path.replace("\\", "/")
        if orig_ref_no_slash != orig_ref:
            replacements[orig_ref_no_slash] = new_ref

    # 6. Apply search and replace in source code
    update_code_references(replacements)

    print("\nIMAGE OPTIMIZATION AND REFERENCE UPDATING COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
