from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(upload_file) -> str:
    """
    Save an uploaded file locally and return the saved path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = upload_file.filename.replace(" ", "_")
    output_path = UPLOAD_DIR / f"{timestamp}_{safe_name}"

    with open(output_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(output_path)
