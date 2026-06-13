import boto3
from botocore.client import Config

# Configuration
ACCOUNT_ID = "0cd947375cc0cfb75d26ddf1eff7dd8c"
SECRET_KEY = "7dd9c0f86cec5890680c3e874c8fde0d4c49af0616d7d6c0b47bf959078b54f6"
BUCKET_NAME = "global-aerosols-website"

original_key = "8beb191cae4e25f30042330114a91fd8a"

# Variations
variations = {
    "Remove first character": original_key[1:],
    "Remove last character": original_key[:-1]
}

for name, key in variations.items():
    print(f"Testing variation: {name} ({key})")
    print(f"Length of key: {len(key)}")
    try:
        s3 = boto3.client(
            service_name='s3',
            endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=key,
            aws_secret_access_key=SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        # Attempt to list buckets or head bucket to verify
        s3.list_buckets()
        print(f"SUCCESS! The correct key is: {key}\n")
    except Exception as e:
        print(f"FAILED: {e}\n")
