import json, os, uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from app.models.schemas import HomeRequest, PartyRequest
from app.services.recommendation_service import recommend
from app.config import BASE_DIR, settings

router = APIRouter()

def save_history(uid, planner, data, result):
    c = get_connection()
    c.execute(
        "INSERT INTO recommendations(user_id,planner_type,input_json,result_json) VALUES(?,?,?,?)",
        (uid, planner, json.dumps(data), json.dumps(result)))
    c.commit()
    c.close()

@router.post("/generate-home")
def generate_home(data: HomeRequest, user=Depends(get_current_user)):
    result = recommend("home", data.model_dump())
    save_history(user["id"], "home", data.model_dump(), result)
    return result

@router.post("/generate-party")
def generate_party(data: PartyRequest, user=Depends(get_current_user)):
    result = recommend("party", data.model_dump())
    save_history(user["id"], "party", data.model_dump(), result)
    return result

@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form("Wedding"),
    style: str = Form("Elegant"),
    outfit_color: str = Form(""),
    preferences: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user=Depends(get_current_user)
):
    if budget <= 0:
        raise HTTPException(400, "Budget must be greater than zero.")
    image_path = None
    if outfit_image and outfit_image.filename:
        ext = os.path.splitext(outfit_image.filename)[1].lower()
        if ext not in {".jpg",".jpeg",".png",".webp"}:
            raise HTTPException(400, "Only JPG, JPEG, PNG and WEBP are supported.")
        content = await outfit_image.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(400, "Image must be 5 MB or smaller.")
        folder = BASE_DIR / settings.upload_dir
        folder.mkdir(parents=True, exist_ok=True)
        image_path = str(folder / f"{uuid.uuid4().hex}{ext}")
        with open(image_path, "wb") as f:
            f.write(content)
    data = {"budget":budget,"occasion":occasion,"style":style,
            "outfit_color":outfit_color,"preferences":preferences}
    result = recommend("jewelry", data, image_path)
    save_history(user["id"], "jewelry", data, result)
    return result

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id:int, user=Depends(get_current_user)):
    c=get_connection()
    r=c.execute(
        "SELECT * FROM recommendations WHERE id=? AND user_id=?",
        (recommendation_id,user["id"])).fetchone()
    c.close()
    if not r: raise HTTPException(404,"Recommendation not found.")
    return {"id":r["id"],"planner_type":r["planner_type"],
            "input":json.loads(r["input_json"]),
            "result":json.loads(r["result_json"]),
            "created_at":r["created_at"]}

@router.get("/history")
def history(user=Depends(get_current_user)):
    c=get_connection()
    rows=c.execute(
        "SELECT id,planner_type,input_json,result_json,created_at FROM recommendations "
        "WHERE user_id=? ORDER BY id DESC",(user["id"],)).fetchall()
    c.close()
    return [{"id":r["id"],"planner_type":r["planner_type"],
             "input":json.loads(r["input_json"]),
             "result":json.loads(r["result_json"]),
             "created_at":r["created_at"]} for r in rows]
