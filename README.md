# Contract Analysis Agent

An AI-powered legal document analysis agent that automates contract review, clause extraction, risk assessment, and amendment drafting. Built with LangChain, MCP integrations, and Next.js 15.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)

## Problem Statement

Legal teams face significant challenges with contract management:
- **Volume Overload**: Hundreds of contracts requiring review create bottlenecks
- **Inconsistent Review**: Manual review leads to missed clauses and inconsistent analysis
- **Risk Exposure**: Critical terms and unusual provisions can be overlooked
- **Slow Turnaround**: Contract review delays business operations

## Solution

Contract Analysis Agent provides AI-powered contract intelligence:

1. **Document Parsing**: Extracts structured data from contracts (PDF, DOCX, TXT)
2. **Clause Identification**: Identifies and categorizes all contract clauses
3. **Risk Assessment**: Analyzes terms for potential legal and business risks
4. **Comparison Analysis**: Compares contracts against templates and standards
5. **Amendment Drafting**: Generates suggested amendments for problematic clauses

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js 15 Frontend                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Dashboard │  │ Contracts│  │  Clauses │  │  Risk Analysis   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API
┌─────────────────────────────▼───────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   LangChain Agent Core                       ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  ││
│  │  │Doc Parser   │  │Clause       │  │Risk Analyzer        │  ││
│  │  │   Agent     │  │ Extractor   │  │     Agent           │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MCP Integrations                          ││
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────────┐ ││
│  │  │Database│  │Document│  │  Legal │  │Template Repository │ ││
│  │  │  MCP   │  │ Store  │  │   DB   │  │        MCP         │ ││
│  │  └────────┘  └────────┘  └────────┘  └────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Remote LLM │    │  Local LLM   │    │   Vector DB  │
│ (OpenAI/etc) │    │   (Ollama)   │    │  (ChromaDB)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance async API framework
- **LangChain 0.3+** - Agent orchestration, chains, tools, memory
- **LangGraph** - Multi-agent workflow orchestration
- **ChromaDB** - Vector storage for semantic search
- **Pydantic** - Data validation and settings management

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Shadcn/UI** - Accessible component library
- **React Query** - Server state management

### MCP Integrations
- **Database MCP** - Contract and clause storage
- **Document Store MCP** - File storage and retrieval
- **Legal Database MCP** - Legal precedent lookup
- **Template MCP** - Standard contract templates

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)

### 1. Clone the repository
```bash
git clone https://github.com/VaibhavJeet/contract-analysis-agent.git
cd contract-analysis-agent
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Configuration

### LLM Configuration

#### Remote LLM (OpenAI, Anthropic)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Local LLM (Ollama)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Features

### Contract Parsing
- Multi-format support (PDF, DOCX, TXT)
- OCR for scanned documents
- Structured data extraction
- Metadata identification

### Clause Extraction
- Automatic clause identification
- Clause type classification
- Key term extraction
- Cross-reference detection

### Risk Analysis
- Risk scoring per clause
- Industry-specific risk factors
- Compliance checking
- Unusual term detection

### Amendment Generation
- Suggested clause modifications
- Alternative language proposals
- Negotiation point identification

## API Reference

### Contracts
- `POST /api/contracts` - Upload and parse contract
- `GET /api/contracts` - List all contracts
- `GET /api/contracts/{id}` - Get contract details
- `POST /api/contracts/{id}/analyze` - Run full analysis

### Clauses
- `GET /api/contracts/{id}/clauses` - Get extracted clauses
- `POST /api/clauses/{id}/assess-risk` - Assess clause risk

### Amendments
- `POST /api/contracts/{id}/amendments` - Generate amendments
- `GET /api/amendments` - List all amendments

## Project Structure

```
contract-analysis-agent/
├── backend/
│   ├── app/
│   │   ├── agents/           # LangChain agents
│   │   │   ├── document_parser.py
│   │   │   ├── clause_extractor.py
│   │   │   ├── risk_analyzer.py
│   │   │   └── amendment_generator.py
│   │   ├── chains/           # LangChain chains
│   │   ├── tools/            # Custom tools
│   │   ├── mcp/              # MCP integrations
│   │   ├── models/           # Pydantic models
│   │   ├── api/              # FastAPI routes
│   │   └── core/             # Configuration
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   └── package.json
├── config/
│   └── mcp.yaml
└── docker-compose.yml
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [LangChain](https://langchain.com) for the agent framework
- [Model Context Protocol](https://modelcontextprotocol.io) for integration standards
- [Anthropic](https://anthropic.com) for Claude and MCP specification
