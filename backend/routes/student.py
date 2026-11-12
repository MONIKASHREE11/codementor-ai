from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Student, LearnerProfile
from pydantic import BaseModel

router = APIRouter()

class StudentCreate(BaseModel):
    name: str
    email: str

@router.post("/students/register")
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.email == student.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")
    
    new_student = Student(name=student.name, email=student.email)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    profile = LearnerProfile(student_id=new_student.id)
    db.add(profile)
    db.commit()
    
    return {"message": "Student registered", "student_id": new_student.id}

@router.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id, "name": student.name, "email": student.email}


@router.get("/students/{student_id}/profile")
def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profile = db.query(LearnerProfile).filter(
        LearnerProfile.student_id == student_id
    ).first()
    if not profile:
        return {
            "skill_level": "beginner",
            "weak_topics": [],
            "strong_topics": [],
            "misconceptions": [],
            "sessions_count": 0,
        }
    return {
        "skill_level": profile.skill_level,
        "weak_topics": profile.weak_topics or [],
        "strong_topics": profile.strong_topics or [],
        "misconceptions": profile.misconceptions or [],
        "sessions_count": profile.sessions_count or 0,
    }


@router.get("/students/email/{email}")
def get_student_by_email(email: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id, "name": student.name, "email": student.email}