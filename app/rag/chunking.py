"""Chunking utility to split documents into manageable chunks."""

from typing import Any, Dict, List

from app.rag.documents import KnowledgeDocument


class DocumentChunk:
    """Represents a single chunk of a knowledge document with preserved metadata."""

    def __init__(self, text: str, source: str, title: str, chunk_index: int):
        self.text = text
        self.source = source
        self.title = title
        self.chunk_index = chunk_index

    def to_metadata(self) -> Dict[str, Any]:
        """Returns metadata safe for storing in ChromaDB."""
        return {
            "source": self.source,
            "title": self.title,
            "chunk_index": self.chunk_index,
        }


def chunk_document(doc: KnowledgeDocument, chunk_size: int = 1000, overlap: int = 200) -> List[DocumentChunk]:
    """Splits a KnowledgeDocument into logical chunks based on paragraph/character limits.

    Ensures that metadata (filename, title, chunk index) is preserved.
    """
    paragraphs = doc.content.split("\n\n")
    chunks: List[DocumentChunk] = []
    current_chunk_parts: List[str] = []
    current_length = 0
    chunk_idx = 0

    for paragraph in paragraphs:
        paragraph_stripped = paragraph.strip()
        if not paragraph_stripped:
            continue

        p_len = len(paragraph_stripped)

        # If a single paragraph is larger than chunk_size, we just add it to avoid losing information
        if p_len > chunk_size and not current_chunk_parts:
            chunks.append(
                DocumentChunk(
                    text=paragraph_stripped,
                    source=doc.filename,
                    title=doc.title,
                    chunk_index=chunk_idx,
                )
            )
            chunk_idx += 1
            continue

        # If adding this paragraph exceeds chunk size, finalize current chunk
        if current_length + p_len > chunk_size and current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts)
            chunks.append(
                DocumentChunk(
                    text=chunk_text,
                    source=doc.filename,
                    title=doc.title,
                    chunk_index=chunk_idx,
                )
            )
            chunk_idx += 1

            # Keep overlap: we can retain the last paragraph if its length is within overlap limits
            if len(current_chunk_parts[-1]) <= overlap:
                current_chunk_parts = [current_chunk_parts[-1], paragraph_stripped]
                current_length = len(current_chunk_parts[0]) + len(paragraph_stripped) + 2
            else:
                current_chunk_parts = [paragraph_stripped]
                current_length = p_len
        else:
            current_chunk_parts.append(paragraph_stripped)
            current_length += p_len + (2 if current_length > 0 else 0)

    # Add any remaining text
    if current_chunk_parts:
        chunk_text = "\n\n".join(current_chunk_parts)
        chunks.append(
            DocumentChunk(
                text=chunk_text,
                source=doc.filename,
                title=doc.title,
                chunk_index=chunk_idx,
            )
        )

    return chunks


def chunk_all_documents(documents: List[KnowledgeDocument], chunk_size: int = 1000, overlap: int = 200) -> List[DocumentChunk]:
    """Helper to chunk a list of KnowledgeDocuments."""
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc, chunk_size, overlap))
    return all_chunks
