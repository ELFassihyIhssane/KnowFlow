# KnowFlow

KnowFlow is an adaptive, knowledge-driven **multi-agent** orchestrator for scientific Q&A.  
It focuses on **traceability**, **quality evaluation**, and **human control** (human-in-the-loop), instead of “black-box” answers.

## What it does
- Detects the user **intent** (summary, comparison, gap, deep analysis, concepts)
- Retrieves relevant scientific passages (Multi-Vector RAG)
- Generates a structured answer **with sources**
- Builds a **knowledge graph** (Graph RAG)
- Evaluates answer quality (faithfulness, coverage, coherence, depth) based on the retrieved ground-truth passages.
- Suggests tuning actions and lets the user **manually retry** with new parameters

## Main components
- **Intent Agent**: intent + sub-tasks
- **Retriever Agent**: semantic retrieval from Qdrant
- **Summarizer Agent**: grounded answers + citations
- **Concept Graph Agent**: concepts/relations extraction (Graph RAG)
- **Insight Agent**: critical analysis (gaps, limitations, contradictions, future work)
- **Evaluator Agent**: quality metrics + recommendations

## Tech stack
Python, FastAPI, Pydantic, LangGraph, PostgreSQL, SQLAlchemy,  
Sentence-Transformers (all-MiniLM-L6-v2), Qdrant, NetworkX, Docker,  
Next.js, React, Tailwind, Prometheus, structlog, Langfuse, MLflow.

