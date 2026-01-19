# GreenTrust AI - Project Structure

```
GreenTrust_Ai/
│
├── 📄 Core Files
│   ├── pyproject.toml          # Modern Python project config (uv-compatible)
│   ├── README.md                # Complete project documentation
│   ├── QUICKSTART.md            # 3-command setup guide
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── .env                     # Environment variables (API keys)
│   ├── .env.example             # Environment template
│   ├── .gitignore               # Git ignore rules (uv-aware)
│   ├── config.py                # Configuration settings
│   ├── demo_config.py           # Demo mode flag
│   └── llm_providers.py         # Multi-provider LLM abstraction (Groq/Gemini/OpenAI)
│
├── 🤖 Multi-Agent System
│   └── agents/
│       ├── __init__.py
│       ├── state.py             # Pydantic state models
│       ├── extraction_agent.py  # PDF parsing + LLM/regex extraction
│       ├── verification_agent.py # Benchmark comparison
│       ├── compliance_agent.py  # SEBI BRSR evaluation
│       ├── workflow.py          # LangGraph orchestration
│       └── regex_extractor.py   # Fallback extraction (no API)
│
├── 📚 Knowledge Base
│   └── knowledge_base/
│       ├── __init__.py
│       ├── sebi_brsr_standards.md  # SEBI Principle 6 requirements
│       └── logistics_api.py         # Mock emissions benchmarks
│
├── 🛠️ Utilities
│   └── utils/
│       ├── __init__.py
│       ├── currency_converter.py   # EUR/USD/GBP → INR
│       └── risk_assessment.py      # Regional risk scoring
│
├── 📊 Evaluation
│   └── evaluation/
│       ├── __init__.py
│       └── ragas_setup.py          # RAGAS framework
│
├── 📁 Sample Data
│   └── data_samples/
│       ├── README.md
│       ├── valid_invoice.pdf
│       ├── suspicious_invoice.pdf
│       ├── edge_case_missing_date.pdf
│       ├── edge_case_eur_currency.pdf
│       ├── edge_case_high_risk_region.pdf
│       ├── edge_case_multimodal.pdf
│       └── edge_case_zero_emissions.pdf
│
├── 🖥️ Applications
│   ├── app.py                   # Streamlit dashboard (main UI)
│   ├── main.py                  # CLI interface
│   ├── run_demo.py              # Demo mode (no API key)
│   └── test_workflow.py         # System tests
│
├── 🏭 Generators
│   ├── generate_pdfs.py         # Generate valid/suspicious PDFs
│   └── generate_edge_cases.py  # Generate 5 edge case PDFs
│
├── 📦 UV Package Manager
│   ├── .venv/                   # Virtual environment (uv-managed)
│   └── uv.lock                  # Dependency lock file
│
└── 📤 Output
    └── output/                  # Audit results (JSON)
```

## 📊 File Count

| Category | Count |
|----------|-------|
| Python files | 21 |
| Configuration | 6 |
| Documentation | 4 |
| Sample PDFs | 10 |
| **Total** | **41** |

## 🎯 Key Directories

### `agents/` - Multi-Agent System (7 files)
The core AI system with extraction, verification, compliance, and human review agents.

### `knowledge_base/` - Domain Knowledge (2 files)
SEBI BRSR standards and logistics emission benchmarks.

### `utils/` - Utilities (3 files)
Currency conversion and risk assessment helpers.

### `data_samples/` - Test Data (7 PDFs)
Valid, suspicious, and edge case invoices for testing.

## 🚀 Entry Points

1. **`app.py`** - Streamlit dashboard (recommended)
2. **`main.py`** - Command-line interface
3. **`run_demo.py`** - Demo mode without API key

## 📦 Dependencies (via uv)

Installed with: `uv pip install langgraph langchain langchain-openai langchain-groq langchain-google-genai pydantic pymupdf ragas python-dotenv openai reportlab streamlit plotly`

- **LangGraph** - Multi-agent orchestration
- **LangChain** - LLM framework (OpenAI, Groq, Gemini)
- **Pydantic** - Data validation
- **PyMuPDF** - PDF parsing
- **Streamlit** - Dashboard UI
- **Plotly** - Gauge charts
- **ReportLab** - PDF generation

## 🎨 Modern Features

✅ **UV Package Manager** - 10-100x faster than pip  
✅ **pyproject.toml** - Single source of truth  
✅ **Multi-Provider LLM** - Groq (free), Gemini, OpenAI with auto-fallback  
✅ **Flat Structure** - No src/ directory needed  
✅ **Type-Safe** - Pydantic v2 models  
✅ **Modular** - Clean separation of concerns  

## 🏆 Competition Ready!

Total project size: **41 files** across **9 directories**
