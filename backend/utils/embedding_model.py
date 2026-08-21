from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Load LOCAL embedding model
# --------------------------------------------------

print("Loading LOCAL embedding model...")

_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Local embedding model loaded.")


# --------------------------------------------------
# Lightweight wrapper
# --------------------------------------------------

class LocalEmbeddingModel:

    def encode(
        self,
        sentences,
        batch_size=32,
        show_progress_bar=False,
        convert_to_tensor=False
    ):

        return _model.encode(
            sentences,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_tensor=convert_to_tensor
        )


# --------------------------------------------------
# Shared model
# --------------------------------------------------

model = LocalEmbeddingModel()


def get_embedding_model():
    return model


# --------------------------------------------------
# Embedding Service
# --------------------------------------------------

class EmbeddingService:

    def __init__(self):
        self.model = model

    def get_embeddings(self, text):
        return self.model.encode(text)

    @classmethod
    def get_model(cls):
        return model