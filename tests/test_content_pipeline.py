import json
from app.services.content_pipeline import generate_social_content_pack


def main():
    prompt = (
        "Create an Instagram promo for a new AI graphic design class for university students. "
        "Tone should be exciting, modern, and inspiring."
    )

    result = generate_social_content_pack(prompt)

    print("\nFinal content pack:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
