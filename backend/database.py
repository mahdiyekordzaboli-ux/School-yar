from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    id: Optional[int] = None
    username: str
    full_name: str
    role: str
    is_active: bool = True


class Student(BaseModel):
    id: Optional[int] = None
    full_name: str
    national_id: Optional[str] = None
    class_name: str
    average: float = 0.0
    attendance_percent: float = 100.0
    behavior_status: str = "خوب"
    health_status: str = "خوب"


class Attendance(BaseModel):
    student_id: int
    date: str
    status: str = Field(description="present یا absent")
    note: Optional[str] = None


class Grade(BaseModel):
    student_id: int
    subject: str
    score: float
    teacher: Optional[str] = None


class Assignment(BaseModel):
    id: Optional[int] = None
    title: str
    subject: str
    description: Optional[str] = None
    teacher_id: Optional[int] = None


class Notice(BaseModel):
    id: Optional[int] = None
    title: str
    body: str
    author: str


class Message(BaseModel):
    sender_id: int
    receiver_id: int
    body: str


class EducationalVideo(BaseModel):
    id: Optional[int] = None
    title: str
    subject: str
    video_url: str
    teacher_id: Optional[int] = None
