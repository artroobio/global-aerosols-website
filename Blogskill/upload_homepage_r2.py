import os
import boto3
from botocore.client import Config
from PIL import Image

ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

# Initialize S3 Client for Cloudflare R2
s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

base_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Formulation website\public"
images_dir = os.path.join(base_dir, "images")

print("Scanning images directory for homepage assets...")

upload_count = 0
fail_count = 0

for root, dirs, files in os.walk(images_dir):
    # Ignore the blog directory since those are managed by upload_to_r2.py
    if "blog" in root.split(os.sep):
        continue
        
    for file in files:
        # Process only PNG, JPG, JPEG
        ext = os.path.splitext(file)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            continue
            
        filepath = os.path.join(root, file)
        
        # Determine the relative path from public directory
        rel_path = os.path.relpath(filepath, base_dir)
        # Normalize backslashes to forward slashes for R2 keys
        rel_path_key = rel_path.replace("\\", "/")
        
        # Determine output webp key and path
        base_key, _ = os.path.splitext(rel_path_key)
        webp_key = f"{base_key}.webp"
        
        base_file_path, _ = os.path.splitext(filepath)
        webp_filepath = f"{base_file_path}.webp"
        
        print(f"\n--- Processing: {rel_path_key} ---")
        
        # 1. Convert to WebP if it doesn't already exist as a webp file locally, or just always do it
        try:
            with Image.open(filepath) as img:
                # Convert to RGB mode if RGBA/P to save as WebP cleanly
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    alpha = img.convert('RGBA').split()[-1]
                    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                    bg.paste(img, mask=alpha)
                    rgb_img = bg.convert('RGB')
                else:
                    rgb_img = img.convert('RGB')
                    
                rgb_img.save(webp_filepath, "WEBP", quality=90)
                print(f"Successfully converted to WebP: {webp_filepath}")
        except Exception as e:
            print(f"Failed to convert {file} to WebP: {e}")
            fail_count += 1
            continue
            
        # 2. Upload to Cloudflare R2
        print(f"Uploading to R2: {BUCKET_NAME}/{webp_key}...")
        try:
            s3.upload_file(
                Filename=webp_filepath,
                Bucket=BUCKET_NAME,
                Key=webp_key,
                ExtraArgs={'ContentType': 'image/webp'}
            )
            print(f"Successfully uploaded: {webp_key}!")
            upload_count += 1
        except Exception as e:
            print(f"Failed to upload {webp_key}: {e}")
            fail_count += 1

print("\n==========================================")
print(f"Finished! Successfully uploaded {upload_count} homepage images to R2 CDN.")
print(f"Failed uploads/conversions: {fail_count}")
print("==========================================")
