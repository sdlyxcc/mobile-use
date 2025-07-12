import adbutils
from adbutils import AdbDevice

adb = adbutils.AdbClient(host="127.0.0.1", port=5037)


def get_device() -> AdbDevice:
    """Gets the first available device."""
    devices = adb.device_list()
    if not devices:
        raise ConnectionError("No device found.")
    return devices[0]


# TODO Deal with the IOS case
