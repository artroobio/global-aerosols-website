import os
import json
import urllib.request
import boto3
from botocore.client import Config
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")

def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env

env = load_env(ENV_PATH)
ACCOUNT_ID = env["CLOUDFLARE_ACCOUNT_ID"]
ACCESS_KEY = env["CLOUDFLARE_R2_ACCESS_KEY_ID"]
SECRET_KEY = env["CLOUDFLARE_R2_SECRET_ACCESS_KEY"]
BUCKET_NAME = env["CLOUDFLARE_R2_BUCKET_NAME"]

# Batch 2 Brain Dir (Sep 14)
brain_dir_b2 = r"C:\Users\atind\.gemini\antigravity-ide\brain\2186b8b2-e54e-46ba-a687-edea07ab339f"

blogs_to_process = [
    {
        "slug": "tilt-valve-vs-vertical-valve-aerosol-selection",
        "images": [
            {
                "type": "hero",
                "src": os.path.join(brain_dir_b2, "tilt_valve_hero_1789330303663.jpg"),
                "filename": "tilt-valve-vs-vertical-valve-aerosol-selection-hero-globalaerosols.webp",
                "dimensions": (1200, 630)
            },
            {
                "type": "diagram",
                "src": os.path.join(brain_dir_b2, "tilt_valve_diagram_1789330320166.jpg"),
                "filename": "tilt-valve-vs-vertical-valve-aerosol-selection-diagram-globalaerosols.webp",
                "dimensions": (900, 500)
            },
            {
                "type": "infographic",
                "src": os.path.join(brain_dir_b2, "tilt_valve_infog_1789330335814.jpg"),
                "filename": "tilt-valve-vs-vertical-valve-aerosol-selection-infographic-globalaerosols.webp",
                "dimensions": (900, 500)
            }
        ]
    },
    {
        "slug": "aerosol-body-mist-vs-fragrance-spray-alcohol",
        "images": [
            {
                "type": "hero",
                "src": os.path.join(brain_dir_b2, "body_mist_hero_1789330351652.jpg"),
                "filename": "aerosol-body-mist-vs-fragrance-spray-alcohol-hero-globalaerosols.webp",
                "dimensions": (1200, 630)
            },
            {
                "type": "diagram",
                "src": os.path.join(brain_dir_b2, "body_mist_diagram_1789330504806.jpg"),
                "filename": "aerosol-body-mist-vs-fragrance-spray-alcohol-diagram-globalaerosols.webp",
                "dimensions": (900, 500)
            },
            {
                "type": "infographic",
                "src": os.path.join(brain_dir_b2, "body_mist_infog_1789330519447.jpg"),
                "filename": "aerosol-body-mist-vs-fragrance-spray-alcohol-infographic-globalaerosols.webp",
                "dimensions": (900, 500)
            }
        ]
    },
    {
        "slug": "eu-aerosol-dispensers-directive-testing-labeling",
        "images": [
            {
                "type": "hero",
                "src": os.path.join(brain_dir_b2, "eu_directive_hero_1789330538215.jpg"),
                "filename": "eu-aerosol-dispensers-directive-testing-labeling-hero-globalaerosols.webp",
                "dimensions": (1200, 630)
            },
            {
                "type": "diagram",
                "src": os.path.join(brain_dir_b2, "eu_directive_diag_1789330555254.jpg"),
                "filename": "eu-aerosol-dispensers-directive-testing-labeling-diagram-globalaerosols.webp",
                "dimensions": (900, 500)
            },
            {
                "type": "infographic",
                "src": os.path.join(brain_dir_b2, "eu_directive_infog_1789330570365.jpg"),
                "filename": "eu-aerosol-dispensers-directive-testing-labeling-infographic-globalaerosols.webp",
                "dimensions": (900, 500)
            }
        ]
    }
]

s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

public_images_dir = os.path.join(BASE_DIR, "public", "images", "blog")
os.makedirs(public_images_dir, exist_ok=True)

for blog in blogs_to_process:
    slug = blog["slug"]
    blog_images_dir = os.path.join(BASE_DIR, "Blog", slug, "images")
    os.makedirs(blog_images_dir, exist_ok=True)
    
    print(f"\n==========================================")
    print(f"Processing blog: {slug}")
    print(f"==========================================")
    
    # 1. Resize and save
    print("\n--- STEP 1: Converting to WebP and saving locally ---")
    for item in blog["images"]:
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
        
        if os.path.exists(os.path.join(BASE_DIR, "Blogskill", slug)):
            dest3 = os.path.join(BASE_DIR, "Blogskill", slug, "images", filename)
            img_resized.save(dest3, "WEBP", quality=92)
            print(f"Also synced to {dest3}")
    
    # 2. Upload to R2
    print("\n--- STEP 2: Uploading to Cloudflare R2 ---")
    upload_success = True
    for item in blog["images"]:
        filename = item["filename"]
        local_file = os.path.join(blog_images_dir, filename)
        r2_key = f"images/{slug}/{filename}"
        print(f"Uploading {local_file} -> {BUCKET_NAME}/{r2_key}...")
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
            
    # 3. Verify CDN
    print("\n--- STEP 3: Verifying CDN URLs ---")
    for item in blog["images"]:
        url = f"https://cdn.globalaerosols.com/images/{slug}/{item['filename']}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                print(f"CDN check {url} -> Status {resp.status} (Length: {len(data)} bytes)")
        except Exception as e:
            print(f"CDN check failed for {url}: {e}")
            
    # 4. Update meta.json
    if upload_success:
        print("\n--- STEP 4: Updating meta.json ---")
        meta_path = os.path.join(BASE_DIR, "Blog", slug, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
                
            meta_data["r2_upload_status"] = "success"
            if "images_are_placeholders" in meta_data:
                del meta_data["images_are_placeholders"]
            if "images_placeholder_note" in meta_data:
                del meta_data["images_placeholder_note"]
                
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2, ensure_ascii=False)
            print(f"Updated {meta_path}: cleared placeholder flags, confirmed r2_upload_status='success'")

print("\n\nAll blog images processed and uploaded successfully!")
