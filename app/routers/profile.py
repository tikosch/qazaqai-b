from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.profile import TeacherProfileDetails, StudentProfileDetails, StudentDetails, TeacherDetails
from app.core.security import decode_token
from app.models.teacher_referral import TeacherReferral
from app.models.teacher_student import TeacherStudents
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

SYSTEM_ROLES_TEACHER = "Teacher"
SYSTEM_ROLES_STUDENT = "Student"

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user_id: str = payload.get("UserId")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user, payload  # Return both user and payload

@router.get("/profile")
def get_profile(db: Session = Depends(get_db), current_user_and_payload=Depends(get_current_user)):
    user, payload = current_user_and_payload
    roles = payload.get("roles", [])
    user_id = user.id

    if SYSTEM_ROLES_TEACHER in roles:
        referral = db.query(TeacherReferral).filter(TeacherReferral.teacher_id == user_id).first()
        teacher_students = db.query(TeacherStudents).filter(TeacherStudents.teacher_id == user_id).all()
        count = len(teacher_students)
        student_ids = [ts.student_id for ts in teacher_students]
        students = []
        if student_ids:
            q = db.query(User).filter(User.id.in_(student_ids)).all()
            students = [StudentDetails(StudentId=str(s.id), StudentName=s.username) for s in q]

        return TeacherProfileDetails(
            Id=str(user_id),
            UserName=user.username,
            Email=user.email,
            PhoneNumber=user.phone_number or "",
            ReferralCode=referral.referral if referral else "",
            StudentCount=count,
            Role=SYSTEM_ROLES_TEACHER,
            Students=students
        )
    elif SYSTEM_ROLES_STUDENT in roles:
        teacher_student = db.query(TeacherStudents).filter(TeacherStudents.student_id == user_id).first()
        if not teacher_student:
            raise HTTPException(status_code=404, detail="Student-Teacher relationship not found.")
        teacher = db.query(User).filter(User.id == teacher_student.teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found.")

        return StudentProfileDetails(
            Id=str(user_id),
            UserName=user.username,
            Email=user.email,
            PhoneNumber=user.phone_number or "",
            Teacher=TeacherDetails(
                TeacherId=str(teacher.id),
                TeacherName=teacher.username
            )
        )
    else:
        raise HTTPException(status_code=403, detail="Role not supported")
