"""Clause extraction agent."""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_llm
from app.models.clause import ClauseType


class ExtractedClause(BaseModel):
    """Extracted clause schema."""
    clause_type: str = Field(description="Type of clause")
    title: str = Field(description="Clause title or header")
    text: str = Field(description="Full clause text")
    section_number: str = Field(description="Section or article number")
    key_terms: List[str] = Field(description="Important terms in this clause")


class ClauseExtractionResult(BaseModel):
    """Clause extraction result."""
    clauses: List[ExtractedClause]


class ClauseExtractorAgent:
    """Agent for extracting clauses from contracts."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=ClauseExtractionResult)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal document analyst specializing in clause identification.

Extract all distinct clauses from the contract. For each clause, identify:
1. clause_type: One of: termination, confidentiality, indemnification, liability, intellectual_property, non_compete, non_solicitation, payment, warranty, dispute_resolution, force_majeure, governing_law, assignment, amendment, notices, entire_agreement, severability, other
2. title: The clause heading or a descriptive title
3. text: The complete clause text
4. section_number: The section, article, or paragraph number
5. key_terms: Important legal or business terms in the clause

Be thorough and extract all identifiable clauses.

{format_instructions}"""),
            ("human", "Extract clauses from this contract:\n\n{contract_text}")
        ])

    async def extract(self, contract_text: str) -> List[ExtractedClause]:
        """Extract clauses from contract text."""
        # Truncate if too long
        max_chars = 50000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars]

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "contract_text": contract_text,
            "format_instructions": self.parser.get_format_instructions()
        })

        clauses = []
        for clause_data in result.get("clauses", []):
            try:
                clause_type = clause_data.get("clause_type", "other").lower()
                if clause_type not in [ct.value for ct in ClauseType]:
                    clause_type = "other"

                clauses.append(ExtractedClause(
                    clause_type=clause_type,
                    title=clause_data.get("title", "Untitled Clause"),
                    text=clause_data.get("text", ""),
                    section_number=clause_data.get("section_number", ""),
                    key_terms=clause_data.get("key_terms", [])
                ))
            except Exception:
                continue

        return clauses
