# AI Resume Screening & Ranking System

An intelligent, production-minded resume screening and ranking backend built for high-throughput evaluation of candidates applying for Python + AI/Agentic SDE roles.

---

## 📌 Overview

The system ingests candidate resumes (`.pdf`, `.docx`, `.txt`), deterministically enforces hard eligibility filters (Python fundamentals + practical AI/agentic exposure), scores eligible candidates across a calibrated 100-point rubric with strict project-quality penalties, enriches candidate scores using public GitHub activity, and exports explainable ranked shortlists with detailed score breakdowns.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.10 – 3.14)
- Zero mandatory external dependencies required for core execution (includes pure-Python fallbacks for PDF parsing, text extraction, JSON schema validation, and HTTP APIs).

### 2. Setup Environment
```bash
# Clone or navigate to the project directory
cd /path/to/project

# Copy environment template
cp .env.example .env
```

### 3. Run the Screening Pipeline (CLI)
```bash
python3 main.py --input ./resumes --output ./output/results.json
```

### 4. Run Unit Tests
```bash
python3 -m unittest discover tests
```

### 5. (Optional) Run the REST API Server
```bash
python3 server.py --port 8000
```
- **Health Check**: `GET http://localhost:8000/health`
- **Trigger Batch Run**: `POST http://localhost:8000/screen` (Body: `{"input_dir": "./resumes"}`)
- **Get Results**: `GET http://localhost:8000/results`

---

## 📊 100-Point Scoring Model & Penalties

| Dimension | Max Points | Criteria & Signals |
| :--- | :---: | :--- |
| **AI / Agentic / RAG Project Depth** | **40** | Multi-agent stateful workflows (LangGraph, CrewAI, AutoGen), RAG pipelines, vector search (ChromaDB, Pinecone, FAISS), tool-calling, evaluation metrics (DeepEval, Ragas). |
| **Python & Backend Engineering** | **30** | Production Python, asynchronous FastAPI/AsyncIO, PostgreSQL, Redis caching, task queues (Celery). |
| **Cloud / Deployment / Full Stack** | **15** | Docker containerization, GCP / AWS deployment, CI/CD pipelines, React/Next.js frontend integration. |
| **GitHub Activity** | **10** | 0–5 pts for recent commits/events + 0–5 pts for active, maintained Python/AI repositories. |
| **Engineering Depth Signals** | **5** | Automated testing (pytest), observability, caching, concurrency, rate limiting. |

### ⚠️ Project-Quality Penalties (Crucial Guardrails)
- **-5 to -15 Points (Thin Wrapper Deduction)**: Applied when an "AI project" is merely a single-prompt API wrapper around OpenAI/LLMs without retrieval, state management, backend logic, or evaluation.
- **-5 to -10 Points (Tutorial Project Deduction)**: Deducted for generic tutorial copies or boilerplate clones lacking evidence of independent ownership.
- **Keyword Stuffing Discount**: Frameworks listed only in skills without contextual project implementation details are not awarded project depth points.
- **Non-AI Cap**: Strong Python developers lacking AI project depth are capped at low AI depth scores and cannot rank at the top.

---

## 📂 Project Structure

```
.
├── src/
│   ├── config.py             # Centralized settings & scoring weights
│   ├── generate_test_resumes.py # Benchmark synthetic resume generator
│   ├── enrichment/
│   │   └── github.py         # GitHub API client with caching & rate-limit resilience
│   ├── llm/
│   │   ├── client.py         # Pluggable LLM client adapter (Mock, OpenAI, Gemini)
│   │   └── prompts.py        # Structured JSON prompts and system schema
│   ├── models/
│   │   └── schemas.py        # Pydantic data schemas (CandidateResult, ScoreBreakdown, BatchSummary)
│   ├── parser/
│   │   ├── cleaner.py        # Regex extraction (emails, GitHub handles, sections)
│   │   └── extractor.py      # Resilient PDF/DOCX/TXT document parsing engine
│   ├── screening/
│   │   ├── filter.py         # Deterministic hard-rule eligibility filter
│   │   └── scorer.py         # 100-pt scoring engine with penalty logic
│   └── pipeline.py           # ThreadPoolExecutor batch orchestrator
├── tests/
│   ├── test_eligibility.py   # Unit tests for hard filtering edge cases
│   ├── test_parser.py        # Unit tests for text & metadata extraction
│   └── test_scoring.py       # Unit tests for 100-pt scoring and penalties
├── resumes/                  # Synthetic test resumes
├── output/
│   └── results.json          # Formatted screening output
├── main.py                   # CLI entrypoint
├── server.py                 # REST API server
├── requirements.txt          # Package requirements
├── .env.example              # Environment variables template
└── README.md
```

---

## 🏗️ Design Decisions

### 1. Deterministic Hard Filtering Outside the LLM
- Hard eligibility filters (verifying genuine Python experience AND meaningful AI/agentic project presence) are executed deterministically before expensive semantic or network operations.
- This guarantees 100% predictable exclusion of Java/React-only or non-AI profiles while keeping the pipeline cost-efficient and sub-second fast.

### 2. Multi-Tiered Penalty Engine
- To prevent candidates who merely called an LLM API or cloned a tutorial repo from receiving top ranks, the scoring engine analyzes project descriptions for markers of shallow wrappers (`simple wrapper`, `streamlit calling openai`, etc.) and deducts 5–15 points, explaining the deduction explicitly in the output JSON.

### 3. Resilient Parsing with Zero-Crash Guarantee
- Candidate resumes come in diverse formats (PDF streams, DOCX XML, plain text). The parser isolates errors per file. If a file is empty, corrupted, or password-protected, the batch records the failure under `failed_files` and continues without crashing.

### 4. Rate-Limit Resilient GitHub Enrichment & In-Memory Caching
- GitHub enrichment is bounded and capped at 10 points. If the GitHub API is unavailable, rate-limited, or the username is missing/private, the system logs the enrichment status and awards 0 GitHub points without failing screening.
- Responses are cached in-memory during the batch run to avoid redundant requests.

### 5. Pluggable LLM Adapter
- The LLM interface (`BaseLLMClient`) isolates model-specific code. The default `MockLLMClient` uses an explainable heuristic parser for fast offline evaluation, while `OpenAIClient` and `GeminiClient` can be enabled seamlessly via `.env` (`LLM_PROVIDER=openai` / `LLM_PROVIDER=gemini`).

---

## 🔮 If I Had More Time

1. **OCR Support for Scanned Image Resumes**: Integrate `pdf2image` and `tesseract` for resumes exported as pure bitmap images.
2. **Asynchronous GitHub Graph Analysis**: Fetch commit frequency distributions, PR merge history, and repository README semantic embeddings to measure code quality directly from candidate repos.
3. **Automated LLM Judge Calibration Benchmark**: Implement a continuous evaluation harness comparing LLM scoring output against human recruiter ground-truth datasets using Cohen's Kappa score.
4. **Interactive Dashboard UI**: Build a lightweight web view in Next.js/Tailwind to search, filter by skill, and inspect candidate score breakdowns interactively.
# AI-Resume-Screening-App
