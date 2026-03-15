from __future__ import annotations

import base64
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google.genai import types

from app.live.live_session import (
    LIVE_MODEL,
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

    config = {
        "response_modalities": ["TEXT"],
        "system_instruction": SYSTEM_INSTRUCTION,
    }

    try:
        async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
            connected = await safe_send_json(
                websocket,
                {
                    "type": "system",
                    "message": "Live text session connected.",
                },
            )
            if not connected:
                return

            while True:
                # ---- Receive one client message ----
                try:
                    raw_message = await websocket.receive_text()
                except WebSocketDisconnect:
                    break
                except Exception:
                    # If receive itself fails, end the route quietly.
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

                # ---- Heartbeat / keepalive ----
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

                # ---- Transcript request ----
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

                # ---- Main user message path ----
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
                        # Ignore malformed image input without killing the session.
                        pass

                # ---- Send one turn to Gemini Live ----
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
                    # Keep session alive for next user turn
                    continue

                # ---- Receive Gemini Live response for this turn ----
                chunks: list[str] = []

                try:
                    async for response in session.receive():
                        if getattr(response, "text", None):
                            chunks.append(response.text)

                        server_content = getattr(response, "server_content", None)
                        if server_content and getattr(server_content, "turn_complete", False):
                            break

                except Exception as e:
                    # IMPORTANT:
                    # Do not kill the websocket route here. Report the issue and keep going.
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

    except WebSocketDisconnect:
        # Normal client disconnect
        pass
    except Exception as e:
        # Outer safety net
        await safe_send_json(
            websocket,
            {
                "type": "system",
                "message": f"Live session error: {str(e)}",
            },
        )
