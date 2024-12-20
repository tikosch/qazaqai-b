from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationCreate


def create_evaluation(db: Session, user_id: str, evaluation_data: EvaluationCreate):
    evaluation = Evaluation(
        user_id=user_id,
        **evaluation_data.dict()
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation
