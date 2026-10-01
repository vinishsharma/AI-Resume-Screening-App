"""
Comprehensive Edge-Case Testing Suite for AI Resume Screening & Ranking System.
"""
import os
import unittest
import tempfile
from src.models.schemas import ParsedResume
from src.screening.filter import evaluate_eligibility
from src.screening.scorer import compute_deterministic_score, detect_penalties
from src.enrichment.github import analyze_github_profile, _GITHUB_CACHE
from src.llm.client import MockLLMClient, GeminiClient
from src.parser.extractor import parse_resume

class TestComprehensiveEdgeCases(unittest.TestCase):

    def test_edge_case_case_insensitive_filtering(self):
        """Ensure case variations like PYTHON, PyThOn, LANGGRAPH pass filtering."""
        text = """
        JOHN DOE
        EXPERIENCE WITH PYTHON, FASTAPI, AND STATEFUL MULTI-AGENT SYSTEMS USING LANGGRAPH.
        """
        parsed = ParsedResume(file_path="case.pdf", raw_text=text, candidate_name="John Doe")
        is_eligible, reasons, skills = evaluate_eligibility(parsed)
        self.assertTrue(is_eligible)
        self.assertEqual(len(reasons), 0)

    def test_edge_case_javascript_java_react_with_python_ai(self):
        """Rule: Do not reject candidate merely because JS/Java/React is present if Python+AI is satisfied."""
        text = """
        Multi-Stack Engineer
        Skills: Java, React.js, Next.js, Python, LangChain, RAG
        Projects:
        - Enterprise RAG: Built RAG pipeline using Python, LangChain, and Next.js UI.
        """
        parsed = ParsedResume(file_path="multistack.pdf", raw_text=text, candidate_name="Multi Stack")
        is_eligible, reasons, skills = evaluate_eligibility(parsed)
        self.assertTrue(is_eligible)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("LangChain", skills)

    def test_edge_case_thin_wrapper_vs_agentic_scoring_contrast(self):
        """Test that thin wrapper gets heavily penalized compared to deep agentic project."""
        thin_resume = ParsedResume(
            file_path="thin.pdf",
            raw_text="Developer who built a simple wrapper around OpenAI API call using Streamlit.",
            candidate_name="Thin Wrapper Dev",
            projects_text="Simple wrapper around OpenAI API call"
        )
        deep_resume = ParsedResume(
            file_path="deep.pdf",
            raw_text="Architected stateful LangGraph multi-agent system with tool-calling, vector search in ChromaDB, Redis caching, and DeepEval evaluation.",
            candidate_name="Deep Agentic Dev",
            projects_text="Stateful LangGraph multi-agent system with tool-calling and DeepEval"
        )

        thin_breakdown, thin_penalties, _, _, _ = compute_deterministic_score(thin_resume)
        deep_breakdown, deep_penalties, _, _, _ = compute_deterministic_score(deep_resume)

        self.assertGreater(thin_penalties.thin_wrapper_deduction, 0)
        self.assertEqual(deep_penalties.thin_wrapper_deduction, 0)
        self.assertGreater(deep_breakdown.ai_project_depth, thin_breakdown.ai_project_depth)

    def test_edge_case_github_rate_limit_or_missing_user(self):
        """Test that invalid or rate-limited GitHub handle returns 0 score without raising exception."""
        score, summary = analyze_github_profile("non_existent_user_xyz_123456789_test")
        self.assertEqual(score, 0.0)
        self.assertIn("not reachable", summary.lower())

    def test_edge_case_github_caching(self):
        """Verify GitHub results are cached and not refetched within the batch."""
        test_user = "cached_test_user_unique"
        _GITHUB_CACHE[test_user] = (7.5, "Cached active profile.")
        score, summary = analyze_github_profile(test_user)
        self.assertEqual(score, 7.5)
        self.assertEqual(summary, "Cached active profile.")

    def test_edge_case_gemini_client_fallback_on_invalid_key(self):
        """Verify GeminiClient falls back gracefully to deterministic analysis if API key is invalid."""
        client = GeminiClient(api_key="invalid_fake_key_123")
        parsed = ParsedResume(
            file_path="test.pdf",
            raw_text="Python engineer with FastAPI and LangGraph multi-agent experience.",
            candidate_name="Fallback Test"
        )
        # Should not raise an exception, returns valid LLMAnalysisResult via fallback
        result = client.evaluate_resume(parsed)
        self.assertIsNotNone(result)
        self.assertGreater(result.ai_project_depth_score, 0)

    def test_edge_case_corrupted_file_handling(self):
        """Verify zero-byte or non-existent file doesn't crash parser."""
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            temp_path = f.name  # 0 bytes
            parsed = parse_resume(temp_path)
            self.assertTrue(parsed.is_malformed)
            self.assertIn("0 bytes", parsed.error_message)

if __name__ == "__main__":
    unittest.main()
