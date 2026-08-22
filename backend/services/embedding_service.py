from backend.utils.embedding_model import get_embedding_model


def get_embedding_model_service():
    return get_embedding_model()


class EmbeddingService:

    @classmethod
    def get_model(cls):
        return get_embedding_model()

    def __init__(self):
        self.model = get_embedding_model()

    def get_embeddings(self, text):
        return self.model.encode(text)