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

# File Paths
PROJECT_ROOT = r"C:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
BACKUP_DIR = os.path.join(PUBLIC_DIR, "original_backups")

# Initialize Boto3 S3 Client for Cloudflare R2
s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

# New PNG image files generated
new_images = [
    {
        "generated_png": r"C:\Users\atind\.gemini\antigravity-ide\brain\a953663d-6fe8-4694-8ca8-bc3c16c438b0\aerosols_hero_sophistication_1781282194889.png",
        "target_webp_rel": "images/aerosols/aerosols_hero.webp"
    },
    {
        "generated_png": r"C:\Users\atind\.gemini\antigravity-ide\brain\a953663d-6fe8-4694-8ca8-bc3c16c438b0\process_consultation_scroll_1781282217080.png",
        "target_webp_rel": "images/home/process_consultation.webp"
    }
]

def compress_image(src_path, dest_path):
    img = Image.open(src_path)
    # Convert RGBA/P to RGB if needed to save as WebP cleanly
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        alpha = img.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=alpha)
        img = bg.convert('RGB')
    else:
        img = img.convert('RGB')

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

def main():
    for img_info in new_images:
        png_path = img_info["generated_png"]
        webp_rel = img_info["target_webp_rel"]
        webp_abs = os.path.join(PUBLIC_DIR, webp_rel)

        # 1. Back up existing local WebP (if present) before overwriting it
        if os.path.exists(webp_abs):
            backup_webp_path = os.path.join(BACKUP_DIR, webp_rel)
            os.makedirs(os.path.dirname(backup_webp_path), exist_ok=True)
            # Only back up if the backup file doesn't exist yet, to avoid overwriting a previous backup of the original
            if not os.path.exists(backup_webp_path):
                shutil.copy2(webp_abs, backup_webp_path)
                print(f"Backed up old local webp to backups: {webp_rel}")

        # 2. Compress the new generated PNG into WebP at the target path
        os.makedirs(os.path.dirname(webp_abs), exist_ok=True)
        success = compress_image(png_path, webp_abs)
        if not success:
            continue

        # 3. Upload the newly optimized WebP to R2
        r2_key = webp_rel.replace("\\", "/")
        upload_to_r2(webp_abs, r2_key)

    print("\nIMAGE REPLACEMENT AND UPLOAD COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
