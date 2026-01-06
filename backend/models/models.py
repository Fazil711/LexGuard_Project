from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Text, BigInteger, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    role = Column(String, default="user")
    company_id = Column(String, ForeignKey("companies.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    domain = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Case(Base):
    __tablename__ = "cases"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    title = Column(String)
    category = Column(String) 
    status = Column(String, default="intake")
    jurisdiction = Column(String, default="IN")
    amount = Column(BigInteger, nullable=True)
    risk_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("CaseMessage", back_populates="case")
    documents = relationship("Document", back_populates="case")

class CaseMessage(Base):
    __tablename__ = "case_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"))
    sender = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"))
    filename = Column(String)
    s3_key = Column(String)
    extracted_text = Column(Text)
    analysis_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="documents")