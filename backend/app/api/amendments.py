"""Amendment API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.amendment import (
    Amendment,
    AmendmentCreate,
    AmendmentResponse,
    AmendmentStatus
)
from app.models.contract import Contract
from app.models.clause import Clause, RiskLevel
from app.agents.amendment_generator import AmendmentGeneratorAgent

router = APIRouter()


@router.get("", response_model=List[AmendmentResponse])
async def list_amendments(
    contract_id: Optional[str] = None,
    status: Optional[AmendmentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List amendments with optional filtering."""
    query = select(Amendment).order_by(Amendment.created_at.desc())

    if contract_id:
        query = query.where(Amendment.contract_id == contract_id)
    if status:
        query = query.where(Amendment.status == status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{amendment_id}", response_model=AmendmentResponse)
async def get_amendment(
    amendment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get amendment details."""
    result = await db.execute(
        select(Amendment).where(Amendment.id == amendment_id)
    )
    amendment = result.scalar_one_or_none()

    if not amendment:
        raise HTTPException(404, "Amendment not found")

    return amendment


@router.post("/contract/{contract_id}/generate")
async def generate_amendments(
    contract_id: str,
    risk_threshold: RiskLevel = RiskLevel.MEDIUM,
    db: AsyncSession = Depends(get_db)
):
    """Generate amendments for high-risk clauses."""
    # Get contract
    contract_result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = contract_result.scalar_one_or_none()

    if not contract:
        raise HTTPException(404, "Contract not found")

    # Get high-risk clauses
    risk_levels = [RiskLevel.CRITICAL, RiskLevel.HIGH]
    if risk_threshold == RiskLevel.MEDIUM:
        risk_levels.append(RiskLevel.MEDIUM)

    clauses_result = await db.execute(
        select(Clause).where(
            Clause.contract_id == contract_id,
            Clause.risk_level.in_(risk_levels)
        )
    )
    clauses = clauses_result.scalars().all()

    if not clauses:
        return {
            "message": "No high-risk clauses found requiring amendments",
            "amendments": []
        }

    # Format clauses for amendment generation
    clauses_text = "\n\n".join([
        f"Clause: {c.title or 'Untitled'} ({c.clause_type.value})\n"
        f"Risk Level: {c.risk_level.value if c.risk_level else 'unknown'}\n"
        f"Risk Factors: {', '.join(c.risk_factors or [])}\n"
        f"Text: {c.text}\n"
        f"Analysis: {c.analysis or 'No analysis'}"
        for c in clauses
    ])

    # Generate amendments
    generator = AmendmentGeneratorAgent()
    suggestions = await generator.generate(
        clauses_with_risks=clauses_text,
        contract_type=contract.contract_type.value,
        contract_summary=contract.summary or ""
    )

    # Create amendment records
    amendments_created = []
    for suggestion in suggestions:
        amendment = Amendment(
            contract_id=contract_id,
            amendment_type=suggestion.amendment_type,
            original_text=suggestion.original_text,
            proposed_text=suggestion.proposed_text,
            rationale=suggestion.rationale,
            risk_mitigation=suggestion.risk_mitigation,
            negotiation_points=suggestion.negotiation_points,
            status=AmendmentStatus.DRAFT
        )
        db.add(amendment)
        amendments_created.append(amendment)

    await db.commit()

    return {
        "message": f"Generated {len(amendments_created)} amendments",
        "amendments": [AmendmentResponse.model_validate(a) for a in amendments_created]
    }


@router.post("/clause/{clause_id}/generate", response_model=AmendmentResponse)
async def generate_clause_amendment(
    clause_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate amendment for a specific clause."""
    # Get clause
    clause_result = await db.execute(
        select(Clause).where(Clause.id == clause_id)
    )
    clause = clause_result.scalar_one_or_none()

    if not clause:
        raise HTTPException(404, "Clause not found")

    # Generate amendment
    generator = AmendmentGeneratorAgent()
    suggestion = await generator.generate_single(
        clause_text=clause.text,
        clause_type=clause.clause_type.value,
        risk_analysis=clause.analysis or "No risk analysis available"
    )

    # Create amendment record
    amendment = Amendment(
        contract_id=clause.contract_id,
        clause_id=clause_id,
        amendment_type=suggestion.amendment_type,
        original_text=suggestion.original_text,
        proposed_text=suggestion.proposed_text,
        rationale=suggestion.rationale,
        risk_mitigation=suggestion.risk_mitigation,
        negotiation_points=suggestion.negotiation_points,
        status=AmendmentStatus.DRAFT
    )
    db.add(amendment)
    await db.commit()
    await db.refresh(amendment)

    return amendment


@router.patch("/{amendment_id}/status", response_model=AmendmentResponse)
async def update_amendment_status(
    amendment_id: str,
    status: AmendmentStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update amendment status."""
    result = await db.execute(
        select(Amendment).where(Amendment.id == amendment_id)
    )
    amendment = result.scalar_one_or_none()

    if not amendment:
        raise HTTPException(404, "Amendment not found")

    amendment.status = status
    await db.commit()
    await db.refresh(amendment)

    return amendment


@router.delete("/{amendment_id}")
async def delete_amendment(
    amendment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an amendment."""
    result = await db.execute(
        select(Amendment).where(Amendment.id == amendment_id)
    )
    amendment = result.scalar_one_or_none()

    if not amendment:
        raise HTTPException(404, "Amendment not found")

    await db.delete(amendment)
    await db.commit()

    return {"message": "Amendment deleted successfully"}
