import asyncio
import platform
import sys
import time
from pathlib import Path
from typing import Any, Optional

import typer
from langchain_core.messages import AIMessage
from rich.console import Console
from typing_extensions import Annotated

from minitap.config import initialize_llm_config
from minitap.constants import (
    RECURSION_LIMIT,
)
from minitap.context import DeviceContext, set_execution_setup
from minitap.controllers.mobile_command_controller import ScreenDataResponse, get_screen_data
from minitap.controllers.platform_specific_commands_controller import get_first_device_id
from minitap.graph.graph import get_graph
from minitap.graph.state import State
from minitap.servers.utils import are_ports_available
from minitap.utils.cli_helpers import display_device_status
from minitap.utils.logger import get_logger
from minitap.utils.media import (
    create_gif_from_trace_folder,
    create_steps_json_from_trace_folder,
    remove_images_from_trace_folder,
    remove_steps_json_from_trace_folder,
)
from minitap.utils.time import convert_timestamp_to_str

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
logger = get_logger(__name__)


def print_ai_response_to_stderr(graph_result: dict[str, Any]):
    for msg in reversed(graph_result["messages"]):
        if isinstance(msg, AIMessage):
            print(msg.content, file=sys.stderr)
            return


async def run_servers():
    from minitap.servers.start_servers import start_servers_and_get_device_id

    device_id = start_servers_and_get_device_id()
    return device_id


async def run_automation(
    goal: str,
    test_name: Optional[str] = None,
    traces_output_path_str: str = "traces",
    graph_config_callbacks: Optional[list] = [],
):
    device_id: str | None = None

    if are_ports_available():
        logger.error("❌ Mobile-use servers are not started. Starting...")
        device_id = await run_servers()

    if not device_id:
        device_id = get_first_device_id()

    host_platform = platform.system()

    llm_config = initialize_llm_config()
    logger.info(str(llm_config))

    screen_data: ScreenDataResponse = get_screen_data()

    device_context_instance = DeviceContext(
        host_platform="WINDOWS" if host_platform == "Windows" else "LINUX",
        mobile_platform="ANDROID" if screen_data.platform == "ANDROID" else "IOS",
        device_id=device_id,
        device_width=screen_data.width,
        device_height=screen_data.height,
    )
    device_context_instance.set()
    logger.info(device_context_instance.to_str())

    start_time = time.time()
    trace_id: str | None = None
    traces_temp_path: Path | None = None
    traces_output_path: Path | None = None

    if test_name:
        traces_output_path = Path(traces_output_path_str).resolve()
        logger.info(f"📂 Traces output path: {traces_output_path}")
        traces_temp_path = Path(__file__).parent.joinpath(f"../traces/{test_name}").resolve()
        logger.info(f"📄📂 Traces temp path: {traces_temp_path}")
        traces_output_path.mkdir(parents=True, exist_ok=True)
        traces_temp_path.mkdir(parents=True, exist_ok=True)
        trace_id = test_name
        set_execution_setup(trace_id)

    logger.info(f"Starting graph with goal: `{goal}`")
    graph_input = State(
        messages=[],
        initial_goal=goal,
        subgoal_plan=[],
        latest_ui_hierarchy=None,
        latest_screenshot_base64=None,
        focused_app_info=None,
        device_date=None,
        structured_decisions=None,
        agents_thoughts=[],
        remaining_steps=RECURSION_LIMIT,
    ).model_dump()

    success = False
    try:
        logger.info(f"Invoking graph with input: {graph_input}")
        result = await (await get_graph()).ainvoke(
            input=graph_input,
            config={
                "recursion_limit": RECURSION_LIMIT,
                "callbacks": graph_config_callbacks,
            },
        )

        print_ai_response_to_stderr(graph_result=result)

        logger.info("✅ Test is success ✅")
        success = True
    except Exception as e:
        logger.info(f"❌ Test failed with error: {e} ❌")
        raise
    finally:
        if traces_temp_path and traces_output_path and start_time:
            formatted_ts = convert_timestamp_to_str(start_time)
            status = "_PASS" if success else "_FAIL"
            new_name = f"{test_name}{status}_{formatted_ts}"

            logger.info("Compiling trace FROM FOLDER: " + str(traces_temp_path))
            create_gif_from_trace_folder(traces_temp_path)
            create_steps_json_from_trace_folder(traces_temp_path)

            logger.info("Video created, removing dust...")
            remove_images_from_trace_folder(traces_temp_path)
            remove_steps_json_from_trace_folder(traces_temp_path)
            logger.info("📽️ Trace compiled, moving to output path 📽️")

            # moving all the content that is inside the traces folder into the new path
            output_folder_path = traces_temp_path.rename(traces_output_path / new_name)
            logger.info(f"📂✅ Trace folder renamed to: {output_folder_path.name}")

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
    traces_path: Annotated[
        str,
        typer.Option(
            "--traces-path",
            "-p",
            help="The path to save the traces.",
        ),
    ] = "traces",
):
    """
    Run the Minitap agent to automate tasks on a mobile device.
    """
    console = Console()
    display_device_status(console)
    asyncio.run(run_automation(goal, test_name, traces_path))


def cli():
    app()


if __name__ == "__main__":
    cli()
