from typing import List

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def chunk_text(text: str) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = ' '.join(words[i:i + CHUNK_SIZE])
        chunks.append(chunk)
    return chunks
