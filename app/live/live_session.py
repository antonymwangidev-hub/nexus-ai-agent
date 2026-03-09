from __future__ import annotations

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
# Live API works against the global endpoint in the official Vertex AI example
LOCATION = "global"

# Use the documented text Live model from the Vertex AI Live API reference
LIVE_MODEL = "gemini-2.0-flash-live-preview-04-09"

SYSTEM_INSTRUCTION = """
You are NEXUS AI Agent in Live Mode.

Your role is to act like a real-time creative strategist for social content creation.
Ask concise clarifying questions to improve the user's campaign brief.

Your goals:
- understand the platform
- understand the audience
- understand the tone
- understand the goal of the post
- understand whether a logo/image/uploaded asset should influence design
- help the user arrive at a polished final creative brief

Important behavior:
- Be concise and interactive.
- Ask one or two useful questions at a time.
- Avoid long essays.
- Keep the conversation practical and production-focused.
- When enough detail is available, clearly say:
  FINAL_BRIEF_READY
  followed by a polished final brief the generation system can use.
"""

def build_live_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

def extract_latest_final_brief(transcript: list[dict[str, str]]) -> str | None:
    for item in reversed(transcript):
        if item["role"] == "assistant" and "FINAL_BRIEF_READY" in item["text"]:
            return item["text"]
    return None
