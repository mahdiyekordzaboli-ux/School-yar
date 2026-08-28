from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from .database import (
    init_database,
    get_students,
    get_school_statistics,
    get_connection,
)

app = FastAPI(
    title="مدرسه‌یار هوشمند",
    description="سامانه مدیریت مدرسه",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

init_database()


class LoginRequest(BaseModel):
    username: str
    password: str


class NoticeRequest(BaseModel):
    title: str
    body: str
    author: str


class MessageRequest(BaseModel):
    sender_id: int
    receiver_id: int
    body: str


class AttendanceRequest(BaseModel):
    student_id: int
    date: str
    status: str
    note: str | None = None


class GradeRequest(BaseModel):
    student_id: int
    subject: str
    score: float
    date: str | None = None


@app.get("/")
def home():
    return {
        "message": "مدرسه‌یار هوشمند فعال است",
        "version": "1.0.0",
        "creator": "مهندس مهدیه کرد",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "SchoolYar",
    }


@app.post("/api/login")
def login(data: LoginRequest):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT id, username, full_name, role, active
        FROM users
        WHERE username = ?
        AND password = ?
        AND active = 1
        """,
        (data.username, data.password),
    ).fetchone()

    connection.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="نام کاربری یا رمز عبور اشتباه است",
        )

    role_names = {
        "admin": "مدیر",
        "deputy": "معاون",
        "teacher": "معلم / هنرآموز",
        "student": "دانش‌آموز",
        "parent": "والد",
    }

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "role_name": role_names.get(
                user["role"],
                user["role"],
            ),
        },
    }


@app.get("/api/dashboard")
def dashboard():

    statistics = get_school_statistics()

    return {
        "success": True,
        "statistics": statistics,
        "teachers": 8,
        "classes": 18,
    }


@app.get("/api/students")
def students():

    return {
        "success": True,
        "students": get_students(),
    }


@app.get("/api/students/{student_id}")
def student_detail(student_id: int):

    connection = get_connection()

    student = connection.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,),
    ).fetchone()

    connection.close()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="دانش‌آموز پیدا نشد",
        )

    return {
        "success": True,
        "student": dict(student),
    }


@app.post("/api/attendance")
def add_attendance(data: AttendanceRequest):

    connection = get_connection()

    student = connection.execute(
        "SELECT id FROM students WHERE id = ?",
        (data.student_id,),
    ).fetchone()

    if not student:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="دانش‌آموز پیدا نشد",
        )

    connection.execute(
        """
        INSERT INTO attendance
        (student_id, date, status, note)
        VALUES (?, ?, ?, ?)
        """,
        (
            data.student_id,
            data.date,
            data.status,
            data.note,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "حضور و غیاب ثبت شد",
    }


@app.get("/api/attendance/{student_id}")
def student_attendance(student_id: int):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
        """,
        (student_id,),
    ).fetchall()

    connection.close()

    return {
        "success": True,
        "attendance": [dict(row) for row in rows],
    }


@app.post("/api/grades")
def add_grade(data: GradeRequest):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO grades
        (student_id, subject, score, date)
        VALUES (?, ?, ?, ?)
        """,
        (
            data.student_id,
            data.subject,
            data.score,
            data.date,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "نمره با موفقیت ثبت شد",
    }


@app.get("/api/grades/{student_id}")
def student_grades(student_id: int):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM grades
        WHERE student_id = ?
        ORDER BY date DESC
        """,
        (student_id,),
    ).fetchall()

    connection.close()

    return {
        "success": True,
        "grades": [dict(row) for row in rows],
    }


@app.post("/api/notices")
def add_notice(data: NoticeRequest):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO notices
        (title, body, author)
        VALUES (?, ?, ?)
        """,
        (
            data.title,
            data.body,
            data.author,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "اطلاعیه منتشر شد",
    }


@app.get("/api/notices")
def notices():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM notices
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return {
        "success": True,
        "notices": [dict(row) for row in rows],
    }


@app.post("/api/messages")
def send_message(data: MessageRequest):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO messages
        (sender_id, receiver_id, body)
        VALUES (?, ?, ?)
        """,
        (
            data.sender_id,
            data.receiver_id,
            data.body,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "پیام ارسال شد",
    }


@app.get("/api/messages/{user_id}")
def user_messages(user_id: int):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM messages
        WHERE sender_id = ?
        OR receiver_id = ?
        ORDER BY created_at DESC
        """,
        (
            user_id,
            user_id,
        ),
    ).fetchall()

    connection.close()

    return {
        "success": True,
        "messages": [dict(row) for row in rows],
    }


@app.get("/api/school/summary")
def school_summary():

    connection = get_connection()

    total = connection.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    health_problem = connection.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE health_status != 'خوب'
        """
    ).fetchone()[0]

    behavior_problem = connection.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE behavior_status IN
        ('متوسط', 'نیازمند پیگیری')
        """
    ).fetchone()[0]

    connection.close()

    return {
        "total_students": total,
        "health_followup": health_problem,
        "behavior_followup": behavior_problem,
    }
