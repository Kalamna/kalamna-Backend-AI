# kalamna 
Multi-Tenant Retrieval-Augmented Generation Platform

This repository contains the backend for a multi-tenant RAG (Retrieval-Augmented Generation) SaaS platform built with FastAPI, PostgreSQL, pgvector, and modern asynchronous Python tooling.

The system provides:

- Multi-organization isolation
- Document ingestion and processing
- Chunking and embeddings
- Semantic search
- Full RAG query pipeline
- JWT authentication
- Role-based access control
- Usage analytics and feedback

The architecture follows a Django-style “apps” pattern while taking full advantage of FastAPI’s async and modular capabilities.

---


## Project Overview

The backend enables organizations to upload internal documents, process them into embeddings, and perform semantic search and RAG-based question answering. Each organization has isolated data, employees, documents, and analytics.

The solution is designed for large-scale usage and can support hundreds of thousands of embeddings, asynchronous document processing, and multiple external LLM providers.

---

## Tech Stack

### Backend
- FastAPI  
- Python 3.12+  
- SQLAlchemy 2.0  
- Pydantic v2  
- Alembic  

### Database
- PostgreSQL  
- pgvector extension for embeddings  

### RAG
- Embedding models (OpenAI, etc.)  
- Chunking pipeline  
- Vector similarity search  
- LLM inference  

### Storage
- S3 / MinIO  

### Queueing (Optional)
- Redis for async task queues  

### Infrastructure
- Docker  
- Docker Compose  

---

## Folder Structure

```

rag_saas/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── migrations/
│   │
│   ├── apps/
│   │   ├── auth/
│   │   ├── organizations/
│   │   ├── employees/
│   │   ├── documents/
│   │   ├── rag/
│   │   ├── analytics/
│   │   └── feedback/
│   │
│   ├── storage/
│   │   ├── s3_client.py
│   │   └── paths.py
│   │
│   ├── rag_infra/
│   │   ├── embeddings.py
│   │   ├── chunking.py
│   │   ├── vector_db.py
│   │   ├── llm_client.py
│   │   └── reranking.py
│   │
│   ├── workers/
│   │   ├── runner.py
│   │   └── queues.py
│   │
│   ├── utils/
│   │   ├── logging.py
│   │   └── common.py
│   │
│   └── **init**.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_documents.py
│   ├── test_rag.py
│   └── ...
│
├── .pre-commit-config.yaml
├── .ruff.toml
├── mypy.ini
├── pytest.ini
│
├── docker-compose.yml
├── Dockerfile
│
├── requirements.txt
└── alembic.ini

```

---

## Architecture Overview

### Django-Style Apps  
Each domain (auth, organizations, employees, documents, rag, analytics, feedback) exists as an isolated app containing:

- models
- schemas
- services
- routers

This keeps concerns clean and modular.

### Layering
- Routers: HTTP endpoint definitions  
- Services: business logic  
- Models: database entities  
- Schemas: request/response validation  
- Infrastructure: chunking, embeddings, vector storage, LLM clients  

### Asynchronous Design
FastAPI enables concurrency for:

- embeddings computation  
- LLM calls  
- file I/O  
- vector search  

---

## Running the Project

### Start the API

```
uvicorn app.main:app --reload
```

### Start background worker (async queue)

```
python app/workers/runner.py
```

---

## Document Processing Workflow

1. User uploads a document
2. File is stored in S3-compatible storage
3. Metadata saved in PostgreSQL
4. Worker processes document:

   * downloads file
   * extracts text
   * chunks text
   * computes embeddings
   * stores vectors in pgvector
5. Document becomes searchable

---

## RAG Pipeline

1. Embed user query
2. Retrieve relevant chunks using pgvector similarity
3. Construct RAG prompt
4. Call LLM to generate final answer
5. Return answer with sources and metadata

---

## Multi-Tenancy Model

Each database table references an `org_id` UUID.
Isolation rules:

* Superadmin: full access
* Organization admin: all data in their org
* Employee: limited access within org

---

## Testing

```
pytest -q
```

Includes:

* API tests
* Service layer tests
* Database tests
* RAG pipeline tests

---



