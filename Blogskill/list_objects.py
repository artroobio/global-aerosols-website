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

try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    print("Objects in bucket:")
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"- {obj['Key']} ({obj['Size']} bytes)")
    else:
        print("Bucket is empty!")
except Exception as e:
    print(f"Error: {e}")
