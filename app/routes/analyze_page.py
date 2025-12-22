import json
import os
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.llm.openrouter_client import call_llm

# --------------------------------------------------
# Router
# --------------------------------------------------
router = APIRouter(prefix="/analysis", tags=["Analysis"])

# --------------------------------------------------
# Storage config
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
# HISTORY MODELS
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
# UTILITIES
# --------------------------------------------------
def read_analyses() -> List[dict]:
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def write_analyses(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --------------------------------------------------
# ANALYZE PAGE (AI)
# --------------------------------------------------
@router.post("/page")
def analyze_page(data: AnalyzePageRequest):
    prompt = f"""
You are a senior marketing strategist and startup advisor.

Perform a deep, structured audit of the website.

STRICT RULES:
- Respond ONLY with valid JSON
- NO markdown
- NO explanations outside JSON
- Follow the schema EXACTLY
- Scores must be out of 10 (allow 1 decimal)

JSON SCHEMA:
{{
  "what_this_site_is": "string",
  "target_audience": "string",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "improvements": ["string"],
  "seo_metadata_feedback": "string",
  "social_presence_analysis": "string",
  "marketing_verdict": "string",
  "investor_verdict": "string",
  "overall_score": number
}}

INPUT DATA:
URL: {data.url}
TITLE: {data.page_content.title}
META DESCRIPTION: {data.page_content.meta_description}
HEADINGS: {data.page_content.headings}
BODY TEXT: {data.page_content.body_text}
CTAs: {data.page_content.cta_texts}
SOCIAL LINKS: {data.page_content.social_links}

USER GOAL:
{data.user_goal if data.user_goal else "Infer the primary business goal."}
"""

    raw_response = call_llm(prompt)

    try:
        analysis = json.loads(raw_response)

        score = float(analysis.get("overall_score", 0))
        analysis["overall_score"] = round(min(max(score, 0), 10), 1)

        return analysis

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI response was invalid or improperly formatted"
        )


# --------------------------------------------------
# SAVE ANALYSIS (HISTORY)
# --------------------------------------------------
@router.post("/save")
def save_analysis(payload: dict):
    try:
        analyses = read_analyses()

        new_entry = SavedAnalysis(
            id=str(uuid4()),
            url=payload.get("url"),
            analysis=payload.get("analysis"),
            score=float(payload.get("analysis", {}).get("overall_score", 0)),
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
