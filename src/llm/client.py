"""
Pluggable LLM client adapter supporting Mock/Heuristic, OpenAI, and Gemini with JSON enforcement and detailed logging.
"""
import os
import json
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..models.schemas import LLMAnalysisResult, ParsedResume
from ..screening.scorer import compute_deterministic_score, detect_penalties
from ..screening.filter import extract_matched_skills
from .prompts import RESUME_EVALUATION_SYSTEM_PROMPT, build_user_prompt
from ..config import config

logger = logging.getLogger("ResumeScreener.LLM")

class BaseLLMClient(ABC):
    @abstractmethod
    def evaluate_resume(self, parsed: ParsedResume) -> LLMAnalysisResult:
        """Evaluate resume text and return structured analysis."""
        pass


class MockLLMClient(BaseLLMClient):
    """
    High-fidelity deterministic scoring engine acting as local LLM adapter.
    Evaluates depth, project authenticity, and penalties predictably and testably.
    """
    def evaluate_resume(self, parsed: ParsedResume) -> LLMAnalysisResult:
        logger.info(f"[LLM:Local] Analyzing project depth and penalties for candidate: '{parsed.candidate_name}'")
        breakdown, penalties, strengths, concerns, summary = compute_deterministic_score(parsed, github_score=0.0)
        matched_skills = extract_matched_skills(parsed.raw_text)

        is_thin = penalties.thin_wrapper_deduction > 0
        is_tut = penalties.tutorial_deduction > 0

        return LLMAnalysisResult(
            candidate_name=parsed.candidate_name,
            ai_project_depth_score=breakdown.ai_project_depth,
            python_backend_score=breakdown.python_backend,
            cloud_fullstack_score=breakdown.cloud_fullstack,
            engineering_depth_score=breakdown.engineering_depth,
            is_thin_wrapper=is_thin,
            is_tutorial_clone=is_tut,
            thin_wrapper_penalty=penalties.thin_wrapper_deduction,
            tutorial_penalty=penalties.tutorial_deduction,
            matched_skills=matched_skills,
            project_summary=summary,
            strengths=strengths,
            concerns=concerns,
            evidence={
                "ai_score_reason": f"AI project depth scored at {breakdown.ai_project_depth}/40",
                "penalties_applied": ", ".join(penalties.penalty_reasons) if penalties.penalty_reasons else "No penalties applied"
            }
        )


class OpenAIClient(BaseLLMClient):
    """OpenAI API Client using structured JSON response."""
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.fallback = MockLLMClient()

    def evaluate_resume(self, parsed: ParsedResume) -> LLMAnalysisResult:
        if not self.api_key:
            logger.warning("[LLM:OpenAI] No OpenAI API key provided. Using local heuristic fallback.")
            return self.fallback.evaluate_resume(parsed)

        logger.info(f"[LLM:OpenAI] Sending request to OpenAI model '{self.model}' for '{parsed.candidate_name}'...")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": RESUME_EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(parsed.raw_text)}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                content = result["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)
                logger.info(f"[LLM:OpenAI] Successfully received JSON response for '{parsed.candidate_name}'")
                return LLMAnalysisResult(**parsed_json)
        except Exception as e:
            logger.warning(f"[LLM:OpenAI] API call failed for '{parsed.candidate_name}': {e}. Falling back to local engine.")
            return self.fallback.evaluate_resume(parsed)


class GeminiClient(BaseLLMClient):
    """Gemini API Client using REST interface."""
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.fallback = MockLLMClient()

    def evaluate_resume(self, parsed: ParsedResume) -> LLMAnalysisResult:
        if not self.api_key:
            logger.warning("[LLM:Gemini] No Gemini API key provided. Using local heuristic fallback.")
            return self.fallback.evaluate_resume(parsed)

        logger.info(f"[LLM:Gemini] Sending request to Google Gemini API (model: '{self.model}') for '{parsed.candidate_name}'...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        prompt_text = f"{RESUME_EVALUATION_SYSTEM_PROMPT}\n\n{build_user_prompt(parsed.raw_text)}"
        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                text_out = result["candidates"][0]["content"]["parts"][0]["text"]
                parsed_json = json.loads(text_out)
                logger.info(f"[LLM:Gemini] Successfully received & parsed structured JSON from Gemini for '{parsed.candidate_name}'")
                return LLMAnalysisResult(**parsed_json)
        except Exception as e:
            logger.warning(f"[LLM:Gemini] API connection error for '{parsed.candidate_name}': {e}. Gracefully falling back to local engine.")
            return self.fallback.evaluate_resume(parsed)


def get_llm_client() -> BaseLLMClient:
    """Factory function to return the configured LLM client."""
    provider = config.llm_provider
    if provider == "openai" and config.openai_api_key:
        return OpenAIClient(api_key=config.openai_api_key, model=config.llm_model)
    elif provider == "gemini" and config.gemini_api_key:
        return GeminiClient(api_key=config.gemini_api_key, model=config.llm_model)
    return MockLLMClient()
