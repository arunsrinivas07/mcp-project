from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

active_chunks = []
active_index = None


def set_active_index(chunks, index):
    global active_chunks, active_index
    active_chunks = chunks
    active_index = index


def create_index(text_chunks):
    embeddings = model.encode(text_chunks)
    embeddings = np.array(embeddings).astype('float32')

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    return index, embeddings

def get_active_chunks():
    return active_chunks
    
def search(query):
    global active_chunks, active_index

    if active_index is None:
        return ["No content currently indexed. Please upload a PDF first."]

    q_vec = np.array(model.encode([query])).astype('float32')

    _, I = active_index.search(q_vec, 3)

    return [active_chunks[i] for i in I[0]]