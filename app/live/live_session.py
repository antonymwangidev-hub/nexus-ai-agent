from __future__ import annotations

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")

LOCATION = "global"
LIVE_MODEL = "gemini-2.0-flash-live-preview-04-09"

SYSTEM_INSTRUCTION = """
You are NEXUS AI Agent in Live Mode.

You are a real-time creative strategist for social content creation.

Your job:
- ask concise clarifying questions
- understand platform, audience, tone, visual style, and campaign goal
- help the user form a polished final creative brief

Important behavior:
- Keep replies short, practical, and interactive.
- Ask one or two useful questions at a time.
- When enough detail is available, clearly include:

FINAL_BRIEF_READY

Then provide a polished final brief suitable for the content generation pipeline.
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
