from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze_page import router as analyze_router
from app.routes.history import router as history_router

app = FastAPI(title="Rook Lite Backend")

# ---- CORS (important for extension) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Health / Root ----
@app.get("/")
def root():
    return {"status": "Rook Lite backend running"}

# ---- Routers ----
app.include_router(analyze_router)
app.include_router(history_router)
