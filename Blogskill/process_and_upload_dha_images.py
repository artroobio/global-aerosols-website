import os
import json
import urllib.request
import boto3
from botocore.client import Config
from PIL import Image

ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

slug = "aerosol-self-tanning-dha-spray-skin-chemistry"
base_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website"
blog_images_dir = os.path.join(base_dir, "Blog", slug, "images")
public_images_dir = os.path.join(base_dir, "public", "images", "blog")
os.makedirs(blog_images_dir, exist_ok=True)
os.makedirs(public_images_dir, exist_ok=True)

# Image artifacts generated
images_to_process = [
    {
        "type": "hero",
        "src": r"C:\Users\atind\.gemini\antigravity-ide\brain\7306b223-a9f3-454b-a9a3-fb4bdb18b43b\dha_hero_photo_1788017350280.jpg",
        "filename": f"{slug}-hero-globalaerosols.webp",
        "dimensions": (1200, 630)
    },
    {
        "type": "diagram",
        "src": r"C:\Users\atind\.gemini\antigravity-ide\brain\7306b223-a9f3-454b-a9a3-fb4bdb18b43b\dha_diagram_photo_1788017369261.jpg",
        "filename": f"{slug}-diagram-globalaerosols.webp",
        "dimensions": (900, 500)
    },
    {
        "type": "infographic",
        "src": r"C:\Users\atind\.gemini\antigravity-ide\brain\7306b223-a9f3-454b-a9a3-fb4bdb18b43b\dha_infographic_photo_1788017528632.jpg",
        "filename": f"{slug}-infographic-globalaerosols.webp",
        "dimensions": (900, 500)
    }
]

print("=== STEP 1: Convert to WebP and save locally ===")
for item in images_to_process:
    src_path = item["src"]
    filename = item["filename"]
    dims = item["dimensions"]
    
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")
        
    img = Image.open(src_path).convert("RGB")
    img_resized = img.resize(dims, Image.Resampling.LANCZOS)
    
    dest1 = os.path.join(blog_images_dir, filename)
    dest2 = os.path.join(public_images_dir, filename)
    
    img_resized.save(dest1, "WEBP", quality=92)
    img_resized.save(dest2, "WEBP", quality=92)
    print(f"Saved {filename} ({dims[0]}x{dims[1]}) -> {dest1} & {dest2}")

print("\n=== STEP 2: Upload to Cloudflare R2 ===")
s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

upload_success = True
for item in images_to_process:
    filename = item["filename"]
    local_file = os.path.join(blog_images_dir, filename)
    r2_key = f"images/{slug}/{filename}"
    print(f"Uploading {local_file} to {BUCKET_NAME}/{r2_key}...")
    try:
        s3.upload_file(
            Filename=local_file,
            Bucket=BUCKET_NAME,
            Key=r2_key,
            ExtraArgs={'ContentType': 'image/webp'}
        )
        print(f"SUCCESS: Uploaded {filename}")
    except Exception as e:
        print(f"FAILED to upload {filename}: {e}")
        upload_success = False

print("\n=== STEP 3: Verify CDN URLs ===")
for item in images_to_process:
    url = f"https://cdn.globalaerosols.com/images/{slug}/{item['filename']}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"CDN check {url} -> Status {resp.status} (Length: {len(resp.read())} bytes)")
    except Exception as e:
        print(f"CDN check failed for {url}: {e}")

if upload_success:
    print("\n=== STEP 4: Update meta.json ===")
    meta_path = os.path.join(base_dir, "Blog", slug, "meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
    
    meta_data["r2_upload_status"] = "success"
    if "images_note" in meta_data:
        del meta_data["images_note"]
        
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2, ensure_ascii=False)
    print(f"Updated {meta_path}: r2_upload_status = 'success'")

print("\nAll done!")
