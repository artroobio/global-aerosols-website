"""
Uploads the 3 blog images for a given slug to the R2 bucket, reading
credentials from the project .env file (never hardcode credentials here).

Usage: python upload_slug_to_r2.py <slug>
"""
import os
import sys

import boto3
from botocore.client import Config

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")


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


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_slug_to_r2.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    env = load_env(ENV_PATH)

    account_id = env["CLOUDFLARE_ACCOUNT_ID"]
    access_key = env["CLOUDFLARE_R2_ACCESS_KEY_ID"]
    secret_key = env["CLOUDFLARE_R2_SECRET_ACCESS_KEY"]
    bucket = env["CLOUDFLARE_R2_BUCKET_NAME"]

    s3 = boto3.client(
        service_name="s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    images_dir = os.path.join(PROJECT_ROOT, "Blog", slug, "images")
    if not os.path.isdir(images_dir):
        print(f"Images directory not found: {images_dir}")
        sys.exit(1)

    uploaded = []
    for filename in sorted(os.listdir(images_dir)):
        if not filename.endswith(".webp"):
            continue
        filepath = os.path.join(images_dir, filename)
        r2_key = f"images/{slug}/{filename}"
        print(f"Uploading {filename} -> {bucket}/{r2_key} ...")
        s3.upload_file(
            Filename=filepath,
            Bucket=bucket,
            Key=r2_key,
            ExtraArgs={"ContentType": "image/webp"},
        )
        uploaded.append(r2_key)
        print("  done.")

    print(f"\nUploaded {len(uploaded)} file(s).")
    for key in uploaded:
        print(f"  https://cdn.globalaerosols.com/{key}")


if __name__ == "__main__":
    main()
