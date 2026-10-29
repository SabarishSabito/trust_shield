import os
# Redundant guard against DLL loader crashes
os.environ["DISABLE_SQLALCHEMY_CEXT_1"] = "1"

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./trustshield.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProfileAudit(Base):
    __tablename__ = "profile_audits"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String, unique=True, index=True)
    platform = Column(String, default="INSTAGRAM")
    username = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    account_age_days = Column(Integer, default=1)
    posts_count = Column(Integer, default=0)
    messages_per_hr = Column(Float, default=0.0)
    mutual_connections = Column(Integer, default=0)
    composite_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    linguistic_score = Column(Float, default=0.0)
    vision_score = Column(Float, default=0.0)
    network_score = Column(Float, default=0.0)
    classification = Column(String, default="Pending")
    threat_indicators = Column(JSON, default=list)
    moderator_status = Column(String, default="Under Review")
    created_at = Column(DateTime, default=datetime.utcnow)