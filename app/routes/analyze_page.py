import json
import os
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.utils.json_repair import safe_json_load

from app.llm.openrouter_client import generate_analysis

from app.utils.asset_detector import detect_asset_type

# --------------------------------------------------
# Router
# --------------------------------------------------
router = APIRouter(prefix="/analysis", tags=["Analysis"])

# --------------------------------------------------
# Storage config (UNCHANGED)
# --------------------------------------------------
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "analyses.json")

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# --------------------------------------------------
# INPUT MODELS
# --------------------------------------------------
class PageContent(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    headings: List[str] = Field(default_factory=list)
    body_text: Optional[str] = None
    cta_texts: List[str] = Field(default_factory=list)
    social_links: List[str] = Field(default_factory=list)


class AnalyzePageRequest(BaseModel):
    url: Optional[str] = None
    page_content: PageContent
    user_goal: Optional[str] = None

# --------------------------------------------------
# HISTORY MODELS (UNCHANGED)
# --------------------------------------------------
class SavedAnalysis(BaseModel):
    id: str
    url: str
    analysis: dict
    score: float
    created_at: str


class HistoryItem(BaseModel):
    id: str
    url: str
    score: float
    created_at: str

# --------------------------------------------------
# UTILITIES (UNCHANGED)
# --------------------------------------------------
def read_analyses() -> List[dict]:
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def write_analyses(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------------------------------
# ANALYZE PAGE (LEVEL-2 INTELLIGENCE)
# --------------------------------------------------
@router.post("/page")
def analyze_page(data: AnalyzePageRequest):
    try:
        asset_type = detect_asset_type(data.url or "")

        prompt = f"""
You are a senior marketing analyst advising a real business owner.

Speak like a human consultant:
- Calm
- Honest
- Practical
- Slightly opinionated
- No hype, no emojis, no generic AI tone

STRICT RULES:
- Respond ONLY with valid JSON
- No markdown
- No explanations outside JSON
- Follow the schema exactly

ASSET TYPE:
{asset_type}

ANALYSIS MINDSET:
- First understand what this asset is and who it is for
- Then analyze it based on how this platform actually works
- Adapt SEO, CTA, and conversion logic to the platform

INPUT DATA:
URL: {data.url}
TITLE: {data.page_content.title}
META DESCRIPTION: {data.page_content.meta_description}
HEADINGS: {data.page_content.headings}
BODY TEXT: {data.page_content.body_text}
CTAs: {data.page_content.cta_texts}
SOCIAL LINKS: {data.page_content.social_links}

USER GOAL:
{data.user_goal if data.user_goal else "Infer the primary business or growth goal."}

OUTPUT JSON SCHEMA:
{{
  "asset_type": "string",
  "overview": "string",
  "target_audience": "string",
  "sections": [
    {{
      "id": "string",
      "title": "string",
      "insights": ["string"]
    }}
  ],
  "verdicts": {{
    "marketing": "string",
    "strategic": "string"
  }},
  "score": {{
    "value": number,
    "reasoning": "string"
  }}
}}

SCORING RULES:
- Score out of 10 (1 decimal)
- Base score on clarity, trust, positioning, and conversion readiness
- Avoid inflated scores
"""

        raw_response = generate_analysis(prompt)
        analysis = safe_json_load(raw_response)
        # Safety clamp for score
        score_val = float(analysis.get("score", {}).get("value", 0))
        analysis["score"]["value"] = round(min(max(score_val, 0), 10), 1)

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed or AI response invalid: {str(e)}"
        )

# --------------------------------------------------
# SAVE ANALYSIS (HISTORY)
# --------------------------------------------------
@router.post("/save")
def save_analysis(payload: Dict[str, Any]):
    try:
        analyses = read_analyses()

        score_val = float(payload.get("analysis", {}).get("score", {}).get("value", 0))

        new_entry = SavedAnalysis(
            id=str(uuid4()),
            url=payload.get("url"),
            analysis=payload.get("analysis"),
            score=score_val,
            created_at=datetime.utcnow().isoformat()
        )

        analyses.append(new_entry.dict())
        write_analyses(analyses)

        return {"success": True, "id": new_entry.id}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save analysis: {str(e)}"
        )

# --------------------------------------------------
# GET HISTORY LIST
# --------------------------------------------------
@router.get("/history", response_model=List[HistoryItem])
def get_history():
    analyses = read_analyses()

    return [
        HistoryItem(
            id=a["id"],
            url=a["url"],
            score=a["score"],
            created_at=a["created_at"]
        )
        for a in reversed(analyses)
    ]

# --------------------------------------------------
# GET SINGLE HISTORY ITEM
# --------------------------------------------------
@router.get("/history/{analysis_id}")
def get_history_detail(analysis_id: str):
    analyses = read_analyses()

    for item in analyses:
        if item["id"] == analysis_id:
            return item

    raise HTTPException(status_code=404, detail="Analysis not found")
