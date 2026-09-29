from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import RegisterRequest, LoginRequest
from app.database import get_connection
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register")
def register(data: RegisterRequest):
    c = get_connection()
    try:
        if c.execute("SELECT id FROM users WHERE email=?", (data.email.lower(),)).fetchone():
            raise HTTPException(400, "Email is already registered.")
        cur = c.execute(
            "INSERT INTO users(email,name,password_hash) VALUES(?,?,?)",
            (data.email.lower(), data.name.strip(), hash_password(data.password)))
        c.commit()
        return {"message":"Registration successful","user_id":cur.lastrowid}
    finally:
        c.close()

@router.post("/login")
def login(data: LoginRequest):
    c = get_connection()
    user = c.execute("SELECT * FROM users WHERE email=?", (data.email.lower(),)).fetchone()
    c.close()
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password.")
    return {
        "access_token": create_access_token(user["id"], user["email"]),
        "token_type":"bearer",
        "user":{"id":user["id"],"name":user["name"],"email":user["email"]}
    }

@router.post("/logout")
def logout():
    return {"message":"Logout successful. Remove the token on the client."}

@router.post("/token")
def token(data: LoginRequest):
    return login(data)

@router.get("/session-info")
def session_info(user=Depends(get_current_user)):
    return {"logged_in":True,"user":user}

@router.get("/session-data")
def session_data(user=Depends(get_current_user)):
    c = get_connection()
    count = c.execute(
        "SELECT COUNT(*) FROM recommendations WHERE user_id=?", (user["id"],)
    ).fetchone()[0]
    c.close()
    return {"user":user,"recommendation_count":count}
