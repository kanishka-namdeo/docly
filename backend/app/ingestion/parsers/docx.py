try:
    from unstructured.partition.docx import partition_docx
    HAS_UNSTRUCTURED_DOCX = True
except ImportError:
    HAS_UNSTRUCTURED_DOCX = False

from app.ingestion.parsers.base import BaseParser

class DOCXParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if not HAS_UNSTRUCTURED_DOCX:
            raise ImportError(
                "unstructured DOCX extras not installed. "
                "Install with: pip install unstructured[all-docs]"
            )
        
        if isinstance(content, str):
            elements = partition_docx(filename=content)
        else:
            elements = partition_docx(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
