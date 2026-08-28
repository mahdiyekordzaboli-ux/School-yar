from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="مدرسه‌یار هوشمند",
    description="سامانه مدیریت هوشمند مدرسه",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "مدرسه‌یار هوشمند فعال است",
        "status": "ok",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/dashboard")
def dashboard(role: str = Query("manager")):

    data = {
        "manager": {
            "title": "داشبورد مدیر",
            "students": 0,
            "teachers": 0,
            "present_today": 0,
            "absent_today": 0,
            "improved_students": 0,
            "declined_students": 0,
            "announcements": [],
            "messages": []
        },

        "teacher": {
            "title": "داشبورد معلم",
            "students": 0,
            "present_today": 0,
            "absent_today": 0,
            "lessons_completed": 0,
            "lessons_not_completed": 0,
            "assignments": [],
            "messages": []
        },

        "parent": {
            "title": "داشبورد والد",
            "student_name": "",
            "school_attendance": "نامشخص",
            "classes": [],
            "studied_classes": [],
            "not_studied_classes": [],
            "physical_status": "ثبت نشده",
            "disciplinary_status": "ثبت نشده",
            "messages": []
        },

        "student": {
            "title": "داشبورد دانش‌آموز",
            "attendance": "ثبت نشده",
            "classes": [],
            "educational_videos": [],
            "assignments": [],
            "messages": []
        }
    }

    return data.get(
        role,
        {
            "error": "نقش وارد شده معتبر نیست",
            "available_roles": [
                "manager",
                "teacher",
                "parent",
                "student"
            ]
        }
    )


@app.get("/announcements")
def announcements():
    return {
        "items": []
    }


@app.get("/messages")
def messages():
    return {
        "items": []
    }


@app.get("/attendance")
def attendance():
    return {
        "present": 0,
        "absent": 0,
        "students": []
    }


@app.get("/students")
def students():
    return {
        "total": 0,
        "items": []
    }


@app.get("/teachers")
def teachers():
    return {
        "total": 0,
        "items": []
    }


@app.get("/educational-videos")
def educational_videos():
    return {
        "items": []
    }


@app.get("/assignments")
def assignments():
    return {
        "items": []
    }
