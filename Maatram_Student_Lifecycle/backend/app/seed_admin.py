from getpass import getpass
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password
Base.metadata.create_all(bind=engine)
db=SessionLocal()
try:
    username=input("Admin username: ").strip()
    email=input("Admin email: ").strip()
    name=input("Admin display name: ").strip()
    password=getpass("Admin password (10+ characters): ")
    if len(password)<10: raise SystemExit("Password must be at least 10 characters")
    if db.scalar(select(User).where((User.username==username)|(User.email==email))): raise SystemExit("Username/email already exists")
    db.add(User(username=username,email=email,full_name=name,password_hash=hash_password(password),role="admin"))
    db.commit()
    print("Admin created. Keep credentials private.")
finally: db.close()
