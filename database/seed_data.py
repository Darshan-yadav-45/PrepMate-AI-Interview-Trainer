"""
Demo data seeder for PrepMate - AI Interview Trainer Agent.
Populates realistic student profiles and completed mock interview sessions
with transcripts, 4-dimension evaluations, and summaries for academic demonstrations.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import init_db
from database.models import StudentProfileModel, InterviewSessionModel

def seed():
    print("[Seeder] Initializing database schema...")
    init_db()

    print("[Seeder] Seeding sample student candidate profile...")
    profile_id = StudentProfileModel.save({
        'full_name': 'Aditi Sharma',
        'education': 'B.Tech in Computer Science & Engineering (Final Year)',
        'college': 'Delhi Technological University (DTU)',
        'technical_skills': 'Flask, Django, PostgreSQL, Docker, REST APIs, Microservices, Git',
        'programming_languages': 'Python, Java, SQL, JavaScript',
        'internship_experience': 'Summer Software Intern at CloudNative Systems (8 weeks): Designed asynchronous task queues with Redis and optimized SQL relational queries.',
        'projects': 'PrepMate AI Interview Coach (Flask, IBM Granite, SQLite), Campus Placement Portal (Full Stack, PostgreSQL), Distributed Key-Value Store (Python, Socket programming)',
        'certifications': 'IBM SkillsBuild AI Practitioner, AWS Certified Cloud Practitioner',
        'target_role': 'Junior Backend Software Engineer',
        'experience_level': 'Fresher (Graduating 2026)'
    })
    print(f"[Seeder] Profile created with ID: {profile_id}")

    # Seed Mock Interview Session 1: Technical Round
    print("[Seeder] Seeding completed Technical Mock Interview session...")
    session_id_1 = InterviewSessionModel.create({
        'profile_id': profile_id,
        'job_role': 'Junior Backend Software Engineer',
        'interview_type': 'Technical',
        'difficulty': 'Beginner',
        'questions_count': 5,
        'completed_count': 5,
        'feedback_summary': 'Aditi demonstrated exceptional depth in core Python and database transaction concepts. Her responses were structured logically, articulating both conceptual definitions and practical trade-offs.',
        'strengths': '- Crisp and accurate explanations of Python memory management, GIL, and mutable vs immutable types.\n- Deep understanding of ACID properties and database indexing performance trade-offs.\n- Articulate and professional tone throughout the session.',
        'improvements': '- Include concrete space-time algorithmic complexity figures (Big-O) when discussing data structures.\n- Explicitly highlight unit testing and edge case validation strategies.'
    })

    # QA Records for Session 1
    session_1_qas = [
        {
            'session_id': session_id_1,
            'question_number': 1,
            'category': 'Python Fundamentals & Memory',
            'question_text': 'How does Python manage memory internally, and what is the key difference between mutable and immutable types?',
            'student_answer': 'In Python, memory is managed inside a private heap controlled by the Python memory manager. Python uses reference counting as its primary garbage collection mechanism, complemented by a cyclic garbage collector to detect reference cycles. Mutable types like lists and dictionaries can be modified in-place without altering their memory address, whereas immutable types like tuples, integers, and strings create a new object in memory upon modification.',
            'relevance_feedback': 'Directly addresses internal memory architecture and type mutability.',
            'correctness_feedback': 'Technically accurate regarding private heap, reference counting, and cyclic GC.',
            'clarity_feedback': 'Logical progression from memory allocation to data structure behavior.',
            'completeness_feedback': 'Thorough coverage including examples of both mutable and immutable types.',
            'overall_feedback': 'An outstanding response that demonstrates rigorous computer science fundamentals.',
            'missing_points': '- Mentioning the sys.getrefcount() function for debugging reference counts.',
            'improved_answer': 'Python manages memory in a private heap using reference counting paired with a generational cyclic garbage collector (Generation 0, 1, and 2). Mutable types (lists, dicts, sets) can be mutated in-place, preserving object identity (id()), while immutable types (int, float, str, tuple) cannot be altered after instantiation; modifications allocate a new memory block.',
            'rag_sources': 'python_questions.txt (Memory Management)',
            'model_used': 'IBM Granite 3-8B Instruct'
        },
        {
            'session_id': session_id_1,
            'question_number': 2,
            'category': 'Database Systems & ACID',
            'question_text': 'Explain the ACID properties in database management systems and why they are vital for financial transactions.',
            'student_answer': 'ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity ensures all operations in a transaction succeed together or all roll back upon failure. Consistency maintains schema integrity rules. Isolation prevents concurrent transactions from interfering with each other. Durability guarantees that committed data survives hardware crashes via write-ahead logging.',
            'relevance_feedback': 'Directly explains all four properties and relates them to transactional integrity.',
            'correctness_feedback': 'Correct definitions and accurate connection to Write-Ahead Logging (WAL).',
            'clarity_feedback': 'Clear, concise definitions with zero ambiguity.',
            'completeness_feedback': 'Covers all four pillars comprehensively.',
            'overall_feedback': 'A textbook-quality explanation demonstrating strong relational database knowledge.',
            'missing_points': '- Citing specific transaction isolation levels (e.g., Read Committed vs Serializable).',
            'improved_answer': 'ACID properties govern transactional reliability in RDBMS: Atomicity (all-or-nothing execution), Consistency (state transitions strictly obey schema constraints), Isolation (concurrent execution yields the same outcome as serial execution, managed via isolation levels like Serializable), and Durability (WAL logs commit permanently to disk). In banking, if debiting Account A succeeds but crediting Account B fails, Atomicity guarantees an automatic rollback to prevent monetary discrepancies.',
            'rag_sources': 'dbms_questions.txt (ACID Properties)',
            'model_used': 'IBM Granite 3-8B Instruct'
        },
        {
            'session_id': session_id_1,
            'question_number': 3,
            'category': 'SQL Querying & Indexing',
            'question_text': 'What is a database index, and what are the performance trade-offs of creating multiple indexes on a table?',
            'student_answer': 'An index is a data structure, typically a B-Tree, that speeds up data retrieval on specified columns without scanning the entire table. The trade-off is that every INSERT, UPDATE, or DELETE operation must update the index tree, slowing down write operations and consuming extra disk storage.',
            'relevance_feedback': 'Addresses what an index is and highlights both read gains and write costs.',
            'correctness_feedback': 'Correct identification of B-Tree structure and write latency trade-off.',
            'clarity_feedback': 'Structured and concise comparison.',
            'completeness_feedback': 'Covers read speed, write penalty, and storage cost.',
            'overall_feedback': 'Strong practical understanding of backend performance tuning.',
            'missing_points': '- Mentioning Clustered vs Non-Clustered index distinctions.',
            'improved_answer': 'An index is a lookup data structure (most commonly a balanced B+ Tree) that enables logarithmic O(log N) search times rather than linear O(N) table scans for WHERE, JOIN, and ORDER BY queries. The trade-offs are: 1) Write overhead—every DML operation requires rebalancing index nodes; 2) Storage overhead—indexes consume memory and disk space; 3) Over-indexing can lead query optimizers to make sub-optimal execution plan decisions.',
            'rag_sources': 'sql_questions.txt (SQL Indexing and Performance)',
            'model_used': 'IBM Granite 3-8B Instruct'
        },
        {
            'session_id': session_id_1,
            'question_number': 4,
            'category': 'Architecture & Project Defense',
            'question_text': 'In your resume project involving asynchronous task queues with Redis, what was the primary architectural challenge you encountered?',
            'student_answer': 'During peak load testing, when multiple tasks failed simultaneously due to an external API rate limit, the queues filled up and tasks were lost. I resolved this by introducing an exponential backoff retry mechanism and a Dead Letter Queue (DLQ) to isolate poisonous messages.',
            'relevance_feedback': 'Answers with a concrete real-world engineering problem and resolution.',
            'correctness_feedback': 'Demonstrates appropriate architectural patterns (DLQ, backoff).',
            'clarity_feedback': 'Excellent problem-action-result narrative.',
            'completeness_feedback': 'Identified the bottleneck, the root cause, and the architectural resolution.',
            'overall_feedback': 'Very impressive project defense that reveals real hands-on implementation experience.',
            'missing_points': '- Quantifying the scale (number of requests per second handled).',
            'improved_answer': 'In our backend task pipeline, sudden third-party API rate limiting caused unhandled task rejections and worker exhaustion. I designed a two-tiered reliability strategy: 1) Implemented exponential backoff with jitter in the worker consumers; 2) Routed tasks exceeding 5 retry attempts to a dedicated Dead Letter Queue (DLQ) for alerting and manual replay, ensuring zero message loss and keeping throughput steady at 800 tasks/second.',
            'rag_sources': 'fresher_guidance.txt (Project Defense)',
            'model_used': 'IBM Granite 3-8B Instruct'
        },
        {
            'session_id': session_id_1,
            'question_number': 5,
            'category': 'Software Engineering Principles',
            'question_text': 'What does "Favor composition over inheritance" mean in object-oriented design?',
            'student_answer': 'Inheritance creates a tight "is-a" relationship where child classes become dependent on parent class internals. Composition establishes a loose "has-a" relationship, allowing components to be injected or swapped dynamically at runtime without breaking subclasses.',
            'relevance_feedback': 'Directly explains the core difference between is-a and has-a relationships.',
            'correctness_feedback': 'Accurately highlights the fragile base class problem and loose coupling.',
            'clarity_feedback': 'Short, elegant, and conceptual.',
            'completeness_feedback': 'Covers runtime flexibility and decoupling.',
            'overall_feedback': 'Solid grasp of software design principles.',
            'missing_points': '- Providing a code example or citing Strategy / Dependency Injection patterns.',
            'improved_answer': '"Favor composition over inheritance" advises using "has-a" relationships (encapsulating helper objects) instead of deep "is-a" class hierarchies. Deep inheritance creates the "fragile base class problem," where modifying a superclass inadvertently breaks subclass behaviors. Composition enables loose coupling, facilitates unit testing through dependency injection and mocking, and allows runtime behavior swapping using patterns like Strategy or Decorator.',
            'rag_sources': 'oop_questions.txt (Composition vs Inheritance)',
            'model_used': 'IBM Granite 3-8B Instruct'
        }
    ]

    for qa in session_1_qas:
        InterviewSessionModel.save_qa(qa)
    print(f"[Seeder] Saved {len(session_1_qas)} Q&A records for Session #{session_id_1}.")

    # Seed Mock Interview Session 2: HR Behavioral Round
    print("[Seeder] Seeding completed HR Behavioral Mock Interview session...")
    session_id_2 = InterviewSessionModel.create({
        'profile_id': profile_id,
        'job_role': 'Associate Software Engineer',
        'interview_type': 'HR',
        'difficulty': 'Beginner',
        'questions_count': 5,
        'completed_count': 5,
        'feedback_summary': 'Aditi communicated with clarity, emotional intelligence, and composure. Her behavioral answers effectively utilized the STAR framework.',
        'strengths': '- Natural application of the STAR method (Situation, Task, Action, Result).\n- High team empathy and professional conflict resolution mindset.\n- Clear, realistic 3-year career vision.',
        'improvements': '- Mention personal initiatives in open-source or peer mentorship.\n- Keep introductory elevator pitch under 90 seconds.'
    })

    session_2_qas = [
        {
            'session_id': session_id_2,
            'question_number': 1,
            'category': 'HR - Introduction & Elevator Pitch',
            'question_text': 'Tell me about yourself and why you want to join our software engineering team.',
            'student_answer': 'I am a final-year Computer Science student at DTU passionate about backend systems and cloud APIs. Over the last two years, I built several projects in Python and Flask, including an AI Interview Trainer and an asynchronous task pipeline. During my summer internship at CloudNative Systems, I learned how production microservices scale. I want to join your team because of your engineering culture, focus on clean architecture, and the opportunity to build scalable software.',
            'relevance_feedback': 'Directly targets professional background and company motivation.',
            'correctness_feedback': 'Structured using the Present-Past-Future framework.',
            'clarity_feedback': 'Smooth, confident, and professional.',
            'completeness_feedback': 'Touches upon academics, technical projects, internship, and career alignment.',
            'overall_feedback': 'A great elevator pitch that establishes value immediately.',
            'missing_points': '- Stating a unique personal differentiator or competitive programming accomplishment.',
            'improved_answer': 'I am a final-year Computer Science student at DTU specializing in backend distributed architectures. During my recent internship at CloudNative Systems, I optimized database queries and built asynchronous Redis queues that handled high data ingestion. I recently architected PrepMate, integrating IBM Granite foundation models. I am excited about this role because your team tackles high-concurrency systems, where my foundation in Python, SQL, and clean software architecture can create tangible impact from day one.',
            'rag_sources': 'hr_questions.txt (Introduction and Elevator Pitch)',
            'model_used': 'IBM Granite 3-8B Instruct'
        },
        {
            'session_id': session_id_2,
            'question_number': 2,
            'category': 'HR - Behavioral & Conflict Resolution',
            'question_text': 'Describe a time when you had a technical disagreement with a team member. How did you handle it?',
            'student_answer': 'During our capstone project, my teammate wanted to use MongoDB for storing relational user transaction logs, while I advocated for PostgreSQL. Rather than arguing, I proposed benchmarking both on mock transaction loads. When we tested multi-table joins and data consistency, the data showed that PostgreSQL preserved ACID constraints much better. We agreed on PostgreSQL and implemented it collaboratively.',
            'relevance_feedback': 'Answers the conflict resolution prompt directly.',
            'correctness_feedback': 'Exemplifies data-driven resolution rather than emotional argument.',
            'clarity_feedback': 'Clear STAR narrative: Situation (capstone), Task (choosing DB), Action (benchmarking), Result (consensus).',
            'completeness_feedback': 'Shows both empathy and rigorous technical decision-making.',
            'overall_feedback': 'Superb behavioral response showcasing mature engineering mindset.',
            'missing_points': '- Highlighting how the relationship remained positive post-decision.',
            'improved_answer': 'In our capstone project, my peer suggested MongoDB while I recommended PostgreSQL for our transactional data. To maintain objectivity, I suggested creating a quick prototype to benchmark both databases against our target write throughput and ACID consistency needs. The benchmark demonstrated that PostgreSQL reduced redundant queries by 40%. My teammate appreciated the objective approach, and we documented the architectural decision record (ADR) together, strengthening our collaboration.',
            'rag_sources': 'hr_questions.txt (Conflict Resolution & Teamwork)',
            'model_used': 'IBM Granite 3-8B Instruct'
        }
    ]

    for qa in session_2_qas:
        InterviewSessionModel.save_qa(qa)
    print(f"[Seeder] Saved {len(session_2_qas)} Q&A records for Session #{session_id_2}.")

    print("\n[Seeder] Seeding completed successfully! Demo data is ready for presentation.")

if __name__ == '__main__':
    seed()

