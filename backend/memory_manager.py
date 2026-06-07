from sqlalchemy.orm import Session
from models import Student, LearnerProfile, CodeSubmission
import json

def get_learner_profile(db: Session, student_id: int):
    profile = db.query(LearnerProfile).filter(
        LearnerProfile.student_id == student_id
    ).first()
    return profile

def build_prompt_with_memory(db: Session, student_id: int, new_code: str, language: str):
    profile = get_learner_profile(db, student_id)
    
    if not profile:
        context = "This is a new student. No history available yet."
    else:
        context = f"""
        STUDENT PROFILE:
        - Skill Level: {profile.skill_level}
        - Weak Topics: {json.dumps(profile.weak_topics)}
        - Strong Topics: {json.dumps(profile.strong_topics)}
        - Misconceptions: {json.dumps(profile.misconceptions)}
        - Explanation Style: {profile.explanation_style}
        - Sessions Completed: {profile.sessions_count}
        """
    
    prompt = f"""
    You are CodeMentor AI, a personalized programming tutor.
    
    {context}
    
    Now analyze this {language} code submitted by the student:
    
    {new_code}
    
    Based on the student profile above:
    1. Identify errors and explain them in the student's preferred style
    2. Point out if this is a repeated mistake from their history
    3. Give a personalized tip targeting their weak topics
    4. End with an encouraging message
    
    Be specific, be personal, be helpful.
    """
    
    return prompt

def update_learner_profile(db: Session, student_id: int, new_errors: list, topic: str):
    profile = db.query(LearnerProfile).filter(
        LearnerProfile.student_id == student_id
    ).first()
    
    if not profile:
        profile = LearnerProfile(student_id=student_id)
        db.add(profile)
    
    weak_topics = profile.weak_topics or []
    if topic and topic not in weak_topics:
        weak_topics.append(topic)
        profile.weak_topics = weak_topics
    
    misconceptions = profile.misconceptions or []
    for error in new_errors:
        existing = [m for m in misconceptions if error in m]
        if existing:
            idx = misconceptions.index(existing[0])
            count = int(misconceptions[idx].split("- seen ")[-1].split(" ")[0]) + 1
            misconceptions[idx] = f"{error} - seen {count} times"
        else:
            misconceptions.append(f"{error} - seen 1 time")
    
    profile.misconceptions = misconceptions
    profile.sessions_count = (profile.sessions_count or 0) + 1
    
    db.commit()
    db.refresh(profile)
    return profile

def save_code_submission(db: Session, student_id: int, code: str, language: str, errors: list, topic: str):
    last_submission = db.query(CodeSubmission).filter(
        CodeSubmission.student_id == student_id
    ).order_by(CodeSubmission.session_number.desc()).first()
    
    session_number = (last_submission.session_number + 1) if last_submission else 1
    
    submission = CodeSubmission(
        student_id=student_id,
        session_number=session_number,
        code_submitted=code,
        language=language,
        errors_found=errors,
        topic=topic
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

def get_student_context(db: Session, student_id: int):
    profile = get_learner_profile(db, student_id)
    if not profile:
        return {"sessions_count": 0, "summary": "New student, no history yet."}
    return {
        "sessions_count": profile.sessions_count or 0,
        "skill_level": profile.skill_level,
        "weak_topics": profile.weak_topics,
        "strong_topics": profile.strong_topics,
        "misconceptions": profile.misconceptions,
        "explanation_style": profile.explanation_style
    }

def update_student_profile(db: Session, student_id: int):
    update_learner_profile(db, student_id, new_errors=[], topic="general")