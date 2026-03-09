from __future__ import annotations

import tempfile
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

from app.services.content_pipeline import generate_social_content_pack
from app.services.firestore_service import list_content_history, get_content_history
from app.services.upload_service import save_uploaded_file

router = APIRouter()


def build_text_export(data: dict) -> str:
    hashtags = " ".join(data.get("hashtags", []))

    return f"""NEXUS AI Agent Export

Platform:
{data.get("platform", "")}

Target Audience:
{data.get("target_audience", "")}

Tone:
{data.get("tone", "")}

Original Prompt:
{data.get("user_prompt", "")}

Caption:
{data.get("caption", "")}

Hashtags:
{hashtags}

Image Prompt:
{data.get("image_prompt", "")}

Notes:
{data.get("notes", "")}

Generated Image URL:
{data.get("image_url", "")}

Uploaded Image URL:
{data.get("uploaded_image_url", "")}

GCS URI:
{data.get("gcs_uri", "")}

Firestore Document ID:
{data.get("document_id", data.get("firestore_document_id", ""))}
"""


def _download_image_temp(image_url: str) -> str | None:
    if not image_url:
        return None

    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()

        suffix = ".png"
        content_type = response.headers.get("content-type", "")
        if "jpeg" in content_type or "jpg" in content_type:
            suffix = ".jpg"
        elif "webp" in content_type:
            suffix = ".webp"

        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / f"nexus_pdf_image{suffix}"
        temp_path.write_bytes(response.content)
        return str(temp_path)
    except Exception:
        return None


def build_pdf_export(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    title_style.textColor = colors.HexColor("#0f172a")
    heading_style.textColor = colors.HexColor("#2563eb")
    body_style.leading = 16

    story.append(Paragraph("NEXUS AI Agent Export", title_style))
    story.append(Spacer(1, 12))

    logo_path = Path("app/static/nexus-logo.png")
    if logo_path.exists():
        try:
            story.append(Image(str(logo_path), width=1.3 * inch, height=1.3 * inch))
            story.append(Spacer(1, 14))
        except Exception:
            pass

    def add_section(title: str, value: str):
        story.append(Paragraph(title, heading_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph((value or "").replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 12))

    add_section("Platform", data.get("platform", ""))
    add_section("Target Audience", data.get("target_audience", ""))
    add_section("Tone", data.get("tone", ""))
    add_section("Original Prompt", data.get("user_prompt", ""))
    add_section("Caption", data.get("caption", ""))
    add_section("Hashtags", " ".join(data.get("hashtags", [])))
    add_section("Image Prompt", data.get("image_prompt", ""))
    add_section("Notes", data.get("notes", ""))

    uploaded_image_temp = _download_image_temp(data.get("uploaded_image_url", ""))
    if uploaded_image_temp:
        try:
            story.append(Paragraph("Uploaded Reference Image", heading_style))
            story.append(Spacer(1, 6))
            story.append(Image(uploaded_image_temp, width=4.8 * inch, height=4.8 * inch))
            story.append(Spacer(1, 12))
        except Exception:
            pass

    generated_image_temp = _download_image_temp(data.get("image_url", ""))
    if generated_image_temp:
        try:
            story.append(Paragraph("Generated Image", heading_style))
            story.append(Spacer(1, 6))
            story.append(Image(generated_image_temp, width=4.8 * inch, height=4.8 * inch))
            story.append(Spacer(1, 12))
        except Exception:
            pass

    add_section("Generated Image URL", data.get("image_url", ""))
    add_section("Uploaded Image URL", data.get("uploaded_image_url", ""))
    add_section("GCS URI", data.get("gcs_uri", ""))
    add_section(
        "Firestore Document ID",
        data.get("document_id", data.get("firestore_document_id", "")),
    )

    doc.build(story)


@router.get("/")
def root():
    return {"message": "NEXUS AI Agent API is running"}


@router.post("/generate-content-pack")
def generate_content_pack(prompt: str = Form(...), image: UploadFile | None = File(default=None)):
    try:
        uploaded_image_path = None

        if image and image.filename:
            uploaded_image_path = save_uploaded_file(image)

        result = generate_social_content_pack(prompt, uploaded_image_path=uploaded_image_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history(limit: int = 10):
    try:
        return list_content_history(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{document_id}")
def get_history_item(document_id: str):
    try:
        result = get_content_history(document_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{document_id}/export/json")
def export_history_json(document_id: str):
    try:
        result = get_content_history(document_id)
        if result is None:
          raise HTTPException(status_code=404, detail="Record not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{document_id}/export/txt")
def export_history_txt(document_id: str):
    try:
        result = get_content_history(document_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Record not found")

        text_content = build_text_export(result)

        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / f"nexus_export_{document_id}.txt"
        output_path.write_text(text_content, encoding="utf-8")

        return FileResponse(
            path=str(output_path),
            media_type="text/plain",
            filename=f"nexus_export_{document_id}.txt",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{document_id}/export/pdf")
def export_history_pdf(document_id: str):
    try:
        result = get_content_history(document_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Record not found")

        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / f"nexus_export_{document_id}.pdf"

        build_pdf_export(result, str(output_path))

        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=f"nexus_export_{document_id}.pdf",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
