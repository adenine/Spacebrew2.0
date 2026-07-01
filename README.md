# Spacebrew 2.0

A dynamic re-routable software toolkit for choreographing interactive spaces utilizing MQTT.

Spacebrew 2.0 is a router that sits between your interactive devices (clients) and an MQTT broker. It allows you to dynamically route messages between publishers and subscribers without changing the code on the devices themselves.

## Features
- **Dynamic Routing**: Connect publishers to subscribers on the fly via a web interface or CLI.
- **Multiple Pubs/Subs**: Clients can have multiple publishers and subscribers.
- **Web Interface**: A real-time dashboard to manage clients, routes, and visualize activity, with live message content and per-client activity indicators.
- **WebSocket Gateway**: Connect web-based clients directly to the Spacebrew network.
- **Automatic Disconnect Detection**: Clients that crash, lose power, or close their connection are automatically deregistered — no polling required.
- **Persistence**: Routes are automatically saved and loaded.
- **Tray App**: Run the server as a menu bar app instead of a terminal process.

## Prerequisites

Before running Spacebrew 2.0, you need:

1.  **Python 3.7+**: Ensure Python is installed.
2.  **MQTT Broker**: You need a running MQTT broker (e.g., Mosquitto).
    -   **Mac (Homebrew)**: `brew install mosquitto` -> `brew services start mosquitto`
    -   **Linux (apt)**: `sudo apt install mosquitto` -> `sudo systemctl start mosquitto`
    -   **Windows**: Download and install from [mosquitto.org](https://mosquitto.org/download/).
3.  **Node.js 18+**: Only needed to build the new web admin SPA (see [Web Admin](#web-admin-new) below).

## Installation

1.  Clone this repository.
2.  Install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

Start the Spacebrew 2.0 Router using the following command:

```bash
python3 main.py
```

By default, it connects to an MQTT broker at `localhost:1883` and starts the web interface at `http://localhost:8088`.

### Command Line Arguments

You can override the default broker settings:

```bash
python3 main.py --server <broker_address> --port <broker_port>
```

**Example:**
```bash
python3 main.py --server 192.168.1.100 --port 1883
```

## Usage

### Tray App
Instead of running `main.py` from a terminal, you can run Spacebrew as a system tray / menu bar app:

```bash
python3 tray_app.py
```

On macOS, you can instead double-click `Spacebrew.command` in Finder, which opens a Terminal window and launches the tray app for you.

This adds a Spacebrew icon to your tray with:
-   **Start Server / Stop Server**: toggles the MQTT router and web server on/off (no terminal required).
-   **Settings...**: edit the broker address/port and web admin port (saved to `spacebrew_config.json`; restart the server from the menu to apply).
-   **Open Web Admin**: opens the [new web admin SPA](#web-admin-new) (`/app/`) in your default browser — build it first (see below) or this will 404.
-   **Quit**: stops the server and exits.

> Settings are edited in a small Tkinter window. On Linux, Tkinter may need a separate package, e.g. `sudo apt install python3-tk`. On macOS, if the settings window appears blank, install a modern Tk via `brew install python-tk@3.11` — the bundled system Tk (8.5) doesn't render correctly in Dark Mode.

### Web Interface
Open your browser and navigate to `http://localhost:8088` (or the IP address of the machine running the server).
-   **Dashboard**: View registered clients and current routes.
-   **Registered Clients**: Shows each client's publishers/subscribers, the last message seen on any of their topics, and an indicator dot that blinks on new activity.
-   **Add Route**: Select a publisher and subscriber to create a connection.
-   **Visual Feedback**: LEDs blink when messages are routed.
-   **Web Client**: Click "Open Web Client" to launch a browser-based client for testing.

### Web Admin (New)
A React + Rete.js rebuild of the dashboard, styled after the original 2012 Spacebrew admin UI, with a visual patch bay for connecting publishers to subscribers by dragging or clicking between sockets. This is what the tray app's **Open Web Admin** menu item opens.

It has to be built once before the server can serve it (this produces `web/dist`, which is gitignored — rebuild after pulling changes to `web/`):

```bash
cd web
npm install
npm run build
```

Then restart the Spacebrew server and open `http://localhost:8088/app/`.

For active frontend development, run the Vite dev server instead (proxies `/api` and `/ws` to the Python backend on `:8088`, with hot reload):

```bash
cd web
npm run dev
```

### Command Line Interface (CLI)
The terminal running `main.py` also provides a CLI for management:
-   `clients`: List registered clients.
-   `routes`: List current routes.
-   `addroute <pub> <sub>`: Add a route.
-   `delroute <pub>`: Delete a route.
-   `testclient`: Spawn a temporary test client.

## Examples

Check the `Examples` folder for client implementations:
-   **Python**: `Examples/Python/simple_client.py`
-   **Web (JS/HTML)**: `Examples/Web/simple_client.html`
-   **Arduino**: `Examples/Arduino/arduino_client.ino`
-   **Processing**: `Examples/Processing/processing_client.pde`

## Client Disconnect Detection

The router deregisters a client as soon as it disconnects, rather than leaving stale entries in the dashboard:
-   **MQTT clients** (Python, Arduino, Processing) should register an MQTT **Last Will** that publishes their name to `YuxiSpace/leave` — the broker sends it automatically if the connection drops uncleanly (crash, power loss, network failure). See any file in `Examples/` for how to set this up in your client library. Clients that exit cleanly should also publish to `YuxiSpace/leave` explicitly before disconnecting, since a clean disconnect doesn't trigger the will message.
-   **Web clients** (using the `/ws/client` WebSocket bridge) are deregistered automatically when their WebSocket connection closes — no extra code needed.

## TODO
- [x] Support multiple publishers/subscribers
- [x] Unique client name enforcement
- [x] CLI arguments for server/port
- [x] Web Interface
- [ ] Add new types (image, audio, video)
- [ ] Bag file recording/playback
- [ ] Force client disconnect
- [ ] Make it possible accept an MQTT message to create a new route
- [ ] Make it possible accept an MQTT message to delete a route
