# app/utils/asset_detector.py

from urllib.parse import urlparse


def detect_asset_type(url: str) -> str:
    if not url:
        return "unknown"

    parsed = urlparse(url.lower())
    domain = parsed.netloc
    path = parsed.path

    if "instagram.com" in domain:
        return "instagram_profile"

    if "linkedin.com" in domain:
        if "/company/" in path:
            return "linkedin_company"
        return "linkedin_profile"

    if "twitter.com" in domain or "x.com" in domain:
        return "x_profile"

    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube_channel"

    if "reddit.com" in domain:
        if "/r/" in path:
            return "reddit_community"
        return "reddit_profile"

    return "website"
