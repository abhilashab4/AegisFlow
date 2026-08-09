from huggingface_hub import InferenceClient

from app.core.config import settings


class EmbeddingService:

    def __init__(self):

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=settings.HF_TOKEN
        )

        self.model = "sentence-transformers/all-MiniLM-L6-v2"

    def encode(self, text: str):

        result = self.client.feature_extraction(
            text,
            model=self.model
        )

        return result.tolist()