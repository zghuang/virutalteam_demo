from app.database import engine, Base, SessionLocal
from app.models import seed_official_sources


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_official_sources(db)
        print("Database initialized with official sources.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
