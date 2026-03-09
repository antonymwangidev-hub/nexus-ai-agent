def normalize_platform(platform: str) -> str:
    """
    Normalize platform names for consistent prompting.
    """
    if not platform:
        return "Instagram"

    p = platform.strip().lower()

    mapping = {
        "ig": "Instagram",
        "instagram": "Instagram",
        "x": "X",
        "twitter": "X",
        "linkedin": "LinkedIn",
        "facebook": "Facebook",
        "fb": "Facebook",
        "tiktok": "TikTok",
    }

    return mapping.get(p, platform.title())
