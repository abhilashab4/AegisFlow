"""
Module: Embedding Service (Hugging Face)

Purpose:
Provides a reusable service for converting text into numerical vector
representations (embeddings) using a Hugging Face-hosted Sentence Transformer
model. These embeddings can be used for semantic similarity, vector search,
and storing/searching policies with PostgreSQL + pgvector.

Technical Workflow:
1. Initializes the Hugging Face InferenceClient using the API token stored in
   the application settings.
2. Uses the "sentence-transformers/all-MiniLM-L6-v2" model to generate
   embeddings.
3. Sends the input text to the Hugging Face Inference API through
   feature_extraction().
4. The model converts the text into a numerical vector that captures its
   semantic meaning.
5. Converts the returned result into a Python list using tolist().
6. Returns the embedding vector for storage or similarity search.

Example Usage:
embedding_service = EmbeddingService()

embedding = embedding_service.encode(
    "Employees must not share confidential company data."
)

Example Output:
[
    0.0234,
    -0.1187,
    0.0521,
    ...
]

The output is a fixed-size numerical vector representing the semantic meaning
of the input sentence.

Example in Policy Search:
Policy Text
    │
    ▼
EmbeddingService
    │
    ▼
MiniLM Sentence Transformer
    │
    ▼
Embedding Vector
    │
    ▼
PostgreSQL + pgvector
    │
    ▼
Semantic Similarity Search

Why Embeddings?
Traditional keyword search looks for exact words, whereas embeddings represent
the meaning of text. This allows semantically similar sentences to be matched
even when they use different words.

Example:
Query:
"Can I send customer information to my personal email?"

Stored Policy:
"Customer data must not be transferred outside approved company systems."

Although the wording is different, their semantic meaning is related. Their
embedding vectors can therefore be compared using vector similarity.

Why all-MiniLM-L6-v2?
all-MiniLM-L6-v2 is a lightweight Sentence Transformer model that provides
useful semantic embeddings while being relatively efficient, making it
suitable for semantic search applications.

Benefits:
- Converts unstructured text into searchable numerical vectors.
- Enables semantic rather than exact keyword-based search.
- Provides a reusable abstraction around the Hugging Face inference API.
- Keeps API credentials in application configuration instead of hardcoding them.
- Can be integrated with PostgreSQL + pgvector for efficient policy retrieval.
"""

from huggingface_hub import InferenceClient
from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.client = InferenceClient(
            provider="hf-inference", api_key=settings.HF_TOKEN
        )

        self.model = "sentence-transformers/all-MiniLM-L6-v2"

    def encode(self, text: str):
        result = self.client.feature_extraction(text, model=self.model)

        return result.tolist()