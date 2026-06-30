import os
import subprocess
import sys
import threading
import webbrowser

import pystray
import uvicorn
from PIL import Image, ImageDraw

from mqtt_service import SpacebrewMQTT
from router import SpacebrewRouter
from tray_config import load_config
from web_service import SpacebrewWebServer

APP_DIR = os.path.dirname(os.path.abspath(__file__))
RUNNING_COLOR = (0, 170, 0, 255)
STOPPED_COLOR = (190, 0, 0, 255)


def make_icon_image(color):
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, size - 8, size - 8), fill=color)
    return image


class SpacebrewTrayApp:
    def __init__(self):
        self.config = load_config()
        self.router = None
        self.mqtt_service = None
        self.web_service = None
        self.uvicorn_server = None
        self.server_thread = None
        self.running = False

        self.icon = pystray.Icon(
            "spacebrew",
            make_icon_image(STOPPED_COLOR),
            "Spacebrew 2.0 — Stopped",
            menu=self.build_menu(),
        )

    def build_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Spacebrew 2.0", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Server Running", self.toggle_server, checked=lambda item: self.running),
            pystray.MenuItem("Settings...", self.open_settings),
            pystray.MenuItem("Open Web Admin", self.open_web_admin),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app),
        )

    def toggle_server(self, icon, item):
        if self.running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        if self.running:
            return

        self.config = load_config()
        self.router = SpacebrewRouter()
        self.mqtt_service = SpacebrewMQTT(self.router, self.config["broker"], self.config["broker_port"])
        self.web_service = SpacebrewWebServer(self.router, self.mqtt_service, port=self.config["web_port"])

        # Connect directly rather than via mqtt_service.connect(), which calls
        # sys.exit(1) on failure -- fine for the CLI app, fatal for a tray app.
        try:
            self.mqtt_service.client.connect(self.mqtt_service.broker, self.mqtt_service.port)
        except Exception as e:
            self._notify(f"Could not connect to MQTT broker at {self.mqtt_service.broker}:{self.mqtt_service.port}")
            print(f"Error connecting to broker: {e}")
            return

        self.mqtt_service.start()

        uvicorn_config = uvicorn.Config(
            self.web_service.app,
            host=self.web_service.host,
            port=self.web_service.port,
            log_level="error",
        )
        self.uvicorn_server = uvicorn.Server(uvicorn_config)
        self.server_thread = threading.Thread(target=self.uvicorn_server.run, daemon=True)
        self.server_thread.start()

        self.running = True
        self._update_icon()

    def stop_server(self):
        if not self.running:
            return

        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        if self.server_thread:
            self.server_thread.join(timeout=5)
        if self.mqtt_service:
            self.mqtt_service.stop()

        self.running = False
        self._update_icon()

    def _update_icon(self):
        status = "Running" if self.running else "Stopped"
        self.icon.icon = make_icon_image(RUNNING_COLOR if self.running else STOPPED_COLOR)
        self.icon.title = f"Spacebrew 2.0 — {status}"
        self.icon.update_menu()

    def _notify(self, message):
        try:
            self.icon.notify(message, "Spacebrew 2.0")
        except Exception:
            print(message)

    def open_settings(self, icon, item):
        subprocess.Popen([sys.executable, os.path.join(APP_DIR, "settings_window.py")])

    def open_web_admin(self, icon, item):
        webbrowser.open(f"http://localhost:{self.config.get('web_port', 8088)}")

    def quit_app(self, icon, item):
        self.stop_server()
        icon.stop()

    def run(self):
        self.icon.run()


if __name__ == "__main__":
    SpacebrewTrayApp().run()
