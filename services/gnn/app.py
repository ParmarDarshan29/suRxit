"""
FastAPI app for DDI link prediction inference.
POST /predict {drug1, drug2} → returns probability + supporting paths
"""

import os
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from torch_geometric.data import Data
from torch_geometric.nn import GraphSAGE

app = FastAPI()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "surxitpass123")
MODEL_PATH = "models/gnn/graphsage_ddi.pt"

class PredictRequest(BaseModel):
	drug1: str
	drug2: str

def get_node_ids():
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	with driver.session() as session:
		nodes = session.run("MATCH (d:Drug) RETURN d.id AS id").data()
		node_ids = [n['id'] for n in nodes]
		node_id_map = {id_: i for i, id_ in enumerate(node_ids)}
	driver.close()
	return node_ids, node_id_map

def build_pyg_data(node_ids):
	x = torch.eye(len(node_ids))
	data = Data(x=x)
	return data

def load_model(num_nodes):
	model = GraphSAGE(
		in_channels=num_nodes,
		hidden_channels=32,
		num_layers=2
	)
	model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
	model.eval()
	return model

def find_supporting_paths(drug1, drug2, max_paths=3):
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	with driver.session() as session:
		cypher = (
			"MATCH p=shortestPath((a:Drug {id: $d1})-[*..3]-(b:Drug {id: $d2})) "
			"RETURN [n IN nodes(p) | n.id] AS path LIMIT $max_paths"
		)
		results = session.run(cypher, d1=drug1, d2=drug2, max_paths=max_paths).data()
		paths = [r['path'] for r in results]
	driver.close()
	return paths

@app.post("/predict")
def predict_ddi(req: PredictRequest):
	node_ids, node_id_map = get_node_ids()
	if req.drug1 not in node_id_map or req.drug2 not in node_id_map:
		raise HTTPException(status_code=404, detail="Drug not found in KG")
	data = build_pyg_data(node_ids)
	model = load_model(len(node_ids))
	with torch.no_grad():
		out = model(data.x, torch.empty((2,0), dtype=torch.long))
		emb1 = out[node_id_map[req.drug1]]
		emb2 = out[node_id_map[req.drug2]]
		score = torch.sigmoid((emb1 * emb2).sum()).item()
	paths = find_supporting_paths(req.drug1, req.drug2)
	return {"probability": score, "supporting_paths": paths}
