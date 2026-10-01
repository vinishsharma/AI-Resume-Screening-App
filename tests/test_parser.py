"""
Unit tests for document parsing, cleaner regex, and metadata extraction.
"""
import os
import unittest
import tempfile
from src.parser.cleaner import extract_email, extract_github_url, clean_text, extract_candidate_name
from src.parser.extractor import parse_resume

class TestParser(unittest.TestCase):

    def test_extract_email(self):
        text = "Contact me at asha.rao@gmail.com or support@company.org for queries."
        email = extract_email(text)
        self.assertEqual(email, "asha.rao@gmail.com")

    def test_extract_github_url(self):
        text = "Portfolio: https://github.com/asharao-dev. Check out my code!"
        url, user = extract_github_url(text)
        self.assertEqual(url, "https://github.com/asharao-dev")
        self.assertEqual(user, "asharao-dev")

    def test_extract_github_handle(self):
        text = "GitHub: @devuser99"
        url, user = extract_github_url(text)
        self.assertEqual(url, "https://github.com/devuser99")
        self.assertEqual(user, "devuser99")

    def test_parse_txt_resume(self):
        content = """Asha Rao
asha.rao@example.com
https://github.com/asharao
Skills: Python, FastAPI, LangGraph
Projects:
- Multi Agent Workflow: State machine orchestration.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parsed = parse_resume(temp_path)
            self.assertFalse(parsed.is_malformed)
            self.assertEqual(parsed.candidate_name, "Asha Rao")
            self.assertEqual(parsed.email, "asha.rao@example.com")
            self.assertEqual(parsed.github_url, "https://github.com/asharao")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_parse_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            parsed = parse_resume(temp_path)
            self.assertTrue(parsed.is_malformed)
            self.assertIn("empty", parsed.error_message.lower())
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
