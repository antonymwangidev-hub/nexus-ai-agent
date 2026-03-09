from app.agent.runner import run_social_prompt
from app.services.image_service import (
    ensure_hashtag_prefix,
    prepare_image_generation_payload,
    generate_image_from_prompt,
)
from app.services.storage_service import upload_file_to_gcs, upload_user_asset_to_gcs
from app.services.firestore_service import save_content_history


def generate_social_content_pack(user_prompt: str, uploaded_image_path: str | None = None) -> dict:
    result = run_social_prompt(user_prompt, image_path=uploaded_image_path)

    result["hashtags"] = ensure_hashtag_prefix(result.get("hashtags", []))
    result["warnings"] = []

    if uploaded_image_path:
        result["uploaded_image_path"] = uploaded_image_path
        try:
            uploaded_asset = upload_user_asset_to_gcs(uploaded_image_path)
            result["uploaded_image_gcs_uri"] = uploaded_asset["gs_uri"]
            result["uploaded_image_url"] = uploaded_asset["image_url"]
        except Exception as e:
            result["uploaded_image_gcs_uri"] = None
            result["uploaded_image_url"] = None
            result["warnings"].append(f"Uploaded asset storage failed: {str(e)}")

    image_payload = prepare_image_generation_payload(result)
    generated_image_path = generate_image_from_prompt(image_payload["prompt"])
    result["generated_image_path"] = generated_image_path

    try:
        gcs_upload = upload_file_to_gcs(generated_image_path)
        result["gcs_bucket_name"] = gcs_upload["bucket_name"]
        result["gcs_blob_name"] = gcs_upload["blob_name"]
        result["gcs_uri"] = gcs_upload["gs_uri"]
        result["image_url"] = gcs_upload["image_url"]
    except Exception as e:
        result["gcs_bucket_name"] = None
        result["gcs_blob_name"] = None
        result["gcs_uri"] = None
        result["image_url"] = None
        result["warnings"].append(f"Generated image upload failed: {str(e)}")

    result["user_prompt"] = user_prompt

    try:
        firestore_meta = save_content_history(result)
        result["firestore_collection"] = firestore_meta["collection"]
        result["firestore_document_id"] = firestore_meta["document_id"]
    except Exception as e:
        result["firestore_collection"] = None
        result["firestore_document_id"] = None
        result["warnings"].append(f"Firestore save failed: {str(e)}")

    return result
