from __future__ import annotations

import base64
import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from google import genai

from app.config import PROJECT_ID, LOCATION

OUTPUT_DIR = Path("outputs/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_genai_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )


def ensure_hashtag_prefix(hashtags: list[str]) -> list[str]:
    cleaned = []
    for tag in hashtags:
        tag = tag.strip()
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = f"#{tag}"
        cleaned.append(tag)
    return cleaned


def prepare_image_generation_payload(content_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "prompt": content_data.get("image_prompt", ""),
        "platform": content_data.get("platform", ""),
        "tone": content_data.get("tone", ""),
        "target_audience": content_data.get("target_audience", ""),
    }


def _guess_extension(mime_type: str | None) -> str:
    if not mime_type:
        return ".png"
    ext = mimetypes.guess_extension(mime_type)
    return ext if ext else ".png"


def generate_image_from_prompt(prompt: str) -> str:
    """
    Generate an image with Vertex AI and save it locally.
    Returns the saved file path.
    """
    client = build_genai_client()

    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config={
            "number_of_images": 1,
        },
    )

    generated_image = response.generated_images[0]
    image_bytes = generated_image.image.image_bytes
    mime_type = getattr(generated_image.image, "mime_type", "image/png")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = _guess_extension(mime_type)
    output_path = OUTPUT_DIR / f"socialfusion_{timestamp}{extension}"

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return str(output_path)
