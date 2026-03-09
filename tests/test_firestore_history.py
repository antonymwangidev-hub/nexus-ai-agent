import json

from app.services.content_pipeline import generate_social_content_pack
from app.services.firestore_service import list_content_history, get_content_history


def main():
    prompt = (
        "Create an Instagram promo for a student innovation meetup. "
        "Make it modern, exciting, and campus-friendly."
    )

    result = generate_social_content_pack(prompt)

    print("\nSaved generated result:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nRecent history:\n")
    history = list_content_history(limit=5)
    print(json.dumps(history, indent=2, ensure_ascii=False))

    doc_id = result["firestore_document_id"]
    single = get_content_history(doc_id)

    print("\nFetched single record:\n")
    print(json.dumps(single, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
