from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.api_key import ApiKey
from app.core.db import get_db  # helper to get DB session from request

def get_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> ApiKey:
    key = db.query(ApiKey).filter_by(key=x_api_key, active=True).first()
    if not key:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return key

def require_role(required_role: str):
    def role_checker(api_key: ApiKey = Depends(get_api_key)):
        if api_key.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return api_key
    return role_checker
