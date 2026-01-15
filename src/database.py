from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL Bağlantı Bilgisi
# SQL scripti ile oluşturduğumuz 'ai_assessment_final_db' ismini kullanıyoruz.
# Şifreniz '123456' olarak kalmışsa bu şekilde, değilse güncelleyin.
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:My..??45@localhost/ai_assessment_final_db"
# Veritabanı Motoru
# pool_pre_ping=True: Bağlantı kopsa bile otomatik tekrar bağlanmayı sağlar.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Oturum Yöneticisi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modellerin (Tabloların) türeyeceği temel sınıf
Base = declarative_base()

# Dependency Injection
# FastAPI her istekte bu fonksiyonu çağırarak güvenli bir veritabanı oturumu açar ve kapatır.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()