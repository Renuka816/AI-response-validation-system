from sentence_transformers import SentenceTransformer

# Load once
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding_model():
    return model