"""Contract API endpoints."""

import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import aiofiles

from app.core.database import get_db
from app.core.config import settings
from app.models.contract import (
    Contract,
    ContractCreate,
    ContractResponse,
    ContractStatus,
    ContractType
)
from app.models.clause import Clause, ClauseType
from app.agents.document_parser import DocumentParserAgent
from app.agents.clause_extractor import ClauseExtractorAgent

router = APIRouter()


@router.post("", response_model=ContractResponse)
async def upload_contract(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a contract document."""
    # Validate file type
    allowed_types = [".pdf", ".docx", ".doc", ".txt"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(400, f"File type not allowed. Allowed: {allowed_types}")

    # Save file
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}{ext}")

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Create contract record
    contract = Contract(
        id=file_id,
        filename=file.filename,
        title=title or file.filename,
        status=ContractStatus.PARSING
    )
    db.add(contract)
    await db.commit()

    # Parse document
    try:
        parser = DocumentParserAgent()
        raw_text, analysis = await parser.parse(file_path)

        # Update contract with parsed data
        contract.raw_text = raw_text
        contract.summary = analysis.summary
        contract.contract_type = analysis.contract_type
        contract.parties = analysis.parties
        contract.risk_score = analysis.risk_score
        contract.overall_assessment = analysis.overall_assessment

        # Parse dates if provided
        if analysis.effective_date:
            try:
                contract.effective_date = datetime.fromisoformat(analysis.effective_date)
            except:
                pass
        if analysis.expiration_date:
            try:
                contract.expiration_date = datetime.fromisoformat(analysis.expiration_date)
            except:
                pass

        contract.status = ContractStatus.PARSED
        await db.commit()

        # Extract clauses
        extractor = ClauseExtractorAgent()
        extracted_clauses = await extractor.extract(raw_text)

        for clause_data in extracted_clauses:
            clause = Clause(
                contract_id=contract.id,
                clause_type=ClauseType(clause_data.clause_type),
                title=clause_data.title,
                text=clause_data.text,
                section_number=clause_data.section_number,
                key_terms=clause_data.key_terms
            )
            db.add(clause)

        await db.commit()

    except Exception as e:
        contract.status = ContractStatus.ERROR
        await db.commit()
        raise HTTPException(500, f"Error parsing contract: {str(e)}")

    await db.refresh(contract)
    return contract


@router.get("", response_model=List[ContractResponse])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ContractStatus] = None,
    contract_type: Optional[ContractType] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all contracts."""
    query = select(Contract).order_by(Contract.created_at.desc())

    if status:
        query = query.where(Contract.status == status)
    if contract_type:
        query = query.where(Contract.contract_type == contract_type)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get contract details."""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(404, "Contract not found")

    return contract


@router.post("/{contract_id}/analyze")
async def analyze_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Run full analysis on a contract."""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(404, "Contract not found")

    if not contract.raw_text:
        raise HTTPException(400, "Contract has not been parsed yet")

    contract.status = ContractStatus.ANALYZING
    await db.commit()

    try:
        # Re-analyze with fresh LLM call
        parser = DocumentParserAgent()
        _, analysis = await parser.parse.__wrapped__(parser, contract.raw_text)

        contract.summary = analysis.summary
        contract.risk_score = analysis.risk_score
        contract.overall_assessment = analysis.overall_assessment
        contract.status = ContractStatus.ANALYZED
        await db.commit()

    except Exception as e:
        contract.status = ContractStatus.ERROR
        await db.commit()
        raise HTTPException(500, f"Analysis failed: {str(e)}")

    await db.refresh(contract)
    return contract


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a contract."""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(404, "Contract not found")

    await db.delete(contract)
    await db.commit()

    return {"message": "Contract deleted successfully"}
