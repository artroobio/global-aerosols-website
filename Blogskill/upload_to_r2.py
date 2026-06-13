import os
import boto3
from botocore.client import Config

ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
ACCESS_KEY = "8beb191cae4e25f30042330114a91fd8"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

s3 = boto3.client(
    service_name='s3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

images_dir = r"c:\Users\atind\OneDrive\Documents\Projects\Global Aerosols Website\public\images\blog"

files = os.listdir(images_dir)
print(f"Found {len(files)} files in images directory.")

for file in files:
    if not file.endswith('.webp'):
        continue
    
    # Determine the slug by stripping the suffix and '-globalaerosols.webp'
    slug = None
    for suffix in ["hero", "diagram", "infographic"]:
        end_part = f"-{suffix}-globalaerosols.webp"
        if file.endswith(end_part):
            slug = file[:-len(end_part)]
            break
            
    if not slug:
        print(f"Skipping {file} - could not determine slug.")
        continue
        
    filepath = os.path.join(images_dir, file)
    r2_key = f"images/{slug}/{file}"
    print(f"Uploading {file} to {BUCKET_NAME}/{r2_key}...")
    try:
        s3.upload_file(
            Filename=filepath,
            Bucket=BUCKET_NAME,
            Key=r2_key,
            ExtraArgs={'ContentType': 'image/webp'}
        )
        print(f"Successfully uploaded {file}!")
    except Exception as e:
        print(f"Failed to upload {file}: {e}")
