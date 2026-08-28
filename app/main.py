from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.report import router as report_router

app = FastAPI(title="MUDRA Risk Assessment Services", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "mudra-risk-services"}
