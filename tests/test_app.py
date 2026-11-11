"""
Test suite for PrepMate - AI Interview Trainer Agent.
Validates all modules, APIs, database persistence, RAG retrieval, and IBM Granite integration.
"""
import os
import json
import pytest
from app import app
from database.db import init_db, get_connection
from database.models import StudentProfileModel, InterviewSessionModel
from ai.rag_service import rag_service
from ai.granite_service import granite_service

@pytest.fixture
def client():
    """Create Flask test client and ensure test database is initialized."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    init_db()
    with app.test_client() as client:
        yield client


def test_home_page_load(client):
    """Test Module 1: Home page loads successfully with 200 OK and branding."""
    resp = client.get('/')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "PrepMate" in html
    assert "Your Personal" in html
    assert "AI Interview Coach" in html
    assert "IBM Granite" in html
    assert "AICTE–IBM SkillsBuild" in html


def test_api_status(client):
    """Test system status endpoint returns online state and KB stats."""
    resp = client.get('/api/status')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['status'] == 'online'
    assert 'watsonx_live' in data
    assert 'model_id' in data
    assert data['knowledge_base_chunks'] > 0


def test_student_profile_submission_and_validation(client):
    """Test Module 2: Profile validation and SQLite database persistence."""
    # 1. Invalid submission (missing mandatory full_name and college)
    resp_invalid = client.post('/profile', data={
        'full_name': '',
        'education': '',
        'college': '',
        'target_role': ''
    }, follow_redirects=True)
    assert resp_invalid.status_code == 200
    assert "Please fill in all mandatory fields" in resp_invalid.data.decode('utf-8')

    # 2. Valid submission
    resp_valid = client.post('/profile', data={
        'full_name': 'Rohan Verma',
        'education': 'MCA (Master of Computer Applications)',
        'college': 'National Institute of Technology',
        'technical_skills': 'Flask, SQLite, REST API, Git, Docker',
        'programming_languages': 'Python, Java, SQL',
        'internship_experience': 'Software Engineering Intern at CloudWorks',
        'projects': 'Automated Logistics Dispatcher using Python and SQLite',
        'certifications': 'IBM SkillsBuild AI Foundation',
        'target_role': 'Full Stack Python Developer',
        'experience_level': 'Fresher (Graduating 2026)'
    }, follow_redirects=True)
    assert resp_valid.status_code == 200
    assert "Student profile successfully saved" in resp_valid.data.decode('utf-8')

    # 3. Verify record in SQLite database
    latest = StudentProfileModel.get_latest()
    assert latest is not None
    assert latest['full_name'] == 'Rohan Verma'
    assert latest['target_role'] == 'Full Stack Python Developer'


def test_rag_knowledge_retrieval():
    """Test Section 5: RAG local knowledge indexing and TF-IDF search."""
    # Ensure chunks are indexed
    assert len(rag_service.chunks) > 0

    # Test retrieval for OOP in Java
    results_java = rag_service.retrieve("What is polymorphism and inheritance in Java?", top_k=2)
    assert len(results_java) > 0
    assert any("java" in r['source_file'].lower() or "oop" in r['source_file'].lower() for r in results_java)

    # Test retrieval for SQL Joins
    results_sql = rag_service.retrieve("Difference between inner join and left outer join in SQL", top_k=2)
    assert len(results_sql) > 0
    assert any("sql" in r['source_file'].lower() for r in results_sql)

    # Test retrieval for HR STAR technique
    results_hr = rag_service.retrieve("Tell me about yourself and challenging project STAR method", top_k=2)
    assert len(results_hr) > 0
    assert any("hr" in r['source_file'].lower() or "fresher" in r['source_file'].lower() for r in results_hr)


def test_granite_service_generation_and_json_parsing():
    """Test Section 4: IBM Granite client, prompt assembly, and fallback parsing."""
    # Test JSON parser utility
    raw_markdown_json = '```json\n{"questions": [{"number": 1, "question": "What is ACID?"}]}\n```'
    parsed = granite_service._extract_json(raw_markdown_json)
    assert parsed is not None
    assert "questions" in parsed
    assert parsed["questions"][0]["question"] == "What is ACID?"

    # Test generation (live or mock fallback)
    result = granite_service.generate_text("Candidate Profile: Full Name: Test. Generate exactly 3 questions.", max_new_tokens=400)
    assert result.get("success") is True
    assert "model_id" in result
    assert "raw_text" in result


def test_question_generation_api(client):
    """Test Module 3: AI Interview Question Generator REST API."""
    payload = {
        "job_role": "Backend Engineer",
        "interview_type": "Technical",
        "difficulty": "Beginner",
        "num_questions": 5
    }
    resp = client.post('/api/generate-questions',
                       data=json.dumps(payload),
                       content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success'] is True
    assert len(data['questions']) >= 1
    assert 'model_used' in data
    assert 'rag_sources' in data


def test_answer_evaluation_api(client):
    """Test Module 4: AI Answer Evaluator criteria and responsible AI output."""
    payload = {
        "job_role": "Backend Python Developer",
        "question": "What is the difference between a list and a tuple in Python?",
        "answer": "A list is mutable, which means its elements can be changed, added, or removed after creation using square brackets. A tuple is immutable and defined using parentheses, meaning once declared it cannot be altered."
    }
    resp = client.post('/api/evaluate-answer',
                       data=json.dumps(payload),
                       content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success'] is True
    ev = data['evaluation']
    # Check 4 mandatory evaluation dimensions
    assert 'relevance' in ev
    assert 'technical_correctness' in ev
    assert 'clarity' in ev
    assert 'completeness' in ev
    assert 'overall_feedback' in ev
    assert 'missing_points' in ev
    assert 'improved_answer' in ev
    assert 'suggestions' in ev
    assert 'disclaimer' in ev


def test_mock_interview_workflow_end_to_end(client):
    """Test Module 5: Interactive 5-question mock interview flow and SQLite session storage."""
    # Step 1: Start mock session
    start_payload = {
        "job_role": "Data Systems Engineer",
        "interview_type": "Technical",
        "difficulty": "Beginner"
    }
    start_resp = client.post('/api/mock/start',
                             data=json.dumps(start_payload),
                             content_type='application/json')
    assert start_resp.status_code == 200
    start_data = json.loads(start_resp.data)
    assert start_data['success'] is True
    session_id = start_data['session_id']
    questions = start_data['questions']
    assert len(questions) == 5

    # Step 2: Submit answer for Question 1
    q1 = questions[0]
    submit_payload1 = {
        "session_id": session_id,
        "question_number": 1,
        "question_text": q1['question'],
        "category": q1.get('category', 'Technical'),
        "student_answer": "In relational databases, primary keys uniquely identify a tuple and foreign keys establish referential integrity.",
        "job_role": "Data Systems Engineer"
    }
    sub_resp1 = client.post('/api/mock/submit-answer',
                            data=json.dumps(submit_payload1),
                            content_type='application/json')
    assert sub_resp1.status_code == 200
    sub_data1 = json.loads(sub_resp1.data)
    assert sub_data1['success'] is True
    assert 'evaluation' in sub_data1

    # Step 3: Finalize session and generate summary
    fin_resp = client.post('/api/mock/finalize',
                           data=json.dumps({"session_id": session_id}),
                           content_type='application/json')
    assert fin_resp.status_code == 200
    fin_data = json.loads(fin_resp.data)
    assert fin_data['success'] is True
    assert 'summary' in fin_data
    assert 'strengths' in fin_data
    assert 'improvements' in fin_data

    # Step 4: Verify session in SQLite database (Module 6)
    session_record = InterviewSessionModel.get_by_id(session_id)
    assert session_record is not None
    assert session_record['completed_count'] == 1
    assert len(session_record['qa_records']) == 1


def test_history_page_and_detail(client):
    """Test Module 6: History list page and session detail view."""
    # Check history page
    resp = client.get('/history')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "Interview History" in html

    # Create dummy session to view
    session_id = InterviewSessionModel.create({
        "job_role": "Full Stack Dev",
        "interview_type": "Technical",
        "difficulty": "Beginner",
        "questions_count": 5,
        "completed_count": 5,
        "feedback_summary": "Excellent performance on Python and SQLite."
    })

    # Detail page
    detail_resp = client.get(f'/history/{session_id}')
    assert detail_resp.status_code == 200
    assert "Session Transcript" in detail_resp.data.decode('utf-8')

    # Delete session
    del_resp = client.delete(f'/api/history/{session_id}')
    assert del_resp.status_code == 200
    assert json.loads(del_resp.data)['success'] is True


def test_responsive_meta_tags(client):
    """Test that mobile responsive viewport tags are configured across pages."""
    for path in ['/', '/profile', '/generator', '/evaluator', '/mock', '/history']:
        resp = client.get(path)
        assert resp.status_code == 200
        html = resp.data.decode('utf-8')
        assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html

