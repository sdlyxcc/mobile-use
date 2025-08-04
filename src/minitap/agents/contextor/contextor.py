from minitap.controllers.mobile_command_controller import get_screen_data
from minitap.controllers.platform_specific_commands_controller import (
    get_device_date,
    get_focused_app_info,
)
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Contextor Agent...", end="", flush=True),
    on_success=lambda _: logger.info("Contextor Agent ✅", flush=True),
    on_failure=lambda _: logger.info("Contextor Agent ❌", flush=True),
)
def contextor_node():
    device_data = get_screen_data()
    focused_app_info = get_focused_app_info()
    device_date = get_device_date()

    return {
        "latest_screenshot_base64": device_data.base64,
        "latest_ui_hierarchy": device_data.elements,
        "focused_app_info": focused_app_info,
        "screen_size": (device_data.width, device_data.height),
        "device_date": device_date,
    }
