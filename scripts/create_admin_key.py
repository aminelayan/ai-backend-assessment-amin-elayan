import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from app.models.api_key import Base, ApiKey  # Make sure these paths are correct

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_admin_key(email: str):
    session = Session()
    Base.metadata.create_all(engine)

    new_key = ApiKey(
        key=str(uuid.uuid4()),
        role="admin",
        owner_email=email,
        created_at=datetime.utcnow(),
        active=True
    )

    session.add(new_key)
    session.commit()
    print(f"✅ Admin key created: {new_key.key} for {email}")
    session.close()

if __name__ == "__main__":
    email = input("Enter admin email: ").strip()
    create_admin_key(email)
