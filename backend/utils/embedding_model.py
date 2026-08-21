import os
import requests
import time

# Fetch the free token you saved in Render's environment settings
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://huggingface.co"
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

class LightweightEmbeddingModel:
    def encode(self, sentences, batch_size=32, show_progress_bar=False, convert_to_tensor=False):
        """
        Mimics the original sentence-transformers .encode() behavior 
        but routes the data through Hugging Face's free external API.
        """
        # If a single string is passed, wrap it in a list
        is_single_string = isinstance(sentences, str)
        input_data = [sentences] if is_single_string else list(sentences)
        
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": input_data}, timeout=15)
            
            # If the model is cold-starting on Hugging Face, retry gracefully
            if response.status_code == 503:
                time.sleep(3)
                response = requests.post(API_URL, headers=headers, json={"inputs": input_data}, timeout=15)

            if response.status_code == 200:
                result = response.json()
                # Return plain list or single list element matching original layout expectations
                return result[0] if is_single_string else result
            else:
                raise RuntimeError(f"Hugging Face API failed: {response.text}")
                
        except Exception as e:
            # Fallback error mapping to keep application from crashing hard
            raise RuntimeError(f"Embedding Generation Error: {str(e)}")

# Initialize the lightweight class once to mimic your old setup
model = LightweightEmbeddingModel()

def get_embedding_model():
    return model
