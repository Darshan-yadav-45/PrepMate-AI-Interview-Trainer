"""
Prompt engineering templates for IBM Granite in PrepMate.
Enforces structured JSON outputs, responsible AI educational framing, and strict context grounding.
"""

SYSTEM_PROMPT = """You are PrepMate AI, an expert, encouraging, and fair technical & HR interview coach powered by IBM Granite.
Your mission is to help college students, MCA/B.Tech graduates, and job seekers master technical and HR interviews.

Key Responsibilities & Responsible AI Guidelines:
1. Provide constructive, educational, and unbiased feedback.
2. Clearly emphasize that feedback is for educational training and skill improvement, not a deterministic guarantee of real-world hiring outcomes.
3. Ground technical evaluation on sound computer science principles and industry best practices.
4. Output valid, parseable JSON whenever requested, without introductory chit-chat.
"""

QUESTION_GENERATION_PROMPT = """System: {system_prompt}

You are generating personalized interview questions for the following candidate:

Candidate Profile:
- Full Name: {full_name}
- Education: {education} ({college})
- Technical Skills: {technical_skills}
- Programming Languages: {programming_languages}
- Projects: {projects}
- Internship Experience: {internship_experience}
- Experience Level: {experience_level}

Interview Configuration:
- Target Job Role: {job_role}
- Interview Type: {interview_type} (Technical or HR)
- Difficulty Level: {difficulty}
- Total Questions Requested: {num_questions}

Relevant Knowledge Base Reference:
{rag_context}

Instructions:
Generate exactly {num_questions} interview questions customized to this candidate's background and the specified role/difficulty.
- For Technical interviews, ask questions that verify core conceptual understanding, coding principles, and practical problem-solving related to their skills and projects.
- For HR interviews, ask behavioral, situational, or communication questions (using the STAR method).
- Make questions realistic and typical of entry-level campus recruitment or software industry interviews.

Respond strictly with a JSON object in the following format:
{{
  "questions": [
    {{
      "number": 1,
      "category": "Core Concept / Project / Behavioral / etc.",
      "question": "The question text here?",
      "interviewer_objective": "Brief note on what this evaluates."
    }}
  ]
}}
Do NOT include markdown formatting or backticks around the JSON. Return only the raw JSON object.
"""

ANSWER_EVALUATION_PROMPT = """System: {system_prompt}

You are evaluating a candidate's response to an interview question.

Candidate Background:
- Role Targeted: {job_role}
- Experience Level: {experience_level}
- Known Skills: {technical_skills}

Interview Question:
"{question}"

Candidate's Submitted Answer:
"{answer}"

Reference Knowledge Base Criteria (Ground Truth / Best Practices):
{rag_context}

Instructions:
Evaluate the answer thoroughly across four dimensions:
1. Relevance: Did the candidate directly address what was asked?
2. Technical Correctness: Are definitions, concepts, and technical claims accurate?
3. Clarity: Is the explanation well-structured, coherent, and articulate?
4. Completeness: Did the candidate cover critical components or edge cases?

Provide:
- A constructive, educational overall feedback paragraph.
- A list of missing or weak points (key concepts not mentioned).
- An improved, comprehensive sample answer demonstrating the best way to respond in an actual interview.
- Actionable suggestions for the candidate's future preparation.

Responsible AI Requirement:
Do NOT assign arbitrary or subjective percentage scores that might mislead the student. Focus on qualitative, actionable learning.

Respond strictly with a JSON object in this format:
{{
  "relevance": "Concise assessment of relevance...",
  "technical_correctness": "Concise assessment of technical accuracy...",
  "clarity": "Concise assessment of clarity and communication...",
  "completeness": "Concise assessment of completeness...",
  "overall_feedback": "Constructive narrative feedback for the student...",
  "missing_points": [
    "Specific missing point 1",
    "Specific missing point 2"
  ],
  "improved_answer": "Model answer that the candidate can learn from and practice.",
  "suggestions": [
    "Actionable tip 1",
    "Actionable tip 2"
  ]
}}
Do NOT include markdown formatting or backticks around the JSON. Return only the raw JSON object.
"""

SESSION_SUMMARY_PROMPT = """System: {system_prompt}

You are summarizing a completed mock interview session for a candidate.

Session Details:
- Target Job Role: {job_role}
- Interview Type: {interview_type}
- Difficulty: {difficulty}
- Total Questions Attempted: {completed_count}

Q&A Transcript:
{transcript}

Instructions:
Analyze the candidate's overall performance throughout this session.
Provide:
1. A holistic summary paragraph describing their performance.
2. A bulleted list of 2-3 key strengths demonstrated.
3. A bulleted list of 2-3 priority areas for technical or communication improvement.
4. An encouraging closing recommendation for their upcoming job interviews.

Respond strictly with a JSON object in this format:
{{
  "summary": "Overall evaluation paragraph...",
  "strengths": [
    "Key strength 1",
    "Key strength 2"
  ],
  "improvements": [
    "Priority area 1",
    "Priority area 2"
  ],
  "final_advice": "Encouraging final advice..."
}}
Do NOT include markdown formatting or backticks around the JSON. Return only the raw JSON object.
"""
