try:
    from unstructured.partition.xlsx import partition_xlsx
    HAS_UNSTRUCTURED_XLSX = True
except ImportError:
    HAS_UNSTRUCTURED_XLSX = False

from app.ingestion.parsers.base import BaseParser

class ExcelParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if not HAS_UNSTRUCTURED_XLSX:
            raise ImportError(
                "unstructured Excel extras not installed. "
                "Install with: pip install unstructured[all-docs]"
            )
        
        if isinstance(content, str):
            elements = partition_xlsx(filename=content)
        else:
            elements = partition_xlsx(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
