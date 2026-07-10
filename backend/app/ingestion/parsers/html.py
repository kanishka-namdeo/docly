try:
    from unstructured.partition.html import partition_html
    HAS_UNSTRUCTURED_HTML = True
except ImportError:
    HAS_UNSTRUCTURED_HTML = False

from app.ingestion.parsers.base import BaseParser

class HTMLParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if not HAS_UNSTRUCTURED_HTML:
            raise ImportError(
                "unstructured HTML extras not installed. "
                "Install with: pip install unstructured[all-docs]"
            )
        
        if isinstance(content, str):
            elements = partition_html(text=content)
        else:
            elements = partition_html(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
