"""
Document parsing engine supporting PDF, DOCX, and TXT with robust error recovery.
"""
import os
import re
import zlib
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional
from ..models.schemas import ParsedResume
from .cleaner import clean_text, extract_email, extract_github_url, extract_candidate_name, segment_sections

def extract_text_from_pdf_stream(content: bytes) -> str:
    """
    Pure Python PDF stream text extractor.
    Extracts text from PDF objects, font streams, FlateDecode streams, and text operators (BT ... ET).
    """
    text_chunks = []
    
    # 1. Look for FlateDecode streams and decompress them
    stream_pattern = re.compile(b'stream[\r\n]+(.*?)[\r\n]+endstream', re.DOTALL)
    for match in stream_pattern.finditer(content):
        raw_stream = match.group(1)
        decompressed = b""
        try:
            decompressed = zlib.decompress(raw_stream)
        except Exception:
            try:
                decompressed = zlib.decompress(raw_stream, -15)
            except Exception:
                decompressed = raw_stream
                
        if decompressed:
            # Look for Tj, TJ, and ' operators in decompressed text
            # E.g. (Hello World) Tj or [(Hello) -10 (World)] TJ
            tj_matches = re.findall(rb'\((.*?)\)\s*Tj', decompressed)
            for m in tj_matches:
                try:
                    text_chunks.append(m.decode('utf-8', errors='ignore'))
                except Exception:
                    pass
                    
            tj_array_matches = re.findall(rb'\[(.*?)\]\s*TJ', decompressed)
            for array_content in tj_array_matches:
                inner_strings = re.findall(rb'\((.*?)\)', array_content)
                line = "".join(s.decode('utf-8', errors='ignore') for s in inner_strings)
                if line:
                    text_chunks.append(line)

    # 2. Fallback: extract plain ascii / utf-8 text blocks if compressed stream yielded little
    if not text_chunks or len(" ".join(text_chunks)) < 40:
        plain_ascii = re.findall(rb'\(([\w\s\.,;:!@#$%^&*()_\+\-=\/\\<>\"\'\[\]{}~`]+)\)', content)
        for chunk in plain_ascii:
            try:
                decoded = chunk.decode('utf-8', errors='ignore').strip()
                if len(decoded) > 2:
                    text_chunks.append(decoded)
            except Exception:
                pass

    return "\n".join(text_chunks)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pypdf if available, otherwise pure Python parser."""
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        extracted = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted.append(text)
        if extracted:
            return "\n".join(extracted)
    except Exception:
        pass
        
    with open(file_path, 'rb') as f:
        content = f.read()
    return extract_text_from_pdf_stream(content)

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using zipfile & XML."""
    try:
        with zipfile.ZipFile(file_path) as docx:
            tree = ET.fromstring(docx.read('word/document.xml'))
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for p in tree.iterfind('.//w:p', namespace):
                texts = [node.text for node in p.iterfind('.//w:t', namespace) if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n'.join(paragraphs)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {e}")

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT or Markdown file."""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode text file with standard encodings.")

def parse_resume(file_path: str) -> ParsedResume:
    """
    Ingest a resume file, extract text and candidate metadata safely.
    Never crashes the whole batch on a corrupted file.
    """
    if not os.path.exists(file_path):
        return ParsedResume(
            file_path=file_path,
            raw_text="",
            candidate_name="Unknown",
            is_malformed=True,
            error_message="File does not exist"
        )
        
    if os.path.getsize(file_path) == 0:
        return ParsedResume(
            file_path=file_path,
            raw_text="",
            candidate_name=os.path.basename(file_path),
            is_malformed=True,
            error_message="File is empty (0 bytes)"
        )

    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    
    try:
        if ext == '.pdf':
            raw_text = extract_text_from_pdf(file_path)
        elif ext in ('.docx', '.doc'):
            raw_text = extract_text_from_docx(file_path)
        elif ext in ('.txt', '.md', '.markdown'):
            raw_text = extract_text_from_txt(file_path)
        else:
            # Attempt plain text read as fallback
            raw_text = extract_text_from_txt(file_path)
    except Exception as e:
        return ParsedResume(
            file_path=file_path,
            raw_text="",
            candidate_name=os.path.basename(file_path),
            is_malformed=True,
            error_message=f"Corrupted or unreadable format: {str(e)}"
        )

    cleaned = clean_text(raw_text)
    if not cleaned or len(cleaned) < 30:
        return ParsedResume(
            file_path=file_path,
            raw_text=cleaned,
            candidate_name=os.path.basename(file_path),
            is_malformed=True,
            error_message="Insufficient text extracted (scanned image or empty)"
        )

    email = extract_email(cleaned)
    github_url, _ = extract_github_url(cleaned)
    name = extract_candidate_name(cleaned, file_path)
    sections = segment_sections(cleaned)
    
    return ParsedResume(
        file_path=file_path,
        raw_text=cleaned,
        candidate_name=name,
        email=email,
        github_url=github_url,
        projects_text=sections.get("projects", ""),
        experience_text=sections.get("experience", "")
    )
