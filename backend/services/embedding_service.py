from sentence_transformers import SentenceTransformer


# ============================
# Local Embedding Model
# ============================

MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading local embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Local embedding model loaded.")


# ============================
# Embedding Model
# ============================

class LocalEmbeddingModel:

    def encode(
        self,
        sentences,
        batch_size=32,
        show_progress_bar=False,
        convert_to_tensor=False
    ):

        return model.encode(
            sentences,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_tensor=convert_to_tensor
        )


# ============================
# Global Model
# ============================

local_model = LocalEmbeddingModel()


# ============================
# Get Embedding Model
# ============================

def get_embedding_model():

    return local_model


# ============================
# Embedding Service
# ============================

class EmbeddingService:

    def __init__(self):

        self.model = local_model

    @staticmethod
    def get_model():

        return local_model

    def get_embeddings(self, text):

        return self.model.encode(text)