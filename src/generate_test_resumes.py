"""
Synthetic Resume Generator to create diverse benchmark candidate profiles.
"""
import os

RESUMES = {
    "candidate_01_asha_rao.txt": """Asha Rao
asha.rao@example.com | https://github.com/asharao | San Francisco, CA

SUMMARY
Passionate Software Engineer specializing in Python backend architecture and stateful AI agentic workflows.

SKILLS
- Languages: Python, SQL, TypeScript
- Frameworks: FastAPI, LangGraph, LangChain, PyTorch, SQLAlchemy
- Databases & Infra: PostgreSQL, Redis, Docker, GCP, Kubernetes
- AI & Search: RAG pipelines, Vector Databases (ChromaDB, Pinecone), Tool-calling, DeepEval

PROJECTS
Autonomous Research Agent System
- Architected a multi-agent orchestration engine using LangGraph and tool-calling with dynamic task decomposition.
- Implemented hybrid RAG with semantic search, re-ranking, and vector embeddings in ChromaDB.
- Integrated automated LLM evaluation pipeline with DeepEval and benchmark test suites.

High-Throughput Analytics Backend
- Developed asynchronous REST APIs with FastAPI, PostgreSQL, and Redis caching handling 5k req/sec.
- Containerized microservices with Docker and deployed to GCP Cloud Run with CI/CD via GitHub Actions.
- Wrote full unit test coverage using pytest with 94% code coverage.
""",

    "candidate_02_rahul_verma.txt": """Rahul Verma
rahul.verma@example.com | https://github.com/rahulverma | New York, NY

SUMMARY
Full Stack Engineer with extensive experience in enterprise Java and modern React ecosystems.

SKILLS
- Languages: Java, JavaScript, TypeScript, HTML/CSS
- Frameworks: Spring Boot, React, Next.js, Express.js
- Databases & Cloud: MySQL, MongoDB, AWS, Docker

PROJECTS
Enterprise E-Commerce Platform
- Built scalable microservices using Java Spring Boot and Hibernate ORM.
- Developed responsive customer portal in React and Next.js with Redux state management.
- Deployed infrastructure on AWS ECS with Docker containers.

Payment Gateway Integration Service
- Designed resilient REST API for transaction settlement using Spring Cloud and MySQL.
""",

    "candidate_03_vikram_patel.txt": """Vikram Patel
vikram.patel@example.com | https://github.com/vikrampatel | Seattle, WA

SUMMARY
Python Backend Engineer focused on distributed systems and database optimization.

SKILLS
- Languages: Python, C++, SQL
- Backend: Django, Flask, FastAPI, Celery, SQLAlchemy
- Data Stores: PostgreSQL, Redis, RabbitMQ
- Tools: Docker, Linux, Git, PyTest

PROJECTS
Distributed Task Queue & Scheduler
- Built distributed asynchronous worker system using Python, Celery, and Redis message broker.
- Optimized PostgreSQL relational queries, achieving 40% reduction in query execution latency.
- Implemented comprehensive integration test suites using pytest and Docker Compose.

Real-Time Event Processing Engine
- Created high-concurrency event ingestion service in Python with WebSocket support.
""",

    "candidate_04_sam_alt_wrapper.txt": """Sam Altman Jr
sam.wrapper@example.com | https://github.com/samwrapper | Austin, TX

SUMMARY
Developer building quick AI demos and web prototypes.

SKILLS
- Languages: Python, HTML, CSS
- Libraries: Streamlit, Requests, OpenAI API

PROJECTS
AI Summary Tool
- Simple chatbot and summarizer: created a simple wrapper around OpenAI API call using Streamlit.
- Users input text and it forwards the prompt to GPT-4 API endpoint and displays response.
""",

    "candidate_05_kavya_nair.txt": """Kavya Nair
kavya.nair@example.com | https://github.com/kavyanair | Boston, MA

SUMMARY
AI Engineer with strong background in retrieval systems, autonomous agents, and production Python.

SKILLS
- Languages: Python, Go
- AI/Agentic: LangChain, LlamaIndex, Multi-Agent, Vector Search, FAISS, Function-calling
- Backend: FastAPI, Asyncio, PostgreSQL, Redis, Docker, AWS

PROJECTS
Enterprise Document QA System (RAG)
- Designed an end-to-end RAG system using LlamaIndex, FAISS vector index, and hybrid retrieval.
- Implemented tool-calling agents with fallback logic, retry mechanisms, and rate limiting.
- Built async FastAPI backend with Redis caching and PostgreSQL persistence.

Autonomous Data Extraction Agent
- Created multi-agent workflow for structured web scraping with LLM validation.
- Dockerized the pipeline and configured automated CI/CD deployment on AWS.
""",

    "candidate_06_tutorial_clone.txt": """Alex Chen
alex.chen@example.com | https://github.com/alexchen | Chicago, IL

SKILLS
- Languages: Python
- Frameworks: LangChain, Flask

PROJECTS
LangChain Assistant
- Tutorial Project: Followed tutorial to build basic todo app with LangChain wrapper.
- Copied boilerplate code from YouTube walkthrough to test LLM prompts.
""",

    "candidate_07_corrupted_empty.txt": ""
}

def create_synthetic_resumes(output_dir="./resumes"):
    os.makedirs(output_dir, exist_ok=True)
    for filename, content in RESUMES.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    print(f"Created {len(RESUMES)} synthetic test resumes in {output_dir}")

if __name__ == "__main__":
    create_synthetic_resumes()
