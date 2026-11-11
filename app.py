"""
PrepMate - AI Interview Trainer Agent
Flask Application Entry Point
AICTE-IBM SkillsBuild University Engagements 2026 (Problem Statement #22)
"""
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from config import config
from database.db import init_db
from database.models import StudentProfileModel, InterviewSessionModel
from ai.rag_service import rag_service
from ai.granite_service import granite_service
from ai.prompt_templates import (
    SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    SESSION_SUMMARY_PROMPT
)

app = Flask(
    __name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize database on app startup
init_db()


# ==============================================================================
# Helper Context Processors & Utilities
# ==============================================================================
@app.context_processor
def inject_global_data():
    """Make IBM model status and system settings available in all Jinja templates."""
    is_live = granite_service.is_live_configured()
    return {
        'watsonx_configured': is_live,
        'model_id': config.WATSONX_MODEL_ID,
        'mock_mode': config.MOCK_MODE or (not is_live),
        'kb_chunks_count': len(rag_service.chunks)
    }


# ==============================================================================
# Web Page Routes (HTML Views)
# ==============================================================================
@app.route('/')
def index():
    """Module 1: Home Page - Landing page with hero, features, and how it works."""
    profile = StudentProfileModel.get_latest()
    recent_sessions = InterviewSessionModel.get_recent(limit=3)
    return render_template('index.html', profile=profile, recent_sessions=recent_sessions)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Module 2: Student Profile - View and update student profile."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        education = request.form.get('education', '').strip()
        college = request.form.get('college', '').strip()
        target_role = request.form.get('target_role', '').strip()
        experience_level = request.form.get('experience_level', 'Fresher').strip()

        # Validation
        if not full_name or not education or not college or not target_role:
            flash("Please fill in all mandatory fields: Full Name, Education, College, and Target Role.", "danger")
            return redirect(url_for('profile'))

        profile_data = {
            'id': request.form.get('profile_id'),
            'full_name': full_name,
            'education': education,
            'college': college,
            'technical_skills': request.form.get('technical_skills', '').strip(),
            'programming_languages': request.form.get('programming_languages', '').strip(),
            'internship_experience': request.form.get('internship_experience', '').strip(),
            'projects': request.form.get('projects', '').strip(),
            'certifications': request.form.get('certifications', '').strip(),
            'target_role': target_role,
            'experience_level': experience_level
        }

        profile_id = StudentProfileModel.save(profile_data)
        session['profile_id'] = profile_id
        flash("Student profile successfully saved!", "success")
        return redirect(url_for('profile'))

    profile_data = StudentProfileModel.get_latest()
    return render_template('profile.html', profile=profile_data)


@app.route('/generator')
def generator():
    """Module 3: AI Interview Question Generator page."""
    profile = StudentProfileModel.get_latest()
    return render_template('generator.html', profile=profile)


@app.route('/evaluator')
def evaluator():
    """Module 4: AI Answer Evaluator page."""
    profile = StudentProfileModel.get_latest()
    return render_template('evaluator.html', profile=profile)


@app.route('/mock')
def mock_interview():
    """Module 5: Interactive Text-Based Mock Interview."""
    profile = StudentProfileModel.get_latest()
    return render_template('mock_interview.html', profile=profile)


@app.route('/history')
def history():
    """Module 6: Interview History listing past sessions."""
    sessions = InterviewSessionModel.get_recent(limit=50)
    return render_template('history.html', sessions=sessions)


@app.route('/history/<int:session_id>')
def history_detail(session_id: int):
    """View full detailed transcript and evaluation for a specific interview session."""
    session_data = InterviewSessionModel.get_by_id(session_id)
    if not session_data:
        flash("Interview session not found.", "warning")
        return redirect(url_for('history'))
    return render_template('history_detail.html', session=session_data)


# ==============================================================================
# REST API Endpoints (JSON for AJAX / Frontend App)
# ==============================================================================
@app.route('/api/status', methods=['GET'])
def api_status():
    """Return system readiness, IBM watsonx.ai status, and knowledge base stats."""
    is_live = granite_service.is_live_configured()
    return jsonify({
        "status": "online",
        "watsonx_live": is_live,
        "model_id": config.WATSONX_MODEL_ID,
        "mock_mode": config.MOCK_MODE or (not is_live),
        "knowledge_base_chunks": len(rag_service.chunks),
        "watsonx_url": config.WATSONX_URL if is_live else "Mock Service / Unconfigured",
        "api_version": config.WATSONX_API_VERSION
    })


@app.route('/api/profile', methods=['GET', 'POST'])
def api_profile():
    """Fetch or update student profile via JSON API."""
    if request.method == 'GET':
        profile = StudentProfileModel.get_latest()
        return jsonify({"profile": profile or {}})

    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    education = data.get('education', '').strip()
    college = data.get('college', '').strip()
    target_role = data.get('target_role', '').strip()

    if not full_name or not education or not college or not target_role:
        return jsonify({"error": "Full name, education, college, and target role are required."}), 400

    profile_id = StudentProfileModel.save(data)
    return jsonify({"success": True, "profile_id": profile_id, "message": "Profile saved successfully."})


@app.route('/api/generate-questions', methods=['POST'])
def api_generate_questions():
    """
    Generate customized interview questions using IBM Granite and RAG context.
    """
    data = request.get_json() or {}
    job_role = data.get('job_role', 'Software Development Engineer').strip()
    interview_type = data.get('interview_type', 'Technical').strip()
    difficulty = data.get('difficulty', 'Beginner').strip()
    num_questions = int(data.get('num_questions', 5))
    num_questions = max(1, min(10, num_questions))

    # Retrieve student profile from DB or request
    profile = StudentProfileModel.get_latest() or {}
    if data.get('profile_override'):
        profile.update(data.get('profile_override'))

    # Step 1: Query RAG for domain knowledge matching job role, skills, and type
    rag_query = f"{job_role} {interview_type} {difficulty} {profile.get('technical_skills', '')} {profile.get('programming_languages', '')}"
    retrieved_chunks = rag_service.retrieve(rag_query, top_k=3)
    rag_context = rag_service.format_context_for_prompt(retrieved_chunks)

    # Step 2: Assemble prompt for IBM Granite
    prompt = QUESTION_GENERATION_PROMPT.format(
        system_prompt=SYSTEM_PROMPT,
        full_name=profile.get('full_name', 'Student Candidate'),
        education=profile.get('education', 'B.Tech Computer Science'),
        college=profile.get('college', 'Engineering College'),
        technical_skills=profile.get('technical_skills', 'Python, SQL, OOP, Data Structures'),
        programming_languages=profile.get('programming_languages', 'Python, Java, C++'),
        projects=profile.get('projects', 'Web application with database integration'),
        internship_experience=profile.get('internship_experience', 'Academic projects'),
        experience_level=profile.get('experience_level', 'Fresher'),
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        num_questions=num_questions,
        rag_context=rag_context
    )

    # Step 3: Invoke IBM Granite
    gen_result = granite_service.generate_text(prompt, max_new_tokens=1000, temperature=0.4)
    parsed = granite_service.parse_response_or_fallback(gen_result, expected_key="questions")

    questions_list = parsed.get("questions", [])
    if not questions_list:
        # Fallback safe questions if parsing failed
        questions_list = [
            {
                "number": 1,
                "category": "Core Knowledge",
                "question": f"Explain the fundamental principles and architecture required for a {job_role}.",
                "interviewer_objective": "Evaluates foundational understanding."
            }
        ]

    return jsonify({
        "success": True,
        "job_role": job_role,
        "interview_type": interview_type,
        "difficulty": difficulty,
        "questions": questions_list,
        "model_used": gen_result.get("model_id"),
        "is_mock": gen_result.get("is_mock", False),
        "rag_sources": [
            {"source": c["source_file"], "topic": c["topic"], "score": c["score"]}
            for c in retrieved_chunks
        ]
    })


@app.route('/api/evaluate-answer', methods=['POST'])
def api_evaluate_answer():
    """
    Evaluate student's submitted answer using IBM Granite + RAG ground truth.
    Provides relevance, correctness, clarity, completeness, missing points, and sample answer.
    """
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    job_role = data.get('job_role', 'Software Engineer').strip()
    experience_level = data.get('experience_level', 'Fresher').strip()
    technical_skills = data.get('technical_skills', 'Computer Science Fundamentals').strip()

    if not question:
        return jsonify({"error": "Question is required for evaluation."}), 400
    if not answer or len(answer) < 3:
        return jsonify({"error": "Please provide an answer before requesting evaluation."}), 400

    # Step 1: Query RAG for ground-truth criteria on the question
    retrieved_chunks = rag_service.retrieve(f"{question} {job_role}", top_k=3)
    rag_context = rag_service.format_context_for_prompt(retrieved_chunks)

    # Step 2: Format prompt for IBM Granite
    prompt = ANSWER_EVALUATION_PROMPT.format(
        system_prompt=SYSTEM_PROMPT,
        job_role=job_role,
        experience_level=experience_level,
        technical_skills=technical_skills,
        question=question,
        answer=answer,
        rag_context=rag_context
    )

    # Step 3: Invoke IBM Granite
    gen_result = granite_service.generate_text(prompt, max_new_tokens=900, temperature=0.2)
    parsed = granite_service.parse_response_or_fallback(gen_result, expected_key="overall_feedback")

    # Step 4: Ensure structured output conforms to criteria
    evaluation = {
        "relevance": parsed.get("relevance", "The answer addresses the question directly."),
        "technical_correctness": parsed.get("technical_correctness", "Technical concepts are sound."),
        "clarity": parsed.get("clarity", "Well-expressed and coherent."),
        "completeness": parsed.get("completeness", "Covers the fundamental principles."),
        "overall_feedback": parsed.get("overall_feedback", "Solid attempt showing foundational understanding."),
        "missing_points": parsed.get("missing_points", []),
        "improved_answer": parsed.get("improved_answer", "Review core definitions and include an architectural example."),
        "suggestions": parsed.get("suggestions", ["Structure answers clearly using definitions and examples."]),
        "model_used": gen_result.get("model_id"),
        "is_mock": gen_result.get("is_mock", False),
        "disclaimer": "This AI feedback is generated for educational practice purposes and does not represent an actual hiring decision.",
        "rag_sources": [
            {"source": c["source_file"], "topic": c["topic"], "score": c["score"]}
            for c in retrieved_chunks
        ]
    }

    return jsonify({"success": True, "evaluation": evaluation})


# ==============================================================================
# Mock Interview Interactive Flow APIs (Module 5)
# ==============================================================================
@app.route('/api/mock/start', methods=['POST'])
def api_mock_start():
    """
    Start a 5-question mock interview session. Generates questions and saves session in SQLite.
    """
    data = request.get_json() or {}
    job_role = data.get('job_role', 'Software Development Engineer').strip()
    interview_type = data.get('interview_type', 'Technical').strip()
    difficulty = data.get('difficulty', 'Beginner').strip()

    profile = StudentProfileModel.get_latest() or {}
    profile_id = profile.get('id')

    # Create session record
    session_id = InterviewSessionModel.create({
        'profile_id': profile_id,
        'job_role': job_role,
        'interview_type': interview_type,
        'difficulty': difficulty,
        'questions_count': 5,
        'completed_count': 0
    })

    # Retrieve RAG context and generate 5 questions
    rag_query = f"{job_role} {interview_type} {difficulty} {profile.get('technical_skills', '')}"
    retrieved_chunks = rag_service.retrieve(rag_query, top_k=3)
    rag_context = rag_service.format_context_for_prompt(retrieved_chunks)

    prompt = QUESTION_GENERATION_PROMPT.format(
        system_prompt=SYSTEM_PROMPT,
        full_name=profile.get('full_name', 'Student Candidate'),
        education=profile.get('education', 'B.Tech / MCA'),
        college=profile.get('college', 'University'),
        technical_skills=profile.get('technical_skills', 'Programming, Problem Solving'),
        programming_languages=profile.get('programming_languages', 'Python, Java, C++'),
        projects=profile.get('projects', 'Academic and capstone projects'),
        internship_experience=profile.get('internship_experience', 'None / Fresher'),
        experience_level=profile.get('experience_level', 'Fresher'),
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        num_questions=5,
        rag_context=rag_context
    )

    gen_result = granite_service.generate_text(prompt, max_new_tokens=1000, temperature=0.3)
    parsed = granite_service.parse_response_or_fallback(gen_result, expected_key="questions")
    questions = parsed.get("questions", [])

    if len(questions) < 5:
        # Guarantee 5 questions
        default_qs = [
            {"number": 1, "category": "Fundamentals", "question": f"Can you explain the key core principles of {job_role}?"},
            {"number": 2, "category": "Data & Architecture", "question": "How do you choose between different data storage models for an application?"},
            {"number": 3, "category": "Coding & Algorithms", "question": "How do you approach debugging a memory leak or sudden latency spike in code?"},
            {"number": 4, "category": "Project Experience", "question": "Walk me through the architecture and your specific role in your best project."},
            {"number": 5, "category": "Behavioral / Teamwork", "question": "Describe how you handle conflicting technical requirements or tight deadlines."}
        ]
        questions = default_qs[:5]

    return jsonify({
        "success": True,
        "session_id": session_id,
        "job_role": job_role,
        "interview_type": interview_type,
        "difficulty": difficulty,
        "total_questions": len(questions),
        "questions": questions,
        "model_used": gen_result.get("model_id"),
        "is_mock": gen_result.get("is_mock", False)
    })


@app.route('/api/mock/submit-answer', methods=['POST'])
def api_mock_submit_answer():
    """
    Submit and evaluate an answer for an individual question in a mock interview.
    Saves record to SQLite.
    """
    data = request.get_json() or {}
    session_id = data.get('session_id')
    question_number = int(data.get('question_number', 1))
    question_text = data.get('question_text', '').strip()
    category = data.get('category', 'Technical')
    student_answer = data.get('student_answer', '').strip()
    job_role = data.get('job_role', 'Software Engineer')

    if not session_id or not question_text:
        return jsonify({"error": "session_id and question_text are required."}), 400

    # RAG lookup for question
    retrieved_chunks = rag_service.retrieve(f"{question_text} {job_role}", top_k=2)
    rag_context = rag_service.format_context_for_prompt(retrieved_chunks)

    # Prompt IBM Granite for answer evaluation
    prompt = ANSWER_EVALUATION_PROMPT.format(
        system_prompt=SYSTEM_PROMPT,
        job_role=job_role,
        experience_level="Fresher / Job Seeker",
        technical_skills="Computer Science & Engineering",
        question=question_text,
        answer=student_answer or "(No answer provided / candidate skipped)",
        rag_context=rag_context
    )

    gen_result = granite_service.generate_text(prompt, max_new_tokens=800, temperature=0.2)
    parsed = granite_service.parse_response_or_fallback(gen_result, expected_key="overall_feedback")

    sources_str = ", ".join([f"{c['source_file']} ({c['topic']})" for c in retrieved_chunks])
    missing_str = "\n".join([f"- {p}" for p in parsed.get("missing_points", [])])

    # Save to SQLite
    qa_id = InterviewSessionModel.save_qa({
        'session_id': session_id,
        'question_number': question_number,
        'question_text': question_text,
        'category': category,
        'student_answer': student_answer,
        'relevance_feedback': parsed.get('relevance', 'Directly answers prompt.'),
        'correctness_feedback': parsed.get('technical_correctness', 'Concepts are sound.'),
        'clarity_feedback': parsed.get('clarity', 'Clear presentation.'),
        'completeness_feedback': parsed.get('completeness', 'Good coverage.'),
        'overall_feedback': parsed.get('overall_feedback', 'Constructive effort.'),
        'missing_points': missing_str,
        'improved_answer': parsed.get('improved_answer', ''),
        'rag_sources': sources_str,
        'model_used': gen_result.get('model_id', 'IBM Granite')
    })

    return jsonify({
        "success": True,
        "qa_id": qa_id,
        "question_number": question_number,
        "evaluation": parsed,
        "rag_sources": [
            {"source": c["source_file"], "topic": c["topic"]} for c in retrieved_chunks
        ],
        "model_used": gen_result.get("model_id"),
        "is_mock": gen_result.get("is_mock", False)
    })


@app.route('/api/mock/finalize', methods=['POST'])
def api_mock_finalize():
    """
    Finalize mock interview, generate holistic session summary using IBM Granite,
    and update session record in SQLite.
    """
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id is required."}), 400

    session_data = InterviewSessionModel.get_by_id(session_id)
    if not session_data:
        return jsonify({"error": "Session not found."}), 404

    qa_records = session_data.get('qa_records', [])
    completed_count = len(qa_records)

    # Format transcript for summary prompt
    transcript_blocks = []
    for qa in qa_records:
        transcript_blocks.append(
            f"Question {qa.get('question_number')}: {qa.get('question_text')}\n"
            f"Candidate Answer: {qa.get('student_answer')}\n"
            f"Feedback: {qa.get('overall_feedback')}\n"
        )
    transcript_text = "\n---\n".join(transcript_blocks) if transcript_blocks else "Candidate completed session."

    prompt = SESSION_SUMMARY_PROMPT.format(
        system_prompt=SYSTEM_PROMPT,
        job_role=session_data.get('job_role', 'Software Engineer'),
        interview_type=session_data.get('interview_type', 'Technical'),
        difficulty=session_data.get('difficulty', 'Beginner'),
        completed_count=completed_count,
        transcript=transcript_text
    )

    gen_result = granite_service.generate_text(prompt, max_new_tokens=700, temperature=0.3)
    parsed = granite_service.parse_response_or_fallback(gen_result, expected_key="summary")

    summary_text = parsed.get("summary", "Session successfully completed with solid foundational performance.")
    strengths_text = "\n".join([f"- {s}" for s in parsed.get("strengths", ["Solid foundational knowledge", "Positive attitude"])])
    improvements_text = "\n".join([f"- {i}" for i in parsed.get("improvements", ["Practice system trade-offs", "Add concrete metrics from projects"])])

    InterviewSessionModel.update_summary(
        session_id=session_id,
        completed_count=completed_count,
        summary=summary_text,
        strengths=strengths_text,
        improvements=improvements_text
    )

    return jsonify({
        "success": True,
        "session_id": session_id,
        "completed_count": completed_count,
        "summary": summary_text,
        "strengths": parsed.get("strengths", []),
        "improvements": parsed.get("improvements", []),
        "final_advice": parsed.get("final_advice", "Keep practicing!"),
        "model_used": gen_result.get("model_id"),
        "is_mock": gen_result.get("is_mock", False)
    })


@app.route('/api/history/<int:session_id>', methods=['DELETE'])
def api_delete_history(session_id: int):
    """Delete a past interview session."""
    success = InterviewSessionModel.delete(session_id)
    return jsonify({"success": success})


# ==============================================================================
# Main execution
# ==============================================================================
if __name__ == '__main__':
    print(f"Starting PrepMate AI on http://localhost:{config.PORT}")
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)

