from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import student, tutor
from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodeMentor AI",
    description="Personalized Programming Tutor Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(tutor.router, prefix="/tutor", tags=["Tutor"])

@app.get("/")
def root():
    return {"message": "CodeMentor AI is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}