"""
Data access models and repository helpers for PrepMate SQLite storage.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from database.db import get_connection

class StudentProfileModel:
    @staticmethod
    def save(data: Dict[str, Any]) -> int:
        """Create or update a student profile. If id is provided, updates; else creates."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            profile_id = data.get('id')
            if profile_id:
                cur.execute("""
                    UPDATE student_profiles SET
                        full_name = ?,
                        education = ?,
                        college = ?,
                        technical_skills = ?,
                        programming_languages = ?,
                        internship_experience = ?,
                        projects = ?,
                        certifications = ?,
                        target_role = ?,
                        experience_level = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    data.get('full_name', '').strip(),
                    data.get('education', '').strip(),
                    data.get('college', '').strip(),
                    data.get('technical_skills', '').strip(),
                    data.get('programming_languages', '').strip(),
                    data.get('internship_experience', '').strip(),
                    data.get('projects', '').strip(),
                    data.get('certifications', '').strip(),
                    data.get('target_role', '').strip(),
                    data.get('experience_level', 'Fresher').strip(),
                    profile_id
                ))
            else:
                cur.execute("""
                    INSERT INTO student_profiles (
                        full_name, education, college, technical_skills,
                        programming_languages, internship_experience, projects,
                        certifications, target_role, experience_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('full_name', '').strip(),
                    data.get('education', '').strip(),
                    data.get('college', '').strip(),
                    data.get('technical_skills', '').strip(),
                    data.get('programming_languages', '').strip(),
                    data.get('internship_experience', '').strip(),
                    data.get('projects', '').strip(),
                    data.get('certifications', '').strip(),
                    data.get('target_role', '').strip(),
                    data.get('experience_level', 'Fresher').strip()
                ))
                profile_id = cur.lastrowid
            conn.commit()
            return profile_id
        finally:
            conn.close()

    @staticmethod
    def get_latest() -> Optional[Dict[str, Any]]:
        """Retrieve the most recently updated student profile."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM student_profiles ORDER BY updated_at DESC, id DESC LIMIT 1")
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(profile_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM student_profiles WHERE id = ?", (profile_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


class InterviewSessionModel:
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """Create a new mock interview session."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO interview_sessions (
                    profile_id, job_role, interview_type, difficulty,
                    questions_count, completed_count, feedback_summary, strengths, improvements
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('profile_id'),
                data.get('job_role', 'Software Engineer'),
                data.get('interview_type', 'Technical'),
                data.get('difficulty', 'Beginner'),
                data.get('questions_count', 5),
                data.get('completed_count', 0),
                data.get('feedback_summary', ''),
                data.get('strengths', ''),
                data.get('improvements', '')
            ))
            session_id = cur.lastrowid
            conn.commit()
            return session_id
        finally:
            conn.close()

    @staticmethod
    def update_summary(session_id: int, completed_count: int, summary: str, strengths: str, improvements: str):
        """Update session after interview completion."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE interview_sessions SET
                    completed_count = ?,
                    feedback_summary = ?,
                    strengths = ?,
                    improvements = ?
                WHERE id = ?
            """, (completed_count, summary, strengths, improvements, session_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save_qa(data: Dict[str, Any]) -> int:
        """Record an individual Q&A evaluation in a session."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO interview_qa_records (
                    session_id, question_number, question_text, category,
                    student_answer, relevance_feedback, correctness_feedback,
                    clarity_feedback, completeness_feedback, overall_feedback,
                    missing_points, improved_answer, rag_sources, model_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('session_id'),
                data.get('question_number', 1),
                data.get('question_text', ''),
                data.get('category', 'General'),
                data.get('student_answer', ''),
                data.get('relevance_feedback', ''),
                data.get('correctness_feedback', ''),
                data.get('clarity_feedback', ''),
                data.get('completeness_feedback', ''),
                data.get('overall_feedback', ''),
                data.get('missing_points', ''),
                data.get('improved_answer', ''),
                data.get('rag_sources', ''),
                data.get('model_used', 'IBM Granite')
            ))
            qa_id = cur.lastrowid
            conn.commit()
            return qa_id
        finally:
            conn.close()

    @staticmethod
    def get_recent(limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent interview sessions with summary stats."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.*, p.full_name as candidate_name
                FROM interview_sessions s
                LEFT JOIN student_profiles p ON s.profile_id = p.id
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(session_id: int) -> Optional[Dict[str, Any]]:
        """Get session details and all associated Q&A items."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.*, p.full_name as candidate_name, p.education, p.college
                FROM interview_sessions s
                LEFT JOIN student_profiles p ON s.profile_id = p.id
                WHERE s.id = ?
            """, (session_id,))
            session_row = cur.fetchone()
            if not session_row:
                return None
            session = dict(session_row)

            cur.execute("""
                SELECT * FROM interview_qa_records
                WHERE session_id = ?
                ORDER BY question_number ASC
            """, (session_id,))
            session['qa_records'] = [dict(r) for r in cur.fetchall()]
            return session
        finally:
            conn.close()

    @staticmethod
    def delete(session_id: int) -> bool:
        """Delete an interview session and its Q&A records."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM interview_qa_records WHERE session_id = ?", (session_id,))
            cur.execute("DELETE FROM interview_sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

