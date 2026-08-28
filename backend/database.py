import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "schoolyar.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        average REAL DEFAULT 0,
        health_status TEXT DEFAULT 'خوب',
        behavior_status TEXT DEFAULT 'خوب'
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        score REAL NOT NULL,
        date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        teacher_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        file_name TEXT,
        file_path TEXT,
        submitted_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        video_url TEXT NOT NULL,
        teacher_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # حساب‌های آزمایشی
    demo_users = [
        ("admin", "123456", "مدیر مدرسه", "admin"),
        ("deputy", "123456", "معاون مدرسه", "deputy"),
        ("teacher", "123456", "هنرآموز نمونه", "teacher"),
        ("student", "123456", "دانش‌آموز نمونه", "student"),
        ("parent", "123456", "والد دانش‌آموز نمونه", "parent"),
    ]

    for user in demo_users:
        cursor.execute("""
            INSERT OR IGNORE INTO users
            (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        """, user)

    # دیتای نمونه دانش‌آموزان
    students = [
        ("علی رضایی", "دهم کامپیوتر", 18.50, "خوب", "خوب"),
        ("سارا محمدی", "دهم کامپیوتر", 17.25, "خوب", "خوب"),
        ("مریم احمدی", "یازدهم کامپیوتر", 19.10, "خوب", "عالی"),
        ("رضا کریمی", "یازدهم کامپیوتر", 14.80, "نیازمند پیگیری", "متوسط"),
        ("نگار حسینی", "دوازدهم کامپیوتر", 18.90, "خوب", "عالی"),
    ]

    for student in students:
        cursor.execute("""
            INSERT INTO students
            (full_name, class_name, average, health_status, behavior_status)
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM students WHERE full_name = ?
            )
        """, (*student, student[0]))

    connection.commit()
    connection.close()


def get_students():
    connection = get_connection()

    rows = connection.execute("""
        SELECT
            id,
            full_name,
            class_name,
            average,
            health_status,
            behavior_status
        FROM students
        ORDER BY full_name
    """).fetchall()

    connection.close()
    return [dict(row) for row in rows]


def get_school_statistics():
    connection = get_connection()

    total_students = connection.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    average = connection.execute(
        "SELECT COALESCE(AVG(average), 0) FROM students"
    ).fetchone()[0]

    health_followup = connection.execute(
        "SELECT COUNT(*) FROM students WHERE health_status != 'خوب'"
    ).fetchone()[0]

    behavior_followup = connection.execute(
        "SELECT COUNT(*) FROM students WHERE behavior_status IN ('متوسط', 'نیازمند پیگیری')"
    ).fetchone()[0]

    connection.close()

    return {
        "total_students": total_students,
        "average_grade": round(average, 2),
        "health_followup": health_followup,
        "behavior_followup": behavior_followup,
    }
