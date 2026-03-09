from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from app.config import PROJECT_ID

COLLECTION_NAME = "content_history"


def get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def save_content_history(record: Dict[str, Any]) -> Dict[str, Any]:
    db = get_firestore_client()

    payload = dict(record)
    payload["created_at"] = datetime.now(timezone.utc).isoformat()

    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_ref.set(payload)

    return {
        "collection": COLLECTION_NAME,
        "document_id": doc_ref.id,
    }


def list_content_history(limit: int = 10) -> List[Dict[str, Any]]:
    db = get_firestore_client()

    docs = (
        db.collection(COLLECTION_NAME)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    results: List[Dict[str, Any]] = []
    for doc in docs:
        item = doc.to_dict()
        item["document_id"] = doc.id
        results.append(item)

    return results


def get_content_history(document_id: str) -> Optional[Dict[str, Any]]:
    db = get_firestore_client()

    doc_ref = db.collection(COLLECTION_NAME).document(document_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return None

    result = snapshot.to_dict()
    result["document_id"] = snapshot.id
    return result
