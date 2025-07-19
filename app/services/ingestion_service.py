import os
import hashlib
import json
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from app.models.file_record import FileRecord
from app.services.embedding_service import embed_text  # to be implemented
from app.services.chunker import chunk_text  # to be implemented

SUPPORTED_EXTS = ['.json', '.txt']

def calculate_file_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def load_files_from_directory(base_path: str) -> List[str]:
    paths = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTS):
                paths.append(os.path.join(root, file))
    return paths

def process_file(file_path: str, db: Session):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    file_hash = calculate_file_hash(raw_content)
    filename = os.path.relpath(file_path, start="training_data")

    existing = db.query(FileRecord).filter_by(filename=filename, file_hash=file_hash).first()
    if existing:
        print(f"Skipping unchanged file: {filename}")
        return

    print(f"Processing file: {filename}")
    try:
        if file_path.endswith('.json'):
            try:
                data = json.loads(raw_content)
                if isinstance(data, list):
                    content = '\n'.join(json.dumps(item) for item in data)
                else:
                    content = json.dumps(data)
            except json.JSONDecodeError:
                content = raw_content
        else:
            content = raw_content

        chunks = chunk_text(content)
        metadata_list = [{"source": filename, "timestamp": str(datetime.utcnow())} for _ in chunks]
        embed_text(chunks, metadata_list) # store in vector DB

        record = FileRecord(
            filename=filename,
            file_hash=file_hash,
            processed_at=datetime.utcnow(),
            tokens_estimate=len(content.split())
        )
        db.merge(record)
        db.commit()

    except Exception as e:
        print(f"Error processing {filename}: {e}")
