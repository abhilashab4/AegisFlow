from sentence_transformers import SentenceTransformer


class EmbeddingService:

    _model = None

    def __init__(self):

        if EmbeddingService._model is None:

            EmbeddingService._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        self.model = EmbeddingService._model

    def encode(self, text: str):

        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()