import base64
from io import BytesIO

from minitap.client.adb import get_device


def get_focused_app_info():
    device = get_device()
    result = device.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
    return result


def get_screen_size():
    device = get_device()
    width, height = device.window_size()
    return width, height


def get_date():
    device = get_device()
    result = device.shell("date")
    return result


def get_screenshot_base64():
    device = get_device()
    image = device.screenshot()
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")
