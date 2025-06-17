"""
engine：可以在多个线程中共享和使用。
Session：必须为每个线程/请求单独创建，不可共享。
"""
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL NOT SET")

engine = create_engine(DATABASE_URL, echo=True)
def get_session():
    return Session(engine)
