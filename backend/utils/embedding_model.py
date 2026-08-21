import os
import requests
import time

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://huggingface.co"
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

class LightweightEmbeddingModel:
    def encode(self, sentences, batch_size=32, show_progress_bar=False, convert_to_tensor=False):
        is_single_string = isinstance(sentences, str)
        input_data = [sentences] if is_single_string else list(sentences)
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": input_data}, timeout=15)
            if response.status_code == 503:
                time.sleep(3)
                response = requests.post(API_URL, headers=headers, json={"inputs": input_data}, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result if is_single_string else result
            else:
                raise RuntimeError(f"Hugging Face API failed: {response.text}")
        except Exception as e:
            raise RuntimeError(f"Embedding Generation Error: {str(e)}")

model = LightweightEmbeddingModel()

def get_embedding_model():
    return model

class EmbeddingService:
    def __init__(self):
        self.model = model
        
    def get_embeddings(self, text):
        return self.model.encode(text)

    # Added to fix the specific error in hallucination_agent.py
    @classmethod
    def get_model(cls):
        return model
