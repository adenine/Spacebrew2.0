import argparse
import threading
import sys

# Import modules
from router import SpacebrewRouter
from mqtt_service import SpacebrewMQTT
from web_service import SpacebrewWebServer
from cli import SpacebrewCLI

def run():
    # 1. Parse CLI arguments
    parser = argparse.ArgumentParser(description='Spacebrew 2.0 Router')
    parser.add_argument('--server', type=str, default='localhost', help='MQTT Broker address')
    parser.add_argument('--port', type=int, default=1883, help='MQTT Broker port')
    args = parser.parse_args()
    
    broker = args.server
    port = args.port

    # 2. Initialize Components
    router = SpacebrewRouter()
    mqtt_service = SpacebrewMQTT(router, broker, port)
    web_service = SpacebrewWebServer(router, mqtt_service, port=8088)
    cli = SpacebrewCLI(router, mqtt_service)

    # 3. Start MQTT Service
    mqtt_service.connect()
    mqtt_service.start()

    # 4. Start CLI in a separate thread
    def run_cli():
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            pass
            
    cli_thread = threading.Thread(target=run_cli, daemon=True)
    cli_thread.start()

    # 5. Start Web Service (Main Thread)
    # Uvicorn needs to run in the main thread for signal handling usually, 
    # or at least it blocks.
    try:
        web_service.start()
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down...")
        mqtt_service.stop()

if __name__ == '__main__':
    run()