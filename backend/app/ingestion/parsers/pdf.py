try:
    from unstructured.partition.pdf import partition_pdf
    HAS_UNSTRUCTURED_PDF = True
except ImportError:
    HAS_UNSTRUCTURED_PDF = False

from app.ingestion.parsers.base import BaseParser

class PDFParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if not HAS_UNSTRUCTURED_PDF:
            raise ImportError(
                "unstructured PDF extras not installed. "
                "Install with: pip install unstructured[all-docs]"
            )
        
        if isinstance(content, str):
            # Assume it's a file path
            elements = partition_pdf(filename=content)
        else:
            # It's bytes content
            elements = partition_pdf(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements),
                "has_tables": any("Table" in str(type(el)) for el in elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
