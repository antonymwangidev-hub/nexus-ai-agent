from __future__ import annotations

import asyncio
import base64
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google.genai import types

from app.config import MODEL_NAME
from app.live.live_session import (
    LIVE_MODEL,
    LIVE_MODEL_FALLBACKS,
    SYSTEM_INSTRUCTION,
    build_live_client,
    extract_latest_final_brief,
)

router = APIRouter()


async def safe_send_json(websocket: WebSocket, payload: dict[str, Any]) -> bool:
    """
    Send JSON safely. Returns False if the client is already disconnected.
    """
    try:
        await websocket.send_text(json.dumps(payload))
        return True
    except WebSocketDisconnect:
        return False
    except Exception:
        return False


def format_transcript_for_fallback(transcript: list[dict[str, str]]) -> str:
    history_lines = []
    for item in transcript:
        role = "User" if item.get("role") == "user" else "Assistant"
        text = item.get("text", "").strip()
        if text:
            history_lines.append(f"{role}: {text}")

    if not history_lines:
        return ""

    return "\n".join(history_lines)


@router.websocket("/ws/live/{client_id}")
async def live_websocket(websocket: WebSocket, client_id: str):
    await websocket.accept()

    transcript: list[dict[str, str]] = []

    try:
        client = build_live_client()
    except Exception as e:
        await safe_send_json(
            websocket,
            {
                "type": "system",
                "message": f"Live session init error: {str(e)}",
            },
        )
        return

    # Try Live API first, fall back to regular API if not available
    use_live_api = True
    session = None

    config = {
        "response_modalities": ["TEXT"],
        "system_instruction": SYSTEM_INSTRUCTION,
    }

    async def process_message_loop():
        nonlocal session, use_live_api
        while True:
            try:
                raw_message = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception:
                break

            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                still_connected = await safe_send_json(
                    websocket,
                    {
                        "type": "system",
                        "message": "Invalid live message received.",
                    },
                )
                if not still_connected:
                    break
                continue

            msg_type = data.get("type")

            if msg_type == "ping":
                still_connected = await safe_send_json(
                    websocket,
                    {
                        "type": "pong",
                        "message": "alive",
                    },
                )
                if not still_connected:
                    break
                continue

            if msg_type == "get_transcript":
                still_connected = await safe_send_json(
                    websocket,
                    {
                        "type": "transcript",
                        "transcript": transcript,
                        "final_brief": extract_latest_final_brief(transcript),
                    },
                )
                if not still_connected:
                    break
                continue

            if msg_type != "user_text":
                still_connected = await safe_send_json(
                    websocket,
                    {
                        "type": "system",
                        "message": f"Unknown live message type: {msg_type}",
                    },
                )
                if not still_connected:
                    break
                continue

            text = (data.get("text") or "").strip()
            image_base64 = data.get("image_base64")
            image_mime_type = data.get("image_mime_type") or "image/png"
            image_name = data.get("image_name") or "reference_image"

            if not text and not image_base64:
                continue

            # Preserve history separately before appending current user turn
            previous_history = format_transcript_for_fallback(transcript)

            parts: list[types.Part] = []

            if text:
                parts.append(types.Part.from_text(text=text))
                transcript.append({"role": "user", "text": text})

            if image_base64:
                try:
                    image_bytes = base64.b64decode(image_base64)
                    parts.append(
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=image_mime_type,
                        )
                    )
                    transcript.append(
                        {
                            "role": "user",
                            "text": f"[Attached image: {image_name}]",
                        }
                    )
                except Exception:
                    pass

            # Handle response based on API type
            if use_live_api and session:
                # Use Live API
                try:
                    await session.send_client_content(
                        turns=types.Content(
                            role="user",
                            parts=parts,
                        ),
                        turn_complete=True,
                    )
                except Exception as e:
                    still_connected = await safe_send_json(
                        websocket,
                        {
                            "type": "system",
                            "message": f"Live session error: {str(e)}",
                        },
                    )
                    if not still_connected:
                        break
                    continue

                chunks: list[str] = []
                try:
                    async for response in session.receive():
                        if getattr(response, "text", None):
                            chunks.append(response.text)

                        server_content = getattr(response, "server_content", None)
                        if server_content and getattr(server_content, "turn_complete", False):
                            break

                except Exception as e:
                    still_connected = await safe_send_json(
                        websocket,
                        {
                            "type": "system",
                            "message": f"Live session error: {str(e)}",
                        },
                    )
                    if not still_connected:
                        break
                    continue

                reply = "".join(chunks).strip()
            else:
                # Use regular generateContent API with model fallback
                reply = None

                # Build fallback text history to preserve context across turns
                fallback_parts: list[types.Part] = []
                if previous_history:
                    fallback_parts.append(
                        types.Part.from_text(
                            text=f"Conversation history:\n{previous_history}\n---\n"
                        )
                    )

                if text:
                    # Include current user turn explicitly (new request)
                    fallback_parts.append(types.Part.from_text(text=f"User: {text}\nAssistant:"))

                if image_base64:
                    try:
                        image_bytes = base64.b64decode(image_base64)
                        fallback_parts.append(
                            types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type)
                        )
                    except Exception:
                        pass

                # If fallback parts are empty, use current-turn parts as fallback.
                contents_to_send = fallback_parts if fallback_parts else parts

                models_to_try = [LIVE_MODEL] + LIVE_MODEL_FALLBACKS + [MODEL_NAME]
                models_to_try = list(dict.fromkeys(models_to_try))  # keep order, remove duplicates

                for model in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model,
                            contents=contents_to_send,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_INSTRUCTION,
                                temperature=0.7,
                            ),
                        )

                        reply = response.text.strip() if response.text else "I apologize, but I couldn't generate a response."
                        break  # Success, exit the loop

                    except Exception:
                        # Try next model
                        continue

                if reply is None:
                    # All models failed
                    still_connected = await safe_send_json(
                        websocket,
                        {
                            "type": "system",
                            "message": "Response generation failed for all available models.",
                        },
                    )
                    if not still_connected:
                        break
                    continue

            if reply:
                transcript.append({"role": "assistant", "text": reply})

            still_connected = await safe_send_json(
                websocket,
                {
                    "type": "assistant_text",
                    "message": reply,
                    "transcript": transcript,
                    "final_brief": extract_latest_final_brief(transcript),
                },
            )
            if not still_connected:
                break

    # Prefer Live API; if it fails to connect, run fallback loop using generate_content.
    live_models_to_try = list(dict.fromkeys([LIVE_MODEL] + LIVE_MODEL_FALLBACKS + [MODEL_NAME]))
    live_session = None
    connected_live_model = None

    for model in live_models_to_try:
        live_session_ctx = client.aio.live.connect(model=model, config=config)
        try:
            async with asyncio.timeout(12):
                live_session = await live_session_ctx.__aenter__()

            session = live_session
            connected_live_model = model

            await safe_send_json(
                websocket,
                {
                    "type": "system",
                    "message": f"Live text session connected (model={model}).",
                },
            )

            try:
                await process_message_loop()
            finally:
                await live_session_ctx.__aexit__(None, None, None)

            return

        except Exception:
            if live_session is not None:
                try:
                    await live_session_ctx.__aexit__(None, None, None)
                except Exception:
                    pass
            live_session = None
            continue

    # Live mode couldn't connect using any candidate model, fallback to normal generation.
    use_live_api = False

    # Do not emit fallback system message by default in user-facing UI.
    # This keeps the session cleaner and avoids confusing users when the backend fallback is internal.

    try:
        await process_message_loop()
    except WebSocketDisconnect:
        pass
    except Exception as outer_e:
        await safe_send_json(
            websocket,
            {
                "type": "system",
                "message": f"Live session error: {str(outer_e)}",
            },
        )

