from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import pandas as pd

from app.db.session import get_db
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse, QuestionRequest
from app.crud.evaluation import create_evaluation
from app.core.security import decode_token

router = APIRouter()

# Load model and tokenizer
model_path = "final"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForQuestionAnswering.from_pretrained(model_path)
model.eval()

# Load the CSV
df = pd.read_csv("filtered_csv.csv")


@router.post("/get-answer", response_model=dict)
def get_context_and_answer(request: QuestionRequest):
    """Fetch context and the model's answer for a provided question."""
    question = request.question
    context = df.iloc[0]["context"]  # Example retrieval; refine if needed.

    # Predict the answer
    inputs = tokenizer(question, context, max_length=384, truncation=True, padding="max_length", return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    start_idx = torch.argmax(outputs.start_logits, dim=1).item()
    end_idx = torch.argmax(outputs.end_logits, dim=1).item()

    model_answer = tokenizer.decode(inputs["input_ids"][0][start_idx:end_idx + 1], skip_special_tokens=True)

    return {"question": question, "context": context, "model_answer": model_answer.strip()}


@router.get("/ask-random-question", response_model=dict)
def get_random_question():
    """Fetch a random question with a unique ID."""
    random_row = df.sample(n=1).iloc[0]
    question_id = int(random_row.name)  # Explicitly cast to Python int
    question = random_row["question"]
    context = random_row["context"]

    return {"id": question_id, "question": question, "context": context}



@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_answer(
    request: EvaluationCreate,
    db: Session = Depends(get_db),
    token: str = Depends(decode_token)
):
    """Evaluate the user's answer and save the result to the database."""
    user_id = token.get("UserId")

    # Fetch the question and context by ID
    if request.question_id < 0 or request.question_id >= len(df):
        raise HTTPException(status_code=404, detail="Invalid question ID")
    question_row = df.iloc[request.question_id]
    question = question_row["question"]
    context = question_row["context"]

    # Predict the model's answer
    inputs = tokenizer(question, context, max_length=384, truncation=True, padding="max_length", return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    start_idx = torch.argmax(outputs.start_logits, dim=1).item()
    end_idx = torch.argmax(outputs.end_logits, dim=1).item()
    model_answer = tokenizer.decode(inputs["input_ids"][0][start_idx:end_idx + 1], skip_special_tokens=True).strip()

    # Evaluate the answer
    is_correct = request.user_answer.strip().lower() == model_answer.lower()
    similarity_score = 100.0 if is_correct else 0.0  # Example scoring

    # Save the result in the database
    evaluation_data = {
        "question": question,
        "context": context,
        "user_answer": request.user_answer,
        "model_answer": model_answer,
        "is_correct": is_correct,
        "similarity_score": similarity_score
    }
    evaluation = create_evaluation(db, user_id, evaluation_data)

    return evaluation