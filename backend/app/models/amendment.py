"""Amendment models."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class AmendmentStatus(str, Enum):
    """Amendment status enumeration."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"


class AmendmentType(str, Enum):
    """Amendment type enumeration."""
    MODIFICATION = "modification"
    ADDITION = "addition"
    DELETION = "deletion"
    REPLACEMENT = "replacement"


class Amendment(Base):
    """Amendment database model."""
    __tablename__ = "amendments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    clause_id = Column(String, ForeignKey("clauses.id"))
    amendment_type = Column(SQLEnum(AmendmentType), default=AmendmentType.MODIFICATION)
    status = Column(SQLEnum(AmendmentStatus), default=AmendmentStatus.DRAFT)
    original_text = Column(Text)
    proposed_text = Column(Text, nullable=False)
    rationale = Column(Text)
    risk_mitigation = Column(Text)
    negotiation_points = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contract = relationship("Contract", back_populates="amendments")


class AmendmentCreate(BaseModel):
    """Amendment creation schema."""
    clause_id: Optional[str] = None
    amendment_type: AmendmentType = AmendmentType.MODIFICATION
    original_text: Optional[str] = None
    proposed_text: str
    rationale: Optional[str] = None


class AmendmentSuggestion(BaseModel):
    """AI-generated amendment suggestion."""
    original_text: str
    proposed_text: str
    amendment_type: AmendmentType
    rationale: str
    risk_mitigation: str
    negotiation_points: List[str] = []
    priority: str  # low, medium, high


class AmendmentResponse(BaseModel):
    """Amendment response schema."""
    id: str
    contract_id: str
    clause_id: Optional[str] = None
    amendment_type: AmendmentType
    status: AmendmentStatus
    original_text: Optional[str] = None
    proposed_text: str
    rationale: Optional[str] = None
    risk_mitigation: Optional[str] = None
    negotiation_points: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
