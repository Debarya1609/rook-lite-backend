# app/models/analysis_schema.py

from typing import List, Dict, Any
from pydantic import BaseModel


class AnalysisSection(BaseModel):
    id: str
    title: str
    insights: List[str]


class VerdictBlock(BaseModel):
    marketing: str
    strategic: str


class ScoreBlock(BaseModel):
    value: float
    reasoning: str


class AnalysisResponse(BaseModel):
    asset_type: str
    overview: str
    target_audience: str
    sections: List[AnalysisSection]
    verdicts: VerdictBlock
    score: ScoreBlock
