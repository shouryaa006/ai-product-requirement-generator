"""Document loading utilities for the product knowledge base."""

import os
from pathlib import Path
from typing import Dict, List, Optional


class KnowledgeDocument:
    """Represents a single markdown document from the knowledge base."""

    def __init__(self, path: Path, content: str):
        self.path = path
        self.filename = path.name
        self.content = content
        self.title = self._extract_title()

    def _extract_title(self) -> str:
        """Extracts the first H1 header as the document title, or defaults to filename."""
        for line in self.content.splitlines():
            cleaned = line.strip()
            if cleaned.startswith("# "):
                return cleaned[2:].strip()
        return self.filename.replace(".md", "").replace("_", " ").title()


def load_knowledge_documents(directory_path: Path) -> List[KnowledgeDocument]:
    """Loads all Markdown documents from the specified directory."""
    documents = []
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Knowledge directory '{directory_path}' not found.")

    for file_path in Path(directory_path).glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append(KnowledgeDocument(file_path, content))
        except Exception as exc:
            print(f"Error loading {file_path.name}: {exc}")
            raise exc

    return documents
