from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/analysis", tags=["History"])

# Temporary in-memory storage (OK for MVP)
HISTORY_DB = {}


@router.get("/history")
def list_history():
    return list(HISTORY_DB.values())


@router.get("/history/{analysis_id}")
def get_history_detail(analysis_id: str):
    if analysis_id not in HISTORY_DB:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return HISTORY_DB[analysis_id]


@router.post("/save")
def save_analysis(payload: dict):
    analysis_id = str(uuid4())

    record = {
        "id": analysis_id,
        "created_at": datetime.utcnow().isoformat(),
        **payload,
    }

    HISTORY_DB[analysis_id] = record
    return record
