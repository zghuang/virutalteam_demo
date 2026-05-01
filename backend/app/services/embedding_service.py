from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for a single text string."""
    return _model.encode(text).tolist()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for a list of text strings."""
    return _model.encode(texts).tolist()
