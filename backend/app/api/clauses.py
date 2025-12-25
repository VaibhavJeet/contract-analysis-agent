"""Clause API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.clause import Clause, ClauseResponse, ClauseType, RiskLevel
from app.models.contract import Contract
from app.agents.risk_analyzer import RiskAnalyzerAgent

router = APIRouter()


@router.get("/contract/{contract_id}", response_model=List[ClauseResponse])
async def get_contract_clauses(
    contract_id: str,
    clause_type: Optional[ClauseType] = None,
    risk_level: Optional[RiskLevel] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all clauses for a contract."""
    # Verify contract exists
    contract_result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    if not contract_result.scalar_one_or_none():
        raise HTTPException(404, "Contract not found")

    query = select(Clause).where(Clause.contract_id == contract_id)

    if clause_type:
        query = query.where(Clause.clause_type == clause_type)
    if risk_level:
        query = query.where(Clause.risk_level == risk_level)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{clause_id}", response_model=ClauseResponse)
async def get_clause(
    clause_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get clause details."""
    result = await db.execute(
        select(Clause).where(Clause.id == clause_id)
    )
    clause = result.scalar_one_or_none()

    if not clause:
        raise HTTPException(404, "Clause not found")

    return clause


@router.post("/{clause_id}/assess-risk", response_model=ClauseResponse)
async def assess_clause_risk(
    clause_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Assess risk for a clause."""
    result = await db.execute(
        select(Clause).where(Clause.id == clause_id)
    )
    clause = result.scalar_one_or_none()

    if not clause:
        raise HTTPException(404, "Clause not found")

    # Get contract for context
    contract_result = await db.execute(
        select(Contract).where(Contract.id == clause.contract_id)
    )
    contract = contract_result.scalar_one_or_none()

    # Run risk analysis
    analyzer = RiskAnalyzerAgent()
    risk_assessment = await analyzer.analyze_clause(
        clause_text=clause.text,
        clause_type=clause.clause_type.value,
        clause_title=clause.title or "",
        section_number=clause.section_number or "",
        contract_context=contract.summary if contract else ""
    )

    # Update clause with risk assessment
    clause.risk_level = risk_assessment.risk_level
    clause.risk_score = risk_assessment.risk_score
    clause.risk_factors = risk_assessment.risk_factors
    clause.analysis = risk_assessment.analysis

    await db.commit()
    await db.refresh(clause)

    return clause


@router.post("/contract/{contract_id}/assess-all-risks")
async def assess_all_clause_risks(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Assess risk for all clauses in a contract."""
    # Get contract
    contract_result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = contract_result.scalar_one_or_none()

    if not contract:
        raise HTTPException(404, "Contract not found")

    # Get all clauses
    clauses_result = await db.execute(
        select(Clause).where(Clause.contract_id == contract_id)
    )
    clauses = clauses_result.scalars().all()

    if not clauses:
        raise HTTPException(400, "No clauses found for this contract")

    analyzer = RiskAnalyzerAgent()
    assessed_count = 0

    for clause in clauses:
        try:
            risk_assessment = await analyzer.analyze_clause(
                clause_text=clause.text,
                clause_type=clause.clause_type.value,
                clause_title=clause.title or "",
                section_number=clause.section_number or "",
                contract_context=contract.summary or ""
            )

            clause.risk_level = risk_assessment.risk_level
            clause.risk_score = risk_assessment.risk_score
            clause.risk_factors = risk_assessment.risk_factors
            clause.analysis = risk_assessment.analysis
            assessed_count += 1

        except Exception:
            continue

    await db.commit()

    return {
        "message": f"Assessed {assessed_count} of {len(clauses)} clauses",
        "contract_id": contract_id
    }
