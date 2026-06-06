from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("LearnerProfile", back_populates="student", uselist=False)
    submissions = relationship("CodeSubmission", back_populates="student")


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    skill_level = Column(String, default="beginner")
    weak_topics = Column(JSON, default=[])
    strong_topics = Column(JSON, default=[])
    misconceptions = Column(JSON, default=[])
    explanation_style = Column(String, default="simple")
    sessions_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="profile")


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    session_number = Column(Integer)
    code_submitted = Column(String)
    language = Column(String, default="python")
    errors_found = Column(JSON, default=[])
    topic = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="submissions")