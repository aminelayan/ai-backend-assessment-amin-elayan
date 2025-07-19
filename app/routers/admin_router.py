from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.models.api_key import ApiKey
from app.core.db import get_db

router = APIRouter(prefix="/api/admin/keys", tags=["Admin"])

class KeyCreateRequest(BaseModel):
    owner_email: str
    role: str  # "user" or "admin"

@router.post("/")
def create_api_key(req: KeyCreateRequest, db: Session = Depends(get_db), _: ApiKey = Depends(require_role("admin"))):
    key = ApiKey(owner_email=req.owner_email, role=req.role)
    db.add(key)
    db.commit()
    return {"key": key.key, "role": key.role}
