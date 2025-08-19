from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

from mobile_use.controllers.mobile_command_controller import (
    ScreenDataResponse,
    WaitTimeout,
    get_screen_data,
    wait_for_animation_to_end,
)
from mobile_use.controllers.mobile_command_controller import (
    erase_text as erase_text_controller,
)
from mobile_use.graph.state import State
from mobile_use.tools.tool_wrapper import ExecutorMetadata, ToolWrapper
from mobile_use.utils.ui_hierarchy import find_element_by_resource_id


@tool
def erase_text(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
    agent_thought: str,
    input_text_resource_id: str,
    executor_metadata: Optional[ExecutorMetadata],
    nb_chars: Optional[int] = None,
):
    """
    Erases up to `nb_chars` characters from the currently selected text field (default: 50).

    iOS Note:
        This may be flaky on iOS. As a workaround:
            - long_press_on("<input id>")
            - tap_on("Select All")
            - erase_text()

    Matches 'clearText' in search.
    """
    # value of text key from input_text_ressource_id
    latest_ui_hierarchy = state.latest_ui_hierarchy
    previous_text_value = None
    new_text_value = None
    nb_char_erased = -1
    if latest_ui_hierarchy is not None:
        print("Looking for element with resource id: ", input_text_resource_id)
        text_input_element = find_element_by_resource_id(
            ui_hierarchy=latest_ui_hierarchy, resource_id=input_text_resource_id
        )
        print("Found element: ", text_input_element)
        if text_input_element:
            previous_text_value = text_input_element.get("text", None)
        print("Previous text value: ", previous_text_value)

    output = erase_text_controller(nb_chars=nb_chars)
    has_failed = output is not None

    wait_for_animation_to_end(timeout=WaitTimeout.MEDIUM)

    screen_data: ScreenDataResponse = get_screen_data()
    latest_ui_hierarchy = screen_data.elements

    if not has_failed and latest_ui_hierarchy is not None:
        text_input_element = find_element_by_resource_id(
            ui_hierarchy=latest_ui_hierarchy, resource_id=input_text_resource_id
        )
        if text_input_element:
            new_text_value = text_input_element.get("text", None)
        print("New text value: ", new_text_value)

    if previous_text_value is not None and new_text_value is not None:
        if previous_text_value == new_text_value:
            has_failed = True
            output = (
                "Unable to erase text: text is very likely a placeholder."
                " Thus, assuming the text input is empty."
            )
        else:
            nb_char_erased = len(previous_text_value) - len(new_text_value)
    tool_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=erase_text_wrapper.on_failure_fn(output)
        if has_failed
        else erase_text_wrapper.on_success_fn(
            nb_char_erased=nb_char_erased, new_text_value=new_text_value
        ),
        additional_kwargs={"error": output} if has_failed else {},
    )

    return Command(
        update=erase_text_wrapper.handle_executor_state_fields(
            executor_metadata=executor_metadata,
            tool_message=tool_message,
            is_failure=has_failed,
            updates={
                "agents_thoughts": [agent_thought],
                "messages": [tool_message],
            },
        ),
    )


def format_success_message(nb_char_erased: int, new_text_value: Optional[str]):
    output = ""
    if nb_char_erased == -1:
        output = "Text erased successfully."
    else:
        output = f"Text erased successfully. {nb_char_erased} characters were erased."
    if new_text_value is not None:
        output += f" New text in the input is {new_text_value}."
    return output


erase_text_wrapper = ToolWrapper(
    tool_fn=erase_text,
    on_success_fn=format_success_message,
    on_failure_fn=lambda output: "Failed to erase text. " + output,
)
