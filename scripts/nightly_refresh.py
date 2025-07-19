import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Setup environment and path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# Import your services and models
from app.services.ingestion_service import load_files_from_directory, process_file
from app.models.file_record import Base
from app.retrieval.retrieval_service import hybrid_retrieve

# Load DB connection
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("❌ DATABASE_URL not set in .env")

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)

def run_ingestion():
    print("🔄 Running ingestion...")
    Base.metadata.create_all(engine)
    session = Session()

    files = load_files_from_directory("training_data")
    for file in files:
        process_file(file, session)

    session.close()
    print("✅ Ingestion complete.\n")

def run_retrieval_test():
    print("🔍 Running hybrid retrieval test...\n")
    query = "What tech stack does Eltrion use?"
    results = hybrid_retrieve(query, k=3)

    if not results:
        print("⚠️ No results found.")
        return

    for i, (doc, meta) in enumerate(results, start=1):
        preview = doc[:100].replace("\n", " ") + ("..." if len(doc) > 100 else "")
        print(f"{i}. {preview}")
        print(f"   ↳ Source: {meta.get('source')}, Tenant: {meta.get('tenant', 'public')}, Timestamp: {meta.get('timestamp')}\n")

if __name__ == "__main__":
    run_ingestion()
    run_retrieval_test()
from app.services.memory_service import store_message, get_context

print("💬 Testing conversation memory...\n")

conv_id = "test-convo-1"

store_message(conv_id, "user", "What's the tech stack?")
store_message(conv_id, "assistant", "FastAPI, PostgreSQL, Redis, Ollama, etc.")
store_message(conv_id, "user", "How does it learn?")
store_message(conv_id, "assistant", "It re-embeds files nightly into a vector DB.")

context = get_context(conv_id)
for turn in context:
    print(f"[{turn['role']}] {turn['message']} @ {turn['timestamp']}")
