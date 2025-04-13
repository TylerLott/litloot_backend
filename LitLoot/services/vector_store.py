import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from config import VECTOR_INDEX_PATH, METADATA_PATH

model = SentenceTransformer("all-MiniLM-L6-v2")

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

index = faiss.read_index(VECTOR_INDEX_PATH)

def search(query, k=5):
    embedding = model.encode([query])
    distances, indices = index.search(np.array(embedding), k)
    return [(metadata[i], i) for i in indices[0]]
