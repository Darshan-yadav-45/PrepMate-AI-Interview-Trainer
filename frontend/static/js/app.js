/**
 * PrepMate - AI Interview Trainer Agent
 * Frontend Application Logic & IBM Granite API Orchestration
 * AICTE-IBM SkillsBuild University Engagements 2026
 */

// Global State
const PrepMate = {
  currentSession: null,
  mockQuestions: [],
  currentQuestionIndex: 0,
  isLiveModel: false
};

// UI Helpers
function showLoading(message = "Processing with IBM Granite...") {
  const overlay = document.getElementById("loadingOverlay");
  const text = document.getElementById("loadingText");
  if (text) text.textContent = message;
  if (overlay) overlay.style.display = "flex";
}

function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "none";
}

function showAlert(containerId, message, type = "info") {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      <i class="bi ${type === 'danger' ? 'bi-exclamation-triangle-fill' : type === 'success' ? 'bi-check-circle-fill' : 'bi-info-circle-fill'} me-2"></i>
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
}

// Speech Synthesis Helper (Web Speech API)
function speakText(text) {
  if (!window.speechSynthesis) {
    alert("Speech synthesis is not supported on this browser.");
    return;
  }
  window.speechSynthesis.cancel(); // Stop any active speech
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

// ==============================================================================
// Question Generator Module (Module 3)
// ==============================================================================
function initQuestionGenerator() {
  const form = document.getElementById("questionGenForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const job_role = document.getElementById("genJobRole").value.trim();
    const interview_type = document.getElementById("genInterviewType").value;
    const difficulty = document.getElementById("genDifficulty").value;
    const num_questions = parseInt(document.getElementById("genNumQuestions").value, 10);

    if (!job_role) {
      showAlert("genAlertContainer", "Please specify a target job role.", "warning");
      return;
    }

    showLoading("IBM Granite is generating personalized questions with RAG context...");
    try {
      const resp = await fetch("/api/generate-questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_role,
          interview_type,
          difficulty,
          num_questions
        })
      });

      const data = await resp.json();
      hideLoading();

      if (!data.success) {
        showAlert("genAlertContainer", data.error || "Failed to generate questions.", "danger");
        return;
      }

      renderGeneratedQuestions(data);
    } catch (err) {
      hideLoading();
      showAlert("genAlertContainer", "Network or server error while contacting IBM Granite.", "danger");
      console.error(err);
    }
  });
}

function renderGeneratedQuestions(data) {
  const container = document.getElementById("questionsResultContainer");
  const list = document.getElementById("questionsList");
  const metaBadge = document.getElementById("modelUsedBadge");
  const ragSourcesBadge = document.getElementById("ragSourcesBadge");

  if (!container || !list) return;

  if (metaBadge) {
    metaBadge.textContent = data.is_mock
      ? `Model: ${data.model_used}`
      : `Live Granite: ${data.model_used}`;
    metaBadge.className = data.is_mock ? "badge badge-mock" : "badge badge-granite";
  }

  if (ragSourcesBadge) {
    const sourcesCount = data.rag_sources ? data.rag_sources.length : 0;
    ragSourcesBadge.textContent = `RAG: ${sourcesCount} Reference Chunks Attached`;
  }

  list.innerHTML = "";
  data.questions.forEach((q, idx) => {
    const item = document.createElement("div");
    item.className = "card card-custom mb-3";
    item.innerHTML = `
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="question-badge">Question ${q.number || (idx + 1)}</span>
          <span class="badge bg-light text-dark border">${q.category || 'General'}</span>
        </div>
        <h5 class="card-title fw-bold text-dark mt-2">${escapeHtml(q.question)}</h5>
        <p class="text-muted small mb-3">
          <i class="bi bi-bullseye text-primary me-1"></i>
          <strong>Objective:</strong> ${escapeHtml(q.interviewer_objective || 'Evaluates subject matter comprehension.')}
        </p>
        <div class="d-flex gap-2 flex-wrap">
          <button class="btn btn-sm btn-outline-custom" onclick="practiceQuestion(${JSON.stringify(escapeHtml(q.question))}, ${JSON.stringify(escapeHtml(data.job_role))})">
            <i class="bi bi-pencil-square me-1"></i> Answer & Evaluate
          </button>
          <button class="btn btn-sm btn-light border" onclick="speakText(${JSON.stringify(q.question)})">
            <i class="bi bi-volume-up me-1"></i> Read Aloud
          </button>
        </div>
      </div>
    `;
    list.appendChild(item);
  });

  container.style.display = "block";
  container.scrollIntoView({ behavior: "smooth" });
}

function practiceQuestion(questionText, role) {
  // Store in sessionStorage and route to evaluator
  sessionStorage.setItem("eval_question", questionText);
  sessionStorage.setItem("eval_role", role);
  window.location.href = "/evaluator";
}

// ==============================================================================
// Answer Evaluator Module (Module 4)
// ==============================================================================
function initAnswerEvaluator() {
  const form = document.getElementById("answerEvalForm");
  if (!form) return;

  // Check if pre-filled from generator
  const savedQuestion = sessionStorage.getItem("eval_question");
  const savedRole = sessionStorage.getItem("eval_role");
  if (savedQuestion) {
    const qField = document.getElementById("evalQuestion");
    if (qField) qField.value = savedQuestion;
    sessionStorage.removeItem("eval_question");
  }
  if (savedRole) {
    const rField = document.getElementById("evalJobRole");
    if (rField) rField.value = savedRole;
    sessionStorage.removeItem("eval_role");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = document.getElementById("evalQuestion").value.trim();
    const answer = document.getElementById("evalAnswer").value.trim();
    const job_role = document.getElementById("evalJobRole").value.trim();

    if (!question) {
      showAlert("evalAlertContainer", "Please enter or select an interview question.", "warning");
      return;
    }
    if (!answer || answer.length < 5) {
      showAlert("evalAlertContainer", "Please provide a complete answer for IBM Granite to evaluate.", "warning");
      return;
    }

    showLoading("IBM Granite is evaluating your response against engineering benchmarks...");
    try {
      const resp = await fetch("/api/evaluate-answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, answer, job_role })
      });

      const data = await resp.json();
      hideLoading();

      if (!data.success) {
        showAlert("evalAlertContainer", data.error || "Evaluation failed.", "danger");
        return;
      }

      renderEvaluationResult(data.evaluation);
    } catch (err) {
      hideLoading();
      showAlert("evalAlertContainer", "Network or server error contacting IBM Granite.", "danger");
      console.error(err);
    }
  });
}

function renderEvaluationResult(ev) {
  const resultCard = document.getElementById("evaluationResultCard");
  if (!resultCard) return;

  // Set criteria
  document.getElementById("evalRelevance").textContent = ev.relevance || "Addressed correctly.";
  document.getElementById("evalCorrectness").textContent = ev.technical_correctness || "Concepts accurate.";
  document.getElementById("evalClarity").textContent = ev.clarity || "Well-articulated.";
  document.getElementById("evalCompleteness").textContent = ev.completeness || "Fundamental points covered.";
  document.getElementById("evalOverallFeedback").textContent = ev.overall_feedback || "";

  // Missing points
  const missingList = document.getElementById("evalMissingPoints");
  missingList.innerHTML = "";
  if (ev.missing_points && ev.missing_points.length > 0) {
    ev.missing_points.forEach(item => {
      const li = document.createElement("li");
      li.className = "mb-1 text-danger";
      li.innerHTML = `<i class="bi bi-exclamation-circle me-1"></i> ${escapeHtml(item)}`;
      missingList.appendChild(li);
    });
  } else {
    missingList.innerHTML = '<li class="text-success"><i class="bi bi-check-circle me-1"></i> All key technical points addressed!</li>';
  }

  // Improved sample answer
  document.getElementById("evalImprovedAnswer").textContent = ev.improved_answer || "Practice clear definitions and trade-offs.";

  // Suggestions
  const sugList = document.getElementById("evalSuggestions");
  sugList.innerHTML = "";
  if (ev.suggestions && ev.suggestions.length > 0) {
    ev.suggestions.forEach(s => {
      const li = document.createElement("li");
      li.className = "mb-1 text-primary";
      li.innerHTML = `<i class="bi bi-lightbulb me-1"></i> ${escapeHtml(s)}`;
      sugList.appendChild(li);
    });
  }

  // Model & RAG badges
  const modelBadge = document.getElementById("evalModelBadge");
  if (modelBadge) {
    modelBadge.textContent = ev.is_mock ? `Model: ${ev.model_used}` : `Live IBM Granite: ${ev.model_used}`;
    modelBadge.className = ev.is_mock ? "badge badge-mock" : "badge badge-granite";
  }

  resultCard.style.display = "block";
  resultCard.scrollIntoView({ behavior: "smooth" });
}

// ==============================================================================
// Interactive Mock Interview Module (Module 5)
// ==============================================================================
function initMockInterview() {
  const startBtn = document.getElementById("startMockBtn");
  if (!startBtn) return;

  startBtn.addEventListener("click", startMockSession);

  const submitAnswerBtn = document.getElementById("mockSubmitAnswerBtn");
  if (submitAnswerBtn) {
    submitAnswerBtn.addEventListener("click", submitMockAnswer);
  }

  const nextBtn = document.getElementById("mockNextQuestionBtn");
  if (nextBtn) {
    nextBtn.addEventListener("click", advanceToNextQuestion);
  }
}

async function startMockSession() {
  const jobRole = document.getElementById("mockJobRole").value.trim();
  const interviewType = document.getElementById("mockInterviewType").value;
  const difficulty = document.getElementById("mockDifficulty").value;

  if (!jobRole) {
    showAlert("mockAlertContainer", "Please select or type a target job role.", "warning");
    return;
  }

  showLoading("Configuring mock interview and generating 5 questions with IBM Granite...");
  try {
    const resp = await fetch("/api/mock/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_role: jobRole,
        interview_type: interviewType,
        difficulty: difficulty
      })
    });

    const data = await resp.json();
    hideLoading();

    if (!data.success) {
      showAlert("mockAlertContainer", data.error || "Could not start session.", "danger");
      return;
    }

    PrepMate.currentSession = {
      sessionId: data.session_id,
      jobRole: data.job_role,
      interviewType: data.interview_type,
      difficulty: data.difficulty,
      questions: data.questions,
      currentIndex: 0,
      answers: []
    };

    // Transition UI to Active Session
    document.getElementById("mockSetupCard").style.display = "none";
    document.getElementById("mockActiveCard").style.display = "block";
    renderCurrentMockQuestion();

  } catch (err) {
    hideLoading();
    showAlert("mockAlertContainer", "Error starting mock interview session.", "danger");
    console.error(err);
  }
}

function renderCurrentMockQuestion() {
  const s = PrepMate.currentSession;
  if (!s) return;

  const q = s.questions[s.currentIndex];
  const total = s.questions.length;
  const currNum = s.currentIndex + 1;

  // Update progress
  const progressBar = document.getElementById("mockProgressBar");
  const progressText = document.getElementById("mockProgressText");
  const percent = Math.round(((currNum - 1) / total) * 100);

  if (progressBar) progressBar.style.width = `${percent}%`;
  if (progressText) progressText.textContent = `Question ${currNum} of ${total}`;

  // Update question content
  document.getElementById("mockQuestionNumberBadge").textContent = `Question ${currNum}`;
  document.getElementById("mockCategoryBadge").textContent = q.category || 'General';
  document.getElementById("mockQuestionText").textContent = q.question;
  document.getElementById("mockAnswerInput").value = "";
  document.getElementById("mockFeedbackContainer").style.display = "none";

  // Button states
  document.getElementById("mockSubmitAnswerBtn").style.display = "inline-block";
  document.getElementById("mockNextQuestionBtn").style.display = "none";
}

async function submitMockAnswer() {
  const s = PrepMate.currentSession;
  if (!s) return;

  const answer = document.getElementById("mockAnswerInput").value.trim();
  if (!answer || answer.length < 5) {
    showAlert("mockSessionAlert", "Please enter an answer before continuing.", "warning");
    return;
  }

  const q = s.questions[s.currentIndex];
  showLoading("IBM Granite is evaluating your response...");

  try {
    const resp = await fetch("/api/mock/submit-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: s.sessionId,
        question_number: s.currentIndex + 1,
        question_text: q.question,
        category: q.category,
        student_answer: answer,
        job_role: s.jobRole
      })
    });

    const data = await resp.json();
    hideLoading();

    if (!data.success) {
      showAlert("mockSessionAlert", data.error || "Answer submission failed.", "danger");
      return;
    }

    // Save answer to session
    s.answers.push({
      question: q.question,
      answer: answer,
      evaluation: data.evaluation
    });

    // Display inline feedback
    renderMockQuestionFeedback(data.evaluation);

    // Toggle buttons
    document.getElementById("mockSubmitAnswerBtn").style.display = "none";
    const nextBtn = document.getElementById("mockNextQuestionBtn");
    nextBtn.style.display = "inline-block";

    if (s.currentIndex + 1 >= s.questions.length) {
      nextBtn.innerHTML = '<i class="bi bi-award-fill me-1"></i> Finish & Generate Report';
    } else {
      nextBtn.innerHTML = '<i class="bi bi-arrow-right-circle me-1"></i> Next Question';
    }

  } catch (err) {
    hideLoading();
    showAlert("mockSessionAlert", "Error submitting answer to IBM Granite.", "danger");
    console.error(err);
  }
}

function renderMockQuestionFeedback(ev) {
  const container = document.getElementById("mockFeedbackContainer");
  if (!container) return;

  document.getElementById("mockFbOverall").textContent = ev.overall_feedback || "Answer noted.";
  document.getElementById("mockFbImproved").textContent = ev.improved_answer || "Focus on definitions and real-world examples.";
  
  const missingUl = document.getElementById("mockFbMissing");
  missingUl.innerHTML = "";
  if (ev.missing_points && ev.missing_points.length > 0) {
    ev.missing_points.forEach(item => {
      const li = document.createElement("li");
      li.className = "text-danger small";
      li.textContent = item;
      missingUl.appendChild(li);
    });
  } else {
    missingUl.innerHTML = '<li class="text-success small">Great job! No major concepts omitted.</li>';
  }

  container.style.display = "block";
}

async function advanceToNextQuestion() {
  const s = PrepMate.currentSession;
  if (!s) return;

  s.currentIndex++;
  if (s.currentIndex < s.questions.length) {
    renderCurrentMockQuestion();
  } else {
    // Session complete, finalize
    await finalizeMockSession();
  }
}

async function finalizeMockSession() {
  const s = PrepMate.currentSession;
  if (!s) return;

  showLoading("IBM Granite is compiling your complete session report and growth roadmap...");
  try {
    const resp = await fetch("/api/mock/finalize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: s.sessionId })
    });

    const data = await resp.json();
    hideLoading();

    if (!data.success) {
      showAlert("mockSessionAlert", "Failed to finalize session summary.", "danger");
      return;
    }

    renderMockFinalSummary(data);

  } catch (err) {
    hideLoading();
    showAlert("mockSessionAlert", "Network error finalizing session.", "danger");
    console.error(err);
  }
}

function renderMockFinalSummary(data) {
  document.getElementById("mockActiveCard").style.display = "none";
  const summaryCard = document.getElementById("mockSummaryCard");

  document.getElementById("finalSummaryText").textContent = data.summary || "Mock interview session completed.";
  document.getElementById("finalAdviceText").textContent = data.final_advice || "Keep practicing!";

  const strengthsList = document.getElementById("finalStrengthsList");
  strengthsList.innerHTML = "";
  (data.strengths || []).forEach(s => {
    const li = document.createElement("li");
    li.className = "mb-2 text-success";
    li.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${escapeHtml(s)}`;
    strengthsList.appendChild(li);
  });

  const improvementsList = document.getElementById("finalImprovementsList");
  improvementsList.innerHTML = "";
  (data.improvements || []).forEach(i => {
    const li = document.createElement("li");
    li.className = "mb-2 text-primary";
    li.innerHTML = `<i class="bi bi-arrow-up-circle-fill me-2"></i> ${escapeHtml(i)}`;
    improvementsList.appendChild(li);
  });

  const detailLink = document.getElementById("viewHistoryDetailLink");
  if (detailLink) {
    detailLink.href = `/history/${data.session_id}`;
  }

  summaryCard.style.display = "block";
  summaryCard.scrollIntoView({ behavior: "smooth" });
}

// Utility: HTML escaping to prevent injection
function escapeHtml(text) {
  if (!text) return "";
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
}

// DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initQuestionGenerator();
  initAnswerEvaluator();
  initMockInterview();
});
