# LexiGuard – AI Legal Risk & Compliance Reasoning Engine

LexiGuard is an **AI-powered legal intelligence web application** designed to automate **contract analysis, compliance risk detection, and remediation planning** using the advanced reasoning capabilities of **Google Gemini**. Unlike traditional rule-based compliance tools, LexiGuard performs **deep semantic, cross-regulatory legal reasoning** to uncover hidden risks, violations, gaps, and contradictions in legal documents.

---

## Project Overview

LexiGuard enables users to upload legal documents (PDF, DOCX, TXT) and automatically analyzes them against major regulatory frameworks such as **GDPR, HIPAA, CCPA, SOC 2, and PCI-DSS**. The system goes beyond keyword matching by understanding legal intent, obligations, and implicit assumptions embedded within clauses.

By leveraging Gemini as a **legal reasoning engine**, LexiGuard delivers enterprise-grade compliance intelligence suitable for real-world legal and regulatory environments.

---

## Core Capabilities

- Semantic clause extraction with legal context
- Cross-regulatory compliance reasoning
- Detection of direct violations, partial compliance, and missing clauses
- Identification of contradictory obligations
- Severity-based risk classification
- Regulation-to-clause mapping
- Audience-specific explanations (Executive, Engineer, Legal)
- Automated remediation roadmap generation
- Risk visualization through heatmap-ready data

---

## How LexiGuard Works

1. **Document Upload**
   - Users upload legal documents (PDF, DOCX, TXT)
   - Text is automatically extracted and stored

2. **Semantic Clause Extraction**
   - Gemini identifies clause types, obligations, risks, and assumptions
   - Clauses are structured into machine-readable JSON

3. **Compliance Reasoning**
   - Clauses are evaluated against selected regulations
   - Violations, gaps, conflicts, and partial compliance are detected
   - Severity levels and legal reasoning are assigned

4. **Risk Visualization & Explanation**
   - Risk distribution data is generated for heatmaps
   - Risks can be explained for different audiences

5. **Remediation Planning**
   - A prioritized, actionable compliance roadmap is generated
   - Includes timelines, responsibilities, and success criteria

---

## Technologies Used

- Python  
- Flask  
- Google Gemini API  
- Natural Language Processing (NLP)  
- Legal Reasoning with LLMs  
- PyPDF2  
- python-docx  
- Markdown Processing  
- HTML / CSS / JavaScript  

---

## Skills Demonstrated

- Applied AI & Machine Learning  
- LLM-based Reasoning Systems  
- Legal and Regulatory Compliance Analysis  
- Prompt Engineering  
- Backend API Development  
- AI-powered Decision Support Systems  

---

## Repository Structure
```text
LexiGuard-AI-Legal-Risk-Compliance-Reasoning-Engine/
├── app.py
├── templates/
│ └── index.html
└── README.md
```

---

## Supported Regulations

- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- CCPA (California Consumer Privacy Act)
- SOC 2
- PCI-DSS

---

## How to Run

1. Install Python 3.x
2. Install dependencies:
pip install flask flask-cors python-dotenv google-generativeai pypdf2 python-docx markdown2
3. Set your Gemini API key in a `.env` file:
API_KEY=your_gemini_api_key
4. Run the application:
python app.py
5. Open your browser at:
http://localhost:5000
---

## Purpose

LexiGuard demonstrates how **large language models can be used as reasoning engines**, not just text generators, to deliver **real-world, enterprise-grade legal compliance intelligence**.

---

## License

This project is open-source and intended for educational, research, and portfolio use.









