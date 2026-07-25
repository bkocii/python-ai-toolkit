import cProfile
import io
import platform
import pstats
import sys
from collections.abc import Callable

from ai.workflow import (
    FunctionWorkflowStep,
    WorkflowContext,
    WorkflowEngine,
    WorkflowRunResult,
    WorkflowStepResult,
)

COMPONENT_ITERATIONS = 100_000
LIFECYCLE_ITERATIONS = 50_000

INPUT_DATA = {
    "value": 5,
}

WORKFLOW_METADATA = {
    "source": "profile",
}

STATE_UPDATES = {
    "value": 6,
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


def build_single_step_workflow() -> WorkflowEngine:
    return WorkflowEngine(
        steps=[
            FunctionWorkflowStep(
                name="single",
                function=run_single_step,
            ),
        ]
    )


def build_five_step_workflow() -> WorkflowEngine:
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


def profile_workflow_context_construction() -> None:
    context = None

    for _ in range(COMPONENT_ITERATIONS):
        context = WorkflowContext(
            input=INPUT_DATA,
            metadata=WORKFLOW_METADATA,
        )

    if context is None or context.input != INPUT_DATA:
        raise AssertionError("Unexpected workflow context.")


def profile_step_result_construction() -> None:
    result = None

    for _ in range(COMPONENT_ITERATIONS):
        result = WorkflowStepResult(
            step_name="single",
            output=6,
            state_updates=STATE_UPDATES,
        )

    if result is None or result.state_updates != STATE_UPDATES:
        raise AssertionError("Unexpected workflow step result.")


def profile_state_propagation() -> None:
    state: dict[str, int] = {}

    for _ in range(COMPONENT_ITERATIONS):
        state.update(STATE_UPDATES)

    if state != STATE_UPDATES:
        raise AssertionError("Unexpected propagated state.")


def profile_final_result_construction(
    context: WorkflowContext,
    step_results: list[WorkflowStepResult],
) -> None:
    result = None

    for _ in range(COMPONENT_ITERATIONS):
        result = WorkflowRunResult(
            success=True,
            context=context,
            steps=step_results,
        )

    if result is None or result.steps != step_results:
        raise AssertionError("Unexpected workflow run result.")


def profile_workflow_execution(
    workflow: WorkflowEngine,
    expected_step_count: int,
    expected_output: object,
) -> None:
    result = None

    for _ in range(LIFECYCLE_ITERATIONS):
        result = workflow.run(
            input_data=INPUT_DATA,
            metadata=WORKFLOW_METADATA,
        )

    if (
        result is None
        or len(result.steps) != expected_step_count
        or result.final_output != expected_output
    ):
        raise AssertionError("Unexpected workflow execution result.")


def print_profile(
    title: str,
    operation: Callable[[], None],
) -> None:
    profiler = cProfile.Profile()

    profiler.enable()
    operation()
    profiler.disable()

    output = io.StringIO()
    statistics = pstats.Stats(
        profiler,
        stream=output,
    )
    statistics.strip_dirs()
    statistics.sort_stats("cumulative")
    statistics.print_stats(35)
    statistics.print_stats(r"(profile_workflow_execution|workflow)\.py")

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(output.getvalue())


def main() -> None:
    single_step_workflow = build_single_step_workflow()
    five_step_workflow = build_five_step_workflow()

    result_context = WorkflowContext(
        input=INPUT_DATA,
        state={
            "value": 169,
        },
        metadata=WORKFLOW_METADATA,
    )

    one_step_results = [
        WorkflowStepResult(
            step_name="single",
            output=6,
            state_updates={
                "value": 6,
            },
        )
    ]

    five_step_results = [
        WorkflowStepResult(
            step_name="initialize",
            output=5,
            state_updates={
                "value": 5,
            },
        ),
        WorkflowStepResult(
            step_name="double",
            output=10,
            state_updates={
                "value": 10,
            },
        ),
        WorkflowStepResult(
            step_name="increment",
            output=13,
            state_updates={
                "value": 13,
            },
        ),
        WorkflowStepResult(
            step_name="square",
            output=169,
            state_updates={
                "value": 169,
            },
        ),
        WorkflowStepResult(
            step_name="finalize",
            output={
                "result": 169,
                "source": "profile",
            },
        ),
    ]

    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"Component iterations: {COMPONENT_ITERATIONS:,}")
    print(f"Lifecycle iterations: {LIFECYCLE_ITERATIONS:,}")

    profile_cases = (
        (
            "WorkflowContext construction",
            profile_workflow_context_construction,
        ),
        (
            "WorkflowStepResult construction",
            profile_step_result_construction,
        ),
        (
            "State propagation",
            profile_state_propagation,
        ),
        (
            "WorkflowRunResult construction with one step",
            lambda: profile_final_result_construction(
                context=result_context,
                step_results=one_step_results,
            ),
        ),
        (
            "WorkflowRunResult construction with five steps",
            lambda: profile_final_result_construction(
                context=result_context,
                step_results=five_step_results,
            ),
        ),
        (
            "Complete one-step workflow execution",
            lambda: profile_workflow_execution(
                workflow=single_step_workflow,
                expected_step_count=1,
                expected_output=6,
            ),
        ),
        (
            "Complete five-step workflow execution",
            lambda: profile_workflow_execution(
                workflow=five_step_workflow,
                expected_step_count=5,
                expected_output={
                    "result": 169,
                    "source": "profile",
                },
            ),
        ),
    )

    for title, operation in profile_cases:
        print_profile(
            title=title,
            operation=operation,
        )


if __name__ == "__main__":
    main()
