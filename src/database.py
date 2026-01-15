from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL Database Connection
# Using the 'ai_assessment_final_db' database created via SQL script
# Update the password if it differs from the default
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:My..??45@localhost/ai_assessment_final_db"
# Database Engine
# pool_pre_ping=True: Automatically reconnects if the connection drops
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Session Manager
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

# Dependency Injection for Database Sessions
# FastAPI calls this function for each request to provide a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()