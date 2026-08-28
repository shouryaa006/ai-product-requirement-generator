"""Deterministic tests for the local RAG pipeline utilities."""

from pathlib import Path
from unittest.mock import MagicMock

from app.rag.chunking import chunk_all_documents, chunk_document
from app.rag.documents import KnowledgeDocument, load_knowledge_documents
from app.rag.retriever import RetrievalService


def test_load_knowledge_documents_extracts_titles_and_markdown_only(tmp_path):
    first_doc = tmp_path / "product_discovery.md"
    first_doc.write_text(
        "# Product Discovery\n\nDiscovery practices for validating product ideas.",
        encoding="utf-8",
    )
    second_doc = tmp_path / "roadmap_notes.md"
    second_doc.write_text(
        "Prioritize outcomes over outputs.",
        encoding="utf-8",
    )
    ignored_file = tmp_path / "not_knowledge.txt"
    ignored_file.write_text("This should not be loaded.", encoding="utf-8")

    documents = load_knowledge_documents(tmp_path)

    assert [doc.filename for doc in documents] == [
        "product_discovery.md",
        "roadmap_notes.md",
    ]
    assert documents[0].title == "Product Discovery"
    assert documents[1].title == "Roadmap Notes"
    assert "Discovery practices" in documents[0].content


def test_chunk_document_preserves_source_title_and_stable_chunk_indexes():
    document = KnowledgeDocument(
        Path("prioritization.md"),
        "# Prioritization\n\nShort intro.\n\n"
        "A longer paragraph about choosing the highest value work first.\n\n"
        "Closing guidance for product teams.",
    )

    chunks = chunk_document(document, chunk_size=75, overlap=20)

    assert len(chunks) >= 2
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))

    for chunk in chunks:
        assert chunk.source == "prioritization.md"
        assert chunk.title == "Prioritization"
        assert chunk.text.strip()
        assert chunk.to_metadata() == {
            "source": "prioritization.md",
            "title": "Prioritization",
            "chunk_index": chunk.chunk_index,
        }


def test_chunk_all_documents_combines_chunks_from_multiple_documents():
    documents = [
        KnowledgeDocument(Path("first.md"), "# First\n\nAlpha content."),
        KnowledgeDocument(Path("second.md"), "# Second\n\nBeta content."),
    ]

    chunks = chunk_all_documents(documents, chunk_size=100, overlap=10)

    assert len(chunks) == 2
    assert [chunk.source for chunk in chunks] == ["first.md", "second.md"]
    assert [chunk.title for chunk in chunks] == ["First", "Second"]


def test_retrieval_service_embeds_query_and_queries_vector_store():
    embedding_service = MagicMock()
    embedding_service.embed_text.return_value = [0.1, 0.2, 0.3]

    expected_results = [
        {
            "id": "discovery.md_chunk_0",
            "text": "Interview users before writing requirements.",
            "metadata": {"source": "discovery.md", "title": "Discovery"},
            "distance": 0.05,
        }
    ]
    vector_store = MagicMock()
    vector_store.query_similarity.return_value = expected_results

    service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        default_top_k=3,
    )

    results = service.retrieve_relevant_knowledge("Build a tutor marketplace")

    assert results == expected_results
    embedding_service.embed_text.assert_called_once_with("Build a tutor marketplace")
    vector_store.query_similarity.assert_called_once_with([0.1, 0.2, 0.3], top_k=3)


def test_retrieval_service_returns_empty_for_blank_query_without_external_calls():
    embedding_service = MagicMock()
    vector_store = MagicMock()
    service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    assert service.retrieve_relevant_knowledge("   ") == []
    embedding_service.embed_text.assert_not_called()
    vector_store.query_similarity.assert_not_called()


def test_retrieval_service_uses_explicit_top_k_over_default():
    embedding_service = MagicMock()
    embedding_service.embed_text.return_value = [0.4, 0.5]
    vector_store = MagicMock()
    vector_store.query_similarity.return_value = []
    service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        default_top_k=5,
    )

    assert service.retrieve_relevant_knowledge("Prioritize onboarding", top_k=2) == []
    vector_store.query_similarity.assert_called_once_with([0.4, 0.5], top_k=2)