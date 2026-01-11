import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.api import auth_routes, exam_routes, admin_routes, security_routes, report_routes, user_routes

# İskelet modunda tablolar boş oluşacak (Columnsız)
# Base.metadata.create_all(bind=engine) 

app = FastAPI(title="AI Assessment System - Skeleton Mode")

# Klasörler
os.makedirs("src/static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(exam_routes.router, prefix="/api/exam", tags=["Exam"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(security_routes.router, prefix="/api/security", tags=["Security"])
app.include_router(report_routes.router, prefix="/api/report", tags=["Report"])
app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"message": "Sistem İskeleti Çalışıyor!"}
