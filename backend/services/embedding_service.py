import os
import time
import requests


# ============================
# Hugging Face Configuration
# ============================

HF_TOKEN = os.getenv("HF_TOKEN")

# Hugging Face Inference API endpoint
API_URL = (
    "https://api-inference.huggingface.co/"
    "models/sentence-transformers/all-MiniLM-L6-v2"
)

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
} if HF_TOKEN else {}


# ============================
# Lightweight Embedding Model
# ============================

class LightweightEmbeddingModel:

    def encode(
        self,
        sentences,
        batch_size=32,
        show_progress_bar=False,
        convert_to_tensor=False
    ):

        # Check whether input is a single string
        is_single_string = isinstance(sentences, str)

        # Convert single text into list
        input_data = [sentences] if is_single_string else list(sentences)

        try:

            # Call Hugging Face API
            response = requests.post(
                API_URL,
                headers=headers,
                json={
                    "inputs": input_data
                },
                timeout=30
            )

            # Model might be loading
            if response.status_code == 503:

                time.sleep(5)

                response = requests.post(
                    API_URL,
                    headers=headers,
                    json={
                        "inputs": input_data
                    },
                    timeout=30
                )

            # Successful response
            if response.status_code == 200:

                result = response.json()

                return result

            # API error
            raise RuntimeError(
                f"Hugging Face API failed: "
                f"{response.status_code} - {response.text}"
            )

        except requests.exceptions.RequestException as e:

            raise RuntimeError(
                f"Embedding Generation Error: {str(e)}"
            )


# ============================
# Create Global Model Instance
# ============================

model = LightweightEmbeddingModel()


# ============================
# Get Embedding Model
# ============================

def get_embedding_model():

    return model


# ============================
# Embedding Service
# ============================

class EmbeddingService:

    def __init__(self):

        self.model = model


    @staticmethod
    def get_model():

        return model


    def get_embeddings(self, text):

        return self.model.encode(text)