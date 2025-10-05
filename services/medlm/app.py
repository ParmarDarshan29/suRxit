"""
FastAPI app for MedLM QA (RAG pipeline).
- Uses FAISS vector store of KG triples + docs
- POST /qa {question, context} returns answer with evidence
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import faiss
import numpy as np
from typing import List

app = FastAPI()

VECTOR_DIM = 384  # Example dimension for embeddings
FAISS_INDEX_PATH = "models/medlm/faiss.index"
DOCS_PATH = "models/medlm/docs.npy"
METADATA_PATH = "models/medlm/meta.npy"

class QARequest(BaseModel):
	question: str
	context: str = ""

from sentence_transformers import SentenceTransformer
_st_model = None
def embed_text(text: str) -> np.ndarray:
	global _st_model
	if _st_model is None:
		_st_model = SentenceTransformer("all-MiniLM-L6-v2")
	emb = _st_model.encode([text], normalize_embeddings=True)
	return np.array(emb[0], dtype=np.float32)

def load_faiss_index():
	if not os.path.exists(FAISS_INDEX_PATH):
		# Build dummy index for demo
		index = faiss.IndexFlatL2(VECTOR_DIM)
		docs = np.zeros((1, VECTOR_DIM), dtype=np.float32)
		meta = np.array(["No evidence available"])
		index.add(docs)
		np.save(DOCS_PATH, docs)
		np.save(METADATA_PATH, meta)
		faiss.write_index(index, FAISS_INDEX_PATH)
	index = faiss.read_index(FAISS_INDEX_PATH)
	docs = np.load(DOCS_PATH)
	meta = np.load(METADATA_PATH, allow_pickle=True)
	return index, docs, meta

def retrieve_evidence(question: str, top_k=3):
	index, docs, meta = load_faiss_index()
	q_emb = embed_text(question)
	D, I = index.search(np.expand_dims(q_emb, 0), top_k)
	evidences = [meta[i] for i in I[0] if i < len(meta)]
	return evidences

def generate_answer(question: str, evidences: List[str]) -> str:
	# Prompt template: always cite evidence or answer “I don’t know”
	if evidences and any(e for e in evidences if e != "No evidence available"):
		return f"Answer: Based on the following evidence: {evidences[0]}"
	else:
		return "I don't know."

@app.post("/qa")
def qa_endpoint(req: QARequest):
	evidences = retrieve_evidence(req.question)
	answer = generate_answer(req.question, evidences)
	return {"answer": answer, "evidence": evidences}
