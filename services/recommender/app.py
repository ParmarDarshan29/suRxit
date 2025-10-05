"""
FastAPI app for drug recommendation.
- Builds TransE/node2vec embeddings on KG
- POST /recommend/alternatives returns ranked safer drugs
"""

import os
import networkx as nx
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from gensim.models import Word2Vec

app = FastAPI()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "surxitpass123")
EMBED_PATH = "models/recommender/node2vec.kv"

class RecommendRequest(BaseModel):
	drug_id: str
	avoid_ids: list[str] = []

def export_kg_to_nx():
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	G = nx.Graph()
	with driver.session() as session:
		nodes = session.run("MATCH (d:Drug) RETURN d.id AS id, d.ATC AS atc").data()
		for n in nodes:
			G.add_node(n['id'], atc=n.get('atc'))
		rels = session.run("MATCH (a:Drug)-[r:HAS_DDI]->(b:Drug) RETURN a.id AS src, b.id AS dst").data()
		for r in rels:
			G.add_edge(r['src'], r['dst'])
	driver.close()
	return G

def random_walk(G, start, length=10):
	walk = [start]
	for _ in range(length - 1):
		cur = walk[-1]
		neighbors = list(G.neighbors(cur))
		if not neighbors:
			break
		walk.append(np.random.choice(neighbors))
	return walk

def train_node2vec(G, save_path=EMBED_PATH):
	walks = []
	for n in G.nodes():
		for _ in range(10):
			walk = random_walk(G, n, length=10)
			walks.append([str(x) for x in walk])
	model = Word2Vec(walks, vector_size=32, window=5, min_count=1, sg=1, workers=1, epochs=10)
	model.wv.save(save_path)
	return model

def load_embeddings():
	from gensim.models import KeyedVectors
	return KeyedVectors.load(EMBED_PATH, mmap='r')

def get_therapeutic_class(drug_id):
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	with driver.session() as session:
		res = session.run("MATCH (d:Drug {id: $id}) RETURN d.ATC AS atc", id=drug_id).single()
	driver.close()
	return res['atc'] if res else None

def get_drugs_by_atc(atc):
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	with driver.session() as session:
		res = session.run("MATCH (d:Drug {ATC: $atc}) RETURN d.id AS id", atc=atc).data()
	driver.close()
	return [r['id'] for r in res]

def get_allergy_drugs(patient_id):
	driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
	with driver.session() as session:
		res = session.run("MATCH (p:Patient {id: $pid})-[:HAS_ALLERGY]->(a:Allergy)<-[:HAS_ALLERGY]-(d:Drug) RETURN d.id AS id", pid=patient_id).data()
	driver.close()
	return [r['id'] for r in res]

@app.on_event("startup")
def startup_event():
	if not os.path.exists(EMBED_PATH):
		G = export_kg_to_nx()
		train_node2vec(G)

@app.post("/recommend/alternatives")
def recommend_alternatives(req: RecommendRequest):
	kv = load_embeddings()
	atc = get_therapeutic_class(req.drug_id)
	if not atc:
		raise HTTPException(status_code=404, detail="Drug not found or missing ATC")
	candidates = get_drugs_by_atc(atc)
	# Remove the input drug and any to avoid
	candidates = [d for d in candidates if d != req.drug_id and d not in req.avoid_ids]
	# Score by cosine similarity
	scores = []
	for c in candidates:
		if c in kv:
			sim = kv.similarity(req.drug_id, c)
			scores.append((c, sim))
	scores.sort(key=lambda x: -x[1])
	top3 = [c for c, _ in scores[:3]]
	return {"alternatives": top3}
