
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip()
    name = input("Admin display name: ").strip()

    # Password will be visible while typing
    password = input("Admin password (10+ characters): ")

    if len(password) < 10:
        raise SystemExit("Password must be at least 10 characters")

    user = db.scalar(
        select(User).where(
            (User.username == username) |
            (User.email == email)
        )
    )

    if user:
        user.password_hash = hash_password(password)
        user.role = "admin"
        user.full_name = name
        user.email = email

        print("Existing admin account updated.")

    else:
        user = User(
            username=username,
            email=email,
            full_name=name,
            password_hash=hash_password(password),
            role="admin"
        )

        db.add(user)
        print("New admin account created.")

    db.commit()

    print("Admin setup completed successfully.")
    print("Username:", username)
    print("Email:", email)

finally:
    db.close()
