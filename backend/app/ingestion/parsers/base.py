from abc import ABC, abstractmethod
from typing import Any

class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str | bytes) -> dict[str, Any]:
        """
        Parse document content and return structured data.
        
        Returns:
            dict with keys:
            - text: str (extracted text)
            - metadata: dict (document metadata)
            - elements: list[dict] (structured elements like sections, tables)
        """
        pass
