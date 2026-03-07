from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from bson import ObjectId, errors # Added errors for validation
from app.utils.security import decode_token
from app.database import get_collection

security = HTTPBearer()

# =========================
# GET CURRENT USER
# =========================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    users_collection = get_collection("users")

    try:
        # Validate that the string is a proper ObjectId format
        obj_id = ObjectId(user_id)
        user = await users_collection.find_one({"_id": obj_id})
    except (errors.InvalidId, Exception):
        # If the ID is malformed or DB connection fails
        user = None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

# =========================
# ACTIVE USER CHECK
# =========================
async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:

    # Ensure the check handles missing fields or incorrect types
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Better to use 403 for Inactive
            detail="User account is inactive",
        )

    return current_user

# =========================
# ADMIN CHECK
# =========================
async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Dict[str, Any]:

    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required",
        )

    return current_user