import os
import json
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import markdown2
from markupsafe import Markup
import PyPDF2
import docx
from io import BytesIO

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)
CORS(app)

# In-memory storage for demo purposes
documents_db = {}
analysis_cache = {}

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_file(file):
    """Extract text based on file type"""
    filename = file.filename.lower()
    file_bytes = file.read()
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith('.txt'):
        return file_bytes.decode('utf-8')
    else:
        return "Unsupported file format"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload and process legal documents"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        doc_type = request.form.get('doc_type', 'contract')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Extract text from document
        text_content = extract_text_from_file(file)
        
        if text_content.startswith("Error"):
            return jsonify({"error": text_content}), 400
        
        # Generate document ID
        doc_id = f"doc_{len(documents_db) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Store document
        documents_db[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "doc_type": doc_type,
            "content": text_content,
            "upload_time": datetime.now().isoformat(),
            "processed": False
        }
        
        return jsonify({
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "message": "Document uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract-clauses', methods=['POST'])
def extract_clauses():
    """Extract and classify semantic clauses from document"""
    try:
        data = request.json
        doc_id = data.get('doc_id')
        
        if doc_id not in documents_db:
            return jsonify({"error": "Document not found"}), 404
        
        document = documents_db[doc_id]
        
        prompt = f"""You are a senior legal analyst with expertise in contract law and regulatory compliance.

Analyze the following legal document and extract ALL distinct clauses with precise semantic understanding.

Document Type: {document['doc_type']}
Document Content:
{document['content'][:15000]}

For EACH clause, provide:
1. **Clause Type** (e.g., Data Retention, Liability, Termination, Data Handling, Consent, Jurisdiction, Payment, Indemnification, Confidentiality, etc.)
2. **Clause Text** (exact text or summary)
3. **Risk Potential** (Low, Medium, High, Critical) - based on common legal risks
4. **Key Obligations** - what this clause requires
5. **Implicit Assumptions** - unstated but implied requirements

Return your analysis in valid JSON format:
{{
  "clauses": [
    {{
      "clause_id": "C1",
      "clause_type": "Data Retention",
      "text": "exact clause text...",
      "risk_potential": "High",
      "key_obligations": ["obligation 1", "obligation 2"],
      "implicit_assumptions": ["assumption 1"],
      "location": "Section 4.2"
    }}
  ],
  "summary": "Brief overview of document structure"
}}

Be thorough and extract ALL meaningful clauses. Use precise legal language."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON from markdown code blocks
        if response_text.startswith("```"):
            response_text = re.sub(r'^```json\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        
        result = json.loads(response_text)
        
        # Cache the analysis
        analysis_cache[doc_id] = result
        documents_db[doc_id]['processed'] = True
        
        return jsonify({
            "success": True,
            "doc_id": doc_id,
            "clauses": result.get("clauses", []),
            "summary": result.get("summary", "")
        })
        
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {str(e)}", "raw_response": response_text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-compliance', methods=['POST'])
def analyze_compliance():
    """Perform deep compliance analysis across regulations"""
    try:
        data = request.json
        doc_id = data.get('doc_id')
        regulations = data.get('regulations', ['GDPR', 'HIPAA', 'CCPA'])
        
        if doc_id not in documents_db:
            return jsonify({"error": "Document not found"}), 404
        
        if doc_id not in analysis_cache:
            return jsonify({"error": "Please extract clauses first"}), 400
        
        document = documents_db[doc_id]
        clauses_data = analysis_cache[doc_id]
        
        regulations_context = {
            "GDPR": "EU General Data Protection Regulation - focuses on data subject rights, consent, data minimization, retention limits, right to erasure, breach notification",
            "HIPAA": "Health Insurance Portability and Accountability Act - protects health information privacy, requires security safeguards, breach notification",
            "CCPA": "California Consumer Privacy Act - consumer rights to know, delete, opt-out of data sales",
            "SOC2": "System and Organization Controls 2 - security, availability, processing integrity, confidentiality, privacy",
            "PCI-DSS": "Payment Card Industry Data Security Standard - protect cardholder data, secure networks, access control"
        }
        
        selected_regs = {reg: regulations_context.get(reg, reg) for reg in regulations}
        
        prompt = f"""You are an expert legal compliance analyst specializing in regulatory risk assessment.

Perform comprehensive compliance analysis for the following document against specified regulations.

Document: {document['filename']}
Extracted Clauses Analysis:
{json.dumps(clauses_data, indent=2)}

Regulations to Check:
{json.dumps(selected_regs, indent=2)}

Perform deep legal reasoning to identify:

1. **Direct Violations** - clauses that explicitly violate regulations
2. **Partial Compliance** - clauses that partially meet requirements but have gaps
3. **Missing Clauses** - required clauses absent from the document
4. **Contradictory Obligations** - internal conflicts or cross-regulation conflicts
5. **Regulatory Mapping** - map each clause to relevant regulation articles

For EACH issue found, provide:
- **Issue Type** (violation, gap, conflict, partial)
- **Severity** (Low, Medium, High, Critical)
- **Affected Clause** (clause_id and text)
- **Regulation** (which regulation and specific article)
- **Legal Reasoning** (explain WHY this is a problem using legal principles)
- **Penalty Exposure** (potential consequences)
- **Remediation** (specific actionable fix)

Return analysis in valid JSON:
{{
  "compliance_score": 0-100,
  "total_issues": number,
  "issues": [
    {{
      "issue_id": "I1",
      "issue_type": "violation",
      "severity": "Critical",
      "affected_clause_id": "C1",
      "clause_text": "...",
      "regulation": "GDPR Article 17",
      "legal_reasoning": "This clause permits indefinite data storage, which directly conflicts with GDPR Article 5(1)(e) requiring data minimization and storage limitation. Under GDPR, personal data must not be kept longer than necessary.",
      "penalty_exposure": "Up to €20 million or 4% of annual global turnover",
      "remediation": "Introduce maximum retention period of 24 months with documented justification"
    }}
  ],
  "regulation_coverage": {{}},
  "risk_summary": "Executive summary"
}}

Use precise legal reasoning. Ground all findings in provided text."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = re.sub(r'^```json\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        
        result = json.loads(response_text)
        
        # Cache compliance analysis
        analysis_cache[f"{doc_id}_compliance"] = result
        
        return jsonify({
            "success": True,
            "doc_id": doc_id,
            "analysis": result
        })
        
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {str(e)}", "raw_response": response_text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/risk-heatmap', methods=['POST'])
def generate_risk_heatmap():
    """Generate visual risk heatmap data"""
    try:
        data = request.json
        doc_id = data.get('doc_id')
        
        compliance_key = f"{doc_id}_compliance"
        if compliance_key not in analysis_cache:
            return jsonify({"error": "No compliance analysis found"}), 404
        
        compliance_data = analysis_cache[compliance_key]
        issues = compliance_data.get("issues", [])
        
        # Group by severity
        severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        regulation_risks = {}
        clause_risks = {}
        
        for issue in issues:
            severity = issue.get("severity", "Medium")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            regulation = issue.get("regulation", "Unknown")
            regulation_risks[regulation] = regulation_risks.get(regulation, 0) + 1
            
            clause_id = issue.get("affected_clause_id", "Unknown")
            clause_risks[clause_id] = clause_risks.get(clause_id, [])
            clause_risks[clause_id].append({
                "severity": severity,
                "issue_type": issue.get("issue_type")
            })
        
        return jsonify({
            "success": True,
            "heatmap_data": {
                "severity_distribution": severity_counts,
                "regulation_risks": regulation_risks,
                "clause_risks": clause_risks,
                "total_issues": len(issues)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/explain-risk', methods=['POST'])
def explain_risk():
    """Generate human-readable explanation for specific risk"""
    try:
        data = request.json
        issue_id = data.get('issue_id')
        doc_id = data.get('doc_id')
        audience = data.get('audience', 'executive')  # executive, engineer, legal
        
        compliance_key = f"{doc_id}_compliance"
        if compliance_key not in analysis_cache:
            return jsonify({"error": "No compliance analysis found"}), 404
        
        compliance_data = analysis_cache[compliance_key]
        issues = compliance_data.get("issues", [])
        
        target_issue = None
        for issue in issues:
            if issue.get("issue_id") == issue_id:
                target_issue = issue
                break
        
        if not target_issue:
            return jsonify({"error": "Issue not found"}), 404
        
        audience_instructions = {
            "executive": "Explain in business terms focusing on financial and reputational impact. Avoid legal jargon. Use clear, actionable language.",
            "engineer": "Explain in technical terms focusing on implementation requirements and system changes needed. Be specific about what needs to be built or modified.",
            "legal": "Provide comprehensive legal analysis with case law references, regulatory interpretations, and detailed compliance requirements."
        }
        
        prompt = f"""You are translating a legal compliance issue for a {audience} audience.

Issue Details:
{json.dumps(target_issue, indent=2)}

{audience_instructions.get(audience, '')}

Provide a clear, well-structured explanation covering:
1. **What's the Problem?** - in plain language
2. **Why Does It Matter?** - real-world implications
3. **What Happens If Not Fixed?** - specific consequences
4. **How to Fix It?** - actionable steps

Use markdown formatting with **bold** for emphasis and bullet points for clarity.
Make it sound like advice from a trusted advisor, not a robot."""

        response = model.generate_content(prompt)
        html_response = markdown2.markdown(
            response.text,
            extras=["fenced-code-blocks", "tables", "strike", "cuddled-lists"]
        )
        
        return jsonify({
            "success": True,
            "explanation": html_response,
            "issue": target_issue
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    docs = [
        {
            "id": doc_id,
            "filename": doc["filename"],
            "doc_type": doc["doc_type"],
            "upload_time": doc["upload_time"],
            "processed": doc["processed"]
        }
        for doc_id, doc in documents_db.items()
    ]
    return jsonify({"documents": docs})

@app.route('/api/remediation-plan', methods=['POST'])
def generate_remediation_plan():
    """Generate comprehensive remediation plan"""
    try:
        data = request.json
        doc_id = data.get('doc_id')
        
        compliance_key = f"{doc_id}_compliance"
        if compliance_key not in analysis_cache:
            return jsonify({"error": "No compliance analysis found"}), 404
        
        compliance_data = analysis_cache[compliance_key]
        
        prompt = f"""You are a legal operations strategist creating an actionable remediation plan.

Based on this compliance analysis:
{json.dumps(compliance_data, indent=2)[:10000]}

Create a prioritized remediation roadmap that includes:

1. **Immediate Actions** (Critical severity - do within 7 days)
2. **Short-term Fixes** (High severity - do within 30 days)
3. **Medium-term Improvements** (Medium severity - do within 90 days)
4. **Long-term Enhancements** (Low severity - continuous improvement)

For EACH recommendation:
- **Action Title** - clear, specific task
- **Detailed Steps** - how to implement
- **Responsible Party** - who should do this (Legal, Engineering, Compliance, etc.)
- **Estimated Effort** - time/resources required
- **Dependencies** - what needs to happen first
- **Success Criteria** - how to verify completion

Return as valid JSON:
{{
  "plan_summary": "Executive overview",
  "immediate_actions": [],
  "short_term": [],
  "medium_term": [],
  "long_term": [],
  "estimated_timeline": "X weeks",
  "total_actions": number
}}

Make recommendations specific and actionable, not generic advice."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = re.sub(r'^```json\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        
        result = json.loads(response_text)
        
        return jsonify({
            "success": True,
            "remediation_plan": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)