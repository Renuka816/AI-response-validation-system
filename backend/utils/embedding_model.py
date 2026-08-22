import os
import requests
import time


# --------------------------------------------------
# Configuration
# --------------------------------------------------

USE_REMOTE_EMBEDDINGS = os.getenv(
    "USE_REMOTE_EMBEDDINGS",
    "false"
).lower() == "true"

HF_TOKEN = os.getenv("HF_TOKEN")

HF_MODEL_URL = (
    "https://router.huggingface.co/"
    "hf-inference/models/"
    "sentence-transformers/all-MiniLM-L6-v2"
    "/pipeline/feature-extraction"
)


# --------------------------------------------------
# Local Embedding Model
# --------------------------------------------------

_model = None


def _load_local_model():

    global _model

    if _model is None:

        from sentence_transformers import SentenceTransformer

        print("Loading LOCAL embedding model...")

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Local embedding model loaded.")

    return _model


# --------------------------------------------------
# Remote Embedding Model
# --------------------------------------------------

class RemoteEmbeddingModel:

    def encode(
        self,
        sentences,
        batch_size=32,
        show_progress_bar=False,
        convert_to_tensor=False
    ):

        is_single_string = isinstance(
            sentences,
            str
        )

        input_data = (
            [sentences]
            if is_single_string
            else list(sentences)
        )

        headers = {}

        if HF_TOKEN:
            headers["Authorization"] = (
                f"Bearer {HF_TOKEN}"
            )

        try:

            response = requests.post(
                HF_MODEL_URL,
                headers=headers,
                json={
                    "inputs": input_data
                },
                timeout=60
            )

            if response.status_code == 503:

                time.sleep(5)

                response = requests.post(
                    HF_MODEL_URL,
                    headers=headers,
                    json={
                        "inputs": input_data
                    },
                    timeout=60
                )

            if response.status_code != 200:

                raise RuntimeError(
                    f"Hugging Face embedding API failed: "
                    f"{response.status_code} "
                    f"{response.text}"
                )

            result = response.json()

            return (
                result[0]
                if is_single_string
                else result
            )

        except Exception as e:

            raise RuntimeError(
                f"Embedding generation failed: {e}"
            )


# --------------------------------------------------
# Shared Model
# --------------------------------------------------

_remote_model = RemoteEmbeddingModel()


def get_embedding_model():

    if USE_REMOTE_EMBEDDINGS:

        print(
            "Using REMOTE Hugging Face embedding model..."
        )

        return _remote_model

    return _load_local_model()