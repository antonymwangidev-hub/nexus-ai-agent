from app.agent.runner import run_social_prompt
from app.services.image_service import (
    prepare_image_generation_payload,
    generate_image_from_prompt,
    ensure_hashtag_prefix,
)


def main():
    prompt = (
        "Create a LinkedIn post for a startup launching an AI customer support assistant. "
        "Make it professional and persuasive."
    )
    result = run_social_prompt(prompt)

    result["hashtags"] = ensure_hashtag_prefix(result.get("hashtags", []))

    print("Generated content:\n")
    print(result)

    image_payload = prepare_image_generation_payload(result)

    print("\nPrepared image payload:\n")
    print(image_payload)

    print("\nGenerating image...\n")
    saved_path = generate_image_from_prompt(image_payload["prompt"])

    print("Saved image to:\n")
    print(saved_path)


if __name__ == "__main__":
    main()
