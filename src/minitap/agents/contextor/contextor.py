from minitap.agents.executor.utils import is_last_tool_message_take_screenshot
from minitap.controllers.mobile_command_controller import get_screen_data
from minitap.controllers.platform_specific_commands_controller import (
    get_device_date,
    get_focused_app_info,
)
from minitap.graph.state import State
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Contextor Agent"),
    on_success=lambda _: logger.info("Contextor Agent ✅"),
    on_failure=lambda _: logger.info("Contextor Agent ❌"),
)
def contextor_node(state: State):
    device_data = get_screen_data()
    focused_app_info = get_focused_app_info()
    device_date = get_device_date()

    should_add_screenshot_context = is_last_tool_message_take_screenshot(list(state.messages))

    return {
        "latest_screenshot_base64": device_data.base64 if should_add_screenshot_context else None,
        "latest_ui_hierarchy": device_data.elements,
        "focused_app_info": focused_app_info,
        "screen_size": (device_data.width, device_data.height),
        "device_date": device_date,
    }
