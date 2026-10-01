"""
Resume text cleaning and metadata extraction utilities.
"""
import re
from typing import Optional, List, Dict, Tuple

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
GITHUB_REGEX = re.compile(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', re.IGNORECASE)
GITHUB_HANDLE_REGEX = re.compile(r'(?:github|gh):\s*@?([a-zA-Z0-9_-]+)', re.IGNORECASE)

SECTION_HEADERS = [
    r'projects?',
    r'experience|work experience|employment|internships?',
    r'skills?|technical skills?|technologies',
    r'education|academics?',
    r'open source|contributions',
    r'certifications?|achievements?'
]

def clean_text(text: str) -> str:
    """Normalize whitespace and strip non-printable characters."""
    if not text:
        return ""
    # Normalize unicode spaces/quotes
    text = text.replace('\xa0', ' ').replace('\u2013', '-').replace('\u2014', '--')
    text = text.replace('“', '"').replace('”', '"').replace('’', "'")
    # Replace multiple newlines/spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def extract_email(text: str) -> Optional[str]:
    """Extract candidate email from text."""
    matches = EMAIL_REGEX.findall(text)
    if matches:
        return matches[0].strip()
    return None

def extract_github_url(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract full GitHub URL and GitHub username from resume text.
    Returns: (github_url, github_username)
    """
    match = GITHUB_REGEX.search(text)
    if match:
        username = match.group(1).rstrip('/')
        # Filter out generic words
        if username.lower() not in ("about", "features", "pricing", "login", "signup", "contact"):
            return f"https://github.com/{username}", username
            
    match_handle = GITHUB_HANDLE_REGEX.search(text)
    if match_handle:
        username = match_handle.group(1)
        return f"https://github.com/{username}", username
        
    return None, None

def extract_candidate_name(text: str, file_path: str = "") -> str:
    """
    Extract candidate name from the top header lines of the resume
    or fallback to formatted filename.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:5]:
        # Exclude lines that are headers, emails, links, or too long
        if '@' in line or 'http' in line or 'github' in line or 'resume' in line.lower() or 'curriculum' in line.lower():
            continue
        # Check if line looks like a person's name (2-4 capitalized words, no numbers)
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()) and not any(c.isdigit() for c in line):
            # Check length is reasonable
            if len(line) < 40:
                return line
                
    # Fallback to filename
    if file_path:
        import os
        base = os.path.splitext(os.path.basename(file_path))[0]
        # Clean candidate_01 or john_doe_resume
        base_clean = re.sub(r'(_resume|resume|_cv|cv|\d+)', '', base, flags=re.IGNORECASE)
        base_clean = base_clean.replace('_', ' ').replace('-', ' ').strip()
        if base_clean:
            return base_clean.title()
            
    return "Candidate"

def segment_sections(text: str) -> Dict[str, str]:
    """Segment resume text into logical sections."""
    sections = {
        "skills": "",
        "projects": "",
        "experience": "",
        "education": "",
        "other": ""
    }
    
    current_section = "other"
    pattern = re.compile(r'^(?:[#\*\-\s]*)(skills?|projects?|experience|work experience|education|certifications?)(?:[:\s\*\-]*)$', re.IGNORECASE)
    
    for line in text.split('\n'):
        line_clean = line.strip()
        match = pattern.match(line_clean)
        if match:
            header = match.group(1).lower()
            if 'skill' in header:
                current_section = "skills"
            elif 'project' in header:
                current_section = "projects"
            elif 'experience' in header or 'work' in header:
                current_section = "experience"
            elif 'education' in header:
                current_section = "education"
            else:
                current_section = "other"
            continue
        sections[current_section] += line + "\n"
        
    return sections
