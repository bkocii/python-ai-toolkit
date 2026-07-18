from abc import ABC, abstractmethod
from typing import Any
from collections.abc import Callable
from pydantic import BaseModel, Field


class WorkflowContext(BaseModel):
    """
    Shared workflow context.

    input:
        Initial workflow input.

    state:
        Mutable state passed between workflow steps.

    metadata:
        Optional application-specific workflow metadata.
    """

    input: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)


class WorkflowStepResult(BaseModel):
    """
    Result returned by one workflow step.
    """

    step_name: str
    output: Any = None
    state_updates: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)
    success: bool = True
    error: str | None = None


class WorkflowRunResult(BaseModel):
    """
    Final result returned by a workflow engine run.
    """

    success: bool
    context: WorkflowContext
    steps: list[WorkflowStepResult] = Field(default_factory=list)

    @property
    def final_output(self) -> Any:
        """
        Return the output from the last executed step.
        """
        if not self.steps:
            return None

        return self.steps[-1].output


class BaseWorkflowStep(ABC):
    """
    Base interface for workflow steps.
    """

    name: str

    @abstractmethod
    def run(
        self,
        context: WorkflowContext,
    ) -> WorkflowStepResult:
        """
        Run one workflow step.
        """
        raise NotImplementedError


class FunctionWorkflowStep(BaseWorkflowStep):
    """
    Workflow step backed by a Python function.

    The function receives WorkflowContext and returns WorkflowStepResult.
    """

    def __init__(
        self,
        name: str,
        function: Callable[[WorkflowContext], WorkflowStepResult],
    ):
        if not name.strip():
            raise ValueError("Workflow step name cannot be empty.")

        self.name = name
        self.function = function

    def run(
        self,
        context: WorkflowContext,
    ) -> WorkflowStepResult:
        result = self.function(context)

        if result.step_name != self.name:
            return result.model_copy(
                update={
                    "step_name": self.name,
                }
            )

        return result


class WorkflowEngine:
    """
    Sequential workflow engine.

    Runs workflow steps in order and passes shared context between them.
    """

    def __init__(
        self,
        steps: list[BaseWorkflowStep],
    ):
        if not steps:
            raise ValueError("Workflow must contain at least one step.")

        self.steps = steps

    def run(
        self,
        input_data: dict[str, Any] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> WorkflowRunResult:
        context = WorkflowContext(
            input=input_data or {},
            metadata=metadata or {},
        )

        executed_steps: list[WorkflowStepResult] = []

        for step in self.steps:
            try:
                result = step.run(context)
            except Exception as exc:
                result = WorkflowStepResult(
                    step_name=step.name,
                    success=False,
                    error=str(exc),
                )

            executed_steps.append(result)

            if result.state_updates:
                context.state.update(result.state_updates)

            if not result.success:
                return WorkflowRunResult(
                    success=False,
                    context=context,
                    steps=executed_steps,
                )

        return WorkflowRunResult(
            success=True,
            context=context,
            steps=executed_steps,
        )
