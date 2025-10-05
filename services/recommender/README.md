# Drug Recommender Service

## Overview
Recommender system for safer drug alternatives using node2vec embeddings on the KG.

## Embedding Training
- Node2vec embeddings built at startup from Neo4j KG

## API
- FastAPI app exposes POST `/recommend/alternatives` with `{drug_id, avoid_ids}`
- Returns top-3 safer alternatives of the same therapeutic class

### Run API
```bash
uvicorn app:app --reload --port 8090
```

### Example Request
```bash
curl -X POST "http://localhost:8090/recommend/alternatives" -H "Content-Type: application/json" -d '{"drug_id": "D001", "avoid_ids": []}'
```
