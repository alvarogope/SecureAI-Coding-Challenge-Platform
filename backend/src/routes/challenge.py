from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..ai_generator import generate_challenge_with_ai
from ..database.db import (
    get_challenge_quota,
    create_challenge,
    reset_quota_if_needed,
    get_user_challenges, create_challenge_quota,
    try_consume_quota, refund_quota
)
from ..utils import authenticate_and_get_user_details
from ..database.models import get_db
import json
from datetime import datetime

router = APIRouter()

class ChallengeRequest(BaseModel):
    difficulty: str

    class Config:
        json_schema_extra = {"example": {"difficulty": "easy"}}

@router.post("/generate-challenge")
def generate_challenge(request: ChallengeRequest, request_obj: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request_obj)
    user_id = user_details.get('userid')

    quota = get_challenge_quota(db, user_id)
    if not quota:
        quota = create_challenge_quota(db, user_id)

    reset_quota_if_needed(db, quota)

    # Reserve quota atomically before the (slow) AI call so concurrent
    # requests can't all pass the check and overspend.
    if not try_consume_quota(db, user_id):
        raise HTTPException(status_code=429, detail="Daily quota exceeded")

    try:
        challenge_data = generate_challenge_with_ai(request.difficulty)

        new_challenge = create_challenge(
            db=db,
            difficulty=request.difficulty,
            created_by=user_id,
            challenge_title=challenge_data["title"],
            options=json.dumps(challenge_data["options"]),
            correct_answer=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"]
        )
    except Exception:
        db.rollback()
        refund_quota(db, user_id)
        raise

    return {
        "id": new_challenge.id,
        "difficulty": request.difficulty,
        "title": new_challenge.title,
        "options": json.loads(new_challenge.options),
        "correct_answer_id": new_challenge.correct_answer_id,
        "explanation": new_challenge.explanation,
        "timestamp": new_challenge.date_created.isoformat(),
    }

@router.get("/my-history")
def my_history(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get('userid')

    challenges = get_user_challenges(db, user_id)
    return {
        "challenges": [
            {
                "id": c.id,
                "difficulty": c.difficulty,
                "title": c.title,
                "options": json.loads(c.options),
                "correct_answer_id": c.correct_answer_id,
                "explanation": c.explanation,
                "timestamp": c.date_created.isoformat(),
            }
            for c in challenges
        ]
    }

@router.get("/quota")
def get_quota(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get('userid')

    quota = get_challenge_quota(db, user_id)
    if not quota:
        return {
            "user_id": user_id,
            "quota_remaining": 0,
            "last_reset_date": datetime.now().isoformat(),
        }
    quota = reset_quota_if_needed(db, quota)
    return {
        "user_id": quota.user_id,
        "quota_remaining": quota.quota_remaining,
        "last_reset_date": quota.last_reset_date.isoformat(),
    }
