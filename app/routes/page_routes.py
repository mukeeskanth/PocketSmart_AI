from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router=APIRouter()
templates=Jinja2Templates(directory="app/templates")

@router.get("/",response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@router.get("/login",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register",response_class=HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

@router.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request:Request):
    return templates.TemplateResponse("dashboard.html",{"request":request})

@router.get("/planner/{planner}",response_class=HTMLResponse)
async def planner(request:Request,planner:str):
    if planner not in {"home","party","jewelry"}:
        raise HTTPException(404,"Planner not found.")
    return templates.TemplateResponse(f"{planner}_planner.html",
                                      {"request":request,"planner":planner})
