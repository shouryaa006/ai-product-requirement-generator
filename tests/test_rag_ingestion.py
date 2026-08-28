"""Deterministic tests for RAG ingestion and vector-store plumbing."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.rag.chunking import DocumentChunk
from app.rag.documents import KnowledgeDocument
from app.rag.ingest import run_ingestion
from app.rag.vector_store import ChromaVectorStore, VectorStoreError


def test_run_ingestion_loads_chunks_embeds_and_upserts(monkeypatch, tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()

    documents = [
        KnowledgeDocument(
            knowledge_dir / "discovery.md",
            "# Discovery\n\nInterview users before writing requirements.",
        )
    ]
    chunks = [
        DocumentChunk(
            text="Interview users before writing requirements.",
            source="discovery.md",
            title="Discovery",
            chunk_index=0,
        )
    ]
    embeddings = [[0.1, 0.2, 0.3]]

    embedding_service = MagicMock()
    embedding_service.embed_texts.return_value = embeddings

    vector_store = MagicMock()
    vector_store.count.return_value = 1

    load_documents = MagicMock(return_value=documents)
    chunk_documents = MagicMock(return_value=chunks)

    monkeypatch.setattr(
        "app.rag.ingest.settings",
        MagicMock(gemini_api_key="test-api-key"),
    )
    monkeypatch.setattr("app.rag.ingest.load_knowledge_documents", load_documents)
    monkeypatch.setattr("app.rag.ingest.chunk_all_documents", chunk_documents)
    monkeypatch.setattr(
        "app.rag.ingest.get_embedding_service",
        lambda: embedding_service,
    )
    monkeypatch.setattr("app.rag.ingest.get_vector_store", lambda: vector_store)

    run_ingestion(knowledge_dir)

    load_documents.assert_called_once_with(knowledge_dir)
    chunk_documents.assert_called_once_with(documents)
    embedding_service.embed_texts.assert_called_once_with(
        ["Interview users before writing requirements."]
    )
    vector_store.upsert_chunks.assert_called_once_with(chunks, embeddings)
    vector_store.count.assert_called_once_with()


def test_run_ingestion_returns_without_external_calls_when_no_documents(
    monkeypatch,
    tmp_path,
):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()

    embedding_service_factory = MagicMock()
    vector_store_factory = MagicMock()

    monkeypatch.setattr(
        "app.rag.ingest.settings",
        MagicMock(gemini_api_key="test-api-key"),
    )
    monkeypatch.setattr(
        "app.rag.ingest.load_knowledge_documents",
        MagicMock(return_value=[]),
    )
    monkeypatch.setattr(
        "app.rag.ingest.get_embedding_service",
        embedding_service_factory,
    )
    monkeypatch.setattr("app.rag.ingest.get_vector_store", vector_store_factory)

    run_ingestion(knowledge_dir)

    embedding_service_factory.assert_not_called()
    vector_store_factory.assert_not_called()


def test_run_ingestion_exits_when_api_key_is_missing(monkeypatch, tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()

    monkeypatch.setattr(
        "app.rag.ingest.settings",
        MagicMock(gemini_api_key=""),
    )

    with pytest.raises(SystemExit) as exc_info:
        run_ingestion(knowledge_dir)

    assert exc_info.value.code == 1


def test_vector_store_upsert_uses_stable_ids_and_metadata():
    store = object.__new__(ChromaVectorStore)
    store.collection = MagicMock()
    chunks = [
        DocumentChunk(
            text="Prioritize the highest-value requirement first.",
            source="prioritization.md",
            title="Prioritization",
            chunk_index=0,
        ),
        DocumentChunk(
            text="Validate assumptions with user interviews.",
            source="discovery.md",
            title="Discovery",
            chunk_index=2,
        ),
    ]
    embeddings = [[0.1, 0.2], [0.3, 0.4]]

    store.upsert_chunks(chunks, embeddings)

    store.collection.upsert.assert_called_once_with(
        ids=["prioritization.md_chunk_0", "discovery.md_chunk_2"],
        documents=[
            "Prioritize the highest-value requirement first.",
            "Validate assumptions with user interviews.",
        ],
        embeddings=embeddings,
        metadatas=[
            {
                "source": "prioritization.md",
                "title": "Prioritization",
                "chunk_index": 0,
            },
            {
                "source": "discovery.md",
                "title": "Discovery",
                "chunk_index": 2,
            },
        ],
    )


def test_vector_store_rejects_mismatched_chunk_and_embedding_counts():
    store = object.__new__(ChromaVectorStore)
    store.collection = MagicMock()
    chunks = [
        DocumentChunk(
            text="Only one chunk.",
            source="one.md",
            title="One",
            chunk_index=0,
        )
    ]

    with pytest.raises(VectorStoreError) as exc_info:
        store.upsert_chunks(chunks, [])

    assert "number of chunks must match" in str(exc_info.value)
    store.collection.upsert.assert_not_called()


def test_vector_store_query_formats_chromadb_results():
    store = object.__new__(ChromaVectorStore)
    store.collection = MagicMock()
    store.collection.query.return_value = {
        "ids": [["discovery.md_chunk_0"]],
        "documents": [["Interview users before writing requirements."]],
        "metadatas": [[{"source": "discovery.md", "title": "Discovery"}]],
        "distances": [[0.05]],
    }

    results = store.query_similarity([0.1, 0.2, 0.3], top_k=1)

    assert results == [
        {
            "id": "discovery.md_chunk_0",
            "text": "Interview users before writing requirements.",
            "metadata": {"source": "discovery.md", "title": "Discovery"},
            "distance": 0.05,
        }
    ]
    store.collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2, 0.3]],
        n_results=1,
    )