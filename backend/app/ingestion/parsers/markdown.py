import re
from app.ingestion.parsers.base import BaseParser

class MarkdownParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        
        # Extract headings
        headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        
        # Clean markdown syntax for text extraction
        text = content
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)  # Remove heading markers
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Remove bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # Remove italic
        text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # Remove links, keep text
        
        return {
            "text": text.strip(),
            "metadata": {
                "has_headings": len(headings) > 0,
                "heading_count": len(headings),
                "headings": headings
            },
            "elements": []
        }
