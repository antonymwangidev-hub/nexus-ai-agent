import json
from app.services.content_pipeline import generate_social_content_pack


if __name__ == "__main__":
    print("SocialFusion Full Pipeline CLI")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            result = generate_social_content_pack(user_input)
            print("\nFinal Content Pack:\n")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n" + "-" * 60 + "\n")
        except Exception as e:
            print(f"\nError: {e}\n")
