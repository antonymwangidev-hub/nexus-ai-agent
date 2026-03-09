from pathlib import Path
import os

from dotenv import load_dotenv
from google.cloud import storage

from app.config import PROJECT_ID

load_dotenv()

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")


def get_storage_client():
    return storage.Client(project=PROJECT_ID)


def upload_file_to_gcs(local_file_path: str, destination_blob_name: str | None = None) -> dict:
    if not BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME is not set in the environment.")

    local_path = Path(local_file_path)

    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {local_file_path}")

    if destination_blob_name is None:
        destination_blob_name = f"generated-images/{local_path.name}"

    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(str(local_path))

    return {
        "bucket_name": BUCKET_NAME,
        "blob_name": destination_blob_name,
        "gs_uri": f"gs://{BUCKET_NAME}/{destination_blob_name}",
        "image_url": f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}",
    }


def upload_user_asset_to_gcs(local_file_path: str) -> dict:
    local_path = Path(local_file_path)
    return upload_file_to_gcs(
        local_file_path=str(local_path),
        destination_blob_name=f"user-assets/{local_path.name}",
    )
