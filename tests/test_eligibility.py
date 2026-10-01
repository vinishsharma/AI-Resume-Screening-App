"""
Unit tests for deterministic hard eligibility filtering.
"""
import unittest
from src.models.schemas import ParsedResume
from src.screening.filter import evaluate_eligibility, check_python_evidence, check_ai_agentic_evidence

class TestEligibilityFilter(unittest.TestCase):

    def test_eligible_python_and_ai_candidate(self):
        text = """
        Asha Rao
        Email: asha.rao@example.com
        Skills: Python, FastAPI, PostgreSQL, LangGraph, Docker
        Projects:
        - Multi-Agent Orchestrator: Built stateful agentic workflows using LangGraph and tool calling.
        """
        parsed = ParsedResume(file_path="test1.pdf", raw_text=text, candidate_name="Asha Rao")
        is_eligible, reasons, matched_skills = evaluate_eligibility(parsed)
        self.assertTrue(is_eligible)
        self.assertEqual(len(reasons), 0)
        self.assertIn("Python", matched_skills)
        self.assertIn("LangGraph", matched_skills)

    def test_reject_java_react_only_candidate(self):
        text = """
        Rahul Sharma
        Email: rahul.sharma@example.com
        Skills: Java, Spring Boot, React, Next.js, MySQL
        Projects:
        - E-commerce Portal: Built full stack web application in Java and React.
        """
        parsed = ParsedResume(file_path="test2.pdf", raw_text=text, candidate_name="Rahul Sharma")
        is_eligible, reasons, matched_skills = evaluate_eligibility(parsed)
        self.assertFalse(is_eligible)
        self.assertIn("No evidence of Python stack", reasons)
        self.assertIn("No AI/agentic project evidence", reasons)

    def test_reject_python_only_without_ai(self):
        text = """
        Vikram Patel
        Email: vikram.patel@example.com
        Skills: Python, Django, PostgreSQL, Celery
        Projects:
        - Payment Processing Engine: High-throughput payment processing system using Python and Django.
        """
        parsed = ParsedResume(file_path="test3.pdf", raw_text=text, candidate_name="Vikram Patel")
        is_eligible, reasons, matched_skills = evaluate_eligibility(parsed)
        self.assertFalse(is_eligible)
        self.assertNotIn("No evidence of Python stack", reasons)
        self.assertIn("No AI/agentic project evidence", reasons)

    def test_allow_python_ai_with_javascript_react_present(self):
        text = """
        Priya Nair
        Email: priya.nair@example.com
        Skills: Python, TypeScript, React, Next.js, LangChain, ChromaDB
        Projects:
        - RAG Knowledge Base: Built retrieval-augmented generation search with Python FastAPI and React frontend.
        """
        parsed = ParsedResume(file_path="test4.pdf", raw_text=text, candidate_name="Priya Nair")
        is_eligible, reasons, matched_skills = evaluate_eligibility(parsed)
        self.assertTrue(is_eligible)
        self.assertEqual(len(reasons), 0)

    def test_malformed_resume_rejection(self):
        parsed = ParsedResume(
            file_path="corrupt.pdf",
            raw_text="",
            candidate_name="corrupt.pdf",
            is_malformed=True,
            error_message="File is empty"
        )
        is_eligible, reasons, matched_skills = evaluate_eligibility(parsed)
        self.assertFalse(is_eligible)
        self.assertTrue(any("Unreadable" in r for r in reasons))

if __name__ == "__main__":
    unittest.main()
