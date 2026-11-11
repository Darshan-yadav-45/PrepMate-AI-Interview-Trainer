"""
Database connection and initialization module for PrepMate using SQLite3.
Provides thread-safe connections and helper execution functions.
"""
import sqlite3
import os
from pathlib import Path
from config import config

def get_db_path() -> str:
    """Return the absolute path to the SQLite database file."""
    db_path = config.DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    return os.path.abspath(db_path)

def get_connection() -> sqlite3.Connection:
    """Create a new SQLite connection with dict-like row access and foreign keys enabled."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    schema = """
    CREATE TABLE IF NOT EXISTS student_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        education TEXT NOT NULL,
        college TEXT NOT NULL,
        technical_skills TEXT NOT NULL,
        programming_languages TEXT NOT NULL,
        internship_experience TEXT,
        projects TEXT,
        certifications TEXT,
        target_role TEXT NOT NULL,
        experience_level TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER,
        job_role TEXT NOT NULL,
        interview_type TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        questions_count INTEGER DEFAULT 5,
        completed_count INTEGER DEFAULT 0,
        feedback_summary TEXT,
        strengths TEXT,
        improvements TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (profile_id) REFERENCES student_profiles(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS interview_qa_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_number INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        category TEXT,
        student_answer TEXT,
        relevance_feedback TEXT,
        correctness_feedback TEXT,
        clarity_feedback TEXT,
        completeness_feedback TEXT,
        overall_feedback TEXT,
        missing_points TEXT,
        improved_answer TEXT,
        rag_sources TEXT,
        model_used TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
    );
    """
    conn = get_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", get_db_path())
