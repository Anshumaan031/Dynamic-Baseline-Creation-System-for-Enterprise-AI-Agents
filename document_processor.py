"""
Document Processor for AI Control Tower

This module handles document processing for various formats including PDF, TXT, and DOCX.
It extracts text content for analysis by the baseline generation agent.
"""

import os
import re
from typing import Dict, Any, Optional
import PyPDF2
from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from PDF files.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        # Try with pypdf first (more modern)
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        try:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e2:
            print(f"Error extracting PDF content: {e2}")
            return ""

def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text content from TXT files.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from DOCX files (basic implementation).
    Note: This is a simplified implementation. For production use, consider python-docx.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text content (basic)
    """
    try:
        # For now, return a message that DOCX support is limited
        return f"DOCX file detected: {file_path}. Full DOCX support requires python-docx package."
    except Exception as e:
        print(f"Error processing DOCX file: {e}")
        return ""

def process_document(file_path: str) -> Dict[str, Any]:
    """
    Process a document file and extract its content.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary containing document metadata and extracted content
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "content": "",
            "metadata": {}
        }
    
    file_ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    content = ""
    
    if file_ext == ".pdf":
        content = extract_text_from_pdf(file_path)
    elif file_ext == ".txt":
        content = extract_text_from_txt(file_path)
    elif file_ext == ".docx":
        content = extract_text_from_docx(file_path)
    elif file_ext == ".md":
        content = extract_text_from_txt(file_path)  # Markdown files are text files
    else:
        return {
            "success": False,
            "error": f"Unsupported file format: {file_ext}",
            "content": "",
            "metadata": {}
        }
    
    # Basic content analysis
    word_count = len(content.split()) if content else 0
    char_count = len(content) if content else 0
    
    return {
        "success": True,
        "error": None,
        "content": content,
        "metadata": {
            "file_name": file_name,
            "file_path": file_path,
            "file_extension": file_ext,
            "file_size_bytes": file_size,
            "word_count": word_count,
            "character_count": char_count,
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
    }

def extract_agent_specifications(content: str) -> Dict[str, Any]:
    """
    Extract key agent specifications from document content using pattern matching.
    
    Args:
        content: Document content as string
        
    Returns:
        Dictionary containing extracted specifications
    """
    specs = {
        "capabilities": [],
        "tools": [],
        "performance_targets": [],
        "constraints": [],
        "use_case_info": {},
        "domain_info": {}
    }
    
    content_lower = content.lower()
    
    # Extract capabilities (look for capability patterns)
    capability_patterns = [
        r"capabilit(?:y|ies):\s*([^.]*)",
        r"can\s+([\w\s,]+?)(?:\.|;|\n)",
        r"able to\s+([\w\s,]+?)(?:\.|;|\n)",
        r"supports?\s+([\w\s,]+?)(?:\.|;|\n)"
    ]
    
    for pattern in capability_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE)
        for match in matches:
            capability = match.group(1).strip()
            if capability and len(capability) > 3:
                specs["capabilities"].append(capability)
    
    # Extract tools (look for tool patterns)
    tool_patterns = [
        r"tools?:\s*([^.]*)",
        r"uses?\s+([\w\s]+(?:api|system|tool|service))",
        r"integrat(?:es?|ion)\s+with\s+([\w\s,]+?)(?:\.|;|\n)"
    ]
    
    for pattern in tool_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE)
        for match in matches:
            tool = match.group(1).strip()
            if tool and len(tool) > 3:
                specs["tools"].append(tool)
    
    # Extract performance targets (look for percentage and number patterns)
    performance_patterns = [
        r"(\d+)%\s+(?:of|resolution|accuracy|satisfaction)",
        r"(?:target|goal|expect)[\w\s]*?:?\s*(\d+)%",
        r"(\d+)%\s+(?:first contact|escalation|success)",
        r"(?:within|under|less than)\s+(\d+)\s+(?:minutes?|seconds?|hours?)"
    ]
    
    for pattern in performance_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE)
        for match in matches:
            target = match.group(0).strip()
            if target:
                specs["performance_targets"].append(target)
    
    # Extract complexity indicators
    if any(word in content_lower for word in ["simple", "basic", "routine"]):
        specs["use_case_info"]["complexity"] = "simple"
    elif any(word in content_lower for word in ["complex", "advanced", "sophisticated"]):
        specs["use_case_info"]["complexity"] = "complex"
    elif any(word in content_lower for word in ["specialized", "expert", "technical"]):
        specs["use_case_info"]["complexity"] = "highly_specialized"
    else:
        specs["use_case_info"]["complexity"] = "moderate"
    
    # Extract domain maturity indicators
    if any(word in content_lower for word in ["established", "mature", "stable", "proven"]):
        specs["domain_info"]["maturity"] = "stable"
    elif any(word in content_lower for word in ["new", "novel", "emerging", "experimental"]):
        specs["domain_info"]["maturity"] = "new"
    else:
        specs["domain_info"]["maturity"] = "evolving"
    
    # Clean up extracted data (remove duplicates and empty items)
    for key in ["capabilities", "tools", "performance_targets", "constraints"]:
        specs[key] = list(set([item for item in specs[key] if item and len(item.strip()) > 3]))
    
    return specs

def process_document_for_baseline_analysis(file_path: str) -> Dict[str, Any]:
    """
    Process a document specifically for baseline analysis.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary containing processed content and extracted specifications
    """
    # First, extract the raw content
    doc_result = process_document(file_path)
    
    if not doc_result["success"]:
        return doc_result
    
    content = doc_result["content"]
    
    # Extract agent specifications
    specifications = extract_agent_specifications(content)
    
    # Combine results
    return {
        "success": True,
        "error": None,
        "raw_content": content,
        "metadata": doc_result["metadata"],
        "extracted_specifications": specifications,
        "analysis_summary": {
            "total_capabilities": len(specifications["capabilities"]),
            "total_tools": len(specifications["tools"]),
            "total_performance_targets": len(specifications["performance_targets"]),
            "complexity_assessment": specifications["use_case_info"].get("complexity", "moderate"),
            "domain_maturity": specifications["domain_info"].get("maturity", "evolving")
        }
    }

# Example usage and testing
if __name__ == "__main__":
    # Test with sample content
    sample_content = """
    Customer Service Agent Documentation:
    
    Purpose: Handle customer inquiries for e-commerce platform
    
    Capabilities:
    - Order status checking
    - Product recommendations  
    - Basic troubleshooting
    - Account management
    
    Tools:
    - Order management system API
    - Product catalog search tool
    - Knowledge base retrieval system
    - Email notification service
    
    Performance Targets:
    - 80% first contact resolution
    - 90% customer satisfaction
    - Response time under 30 seconds
    - Handle complex technical issues
    
    This agent operates in a stable e-commerce domain with established processes.
    """
    
    print("Testing specification extraction:")
    specs = extract_agent_specifications(sample_content)
    
    print(f"\nCapabilities ({len(specs['capabilities'])}):")
    for cap in specs['capabilities']:
        print(f"  • {cap}")
    
    print(f"\nTools ({len(specs['tools'])}):")
    for tool in specs['tools']:
        print(f"  • {tool}")
    
    print(f"\nPerformance Targets ({len(specs['performance_targets'])}):")
    for target in specs['performance_targets']:
        print(f"  • {target}")
    
    print(f"\nComplexity: {specs['use_case_info'].get('complexity', 'unknown')}")
    print(f"Domain Maturity: {specs['domain_info'].get('maturity', 'unknown')}")