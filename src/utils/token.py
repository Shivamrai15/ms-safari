import jwt
from fastapi import Request, HTTPException
from src.config import settings

def verify_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


async def auth_middleware(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header.split("Bearer ")[1]
    print(f"Received token: {settings.JWT_SECRET}")  # Debugging log
    try:
        payload = verify_token(token, settings.JWT_SECRET)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = payload.get("userId")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Token payload missing userId or email")

    return {"userId": user_id, "email": email}