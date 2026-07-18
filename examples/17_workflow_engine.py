from ai.client import AIClient
from ai.embeddings import EmbeddingInput
from ai.retriever import VectorStoreRetriever, format_retrieved_context
from ai.vector_store import InMemoryVectorStore, VectorRecord
from ai.workflow import (
    FunctionWorkflowStep,
    WorkflowContext,
    WorkflowEngine,
    WorkflowStepResult,
)


def main() -> None:
    ai = AIClient()
    store = InMemoryVectorStore()

    knowledge = [
        EmbeddingInput(
            text="Redis is often used as a cache and message broker.",
            metadata={"topic": "redis"},
        ),
        EmbeddingInput(
            text="PostgreSQL is a relational database used for structured data.",
            metadata={"topic": "postgres"},
        ),
        EmbeddingInput(
            text="Django is a Python web framework for building web applications.",
            metadata={"topic": "django"},
        ),
    ]

    embedding_response = ai.embed_texts(knowledge)

    records = [
        VectorRecord(
            id=f"doc-{embedding.index}",
            text=embedding.text,
            vector=embedding.vector,
            metadata=embedding.metadata,
        )
        for embedding in embedding_response.embeddings
    ]

    store.add(records)

    retriever = VectorStoreRetriever(
        ai_client=ai,
        vector_store=store,
    )

    def retrieve_step(context: WorkflowContext) -> WorkflowStepResult:
        question = context.input["question"]

        contexts = retriever.retrieve(
            query=question,
            limit=2,
        )

        context_text = format_retrieved_context(contexts)

        return WorkflowStepResult(
            step_name="retrieve",
            output=context_text,
            state_updates={
                "question": question,
                "contexts": contexts,
                "context_text": context_text,
            },
        )

    def answer_step(context: WorkflowContext) -> WorkflowStepResult:
        question = context.state["question"]
        context_text = context.state["context_text"]

        prompt = f"""
Answer the question using only the context below.

Context:
{context_text}

Question:
{question}
"""

        result = ai.ask(prompt)

        return WorkflowStepResult(
            step_name="answer",
            output=result.data,
            state_updates={
                "answer": result.data,
                "request_id": result.request_id,
                "model": result.model,
            },
        )

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("retrieve", retrieve_step),
            FunctionWorkflowStep("answer", answer_step),
        ]
    )

    result = workflow.run(
        input_data={
            "question": "Which technology should I use for caching?",
        },
        metadata={
            "workflow": "rag_answer",
        },
    )

    print("Workflow success:")
    print(result.success)
    print()

    print("Answer:")
    print(result.final_output)
    print()

    print("Workflow state:")
    print(result.context.state)


if __name__ == "__main__":
    main()
