from fastapi import FastAPI
from app.routes.analyze_page import router as analyze_router

app = FastAPI(title="Rook Lite Backend")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(analyze_router)
