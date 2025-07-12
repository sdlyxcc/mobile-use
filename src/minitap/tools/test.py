from minitap.client.adb import get_device

print("Starting app...")

device = get_device()

cmd = "monkey -p com.google.android.gm -c android.intent.category.LAUNCHER 1"
output: str = device.shell(cmd + " && echo OK || echo KO")  # type: ignore
print(type(output))
print(output)
