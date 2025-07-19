from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


from sentence_transformers import SentenceTransformer
import chromadb

# ✅ Modern Chroma initialization
chroma_client = chromadb.PersistentClient(path="./chroma_store")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

collection = chroma_client.get_or_create_collection(name="eltrion_embeddings")

def embed_text(chunks: list[str], metadata_list: list[dict]):
    vectors = embedding_model.encode(chunks).tolist()
    ids = [f"{meta['source']}::{hash(chunk)}" for chunk, meta in zip(chunks, metadata_list)]

    collection.upsert(
        ids=ids,
        embeddings=vectors,
        documents=chunks,
        metadatas=metadata_list
    )

    print(f"✅ Embedded batch of {len(chunks)} chunks")

def query_similar(text: str, k: int = 3):
    vector = embedding_model.encode(text).tolist()
    results = collection.query(
        query_embeddings=[vector],
        n_results=k
    )
    return results

