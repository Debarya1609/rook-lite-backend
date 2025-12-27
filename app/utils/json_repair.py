# app/utils/json_repair.py

import json
import re
from typing import Any


def extract_json_block(text: str) -> str:
    """
    Extract the first valid-looking JSON object from text.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in response")
    return match.group(0)


def clean_common_json_issues(text: str) -> str:
    """
    Fix common LLM JSON issues:
    - Single quotes → double quotes
    - Trailing commas
    """
    # Replace smart quotes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")

    # Replace single quotes with double quotes (best-effort)
    text = re.sub(r"(?<!\\)'", '"', text)

    # Remove trailing commas
    text = re.sub(r",\s*([\]}])", r"\1", text)

    return text


def safe_json_load(raw_text: str) -> Any:
    """
    Safely parse JSON from LLM output with auto-repair.
    """
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block
    extracted = extract_json_block(raw_text)

    # Clean common issues
    cleaned = clean_common_json_issues(extracted)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to repair JSON: {str(e)}")
