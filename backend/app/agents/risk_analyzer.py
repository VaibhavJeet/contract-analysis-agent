"""Risk analysis agent."""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_llm
from app.models.clause import ClauseRiskAssessment, RiskLevel


class RiskAnalysisResult(BaseModel):
    """Risk analysis result schema."""
    risk_level: str = Field(description="low, medium, high, or critical")
    risk_score: float = Field(description="Score from 0 to 1")
    risk_factors: List[str] = Field(description="Specific risk factors identified")
    analysis: str = Field(description="Detailed risk analysis")
    recommendations: List[str] = Field(description="Risk mitigation recommendations")


class RiskAnalyzerAgent:
    """Agent for analyzing clause and contract risks."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=RiskAnalysisResult)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal risk analyst. Analyze the provided clause for potential legal and business risks.

Consider the following risk categories:
- Liability exposure
- Financial obligations
- Termination rights
- Indemnification scope
- Intellectual property risks
- Compliance requirements
- Ambiguous language
- One-sided terms
- Missing protections
- Industry-specific risks

Provide:
1. risk_level: low, medium, high, or critical
2. risk_score: A score from 0 (no risk) to 1 (extreme risk)
3. risk_factors: List of specific risk factors identified
4. analysis: Detailed explanation of the risks
5. recommendations: Actionable recommendations to mitigate risks

{format_instructions}"""),
            ("human", """Analyze risks in this {clause_type} clause:

Clause Title: {clause_title}
Section: {section_number}

Clause Text:
{clause_text}

Contract Context:
{contract_context}""")
        ])

    async def analyze_clause(
        self,
        clause_text: str,
        clause_type: str,
        clause_title: str = "",
        section_number: str = "",
        contract_context: str = ""
    ) -> ClauseRiskAssessment:
        """Analyze risk for a single clause."""
        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "clause_text": clause_text,
            "clause_type": clause_type,
            "clause_title": clause_title or "Untitled",
            "section_number": section_number or "N/A",
            "contract_context": contract_context or "No additional context provided",
            "format_instructions": self.parser.get_format_instructions()
        })

        risk_level_str = result.get("risk_level", "medium").lower()
        try:
            risk_level = RiskLevel(risk_level_str)
        except ValueError:
            risk_level = RiskLevel.MEDIUM

        risk_score = result.get("risk_score", 0.5)
        if not isinstance(risk_score, (int, float)):
            risk_score = 0.5
        risk_score = max(0, min(1, risk_score))

        return ClauseRiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=result.get("risk_factors", []),
            analysis=result.get("analysis", ""),
            recommendations=result.get("recommendations", [])
        )
