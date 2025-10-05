# GNN Service

## Overview
Graph Neural Network (GNN) for DDI link prediction using Neo4j KG and PyTorch-Geometric.

## Training
- Exports KG from Neo4j
- Converts to PyTorch-Geometric Data
- Trains GraphSAGE for INTERACTS_WITH edge prediction
- Saves model to `models/gnn/`

### Train
```bash
python train.py
```

## Inference API
- FastAPI app exposes POST `/predict` with `{drug1, drug2}`
- Returns probability and supporting KG paths

### Run API
```bash
uvicorn app:app --reload --port 8080
```

### Example Request
```bash
curl -X POST "http://localhost:8080/predict" -H "Content-Type: application/json" -d '{"drug1": "D001", "drug2": "D002"}'
```
