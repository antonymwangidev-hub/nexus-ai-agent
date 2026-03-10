from __future__ import annotations

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.live.live_session import (
    build_live_client,
    extract_latest_final_brief,
    LIVE_MODEL,
    SYSTEM_INSTRUCTION,
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
                await websocket.send_text(json.dumps({
                    "type": "system",
                    "message": "Live text session connected."
                }))
            except WebSocketDisconnect:
                return

            while True:
                try:
                    raw_message = await websocket.receive_text()
                except WebSocketDisconnect:
                    break

                data = json.loads(raw_message)
                msg_type = data.get("type")

                if msg_type == "user_text":
                    text = (data.get("text") or "").strip()
                    if not text:
                        continue

                    transcript.append({"role": "user", "text": text})

                    await session.send_client_content(
                        turns={
                            "role": "user",
                            "parts": [{"text": text}],
                        },
                        turn_complete=True,
                    )

                    chunks: list[str] = []

                    async for response in session.receive():
                        if hasattr(response, "text") and response.text:
                            chunks.append(response.text)

                        server_content = getattr(response, "server_content", None)
                        if server_content and getattr(server_content, "turn_complete", False):
                            break

                    reply = "".join(chunks).strip()

                    if reply:
                        transcript.append({"role": "assistant", "text": reply})

                    try:
                        await websocket.send_text(json.dumps({
                            "type": "assistant_text",
                            "message": reply,
                            "transcript": transcript,
                            "final_brief": extract_latest_final_brief(transcript),
                        }))
                    except WebSocketDisconnect:
                        break

                elif msg_type == "get_transcript":
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "transcript",
                            "transcript": transcript,
                            "final_brief": extract_latest_final_brief(transcript),
                        }))
                    except WebSocketDisconnect:
                        break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "system",
                "message": f"Live session error: {str(e)}"
            }))
        except Exception:
            pass
