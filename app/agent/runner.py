import json
import mimetypes
from pathlib import Path

from google import genai
from google.genai import types

from app.config import PROJECT_ID, LOCATION, USE_VERTEXAI, MODEL_NAME
from app.agent.prompt import SYSTEM_INSTRUCTION
from app.agent.schemas import SocialContentOutput


def build_client():
    if USE_VERTEXAI:
        return genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )
    return genai.Client()


def _build_contents(user_prompt: str, image_path: str | None = None):
    if not image_path:
        return user_prompt

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Uploaded image not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    mime_type = mime_type or "image/png"

    image_bytes = path.read_bytes()

    return [
        user_prompt,
        types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        ),
    ]


def run_social_prompt(user_prompt: str, image_path: str | None = None) -> dict:
    client = build_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=SocialContentOutput,
        ),
        contents=_build_contents(user_prompt, image_path),
    )

    if hasattr(response, "parsed") and response.parsed:
        if hasattr(response.parsed, "model_dump"):
            return response.parsed.model_dump()
        return dict(response.parsed)

    return json.loads(response.text)
