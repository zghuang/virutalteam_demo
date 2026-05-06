"""Embedding service using sentence-transformers (lazy-loaded for Docker)."""

_model = None


def _load_model():
    global _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        _model = None


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for a single text string."""
    if _model is None:
        _load_model()
    if _model is None:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "Install with: pip install sentence-transformers"
        )
    return _model.encode(text).tolist()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for a list of text strings."""
    if _model is None:
        _load_model()
    if _model is None:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "Install with: pip install sentence-transformers"
        )
    return _model.encode(texts).tolist()
