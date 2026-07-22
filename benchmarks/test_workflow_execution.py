import pytest

from ai.workflow import (
    FunctionWorkflowStep,
    WorkflowContext,
    WorkflowEngine,
    WorkflowStepResult,
)

INPUT_DATA = {
    "value": 5,
}

WORKFLOW_METADATA = {
    "source": "benchmark",
}


def run_single_step(
    context: WorkflowContext,
) -> WorkflowStepResult:
    value = context.input["value"] + 1

    return WorkflowStepResult(
        step_name="single",
        output=value,
        state_updates={
            "value": value,
        },
    )


def initialize_value(
    context: WorkflowContext,
) -> WorkflowStepResult:
    value = context.input["value"]

    return WorkflowStepResult(
        step_name="initialize",
        output=value,
        state_updates={
            "value": value,
        },
    )


def double_value(
    context: WorkflowContext,
) -> WorkflowStepResult:
    value = context.state["value"] * 2

    return WorkflowStepResult(
        step_name="double",
        output=value,
        state_updates={
            "value": value,
        },
    )


def increment_value(
    context: WorkflowContext,
) -> WorkflowStepResult:
    value = context.state["value"] + 3

    return WorkflowStepResult(
        step_name="increment",
        output=value,
        state_updates={
            "value": value,
        },
    )


def square_value(
    context: WorkflowContext,
) -> WorkflowStepResult:
    value = context.state["value"] ** 2

    return WorkflowStepResult(
        step_name="square",
        output=value,
        state_updates={
            "value": value,
        },
    )


def finalize_value(
    context: WorkflowContext,
) -> WorkflowStepResult:
    return WorkflowStepResult(
        step_name="finalize",
        output={
            "result": context.state["value"],
            "source": context.metadata["source"],
        },
    )


@pytest.fixture(scope="module")
def single_step_workflow() -> WorkflowEngine:
    return WorkflowEngine(
        steps=[
            FunctionWorkflowStep(
                name="single",
                function=run_single_step,
            ),
        ]
    )


@pytest.fixture(scope="module")
def five_step_workflow() -> WorkflowEngine:
    return WorkflowEngine(
        steps=[
            FunctionWorkflowStep(
                name="initialize",
                function=initialize_value,
            ),
            FunctionWorkflowStep(
                name="double",
                function=double_value,
            ),
            FunctionWorkflowStep(
                name="increment",
                function=increment_value,
            ),
            FunctionWorkflowStep(
                name="square",
                function=square_value,
            ),
            FunctionWorkflowStep(
                name="finalize",
                function=finalize_value,
            ),
        ]
    )


def test_single_step_workflow_execution(
    benchmark,
    single_step_workflow,
):
    result = benchmark(
        single_step_workflow.run,
        input_data=INPUT_DATA,
        metadata=WORKFLOW_METADATA,
    )

    assert result.success is True
    assert len(result.steps) == 1
    assert result.steps[0].step_name == "single"
    assert result.steps[0].output == 6
    assert result.context.state == {
        "value": 6,
    }
    assert result.final_output == 6


def test_five_step_workflow_execution(
    benchmark,
    five_step_workflow,
):
    result = benchmark(
        five_step_workflow.run,
        input_data=INPUT_DATA,
        metadata=WORKFLOW_METADATA,
    )

    assert result.success is True
    assert len(result.steps) == 5

    assert [step.step_name for step in result.steps] == [
        "initialize",
        "double",
        "increment",
        "square",
        "finalize",
    ]

    assert result.context.state == {
        "value": 169,
    }

    assert result.final_output == {
        "result": 169,
        "source": "benchmark",
    }

    assert all(step.success for step in result.steps)
