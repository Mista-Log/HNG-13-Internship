from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import httpx


router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running smoothly 🚀"}

@router.get("/me")
async def my_profile():

    current_time = datetime.now(timezone.utc).isoformat()

    async with httpx.AsyncClient() as client:
        response = await client.get("https://catfact.ninja/fact")
        data = response.json()
        cat_fact = data.get("fact")

    result = {
        "status": "success",
        "user": {
            "email": "oloyedeibrahimsmile@gmail.com",
            "name": "Ibrahim Oloyede",
            "stack": "Django / FastAPI / PostgreSQL"
        },
        "timestamp": current_time,
        "fact": cat_fact
    }

    return result