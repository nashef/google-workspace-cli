"""Google Docs API operations for Phase 1."""

import json
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache
from googleapiclient.discovery import build, Resource

from ..shared.auth import get_credentials


# Define Docs API scopes
DOCS_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


@lru_cache(maxsize=1)
def build_docs_service() -> Resource:
    """Build Docs API service with caching."""
    creds = get_credentials(scopes=DOCS_SCOPES)
    return build("docs", "v1", credentials=creds)


def get_docs_service():
    """Get authenticated Docs API service."""
    return build_docs_service()


# ============================================================================
# Phase 1: Core Document Operations
# ============================================================================


def create_document(title: str = "Untitled Document") -> str:
    """Create a new blank document.

    Args:
        title: Document title

    Returns:
        Document ID
    """
    service = get_docs_service()

    document = {"title": title}

    result = service.documents().create(body=document).execute()

    return result.get("documentId", "")


def get_document(document_id: str) -> Dict[str, Any]:
    """Get document metadata and content.

    Args:
        document_id: Document ID

    Returns:
        Document object with full content and metadata
    """
    service = get_docs_service()

    result = service.documents().get(documentId=document_id).execute()

    return result


def get_document_title(document_id: str) -> str:
    """Get just the document title.

    Args:
        document_id: Document ID

    Returns:
        Document title
    """
    doc = get_document(document_id)
    return doc.get("title", "Untitled")


def extract_text(document_id: str) -> str:
    """Extract all text content from a document.

    Recursively extracts text from all structural elements,
    preserving basic structure with newlines.

    Args:
        document_id: Document ID

    Returns:
        Plain text content
    """
    doc = get_document(document_id)
    text_parts = []

    # Get the document body
    body = doc.get("body", {})
    content = body.get("content", [])

    # Recursively extract text from structural elements
    _extract_text_from_elements(content, text_parts)

    return "".join(text_parts)


def _extract_text_from_elements(elements: List[Dict[str, Any]], text_parts: List[str]):
    """Recursively extract text from structural elements.

    Args:
        elements: List of StructuralElement dicts
        text_parts: List to append text fragments to
    """
    for element in elements:
        if "paragraph" in element:
            paragraph = element["paragraph"]
            _extract_text_from_paragraph(paragraph, text_parts)
            text_parts.append("\n")
        elif "table" in element:
            table = element["table"]
            _extract_text_from_table(table, text_parts)
            text_parts.append("\n")
        elif "tableOfContents" in element:
            text_parts.append("[Table of Contents]\n")
        elif "horizontalRule" in element:
            text_parts.append("---\n")


def _extract_text_from_paragraph(paragraph: Dict[str, Any], text_parts: List[str]):
    """Extract text from a paragraph.

    Args:
        paragraph: Paragraph dict
        text_parts: List to append text fragments to
    """
    elements = paragraph.get("elements", [])
    for element in elements:
        if "textRun" in element:
            text_parts.append(element["textRun"].get("content", ""))
        elif "inlineObjectElement" in element:
            text_parts.append("[Image]")
        elif "autoText" in element:
            text_parts.append("[AutoText]")
        elif "pageBreak" in element:
            text_parts.append("\n[Page Break]\n")


def _extract_text_from_table(table: Dict[str, Any], text_parts: List[str]):
    """Extract text from a table.

    Args:
        table: Table dict
        text_parts: List to append text fragments to
    """
    rows = table.get("tableRows", [])
    for row in rows:
        cells = row.get("tableCells", [])
        cell_texts = []
        for cell in cells:
            cell_content = cell.get("content", [])
            cell_text_parts = []
            _extract_text_from_elements(cell_content, cell_text_parts)
            cell_texts.append("".join(cell_text_parts).strip())
        text_parts.append(" | ".join(cell_texts))
        text_parts.append("\n")


def get_document_stats(document_id: str) -> Dict[str, Any]:
    """Get document statistics.

    Args:
        document_id: Document ID

    Returns:
        Dict with title, character count, word count, paragraph count
    """
    doc = get_document(document_id)
    text = extract_text(document_id)

    title = doc.get("title", "Untitled")
    char_count = len(text)
    word_count = len(text.split())

    # Count paragraphs
    body = doc.get("body", {})
    content = body.get("content", [])
    paragraph_count = sum(1 for elem in content if "paragraph" in elem)
    table_count = sum(1 for elem in content if "table" in elem)

    return {
        "title": title,
        "document_id": document_id,
        "character_count": char_count,
        "word_count": word_count,
        "paragraph_count": paragraph_count,
        "table_count": table_count,
    }


def get_document_structure(document_id: str) -> Dict[str, Any]:
    """Get document structure overview.

    Returns a hierarchical view of the document structure.

    Args:
        document_id: Document ID

    Returns:
        Dict with document structure
    """
    doc = get_document(document_id)

    structure = {
        "title": doc.get("title", "Untitled"),
        "document_id": document_id,
        "revision_id": doc.get("revisionId", ""),
        "elements": _parse_structure(doc.get("body", {}).get("content", [])),
    }

    return structure


def _parse_structure(elements: List[Dict[str, Any]], indent: int = 0) -> List[Dict[str, Any]]:
    """Parse document structure recursively.

    Args:
        elements: List of StructuralElement dicts
        indent: Indentation level

    Returns:
        List of parsed structure elements
    """
    structure = []

    for element in elements:
        if "paragraph" in element:
            para = element["paragraph"]
            style = para.get("paragraphStyle", {})
            heading_id = para.get("paragraphStyle", {}).get("headingId")

            element_count = len(para.get("elements", []))
            structure.append({
                "type": "paragraph",
                "style": style.get("namedStyleType", "NORMAL_TEXT"),
                "heading_id": heading_id,
                "element_count": element_count,
                "indent": indent,
            })

        elif "table" in element:
            table = element["table"]
            rows = table.get("tableRows", [])
            row_count = len(rows)
            col_count = 0
            if rows:
                col_count = len(rows[0].get("tableCells", []))

            structure.append({
                "type": "table",
                "rows": row_count,
                "columns": col_count,
                "indent": indent,
            })

        elif "tableOfContents" in element:
            structure.append({
                "type": "table_of_contents",
                "indent": indent,
            })

        elif "horizontalRule" in element:
            structure.append({
                "type": "horizontal_rule",
                "indent": indent,
            })

        elif "pageBreak" in element:
            structure.append({
                "type": "page_break",
                "indent": indent,
            })

    return structure


def export_document_as_text(document_id: str) -> str:
    """Export document as plain text.

    Args:
        document_id: Document ID

    Returns:
        Plain text content with title
    """
    doc = get_document(document_id)
    title = doc.get("title", "Untitled")
    text = extract_text(document_id)

    return f"# {title}\n\n{text}"


def export_document_as_json(document_id: str) -> str:
    """Export document as JSON.

    Args:
        document_id: Document ID

    Returns:
        JSON string with document content
    """
    doc = get_document(document_id)
    return json.dumps(doc, indent=2)


def export_document_as_markdown(document_id: str) -> str:
    """Export document as Markdown.

    Basic markdown conversion preserving headings, paragraphs, and tables.

    Args:
        document_id: Document ID

    Returns:
        Markdown formatted content
    """
    doc = get_document(document_id)
    title = doc.get("title", "Untitled")
    body = doc.get("body", {})
    content = body.get("content", [])

    md_parts = [f"# {title}\n"]

    for element in content:
        if "paragraph" in element:
            para = element["paragraph"]
            style = para.get("paragraphStyle", {})
            named_style = style.get("namedStyleType", "NORMAL_TEXT")

            text = _extract_paragraph_text(para)

            # Add heading level based on style
            if named_style == "HEADING_1":
                md_parts.append(f"## {text}\n")
            elif named_style == "HEADING_2":
                md_parts.append(f"### {text}\n")
            elif named_style == "HEADING_3":
                md_parts.append(f"#### {text}\n")
            elif named_style.startswith("HEADING"):
                md_parts.append(f"##### {text}\n")
            else:
                if text.strip():
                    md_parts.append(f"{text}\n\n")

        elif "table" in element:
            table = element["table"]
            md_parts.append(_table_to_markdown(table))

        elif "horizontalRule" in element:
            md_parts.append("---\n\n")

    return "".join(md_parts)


def _extract_paragraph_text(paragraph: Dict[str, Any]) -> str:
    """Extract text from a paragraph element."""
    parts = []
    elements = paragraph.get("elements", [])
    for elem in elements:
        if "textRun" in elem:
            parts.append(elem["textRun"].get("content", ""))
        elif "inlineObjectElement" in elem:
            parts.append("[Image]")
    return "".join(parts)


def _table_to_markdown(table: Dict[str, Any]) -> str:
    """Convert table to Markdown format."""
    rows = table.get("tableRows", [])
    md_lines = []

    for i, row in enumerate(rows):
        cells = row.get("tableCells", [])
        cell_texts = []

        for cell in cells:
            cell_content = cell.get("content", [])
            text_parts = []
            for elem in cell_content:
                if "paragraph" in elem:
                    text_parts.append(_extract_paragraph_text(elem["paragraph"]))
            cell_texts.append("".join(text_parts).strip())

        md_lines.append("| " + " | ".join(cell_texts) + " |")

        # Add header separator after first row
        if i == 0:
            separators = ["-" * max(3, len(text)) for text in cell_texts]
            md_lines.append("|" + "|".join(separators) + "|")

    return "\n".join(md_lines) + "\n\n"


def format_document_for_display(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Format document metadata for display.

    Args:
        doc: Document dict from API

    Returns:
        Formatted dict for output
    """
    formatted = {
        "id": doc.get("documentId"),
        "title": doc.get("title"),
        "revision_id": doc.get("revisionId"),
        "mime_type": doc.get("mimeType"),
    }
    return formatted
