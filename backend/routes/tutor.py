from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Student, LearnerProfile, CodeSubmission
from memory_manager import (
    build_prompt_with_memory,
    get_student_context,
    update_learner_profile,
)
from groq import Groq
from groq import GroqError, NotFoundError
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel
import json
import logging
import os

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
logger = logging.getLogger(__name__)

class CodeSubmit(BaseModel):
    student_id: int
    code: str
    language: str = "python"
    topic: str = "general"


def _parse_tutor_response(raw_content: str, default_topic: str, default_skill: str):
    cleaned = raw_content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines else lines
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    decoder = json.JSONDecoder()
    parsed = None
    for index, character in enumerate(cleaned):
        if character != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and isinstance(candidate.get("feedback"), str):
            parsed = candidate
            break

    if parsed is None:
        return {
            "feedback": raw_content,
            "errors_found": [],
            "misconceptions": [],
            "topic": default_topic,
            "skill_estimate": default_skill,
            "strengths": [],
        }

    def string_list(key):
        values = parsed.get(key)
        if not isinstance(values, list):
            return []
        return [
            value.strip()
            for value in values
            if isinstance(value, str) and value.strip()
        ]

    skill = parsed.get("skill_estimate")
    topic = parsed.get("topic")
    return {
        "feedback": parsed["feedback"],
        "errors_found": string_list("errors_found"),
        "misconceptions": string_list("misconceptions"),
        "topic": topic.strip() if isinstance(topic, str) and topic.strip() else default_topic,
        "skill_estimate": (
            skill
            if isinstance(skill, str)
            and skill in {"beginner", "intermediate", "advanced"}
            else default_skill
        ),
        "strengths": string_list("strengths"),
    }


@router.post("/tutor/analyze")
def analyze_code(submission: CodeSubmit, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == submission.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    context = get_student_context(db, submission.student_id)
    prompt = build_prompt_with_memory(
        db,
        submission.student_id,
        submission.code,
        submission.language,
        submission.topic,
    )

    try:
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=2048,
            reasoning_effort="low",
            messages=[{"role": "user", "content": prompt}]
        )
    except NotFoundError as exc:
        logger.warning("Configured Groq model is unavailable: %s", GROQ_MODEL)
        raise HTTPException(
            status_code=503,
            detail="Configured LLM model is unavailable",
        ) from exc
    except GroqError as exc:
        logger.error("Groq request failed")
        raise HTTPException(
            status_code=502,
            detail="LLM request failed",
        ) from exc

    raw_content = message.choices[0].message.content or ""
    result = _parse_tutor_response(
        raw_content,
        submission.topic,
        context.get("skill_level", "beginner"),
    )

    new_submission = CodeSubmission(
        student_id=submission.student_id,
        code_submitted=submission.code,
        language=submission.language,
        topic=result["topic"],
        errors_found=result["errors_found"],
        session_number=context.get("sessions_count", 0) + 1,
    )
    db.add(new_submission)
    db.flush()

    update_learner_profile(
        db,
        submission.student_id,
        new_errors=result["errors_found"],
        topic=result["topic"],
        misconceptions=result["misconceptions"],
        strengths=result["strengths"],
        skill_estimate=result["skill_estimate"],
    )

    return {
        "feedback": result["feedback"],
        "errors_found": result["errors_found"],
        "misconceptions": result["misconceptions"],
        "topic": result["topic"],
        "skill_estimate": result["skill_estimate"],
        "strengths": result["strengths"],
        "session": new_submission.session_number,
    }