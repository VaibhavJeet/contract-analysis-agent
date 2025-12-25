"""Contract models."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ContractStatus(str, Enum):
    """Contract status enumeration."""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    ERROR = "error"


class ContractType(str, Enum):
    """Contract type enumeration."""
    NDA = "nda"
    EMPLOYMENT = "employment"
    SERVICE = "service"
    LICENSE = "license"
    LEASE = "lease"
    PURCHASE = "purchase"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class Contract(Base):
    """Contract database model."""
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    title = Column(String)
    contract_type = Column(SQLEnum(ContractType), default=ContractType.OTHER)
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.UPLOADED)
    parties = Column(JSON, default=list)
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    raw_text = Column(Text)
    summary = Column(Text)
    metadata = Column(JSON, default=dict)
    risk_score = Column(String)  # low, medium, high
    overall_assessment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")
    amendments = relationship("Amendment", back_populates="contract", cascade="all, delete-orphan")


class ContractCreate(BaseModel):
    """Contract creation schema."""
    title: Optional[str] = None
    contract_type: Optional[ContractType] = ContractType.OTHER


class ContractAnalysis(BaseModel):
    """Contract analysis result schema."""
    summary: str
    contract_type: ContractType
    parties: List[str]
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    key_terms: List[str] = []
    risk_score: str = Field(description="low, medium, or high")
    overall_assessment: str
    recommendations: List[str] = []


class ContractResponse(BaseModel):
    """Contract response schema."""
    id: str
    filename: str
    title: Optional[str] = None
    contract_type: ContractType
    status: ContractStatus
    parties: List[str] = []
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    summary: Optional[str] = None
    risk_score: Optional[str] = None
    overall_assessment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
