from __future__ import annotations

import base64
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google.genai import types

from app.live.live_session import (
    LIVE_MODEL,
    SYSTEM_INSTRUCTION,
    build_live_client,
    extract_latest_final_brief,
)

router = APIRouter()


@router.websocket("/ws/live/{client_id}")
async def live_websocket(websocket: WebSocket, client_id: str):
    await websocket.accept()

    client = build_live_client()
    transcript: list[dict[str, str]] = []

    config = {
        "response_modalities": ["TEXT"],
        "system_instruction": SYSTEM_INSTRUCTION,
    }

    try:
        async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
            try:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "system",
                            "message": "Live text session connected.",
                        }
                    )
                )
            except WebSocketDisconnect:
                return

            while True:
                try:
                    raw_message = await websocket.receive_text()
                except WebSocketDisconnect:
                    break

                try:
                    data = json.loads(raw_message)
                except json.JSONDecodeError:
                    try:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "system",
                                    "message": "Invalid live message received.",
                                }
                            )
                        )
                    except WebSocketDisconnect:
                        break
                    continue

                msg_type = data.get("type")

                if msg_type == "user_text":
                    text = (data.get("text") or "").strip()
                    image_base64 = data.get("image_base64")
                    image_mime_type = data.get("image_mime_type") or "image/png"
                    image_name = data.get("image_name") or "reference_image"

                    if not text and not image_base64:
                        continue

                    parts: list[types.Part] = []

                    if text:
                        parts.append(types.Part.from_text(text=text))

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
                            # Ignore malformed image payloads without killing the live session
                            pass

                    if text:
                        transcript.append({"role": "user", "text": text})

                    try:
                        await session.send_client_content(
                            turns=types.Content(
                                role="user",
                                parts=parts,
                            ),
                            turn_complete=True,
                        )
                    except Exception as e:
                        try:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "system",
                                        "message": f"Live session error: {str(e)}",
                                    }
                                )
                            )
                        except WebSocketDisconnect:
                            break
                        continue

                    chunks: list[str] = []

                    try:
                        async for response in session.receive():
                            if hasattr(response, "text") and response.text:
                                chunks.append(response.text)

                            server_content = getattr(response, "server_content", None)
                            if server_content and getattr(server_content, "turn_complete", False):
                                break
                    except Exception as e:
                        try:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "system",
                                        "message": f"Live session error: {str(e)}",
                                    }
                                )
                            )
                        except WebSocketDisconnect:
                            break
                        continue

                    reply = "".join(chunks).strip()

                    if reply:
                        transcript.append({"role": "assistant", "text": reply})

                    try:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "assistant_text",
                                    "message": reply,
                                    "transcript": transcript,
                                    "final_brief": extract_latest_final_brief(transcript),
                                }
                            )
                        )
                    except WebSocketDisconnect:
                        break

                elif msg_type == "get_transcript":
                    try:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "transcript",
                                    "transcript": transcript,
                                    "final_brief": extract_latest_final_brief(transcript),
                                }
                            )
                        )
                    except WebSocketDisconnect:
                        break

                else:
                    try:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "system",
                                    "message": f"Unknown live message type: {msg_type}",
                                }
                            )
                        )
                    except WebSocketDisconnect:
                        break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "system",
                        "message": f"Live session error: {str(e)}",
                    }
                )
            )
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
