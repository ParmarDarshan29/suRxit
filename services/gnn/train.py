"""
Train a GNN (GraphSAGE/RGCN) for DDI link prediction.
- Exports KG from Neo4j
- Converts to PyTorch-Geometric Data
- Trains for INTERACTS_WITH edge prediction
- Saves model to models/gnn/
"""

import os
import torch
from neo4j import GraphDatabase
from torch_geometric.data import Data
from torch_geometric.nn import GraphSAGE
import numpy as np

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "surxitpass123")

# 1. Export KG from Neo4j
def export_ddi_kg():
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	with driver.session() as session:
		# Get all drugs
		nodes = session.run("MATCH (d:Drug) RETURN d.id AS id").data()
		node_ids = [n['id'] for n in nodes]
		node_id_map = {id_: i for i, id_ in enumerate(node_ids)}
		# Get DDI edges
		rels = session.run("MATCH (a:Drug)-[r:HAS_DDI]->(b:Drug) RETURN a.id AS src, b.id AS dst, r.confidence AS conf").data()
		edges = [(node_id_map[r['src']], node_id_map[r['dst']]) for r in rels]
	edge_conf = [float(r['conf']) if r['conf'] is not None else 0.5 for r in rels]
	driver.close()
	return node_ids, edges, edge_conf

# 2. Convert to PyG Data
def build_pyg_data(node_ids, edges, edge_conf):
	x = torch.eye(len(node_ids))  # One-hot for demo; replace with real features
	edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
	edge_attr = torch.tensor(edge_conf, dtype=torch.float).unsqueeze(1)
	data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
	return data

# 3. Train GraphSAGE for link prediction
def train_gnn(data, save_path):
	model = GraphSAGE(
		in_channels=data.num_node_features,
		hidden_channels=32,
		num_layers=2
	)
	optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
	criterion = torch.nn.BCEWithLogitsLoss()
	# Create positive and negative edge samples
	pos_edge_index = data.edge_index
	neg_edge_index = torch.randint(0, data.num_nodes, pos_edge_index.size(), dtype=torch.long)
	# Training loop (simplified)
	for epoch in range(20):
		model.train()
		optimizer.zero_grad()
		out = model(data.x, data.edge_index)
		pos_score = (out[pos_edge_index[0]] * out[pos_edge_index[1]]).sum(dim=1)
		neg_score = (out[neg_edge_index[0]] * out[neg_edge_index[1]]).sum(dim=1)
		pos_label = torch.ones(pos_score.size(0))
		neg_label = torch.zeros(neg_score.size(0))
		loss = criterion(pos_score, pos_label) + criterion(neg_score, neg_label)
		loss.backward()
		optimizer.step()
		if epoch % 5 == 0:
			print(f"Epoch {epoch} Loss: {loss.item():.4f}")
	torch.save(model.state_dict(), save_path)
	print(f"Model saved to {save_path}")

if __name__ == "__main__":
	node_ids, edges, edge_conf = export_ddi_kg()
	data = build_pyg_data(node_ids, edges, edge_conf)
	os.makedirs("models/gnn", exist_ok=True)
	train_gnn(data, "models/gnn/graphsage_ddi.pt")
