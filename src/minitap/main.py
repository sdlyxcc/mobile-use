import asyncio
import sys
import time
from pathlib import Path
from typing import Any, Optional

import typer
from langchain_core.messages import AIMessage
from minitap.client.adb import get_device, adb
from minitap.constants import RECURSION_LIMIT
from minitap.graph.graph import get_graph
from minitap.graph.state import State
from minitap.utils.media import (
    create_gif_from_trace_folder,
    create_steps_json_from_trace_folder,
    remove_images_from_trace_folder,
    remove_steps_json_from_trace_folder,
)
from typing_extensions import Annotated

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


def print_ai_response_to_stderr(graph_result: dict[str, Any]):
    for msg in reversed(graph_result["messages"]):
        if isinstance(msg, AIMessage):
            print(msg.content, file=sys.stderr)
            return


async def run_automation(
    goal: str,
    test_name: Optional[str] = None,
):
    if not adb.device_list():
        print("❌ No Android device found. Please connect a device and enable USB debugging.")
        raise typer.Exit(code=1)

    device = get_device()
    assert device.serial is not None, "Device serial cannot be None after check."
    trace_id: str | None = None
    trace_folder_path: Path | None = None
    if test_name:
        timestamp = time.time()
        print(f"Recording test with name: {test_name}", flush=True)
        trace_id = f"{test_name}_{timestamp}"
        trace_folder_path = Path("traces") / trace_id
        trace_folder_path.mkdir(parents=True, exist_ok=True)

    print(f"Starting graph with goal: {goal}", flush=True)
    graph_input = State(
        initial_goal=goal,
        remaining_steps=RECURSION_LIMIT,
        messages=[],
        is_goal_achieved=False,
        device_id=device.serial,
        latest_ui_hierarchy=None,
        trace_id=trace_id,
        current_subgoal=None,
        subgoal_history=[],
        memory=None,
    ).model_dump()

    print(f"Invoking graph with input: {graph_input}", flush=True)
    result = await (await get_graph()).ainvoke(
        input=graph_input, config={"recursion_limit": RECURSION_LIMIT}
    )

    print_ai_response_to_stderr(graph_result=result)

    print("✅ Test is success ✅")
    if trace_folder_path:
        print("Compiling trace...")
        create_gif_from_trace_folder(trace_folder_path)
        create_steps_json_from_trace_folder(trace_folder_path)

        print("Video created, removing dust...")
        remove_images_from_trace_folder(trace_folder_path)
        remove_steps_json_from_trace_folder(trace_folder_path)
        print("📽️ Trace compiled 📽️")

    await asyncio.sleep(1)


@app.command()
def main(
    goal: Annotated[str, typer.Argument(help="The main goal for the agent to achieve.")],
    test_name: Annotated[
        Optional[str],
        typer.Option(
            "--test-name",
            "-n",
            help="A name for the test recording. If provided, a trace will be saved.",
        ),
    ] = None,
):
    """
    Run the Minitap agent to automate tasks on an Android device.
    """
    asyncio.run(run_automation(goal, test_name))


def cli():
    app()


if __name__ == "__main__":
    cli()
