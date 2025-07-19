# Eltrion AI Backend System

This is a backend system for Eltrion — a local AI assistant designed to support structured document ingestion, retrieval-augmented generation (RAG), conversation memory, nightly training, and automated DOCX report generation.

---

## 🚀 Quick Start

### 1. Install Requirements

```bash
make setup
make run
Visit: http://localhost:8000/docs


Architecture Overview

FastAPI – REST API server
LangChain + SentenceTransformers – Local embeddings
ChromaDB – Vector store
PostgreSQL – File metadata, API keys
Redis – Memory + rate limiting
python-docx – Structured report generation
APScheduler – Nightly jobs (ingestion, evaluation)

📥 Data Ingestion

Place .json or .txt files under training_data/.

Then run:

python scripts/nightly_refresh.py
This will:

Detect new or updated files
Chunk content
Generate embeddings
Store metadata in PostgreSQL
Store vectors in ChromaDB


💬 Chat + Memory
Short-term: last N turns in Redis
Long-term: summarized memory (every M turns, WIP)

Evaluation

Evaluate benchmark Q&A pairs nightly or on demand:

python evaluate.py
Generates: evaluation_report.md

DOCX Report API

Generate a Report
POST /api/report/generate
{
  "title": "Eltrion System Overview",
  "sections": ["Tech Stack", "How it learns"],
  "prompt_context": "Internal AI assistant overview",
  "tenant": "public"
}
Download it
GET /api/report/{report_id}/download

API Security

Authentication via X-API-Key header. Keys are stored in PostgreSQL.

Admin creates API keys via:
POST /api/admin/keys
Header: X-API-Key: {admin-key}
{
  "owner_email": "someone@example.com",
  "role": "user"
}
Use the script below to generate your first admin key.

Create Admin API Key
python scripts/create_admin_key.py
You will be prompted to enter an email. The script will insert a new admin key into your DB.

Observability

GET /metrics
Returns uptime, request count, average latency, and more.

Extension Guide

Routers → app/routers/
Services → app/services/
Vector Search → app/retrieval/
Benchmarks → benchmark/
Scheduler → scheduler_service.py
