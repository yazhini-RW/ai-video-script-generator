from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=func.now())

    scripts = relationship("Script", back_populates="user")


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    topic = Column(String)
    audience = Column(String)
    platform = Column(String)
    tone = Column(String)
    length_minutes = Column(Integer)
    language = Column(String, default="English")
    scenes = Column(JSON, default=[])
    seo_metadata = Column(JSON, default={})
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="scripts")