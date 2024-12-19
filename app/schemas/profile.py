from pydantic import BaseModel, EmailStr
from typing import Optional, List

class StudentDetails(BaseModel):
    StudentId: str
    StudentName: str

class TeacherDetails(BaseModel):
    TeacherId: str
    TeacherName: str

class TeacherProfileDetails(BaseModel):
    Id: str
    UserName: str
    Email: EmailStr
    StudentCount: int
    PhoneNumber: str
    Role: str
    ReferralCode: Optional[str]
    Students: Optional[List[StudentDetails]] = None
    
    class Config:
        orm_mode = True

class StudentProfileDetails(BaseModel):
    Id: str
    UserName: str
    Email: EmailStr
    PhoneNumber: str
    Teacher: TeacherDetails

    class Config:
        orm_mode = True

class UserProfileResponse(BaseModel):
    # Define fields based on your requirements
    id: str
    username: str
    email: EmailStr
    phone_number: Optional[str]
    roles: List[str]
    # Add other fields as needed

    class Config:
        orm_mode = True
