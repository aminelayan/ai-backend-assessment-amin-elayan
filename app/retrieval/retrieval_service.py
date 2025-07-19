from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

import os
from typing import List, Dict, Optional
from datetime import datetime

# Initialize Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection(name="eltrion_embeddings")

# For TF-IDF keyword fallback
_text_index: List[str] = []
_text_metadata: List[Dict] = []
_vectorizer = TfidfVectorizer()

def load_all_documents():
    global _text_index, _text_metadata, _vectorizer

    query_result = collection.get(include=["documents", "metadatas"])
    _text_index = query_result["documents"]
    _text_metadata = query_result["metadatas"]

    if _text_index:
        _vectorizer.fit(_text_index)


def semantic_search(query: str, k: int = 5):
    result = collection.query(query_texts=[query], n_results=k)

    return {
        "ids": result["ids"][0],
        "documents": result["documents"][0],
        "metadatas": result["metadatas"][0],
    }
def keyword_search(query: str, k: int = 5):
    if not _text_index:
        return {"documents": [], "metadatas": [], "ids": []}

    query_vec = _vectorizer.transform([query])
    doc_vecs = _vectorizer.transform(_text_index)
    similarities = cosine_similarity(query_vec, doc_vecs).flatten()

    top_indices = similarities.argsort()[-k:][::-1]
    docs = [_text_index[i] for i in top_indices]
    metas = [_text_metadata[i] for i in top_indices]
    ids = [f"tfidf-{i}" for i in top_indices]
    return {"documents": docs, "metadatas": metas, "ids": ids}

def reciprocal_rank_fusion(results1, results2, k=5):
    scores = {}
    for rank, id_ in enumerate(results1["ids"]):
        scores[id_] = scores.get(id_, 0) + 1 / (rank + 1)
    for rank, id_ in enumerate(results2["ids"]):
        scores[id_] = scores.get(id_, 0) + 1 / (rank + 1)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_ids = [x[0] for x in ranked[:k]]

    combined_docs = []
    combined_meta = []

    for r in [results1, results2]:
        for idx, id_ in enumerate(r["ids"]):
            if id_ in top_ids and r["documents"][idx] not in combined_docs:
                combined_docs.append(r["documents"][idx])
                combined_meta.append(r["metadatas"][idx])

    return list(zip(combined_docs, combined_meta))

_search_cache = {}

def hybrid_retrieve(query: str, k=5, filters=None):
    key = f"{query}|{k}|{str(filters)}"
    if key in _search_cache:
        print("🔁 Cache hit")
        return _search_cache[key]

    load_all_documents()
    sem = semantic_search(query, k)
    keyw = keyword_search(query, k)
    merged = reciprocal_rank_fusion(sem, keyw)

    if filters:
        merged = [(doc, meta) for doc, meta in merged if _filter_match(meta, filters)]

    _search_cache[key] = merged
    return merged


def _filter_match(meta: Dict, filters: Dict) -> bool:
    if "filename" in filters and filters["filename"] != meta.get("source"):
        return False
    if "tenant" in filters and filters["tenant"] != meta.get("tenant", "public"):
        return False
    if "date_from" in filters:
        meta_ts = meta.get("timestamp")
        if meta_ts and meta_ts < filters["date_from"]:
            return False
    if "date_to" in filters:
        meta_ts = meta.get("timestamp")
        if meta_ts and meta_ts > filters["date_to"]:
            return False
    return True
