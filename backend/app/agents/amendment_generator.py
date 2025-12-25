"""Amendment generation agent."""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_llm
from app.models.amendment import AmendmentSuggestion, AmendmentType


class AmendmentResult(BaseModel):
    """Amendment generation result."""
    amendments: List[dict] = Field(description="List of suggested amendments")


class AmendmentGeneratorAgent:
    """Agent for generating contract amendments."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=AmendmentResult)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal contract drafter. Generate suggested amendments for problematic clauses.

For each clause that needs modification, provide:
1. original_text: The original clause text
2. proposed_text: The improved clause text
3. amendment_type: modification, addition, deletion, or replacement
4. rationale: Why this change is recommended
5. risk_mitigation: How this amendment reduces risk
6. negotiation_points: Key points for negotiation
7. priority: low, medium, or high

Focus on:
- Balancing interests of all parties
- Reducing legal exposure
- Clarifying ambiguous language
- Adding missing protections
- Industry standard practices

{format_instructions}"""),
            ("human", """Generate amendments for these problematic clauses in a {contract_type} contract:

{clauses_with_risks}

Contract Summary:
{contract_summary}""")
        ])

    async def generate(
        self,
        clauses_with_risks: str,
        contract_type: str,
        contract_summary: str = ""
    ) -> List[AmendmentSuggestion]:
        """Generate amendment suggestions."""
        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "clauses_with_risks": clauses_with_risks,
            "contract_type": contract_type,
            "contract_summary": contract_summary or "No summary available",
            "format_instructions": self.parser.get_format_instructions()
        })

        suggestions = []
        for amendment_data in result.get("amendments", []):
            try:
                amendment_type_str = amendment_data.get("amendment_type", "modification").lower()
                try:
                    amendment_type = AmendmentType(amendment_type_str)
                except ValueError:
                    amendment_type = AmendmentType.MODIFICATION

                suggestions.append(AmendmentSuggestion(
                    original_text=amendment_data.get("original_text", ""),
                    proposed_text=amendment_data.get("proposed_text", ""),
                    amendment_type=amendment_type,
                    rationale=amendment_data.get("rationale", ""),
                    risk_mitigation=amendment_data.get("risk_mitigation", ""),
                    negotiation_points=amendment_data.get("negotiation_points", []),
                    priority=amendment_data.get("priority", "medium")
                ))
            except Exception:
                continue

        return suggestions

    async def generate_single(
        self,
        clause_text: str,
        clause_type: str,
        risk_analysis: str
    ) -> AmendmentSuggestion:
        """Generate amendment for a single clause."""
        single_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal contract drafter. Generate an improved version of the problematic clause.

Provide:
1. original_text: The original clause text
2. proposed_text: The improved clause text
3. amendment_type: modification, addition, deletion, or replacement
4. rationale: Why this change is recommended
5. risk_mitigation: How this amendment reduces risk
6. negotiation_points: Key points for negotiation
7. priority: low, medium, or high

{format_instructions}"""),
            ("human", """Generate an amendment for this {clause_type} clause:

Original Clause:
{clause_text}

Risk Analysis:
{risk_analysis}""")
        ])

        chain = single_prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "clause_text": clause_text,
            "clause_type": clause_type,
            "risk_analysis": risk_analysis,
            "format_instructions": self.parser.get_format_instructions()
        })

        amendments = result.get("amendments", [result])
        if not amendments:
            amendments = [result]

        amendment_data = amendments[0] if isinstance(amendments, list) else amendments

        amendment_type_str = amendment_data.get("amendment_type", "modification").lower()
        try:
            amendment_type = AmendmentType(amendment_type_str)
        except ValueError:
            amendment_type = AmendmentType.MODIFICATION

        return AmendmentSuggestion(
            original_text=amendment_data.get("original_text", clause_text),
            proposed_text=amendment_data.get("proposed_text", ""),
            amendment_type=amendment_type,
            rationale=amendment_data.get("rationale", ""),
            risk_mitigation=amendment_data.get("risk_mitigation", ""),
            negotiation_points=amendment_data.get("negotiation_points", []),
            priority=amendment_data.get("priority", "medium")
        )
