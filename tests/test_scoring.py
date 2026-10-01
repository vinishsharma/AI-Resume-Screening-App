"""
Unit tests for the 100-point candidate scoring engine and project penalties.
"""
import unittest
from src.models.schemas import ParsedResume
from src.screening.scorer import compute_deterministic_score, detect_penalties

class TestScoringEngine(unittest.TestCase):

    def test_strong_agentic_candidate_score(self):
        text = """
        Asha Rao
        Skills: Python, FastAPI, PostgreSQL, LangGraph, Docker, GCP, Redis, PyTest
        Projects:
        - Multi-Agent Research System: Built stateful multi-agent workflows using LangGraph and tool-calling with vector search and evaluation pipelines.
        - Async Backend: Deployed async FastAPI service on GCP with Docker, Redis caching, and unit testing using pytest.
        """
        parsed = ParsedResume(file_path="asha.pdf", raw_text=text, candidate_name="Asha Rao", projects_text=text)
        breakdown, penalties, strengths, concerns, summary = compute_deterministic_score(parsed, github_score=8.0)
        
        # Should achieve high scores in AI, Python, Cloud, GitHub
        self.assertGreaterEqual(breakdown.ai_project_depth, 30.0)
        self.assertGreaterEqual(breakdown.python_backend, 20.0)
        self.assertEqual(penalties.thin_wrapper_deduction, 0.0)
        self.assertEqual(penalties.tutorial_deduction, 0.0)

    def test_thin_wrapper_penalty_deduction(self):
        text = """
        John Doe
        Skills: Python, Flask
        Projects:
        - Simple Chatbot: Created a simple wrapper around OpenAI API call using Streamlit.
        """
        parsed = ParsedResume(file_path="john.pdf", raw_text=text, candidate_name="John Doe", projects_text=text)
        breakdown, penalties, strengths, concerns, summary = compute_deterministic_score(parsed, github_score=0.0)
        
        # Penalties must be triggered
        self.assertGreater(penalties.thin_wrapper_deduction, 0.0)
        self.assertTrue(any("Thin Wrapper" in r for r in penalties.penalty_reasons))
        self.assertTrue(any("Thin Wrapper" in c for c in concerns))

    def test_tutorial_project_penalty_deduction(self):
        text = """
        Sam Wilson
        Skills: Python, LangChain
        Projects:
        - Tutorial Project: Followed tutorial to build basic todo app with LangChain wrapper.
        """
        parsed = ParsedResume(file_path="sam.pdf", raw_text=text, candidate_name="Sam Wilson", projects_text=text)
        breakdown, penalties, strengths, concerns, summary = compute_deterministic_score(parsed, github_score=0.0)
        
        # Tutorial penalty must be deducted
        self.assertGreater(penalties.tutorial_deduction, 0.0)
        self.assertTrue(any("Tutorial" in r for r in penalties.penalty_reasons))

    def test_score_caps(self):
        # Even with excessive keywords, category scores cannot exceed category limits
        text = """
        Mega Candidate
        Python FastAPI Flask Django Asyncio Celery Uvicorn PostgreSQL MySQL SQLAlchemy Alembic Redis Memcached
        LangGraph Multi-Agent AutoGen CrewAI RAG Retrieval Vector Embeddings ChromaDB Pinecone Tool-Calling Evaluation DeepEval LangChain
        Docker GCP AWS Azure Kubernetes React Next.js TypeScript
        PyTest CI/CD GitHub Actions Prometheus Grafana Logging Concurrency
        """
        parsed = ParsedResume(file_path="mega.pdf", raw_text=text, candidate_name="Mega Candidate", projects_text=text)
        breakdown, penalties, strengths, concerns, summary = compute_deterministic_score(parsed, github_score=15.0)
        
        self.assertLessEqual(breakdown.ai_project_depth, 40.0)
        self.assertLessEqual(breakdown.python_backend, 30.0)
        self.assertLessEqual(breakdown.cloud_fullstack, 15.0)
        self.assertLessEqual(breakdown.github, 10.0)
        self.assertLessEqual(breakdown.engineering_depth, 5.0)

if __name__ == "__main__":
    unittest.main()
