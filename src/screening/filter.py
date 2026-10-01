"""
Deterministic hard-rule eligibility filter for screening resumes.
"""
import re
from typing import Tuple, List, Dict, Set
from ..models.schemas import ParsedResume

# Python Stack Keywords & Patterns
PYTHON_PATTERNS = [
    r'\bpython\b',
    r'\bpython3\b',
    r'\bfastapi\b',
    r'\bflask\b',
    r'\bdjango\b',
    r'\bpytorch\b',
    r'\btensorflow\b',
    r'\bpandas\b',
    r'\bnumpy\b',
    r'\bscikit-learn\b',
    r'\bpoetry\b',
    r'\bpipenv\b'
]

# AI / Agentic / RAG Patterns
AI_AGENTIC_PATTERNS = [
    r'\blangchain\b',
    r'\blanggraph\b',
    r'\bllamaindex\b',
    r'\bllama-index\b',
    r'\bgoogle adk\b',
    r'\bautogen\b',
    r'\bcrewai\b',
    r'\brag\b',
    r'\bretrieval[- ]augmented generation\b',
    r'\bvector database\b|\bvector db\b|\bvector search\b|\bembeddings?\b|\bchromadb\b|\bpinecone\b|\bqdrant\b|\bweaviate\b|\bfaiss\b',
    r'\btool[- ]calling\b|\btool[- ]use\b|\bfunction[- ]calling\b',
    r'\bmulti[- ]agent\b|\bagentic\b|\bautonomous agent\b|\bllm agent\b|\bai agent\b',
    r'\bprompt engineering\b|\bevaluation pipeline\b|\bllm evaluation\b|\bfinetun\w*\b|\bfine-tun\w*\b',
    r'\bopenai\b|\banthropic\b|\bclaude\b|\bgpt[- ]?4\b|\bgpt[- ]?3\.5\b|\bgemini\b|\bllm\b|\blarge language models?\b'
]

# Common non-Python/other tech skills to capture matched skills
GENERAL_SKILLS = [
    "Python", "FastAPI", "Flask", "Django", "PostgreSQL", "Redis", "Docker", "Kubernetes", "GCP", "AWS", "Azure",
    "LangChain", "LangGraph", "LlamaIndex", "ChromaDB", "Pinecone", "Qdrant", "FAISS", "OpenAI", "PyTorch", "TensorFlow",
    "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Vue", "Java", "Spring Boot", "C++", "Golang", "Rust", "GraphQL", "MongoDB", "SQL"
]

def check_python_evidence(text: str) -> bool:
    """Check if Python appears genuinely in the resume."""
    text_lower = text.lower()
    for pattern in PYTHON_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def check_ai_agentic_evidence(text: str) -> bool:
    """Check if meaningful AI/LLM/RAG/agentic evidence exists."""
    text_lower = text.lower()
    for pattern in AI_AGENTIC_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def extract_matched_skills(text: str) -> List[str]:
    """Extract list of recognized technologies present in the text."""
    matched = []
    text_lower = text.lower()
    for skill in GENERAL_SKILLS:
        skill_clean = skill.lower()
        # Word boundary search
        pattern = r'\b' + re.escape(skill_clean) + r'\b'
        if re.search(pattern, text_lower):
            matched.append(skill)
    return matched

def evaluate_eligibility(parsed: ParsedResume) -> Tuple[bool, List[str], List[str]]:
    """
    Evaluate candidate hard eligibility.
    Returns:
        (is_eligible, rejection_reasons, matched_skills)
    """
    if parsed.is_malformed:
        return False, [f"Unreadable file: {parsed.error_message or 'Corrupted format'}"], []

    text = parsed.raw_text
    has_python = check_python_evidence(text)
    has_ai = check_ai_agentic_evidence(text)
    matched_skills = extract_matched_skills(text)

    rejection_reasons = []
    if not has_python:
        rejection_reasons.append("No evidence of Python stack")
    if not has_ai:
        rejection_reasons.append("No AI/agentic project evidence")

    is_eligible = len(rejection_reasons) == 0
    return is_eligible, rejection_reasons, matched_skills
