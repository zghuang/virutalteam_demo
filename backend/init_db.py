import bcrypt

from app.database import engine, Base, SessionLocal
from app.models import seed_official_sources, User
from app.config import settings


def seed_admin_user(db):
    user = db.query(User).first()
    if user is not None:
        return
    hashed = bcrypt.hashpw(
        settings.DEFAULT_ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    admin = User(username=settings.DEFAULT_ADMIN_USERNAME, hashed_password=hashed)
    db.add(admin)
    db.commit()
    print(f"Admin user '{settings.DEFAULT_ADMIN_USERNAME}' seeded.")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_official_sources(db)
        seed_admin_user(db)
        print("Database initialized with official sources.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
