from typing import Optional

from pydantic import BaseModel, Field

from minitap.clients.device_hardware_client import get_client as get_device_hardware_client
from minitap.clients.screen_api_client import get_client as get_screen_api_client
from minitap.utils.errors import ControllerErrors
from minitap.utils.logger import get_logger

screen_api = get_screen_api_client()
device_hardware_api = get_device_hardware_client()
logger = get_logger(__name__)


class ScreenDataResponse(BaseModel):
    base64: str
    elements: list
    width: int
    height: int
    platform: str


def get_screen_data():
    response = screen_api.get("/screen-info")
    return ScreenDataResponse(**response.json())


class RunFlowRequest(BaseModel):
    yaml: str
    dry_run: bool = Field(default=False, alias="dryRun")


def run_flow(yaml: str, dry_run: bool = False):
    logger.info(f"Running flow: {yaml}")
    payload = RunFlowRequest(yaml=yaml, dryRun=dry_run).model_dump(by_alias=True)
    response = device_hardware_api.post("run-command", json=payload)
    logger.info("Status code: " + str(response.status_code))
    logger.info("Raw response text: " + response.text)
    return response.json()


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
        yaml += f" {request.text}\n"
    return yaml


def tap(request: SelectorRequest):
    yaml = format_selector_request_for_yaml(request)
    if not yaml:
        error = "Invalid tap selector request, could not format yaml"
        logger.error(error)
        raise ControllerErrors(error)
    return run_flow(f"tapOn:{yaml}")


def long_press_on(request: SelectorRequest):
    yaml = format_selector_request_for_yaml(request)
    if not yaml:
        error = "Invalid long press on selector request, could not format yaml"
        logger.error(error)
        raise ControllerErrors(error)
    return run_flow(f"longPressOn:{yaml}")


def back():
    return run_flow("back\n", dry_run=True)


def erase_text(nb_chars: Optional[int] = None):
    """
    Removes characters from the currently selected textfield (if any)
    Removes 50 characters if nb_chars is not specified.
    """
    if nb_chars is None:
        return run_flow("eraseText\n")
    return run_flow(f"eraseText: {nb_chars}\n")


if __name__ == "__main__":
    back()
