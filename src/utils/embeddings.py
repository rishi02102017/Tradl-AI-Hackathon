"""Embedding service for semantic similarity."""
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple

# Initialize the embedding model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Fast and efficient
_embedding_model = None


def get_embedding_model():
    """Get or initialize the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def get_embeddings(texts: List[str]) -> np.ndarray:
    """Get embeddings for a list of texts."""
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True)


def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts."""
    model = get_embedding_model()
    embeddings = model.encode([text1, text2], convert_to_numpy=True)
    
    # Cosine similarity
    dot_product = np.dot(embeddings[0], embeddings[1])
    norm1 = np.linalg.norm(embeddings[0])
    norm2 = np.linalg.norm(embeddings[1])
    
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)


def find_similar_articles(
    query_text: str,
    article_texts: List[str],
    threshold: float = 0.85
) -> List[Tuple[int, float]]:
    """Find articles similar to query text."""
    model = get_embedding_model()
    query_embedding = model.encode([query_text], convert_to_numpy=True)[0]
    article_embeddings = model.encode(article_texts, convert_to_numpy=True)
    
    # Compute similarities
    similarities = []
    for idx, article_emb in enumerate(article_embeddings):
        dot_product = np.dot(query_embedding, article_emb)
        norm1 = np.linalg.norm(query_embedding)
        norm2 = np.linalg.norm(article_emb)
        similarity = dot_product / (norm1 * norm2)
        
        if similarity >= threshold:
            similarities.append((idx, float(similarity)))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities

