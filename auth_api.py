from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Customer Authentication API"
)


# ============================================================
# LOGIN REQUEST
# ============================================================

class LoginRequest(BaseModel):
    email: str
    password: str


# ============================================================
# LOGIN ENDPOINT
# ============================================================

@app.post("/api/auth/login")
def login(request: LoginRequest):

    # Temporary test credentials.
    # PostgreSQL authentication will be added next.

    if (
        request.email == "test@example.com"
        and request.password == "123456"
    ):

        return {
            "success": True,
            "message": "Login successful",
            "customerID": "TEST-2001",
            "email": request.email
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )