from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

from minitap.clients.device_hardware_client import get_client as get_device_hardware_client
from minitap.clients.screen_api_client import get_client as get_screen_api_client
from minitap.utils.errors import ControllerErrors
from minitap.utils.logger import get_logger

screen_api = get_screen_api_client()
device_hardware_api = get_device_hardware_client()
logger = get_logger(__name__)


###### Screen elements retrieval ######


class ScreenDataResponse(BaseModel):
    base64: str
    elements: list
    width: int
    height: int
    platform: str


def get_screen_data():
    response = screen_api.get("/screen-info")
    return ScreenDataResponse(**response.json())


def take_screenshot():
    return get_screen_data().base64


class RunFlowRequest(BaseModel):
    yaml: str
    dry_run: bool = Field(default=False, alias="dryRun")


def run_flow(yaml: str, dry_run: bool = False):
    logger.info(f"Running flow: {yaml}")
    payload = RunFlowRequest(yaml=yaml, dryRun=dry_run).model_dump(by_alias=True)
    response = device_hardware_api.post("run-command", json=payload)
    logger.info("Status code: " + str(response.status_code))
    json_response = response.json()
    json_response = {k: v for k, v in json_response.items() if v is not None}
    return json_response


class CoordinatesSelectorRequest(BaseModel):
    x: int
    y: int


class PercentagesSelectorRequest(BaseModel):
    """
    0%,0%        # top-left corner
    100%,100%    # bottom-right corner
    50%,50%      # center
    """

    x_percent: int
    y_percent: int


class SelectorRequest(BaseModel):
    id: Optional[str] = None
    coordinates: Optional[CoordinatesSelectorRequest] = None
    percentages: Optional[PercentagesSelectorRequest] = None
    text: Optional[str] = None


def format_selector_request_for_yaml(request: SelectorRequest):
    if not request.id and not request.coordinates and not request.percentages and not request.text:
        return None
    yaml = ""
    if request.id:
        yaml += f"\n id: {request.id}\n"
    elif request.coordinates:
        yaml += f"\n point: {request.coordinates.x},{request.coordinates.y}\n"
    elif request.percentages:
        yaml += f"\n point: {request.percentages.x_percent}%,{request.percentages.y_percent}%\n"
    elif request.text:
        yaml += f"\n text: {request.text}\n"
    return yaml


def tap(selector_request: SelectorRequest, dry_run: bool = False, index: Optional[int] = None):
    """
    Tap on a selector.
    Index is optional and is used when you have multiple views matching the same selector.
    """
    yaml = format_selector_request_for_yaml(selector_request)
    if not yaml:
        error = "Invalid tap selector request, could not format yaml"
        logger.error(error)
        raise ControllerErrors(error)
    flow_input = f"tapOn:{yaml}"
    if index:
        flow_input += f"\nindex: {index}\n"
    return run_flow(flow_input, dry_run=dry_run)


def long_press_on(
    selector_request: SelectorRequest, dry_run: bool = False, index: Optional[int] = None
):
    yaml = format_selector_request_for_yaml(selector_request)
    if not yaml:
        error = "Invalid long press on selector request, could not format yaml"
        logger.error(error)
        raise ControllerErrors(error)
    flow_input = f"longPressOn:{yaml}"
    if index:
        flow_input += f"\nindex: {index}\n"
    return run_flow(flow_input, dry_run=dry_run)


class SwipeStartEndCoordinatesRequest(BaseModel):
    start: CoordinatesSelectorRequest
    end: CoordinatesSelectorRequest


class SwipeStartEndPercentagesRequest(BaseModel):
    start: PercentagesSelectorRequest
    end: PercentagesSelectorRequest


class SwipeRequest(BaseModel):
    start_end_coordinates: Optional[SwipeStartEndCoordinatesRequest] = None
    start_end_percentages: Optional[SwipeStartEndPercentagesRequest] = None
    direction: Optional[Literal["UP", "DOWN", "LEFT", "RIGHT"]] = None
    duration: Optional[int] = None  # in ms, default is 400ms


def swipe(swipe_request: SwipeRequest, dry_run: bool = False):
    yaml = ""
    if swipe_request.start_end_coordinates:
        yaml += f"\n start: {swipe_request.start_end_coordinates.start.x},"
        yaml += f"{swipe_request.start_end_coordinates.start.y}\n"
        yaml += f"\n end: {swipe_request.start_end_coordinates.end.x},"
        yaml += f"{swipe_request.start_end_coordinates.end.y}\n"
    elif swipe_request.start_end_percentages:
        yaml += f"\n start: {swipe_request.start_end_percentages.start.x_percent}%,"
        yaml += f"{swipe_request.start_end_percentages.start.y_percent}%\n"
        yaml += f"\n end: {swipe_request.start_end_percentages.end.x_percent}%,"
        yaml += f"{swipe_request.start_end_percentages.end.y_percent}%\n"
    if swipe_request.direction:
        yaml += f"\n direction: {swipe_request.direction}\n"
    if swipe_request.duration:
        yaml += f"\n duration: {swipe_request.duration}\n"
    if not yaml:
        error = "Invalid swipe selector request, could not format yaml"
        logger.error(error)
        raise ControllerErrors(error)
    return run_flow(f"swipe:{yaml}", dry_run=dry_run)


##### Text related commands #####


def input_text(text: str, dry_run: bool = False):
    return run_flow(f"inputText: {text}\n", dry_run=dry_run)


def copy_text_from(selector_request: SelectorRequest, dry_run: bool = False):
    yaml = format_selector_request_for_yaml(selector_request)
    if not yaml:
        error = "Invalid copy text from selector request, could not format yaml"
        logger.error(error)
        raise ControllerErrors(error)
    return run_flow(f"copyTextFrom:{yaml}\n", dry_run=dry_run)


def paste_text(dry_run: bool = False):
    return run_flow("pasteText\n", dry_run=dry_run)


def erase_text(nb_chars: Optional[int] = None, dry_run: bool = False):
    """
    Removes characters from the currently selected textfield (if any)
    Removes 50 characters if nb_chars is not specified.
    """
    if nb_chars is None:
        return run_flow("eraseText\n", dry_run=dry_run)
    return run_flow(f"eraseText: {nb_chars}\n", dry_run=dry_run)


##### App related commands #####


def launch_app(package_name: str, dry_run: bool = False):
    return run_flow(f"launchApp: {package_name}\n", dry_run=dry_run)


def stop_app(package_name: str, dry_run: bool = False):
    return run_flow(f"stopApp: {package_name}\n", dry_run=dry_run)


def open_link(url: str, dry_run: bool = False):
    return run_flow(f"openLink: {url}\n", dry_run=dry_run)


##### Key related commands #####


def back(dry_run: bool = False):
    return run_flow("back\n", dry_run=dry_run)


class Key(Enum):
    ENTER = "Enter"
    HOME = "Home"
    BACK = "Back"


def press_key(key: Key, dry_run: bool = False):
    return run_flow(f"pressKey: {key.value}\n", dry_run=dry_run)


#### Other commands ####


class WaitTimeout(Enum):
    SHORT = 500
    MEDIUM = 1000
    LONG = 5000


def wait_for_animation_to_end(timeout: Optional[WaitTimeout] = None, dry_run: bool = False):
    if timeout is None:
        return run_flow("waitForAnimationToEnd\n", dry_run=dry_run)
    return run_flow(f"waitForAnimationToEnd:\n  timeout: {timeout.value}\n", dry_run=dry_run)


if __name__ == "__main__":
    launch_app("org.mozilla.firefox")
    tap(SelectorRequest(text="Search or enter.*"))
    input_text("tesla model s")
    wait_for_animation_to_end()
    press_key(Key.ENTER)
    wait_for_animation_to_end()
    print("done")
