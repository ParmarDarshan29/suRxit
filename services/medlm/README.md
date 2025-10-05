# MedLM QA Service

## Overview
Retrieval-Augmented Generation (RAG) QA pipeline over KG triples and medical documents using FAISS and SentenceTransformers.

## Build Vector Store
- Add triples to `data/manual/example_kg_triples.txt`
- Add docs to `data/manual/example_med_docs.txt`
- Build FAISS index:
```bash
python build_faiss.py
```

## API
- FastAPI app exposes POST `/qa` with `{question, context}`
- Returns answer and evidence citations

### Run API
```bash
uvicorn app:app --reload --port 8100
```

### Example Request
```bash
curl -X POST "http://localhost:8100/qa" -H "Content-Type: application/json" -d '{"question": "What is the interaction between aspirin and warfarin?"}'
```
