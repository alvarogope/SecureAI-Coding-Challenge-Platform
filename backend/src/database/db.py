from sqlalchemy import update
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models

def get_challenge_quota(db: Session, user_id: str):
    return (db.query(models.ChallengeQuota)
            .filter(models.ChallengeQuota.user_id == user_id)
            .first())

def create_challenge_quota(db: Session, user_id: str):
    db_quota = models.ChallengeQuota(user_id=user_id)
    db.add(db_quota)
    db.commit()
    db.refresh(db_quota)
    return db_quota

def reset_quota_if_needed(db: Session, quota: models.ChallengeQuota):
    now = datetime.now()
    if now - quota.last_reset_date > timedelta(hours=24):
        quota.quota_remaining = 15
        quota.last_reset_date = now
        db.commit()
        db.refresh(quota)
    return quota

def try_consume_quota(db: Session, user_id: str) -> bool:
    """Atomically decrement the user's quota. Returns False if none was left."""
    result = db.execute(
        update(models.ChallengeQuota)
        .where(models.ChallengeQuota.user_id == user_id,
               models.ChallengeQuota.quota_remaining > 0)
        .values(quota_remaining=models.ChallengeQuota.quota_remaining - 1)
    )
    db.commit()
    return result.rowcount == 1

def refund_quota(db: Session, user_id: str) -> None:
    """Give back one unit of quota, e.g. when challenge generation fails."""
    db.execute(
        update(models.ChallengeQuota)
        .where(models.ChallengeQuota.user_id == user_id)
        .values(quota_remaining=models.ChallengeQuota.quota_remaining + 1)
    )
    db.commit()

def create_challenge(
    db: Session,
    difficulty: str,
    created_by: str,
    challenge_title: str,
    options: str,
    correct_answer: int,
    explanation: str
):
    db_challenge = models.Challenge(
        difficulty=difficulty,
        created_by=created_by,
        options=options,
        title=challenge_title,
        correct_answer_id=correct_answer,
        explanation=explanation
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_user_challenges(db: Session, user_id: str):
    return db.query(models.Challenge).filter(models.Challenge.created_by == user_id).all()
