"""Analytics API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.contract import Contract, ContractStatus, ContractType
from app.models.clause import Clause, ClauseType, RiskLevel
from app.models.amendment import Amendment, AmendmentStatus

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    # Total contracts
    total_contracts = await db.execute(
        select(func.count(Contract.id))
    )
    total_contracts_count = total_contracts.scalar() or 0

    # Contracts by status
    analyzed_contracts = await db.execute(
        select(func.count(Contract.id)).where(
            Contract.status == ContractStatus.ANALYZED
        )
    )
    analyzed_count = analyzed_contracts.scalar() or 0

    # Total clauses
    total_clauses = await db.execute(
        select(func.count(Clause.id))
    )
    total_clauses_count = total_clauses.scalar() or 0

    # High risk clauses
    high_risk_clauses = await db.execute(
        select(func.count(Clause.id)).where(
            Clause.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        )
    )
    high_risk_count = high_risk_clauses.scalar() or 0

    # Pending amendments
    pending_amendments = await db.execute(
        select(func.count(Amendment.id)).where(
            Amendment.status.in_([AmendmentStatus.DRAFT, AmendmentStatus.PENDING_REVIEW])
        )
    )
    pending_amendments_count = pending_amendments.scalar() or 0

    return {
        "total_contracts": total_contracts_count,
        "analyzed_contracts": analyzed_count,
        "total_clauses": total_clauses_count,
        "high_risk_clauses": high_risk_count,
        "pending_amendments": pending_amendments_count,
        "analysis_rate": round((analyzed_count / total_contracts_count * 100) if total_contracts_count > 0 else 0, 1)
    }


@router.get("")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """Get comprehensive analytics."""
    # Contracts by type
    contracts_by_type = await db.execute(
        select(
            Contract.contract_type,
            func.count(Contract.id).label("count")
        ).group_by(Contract.contract_type)
    )
    contracts_by_type_data = [
        {"type": row[0].value if row[0] else "unknown", "count": row[1]}
        for row in contracts_by_type.all()
    ]

    # Clauses by type
    clauses_by_type = await db.execute(
        select(
            Clause.clause_type,
            func.count(Clause.id).label("count")
        ).group_by(Clause.clause_type)
    )
    clauses_by_type_data = [
        {"type": row[0].value if row[0] else "unknown", "count": row[1]}
        for row in clauses_by_type.all()
    ]

    # Risk distribution
    risk_distribution = await db.execute(
        select(
            Clause.risk_level,
            func.count(Clause.id).label("count")
        ).where(Clause.risk_level.isnot(None)).group_by(Clause.risk_level)
    )
    risk_data = [
        {"level": row[0].value if row[0] else "unknown", "count": row[1]}
        for row in risk_distribution.all()
    ]

    # Amendments by status
    amendments_by_status = await db.execute(
        select(
            Amendment.status,
            func.count(Amendment.id).label("count")
        ).group_by(Amendment.status)
    )
    amendments_data = [
        {"status": row[0].value if row[0] else "unknown", "count": row[1]}
        for row in amendments_by_status.all()
    ]

    # Most common clause types with high risk
    risky_clause_types = await db.execute(
        select(
            Clause.clause_type,
            func.count(Clause.id).label("count")
        ).where(
            Clause.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).group_by(Clause.clause_type).order_by(func.count(Clause.id).desc()).limit(5)
    )
    risky_types_data = [
        {"type": row[0].value if row[0] else "unknown", "count": row[1]}
        for row in risky_clause_types.all()
    ]

    return {
        "contracts_by_type": contracts_by_type_data,
        "clauses_by_type": clauses_by_type_data,
        "risk_distribution": risk_data,
        "amendments_by_status": amendments_data,
        "most_risky_clause_types": risky_types_data
    }
