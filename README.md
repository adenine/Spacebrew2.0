# Spacebrew 2.0

A dynamic re-routable software toolkit for choreographing interactive spaces utilizing MQTT.

Spacebrew 2.0 is a router that sits between your interactive devices (clients) and an MQTT broker. It allows you to dynamically route messages between publishers and subscribers without changing the code on the devices themselves.

## Features
- **Dynamic Routing**: Connect publishers to subscribers on the fly via a web interface or CLI.
- **Multiple Pubs/Subs**: Clients can have multiple publishers and subscribers.
- **Web Interface**: A real-time dashboard to manage clients, routes, and visualize activity.
- **WebSocket Gateway**: Connect web-based clients directly to the Spacebrew network.
- **Persistence**: Routes are automatically saved and loaded.

## Prerequisites

Before running Spacebrew 2.0, you need:

1.  **Python 3.7+**: Ensure Python is installed.
2.  **MQTT Broker**: You need a running MQTT broker (e.g., Mosquitto).
    -   **Mac (Homebrew)**: `brew install mosquitto` -> `brew services start mosquitto`
    -   **Linux (apt)**: `sudo apt install mosquitto` -> `sudo systemctl start mosquitto`
    -   **Windows**: Download and install from [mosquitto.org](https://mosquitto.org/download/).

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

### Web Interface
Open your browser and navigate to `http://localhost:8088` (or the IP address of the machine running the server).
-   **Dashboard**: View registered clients and current routes.
-   **Add Route**: Select a publisher and subscriber to create a connection.
-   **Visual Feedback**: LEDs blink when messages are routed.
-   **Web Client**: Click "Open Web Client" to launch a browser-based client for testing.

### Command Line Interface (CLI)
The terminal running `main.py` also provides a CLI for management:
-   `clients`: List registered clients.
-   `routes`: List current routes.
-   `addroute <pub> <sub>`: Add a route.
-   `delroute <pub>`: Delete a route.
-   `testclient`: Spawn a temporary test client.

## Examples

Check the `Examples` folder for client implementations:
-   **Python**: `Examples/simple_client.py`
-   **Web (JS/HTML)**: `Examples/simple_client.html`
-   **Arduino**: `Examples/arduino_client.ino`
-   **Processing**: `Examples/processing_client.pde`

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
