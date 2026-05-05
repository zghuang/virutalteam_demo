import bcrypt
from app.database import engine, Base, SessionLocal
from app.models import seed_official_sources
from app.models.user import User
from app.config import settings


def seed_admin_user(db):
    """Seed a default admin user if none exists.

    Security notes:
    - Password is hashed with bcrypt (salt rounds = 12, default for bcrypt.hashpw).
    - The default password can be overridden via DEFAULT_ADMIN_PASSWORD env var.
    - The username can be overridden via DEFAULT_ADMIN_USERNAME env var.
    """
    existing = db.query(User).first()
    if existing:
        return  # admin already seeded or other users exist

    hashed = bcrypt.hashpw(
        settings.DEFAULT_ADMIN_PASSWORD.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")
    user = User(username=settings.DEFAULT_ADMIN_USERNAME, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Admin user seeded: {settings.DEFAULT_ADMIN_USERNAME}")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_official_sources(db)
        seed_admin_user(db)
        print("Database initialized with official sources and admin user.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
