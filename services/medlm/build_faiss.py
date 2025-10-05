"""
Build FAISS index for MedLM QA from KG triples and medical docs using SentenceTransformers.
"""
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

VECTOR_DIM = 384
FAISS_INDEX_PATH = "models/medlm/faiss.index"
DOCS_PATH = "models/medlm/docs.npy"
METADATA_PATH = "models/medlm/meta.npy"
KG_TRIPLES_PATH = "data/manual/example_kg_triples.txt"  # One triple per line
DOCS_TEXT_PATH = "data/manual/example_med_docs.txt"      # One doc per line

os.makedirs("models/medlm", exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load triples and docs
triples = []
if os.path.exists(KG_TRIPLES_PATH):
    with open(KG_TRIPLES_PATH) as f:
        triples = [line.strip() for line in f if line.strip()]

docs = []
if os.path.exists(DOCS_TEXT_PATH):
    with open(DOCS_TEXT_PATH) as f:
        docs = [line.strip() for line in f if line.strip()]

corpus = triples + docs
if not corpus:
    corpus = ["No evidence available"]

embeddings = model.encode(corpus, show_progress_bar=True, normalize_embeddings=True)
embeddings = np.array(embeddings, dtype=np.float32)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, FAISS_INDEX_PATH)
np.save(DOCS_PATH, embeddings)
np.save(METADATA_PATH, np.array(corpus))
print(f"Indexed {len(corpus)} items to FAISS.")
