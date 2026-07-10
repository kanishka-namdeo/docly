import pytest
from pathlib import Path
from app.ingestion.parsers.base import BaseParser
from app.ingestion.parsers.markdown import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    content = "# Title\n\nThis is a paragraph.\n\n## Section\n\nAnother paragraph."
    result = parser.parse(content)
    
    assert result["text"] is not None
    assert len(result["text"]) > 0
    assert "Title" in result["text"]
    assert "paragraph" in result["text"]

def test_markdown_parser_preserves_structure():
    parser = MarkdownParser()
    content = "# Main Title\n\nContent here.\n\n## Subsection\n\nMore content."
    result = parser.parse(content)
    
    assert result["metadata"]["has_headings"] is True
