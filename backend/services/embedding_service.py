from sentence_transformers import SentenceTransformer


class EmbeddingService:

    _model = None

    @classmethod
    def get_model(cls):

        if cls._model is None:

            print("Loading shared embedding model...")

            cls._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

            print("Shared embedding model loaded.")

        return cls._model