from pydantic import BaseModel, Field
from ai.client import AIClient
from ai.retriever import BaseRetriever, format_retrieved_context
from ai.retriever import RetrievedContext


class RAGResponse(BaseModel):
    """
    Response returned by a RAG pipeline.

    answer:
        Final model answer.

    contexts:
        Retrieved context items used to build the prompt.

    model:
        Model used to generate the answer.

    request_id:
        Request ID from the underlying AIResult.

    raw_response:
        Raw model response text.
    """

    answer: str
    contexts: list[RetrievedContext] = Field(default_factory=list)
    model: str
    request_id: str
    raw_response: str


def build_rag_prompt(
    question: str,
    context_text: str,
    instructions: str | None = None,
) -> str:
    """
    Build a grounded RAG prompt from retrieved context.
    """
    extra_instructions = (
        f"\nAdditional instructions:\n{instructions}\n" if instructions else ""
    )

    return f"""
Answer the question using only the context below.

If the context does not contain enough information, say that you do not know based on the provided context.
Do not invent facts that are not present in the context.
{extra_instructions}
Context:
{context_text}

Question:
{question}
"""


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    The pipeline retrieves relevant context, builds a grounded prompt,
    asks the AI client for an answer, and returns the answer together
    with the contexts used.
    """

    def __init__(
        self,
        ai_client: AIClient,
        retriever: BaseRetriever,
    ):
        self.ai_client = ai_client
        self.retriever = retriever

    def ask(
        self,
        question: str,
        limit: int = 5,
        metadata_filter: dict[str, str] | None = None,
        instructions: str | None = None,
    ) -> RAGResponse:
        """
        Answer a question using retrieved context.
        """
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        contexts = self.retriever.retrieve(
            query=question,
            limit=limit,
            metadata_filter=metadata_filter,
        )

        context_text = format_retrieved_context(contexts)

        prompt = build_rag_prompt(
            question=question,
            context_text=context_text,
            instructions=instructions,
        )

        result = self.ai_client.ask(prompt)

        return RAGResponse(
            answer=result.data,
            contexts=contexts,
            model=result.model,
            request_id=result.request_id,
            raw_response=result.raw_response,
        )
