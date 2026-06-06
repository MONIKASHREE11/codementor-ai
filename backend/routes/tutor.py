from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Student, LearnerProfile, CodeSubmission
from memory_manager import get_student_context, update_student_profile
from groq import Groq
import os
from pydantic import BaseModel

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class CodeSubmit(BaseModel):
    student_id: int
    code: str
    language: str = "python"
    topic: str = "general"

@router.post("/tutor/analyze")
def analyze_code(submission: CodeSubmit, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == submission.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    context = get_student_context(db, submission.student_id)

    prompt = f"""You are a personalized coding tutor. Here is what you know about this student:
{context}

The student submitted this {submission.language} code on the topic: {submission.topic}

Code:
{submission.code}

Analyze the code. Point out errors, explain concepts they may have misunderstood, and give an encouraging personalized explanation. End with one small challenge to improve their understanding."""

    message = client.chat.completions.create(
        model="llama3-70b-8192",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    feedback = message.choices[0].message.content

    new_submission = CodeSubmission(
        student_id=submission.student_id,
        code_submitted=submission.code,
        language=submission.language,
        topic=submission.topic,
        session_number=context.get("sessions_count", 0) + 1
    )
    db.add(new_submission)
    db.commit()

    update_student_profile(db, submission.student_id)

    return {"feedback": feedback, "session": new_submission.session_number}