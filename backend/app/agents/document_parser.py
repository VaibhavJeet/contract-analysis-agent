"""Document parsing agent."""

from typing import Optional
import fitz  # PyMuPDF
from docx import Document
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.models.contract import ContractAnalysis, ContractType


class DocumentParserAgent:
    """Agent for parsing contract documents."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=ContractAnalysis)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal document analyst. Analyze the provided contract text and extract key information.

Extract the following:
1. A brief summary of the contract (2-3 sentences)
2. The type of contract (nda, employment, service, license, lease, purchase, partnership, other)
3. All parties involved in the contract
4. Effective date (if mentioned)
5. Expiration/termination date (if mentioned)
6. Key terms and conditions
7. Overall risk assessment (low, medium, high)
8. Overall assessment of the contract
9. Recommendations for review

{format_instructions}"""),
            ("human", "Analyze this contract:\n\n{contract_text}")
        ])

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def extract_text(self, file_path: str) -> str:
        """Extract text from document based on file type."""
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif extension in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        elif extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    async def parse(self, file_path: str) -> tuple[str, ContractAnalysis]:
        """Parse contract document and extract analysis."""
        raw_text = self.extract_text(file_path)

        # Truncate if too long
        max_chars = 50000
        if len(raw_text) > max_chars:
            raw_text = raw_text[:max_chars] + "\n\n[Document truncated for analysis...]"

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke({
            "contract_text": raw_text,
            "format_instructions": self.parser.get_format_instructions()
        })

        analysis = ContractAnalysis(
            summary=result.get("summary", ""),
            contract_type=ContractType(result.get("contract_type", "other")),
            parties=result.get("parties", []),
            effective_date=result.get("effective_date"),
            expiration_date=result.get("expiration_date"),
            key_terms=result.get("key_terms", []),
            risk_score=result.get("risk_score", "medium"),
            overall_assessment=result.get("overall_assessment", ""),
            recommendations=result.get("recommendations", [])
        )

        return raw_text, analysis
