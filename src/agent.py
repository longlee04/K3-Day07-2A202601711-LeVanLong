from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base is empty; no context available to answer this question."

        if metadata_filter:
            results = self.store.search_with_filter(question, top_k=top_k, metadata_filter=metadata_filter)
        else:
            results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant context found; cannot answer this question."

        context = "\n".join(
            f"[{index}] (source: {result['metadata'].get('doc_id', result['id'])}) {result['content']}"
            for index, result in enumerate(results, start=1)
        )

        prompt = (
            "Instruction: chỉ dùng context; nói rõ khi context không đủ.\n"
            f"Context: {context}\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
