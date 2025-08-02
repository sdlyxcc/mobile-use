import base64
import json
import threading
import time
from contextlib import asynccontextmanager

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sseclient import SSEClient

from minitap.servers.device_hardware_bridge import MAESTRO_STUDIO_PORT

DEVICE_SCREEN_API_PORT = 9998

MAESTRO_STUDIO_SERVER_ROOT = f"http://localhost:{MAESTRO_STUDIO_PORT}"
MAESTRO_STUDIO_API_URL = f"{MAESTRO_STUDIO_SERVER_ROOT}/api"

_latest_screen_data = None
_data_lock = threading.Lock()
_stream_thread = None
_stop_event = threading.Event()


def _stream_worker():
    global _latest_screen_data
    sse_url = f"{MAESTRO_STUDIO_API_URL}/device-screen/sse"
    headers = {"Accept": "text/event-stream"}

    while not _stop_event.is_set():
        try:
            with requests.get(sse_url, stream=True, headers=headers) as response:
                response.raise_for_status()
                print("--- Stream connected, listening for events... ---")
                event_source = (chunk for chunk in response.iter_content())
                client = SSEClient(event_source)
                for event in client.events():
                    if _stop_event.is_set():
                        break
                    if event.event == "message" and event.data:
                        data = json.loads(event.data)
                        screenshot_path = data.get("screenshot")
                        elements = data.get("elements", [])
                        width = data.get("width")
                        height = data.get("height")
                        platform = data.get("platform")

                        image_url = f"{MAESTRO_STUDIO_SERVER_ROOT}{screenshot_path}"
                        image_response = requests.get(image_url)
                        image_response.raise_for_status()
                        base64_image = base64.b64encode(image_response.content).decode("utf-8")
                        base64_data_url = f"data:image/png;base64,{base64_image}"

                        with _data_lock:
                            _latest_screen_data = {
                                "base64": base64_data_url,
                                "elements": elements,
                                "width": width,
                                "height": height,
                                "platform": platform,
                            }

        except requests.exceptions.RequestException as e:
            print(f"Connection error in stream worker: {e}. Retrying in 2 seconds...")
            with _data_lock:
                _latest_screen_data = None
            time.sleep(2)


def start_stream():
    global _stream_thread
    if _stream_thread is None or not _stream_thread.is_alive():
        _stop_event.clear()
        _stream_thread = threading.Thread(target=_stream_worker, daemon=True)
        _stream_thread.start()
        print("--- Background screen streaming started ---")


def stop_stream():
    global _stream_thread
    if _stream_thread and _stream_thread.is_alive():
        _stop_event.set()
        _stream_thread.join(timeout=2)
        print("--- Background screen streaming stopped ---")


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_stream()
    yield
    stop_stream()


app = FastAPI(lifespan=lifespan)


def get_latest_data():
    """Helper to get the latest data safely."""
    with _data_lock:
        if _latest_screen_data is None:
            raise HTTPException(
                status_code=503,
                detail="Screen data is not yet available. Please try again shortly.",
            )
        return _latest_screen_data


@app.get("/screen-info")
async def get_screen_info():
    data = get_latest_data()
    return JSONResponse(content=data)


@app.get("/health-check")
async def health_check():
    """Check if the Maestro Studio server is healthy."""
    health_url = f"{MAESTRO_STUDIO_API_URL}/banner-message"
    try:
        response = requests.get(health_url, timeout=5)
        response.raise_for_status()
        return JSONResponse(content=response.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Maestro Studio not available: {e}")


def start():
    print("--- Starting Maestro Screen Server ---")
    uvicorn.run(app, host="0.0.0.0", port=DEVICE_SCREEN_API_PORT)


if __name__ == "__main__":
    start()
