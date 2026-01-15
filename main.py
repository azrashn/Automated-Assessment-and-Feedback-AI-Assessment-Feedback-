import os
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request

from src.database import engine, Base
from src.api import auth_routes, exam_routes, admin_routes, report_routes, user_routes

# Create Database Tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI Application
app = FastAPI(title="AI Assessment System")

# Configure Static Files
os.makedirs("src/static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Template Configuration
# This allows automatic lookup of templates in the "src/templates" directory
templates = Jinja2Templates(directory="src/templates")

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routes
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(exam_routes.router, prefix="/api/exam", tags=["Exam"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(report_routes.router, prefix="/api/report", tags=["Report"])
app.include_router(user_routes.router)

# HTML Page Routes

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index.html") 
def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register.html")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login.html")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard.html")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/history.html")
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/exam.html")
def exam_page(request: Request):
    return templates.TemplateResponse("exam.html", {"request": request})

# Analysis Page Route
@app.get("/analysis.html")
def analysis_page(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})

@app.get("/profile.html")
def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/admin.html")
def admin_page(request: Request):
    """
    Serves the admin panel page.
    """
    return templates.TemplateResponse("admin.html", {"request": request})