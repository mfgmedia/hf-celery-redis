import os
import requests
import boto3
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis broker for Celery
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://localhost:6379/0")

# Initialize Celery
celery = Celery("tasks", broker=REDIS_BROKER)

# Cloudflare R2 Credentials
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

# AUTOMATIC1111 API
AUTOMATIC1111_API = os.getenv("AUTOMATIC1111_API", "https://your-huggingface-space-url")

# Initialize R2 Client
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

def generate_r2_presigned_url(file_key: str, expires_in=3600) -> str:
    """Generate a pre-signed URL for R2 storage."""
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": R2_BUCKET_NAME, "Key": file_key},
        ExpiresIn=expires_in
    )

@celery.task
def process_image_task(file_key: str):
    """Celery Task: Process an image asynchronously."""
    presigned_url = generate_r2_presigned_url(file_key)

    payload = {"init_images": [presigned_url]}
    response = requests.post(f"{AUTOMATIC1111_API}/sdapi/v1/img2img", json=payload)

    if response.status_code != 200:
        return {"error": f"Error processing image: {response.text}"}

    processed_image_path = f"/tmp/processed_{file_key}"
    with open(processed_image_path, "wb") as f:
        f.write(response.content)

    processed_key = f"processed/{file_key}"
    s3.upload_file(processed_image_path, R2_BUCKET_NAME, processed_key)

    processed_url = generate_r2_presigned_url(processed_key)

    return {"processed_image_url": processed_url}
