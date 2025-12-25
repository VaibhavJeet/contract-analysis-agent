"""Clause models."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ClauseType(str, Enum):
    """Clause type enumeration."""
    TERMINATION = "termination"
    CONFIDENTIALITY = "confidentiality"
    INDEMNIFICATION = "indemnification"
    LIABILITY = "liability"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    NON_COMPETE = "non_compete"
    NON_SOLICITATION = "non_solicitation"
    PAYMENT = "payment"
    WARRANTY = "warranty"
    DISPUTE_RESOLUTION = "dispute_resolution"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    ASSIGNMENT = "assignment"
    AMENDMENT = "amendment"
    NOTICES = "notices"
    ENTIRE_AGREEMENT = "entire_agreement"
    SEVERABILITY = "severability"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Clause(Base):
    """Clause database model."""
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    clause_type = Column(SQLEnum(ClauseType), default=ClauseType.OTHER)
    title = Column(String)
    text = Column(Text, nullable=False)
    section_number = Column(String)
    page_number = Column(String)
    risk_level = Column(SQLEnum(RiskLevel))
    risk_score = Column(Float)
    risk_factors = Column(JSON, default=list)
    key_terms = Column(JSON, default=list)
    related_clauses = Column(JSON, default=list)
    analysis = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="clauses")


class ClauseCreate(BaseModel):
    """Clause creation schema."""
    clause_type: ClauseType = ClauseType.OTHER
    title: Optional[str] = None
    text: str
    section_number: Optional[str] = None
    page_number: Optional[str] = None


class ClauseRiskAssessment(BaseModel):
    """Clause risk assessment result."""
    risk_level: RiskLevel
    risk_score: float = Field(ge=0, le=1)
    risk_factors: List[str]
    analysis: str
    recommendations: List[str] = []


class ClauseResponse(BaseModel):
    """Clause response schema."""
    id: str
    contract_id: str
    clause_type: ClauseType
    title: Optional[str] = None
    text: str
    section_number: Optional[str] = None
    page_number: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[float] = None
    risk_factors: List[str] = []
    key_terms: List[str] = []
    analysis: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
