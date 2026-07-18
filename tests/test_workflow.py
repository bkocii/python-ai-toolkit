from ai.workflow import (
    FunctionWorkflowStep,
    WorkflowContext,
    WorkflowEngine,
    WorkflowRunResult,
    WorkflowStepResult,
)
import pytest


def test_workflow_context_stores_input_state_and_metadata():
    context = WorkflowContext(
        input={"question": "What is Redis?"},
        state={"step": "start"},
        metadata={"user_id": "123"},
    )

    assert context.input == {"question": "What is Redis?"}
    assert context.state == {"step": "start"}
    assert context.metadata == {"user_id": "123"}


def test_workflow_step_result_stores_values():
    result = WorkflowStepResult(
        step_name="retrieve",
        output="retrieved context",
        state_updates={"context": "retrieved context"},
        metadata={"source": "test"},
    )

    assert result.step_name == "retrieve"
    assert result.output == "retrieved context"
    assert result.state_updates == {"context": "retrieved context"}
    assert result.metadata == {"source": "test"}
    assert result.success is True
    assert result.error is None


def test_workflow_run_result_final_output_returns_last_step_output():
    result = WorkflowRunResult(
        success=True,
        context=WorkflowContext(),
        steps=[
            WorkflowStepResult(
                step_name="first",
                output="first output",
            ),
            WorkflowStepResult(
                step_name="second",
                output="second output",
            ),
        ],
    )

    assert result.final_output == "second output"


def test_workflow_run_result_final_output_returns_none_without_steps():
    result = WorkflowRunResult(
        success=True,
        context=WorkflowContext(),
        steps=[],
    )

    assert result.final_output is None


def test_function_workflow_step_runs_function():
    def step_function(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="test_step",
            output=context.input["value"],
        )

    step = FunctionWorkflowStep(
        name="test_step",
        function=step_function,
    )

    result = step.run(
        WorkflowContext(
            input={"value": "hello"},
        )
    )

    assert result.step_name == "test_step"
    assert result.output == "hello"


def test_function_workflow_step_rewrites_step_name():
    def step_function(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="wrong_name",
            output="ok",
        )

    step = FunctionWorkflowStep(
        name="correct_name",
        function=step_function,
    )

    result = step.run(WorkflowContext())

    assert result.step_name == "correct_name"
    assert result.output == "ok"


def test_function_workflow_step_rejects_empty_name():
    try:
        FunctionWorkflowStep(
            name="   ",
            function=lambda context: WorkflowStepResult(step_name="test"),
        )
    except ValueError as exc:
        assert "Workflow step name cannot be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_workflow_engine_rejects_empty_steps():
    with pytest.raises(
        ValueError,
        match="Workflow must contain at least one step",
    ):
        WorkflowEngine([])


def test_workflow_engine_runs_steps_in_order():
    executed = []

    def first_step(context: WorkflowContext) -> WorkflowStepResult:
        executed.append("first")
        return WorkflowStepResult(
            step_name="first",
            output="first output",
        )

    def second_step(context: WorkflowContext) -> WorkflowStepResult:
        executed.append("second")
        return WorkflowStepResult(
            step_name="second",
            output="second output",
        )

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("first", first_step),
            FunctionWorkflowStep("second", second_step),
        ]
    )

    result = workflow.run()

    assert result.success is True
    assert executed == ["first", "second"]
    assert result.final_output == "second output"


def test_workflow_engine_passes_input_and_metadata_to_context():
    def step_function(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="inspect",
            output={
                "input": context.input,
                "metadata": context.metadata,
            },
        )

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("inspect", step_function),
        ]
    )

    result = workflow.run(
        input_data={"question": "What is Redis?"},
        metadata={"user_id": "123"},
    )

    assert result.final_output == {
        "input": {"question": "What is Redis?"},
        "metadata": {"user_id": "123"},
    }


def test_workflow_engine_applies_state_updates_between_steps():
    def first_step(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="first",
            output="retrieved context",
            state_updates={
                "context": "retrieved context",
            },
        )

    def second_step(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="second",
            output=context.state["context"],
        )

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("first", first_step),
            FunctionWorkflowStep("second", second_step),
        ]
    )

    result = workflow.run()

    assert result.success is True
    assert result.context.state == {"context": "retrieved context"}
    assert result.final_output == "retrieved context"


def test_workflow_engine_stops_on_failed_step():
    def first_step(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="first",
            output="ok",
        )

    def failing_step(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="failing",
            success=False,
            error="Something failed",
        )

    def third_step(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="third",
            output="should not run",
        )

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("first", first_step),
            FunctionWorkflowStep("failing", failing_step),
            FunctionWorkflowStep("third", third_step),
        ]
    )

    result = workflow.run()

    assert result.success is False
    assert len(result.steps) == 2
    assert result.steps[-1].step_name == "failing"
    assert result.steps[-1].error == "Something failed"


def test_workflow_engine_converts_exceptions_to_failed_step_result():
    def failing_step(context: WorkflowContext) -> WorkflowStepResult:
        raise RuntimeError("Boom")

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("failing", failing_step),
        ]
    )

    result = workflow.run()

    assert result.success is False
    assert len(result.steps) == 1
    assert result.steps[0].step_name == "failing"
    assert result.steps[0].success is False
    assert result.steps[0].error == "Boom"


def test_workflow_engine_applies_failed_step_state_updates_before_stopping():
    def failing_step(context: WorkflowContext) -> WorkflowStepResult:
        return WorkflowStepResult(
            step_name="failing",
            success=False,
            error="Failed after partial work",
            state_updates={
                "partial": "value",
            },
        )

    workflow = WorkflowEngine(
        steps=[
            FunctionWorkflowStep("failing", failing_step),
        ]
    )

    result = workflow.run()

    assert result.success is False
    assert result.context.state == {"partial": "value"}
