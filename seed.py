from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models import User
from app.security import hash_password

Base.metadata.create_all(bind=engine)
accounts = [
    ("admin@trustvault.local", "TrustVault Admin", "admin", "Admin@12345"),
    ("owner@trustvault.local", "Alex Owner", "owner", "Owner@12345"),
    ("viewer@trustvault.local", "Vera Viewer", "viewer", "Viewer@12345"),
    ("other@trustvault.local", "Owen Other", "viewer", "Other@12345"),
]
with SessionLocal() as db:
    for email, name, role, password in accounts:
        if not db.scalar(select(User).where(User.email == email)):
            db.add(User(email=email, full_name=name, role=role, password_hash=hash_password(password)))
    db.commit()
print("Seed complete. Demo users:")
for email, name, role, password in accounts: print(f"{role:6} {email:30} {password}")
