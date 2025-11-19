# spacebrew2 - FINAL VERSION (Added auto-save for route modification)
import sys
import time
import random
import cmd
import os 
from paho.mqtt import client as mqtt_client
import Spacebrew2Client as sb2 
import argparse 

# TODO:
# DONE - Make it so that you can have multiple publishers or subsribers
# DONE - Don't add a client unless it has a unique name
# DONE - Pass in the server (broker) and port from CLI args
# DONE - Chnage pubs and subs to have types: boolean, range, string, json
# Add new types like image, audio, video 
# Add an ability to start recording into a bag file and add the ability to play the bag file back
# Create a web interface with the same capabilities as the CLI
# Add error handling for file read/write operations
# Add an ability to force clients to disconnect
# Make it possible accept an MQTT message to create a new route
# Make it possible accept an MQTT message to delete a route



# Setup MQTT Broker details
broker = 'localhost'
port = 1883
p_topic = "Spacebrew2/server"
s_topic = "#" 
client_id = f'Spacebrew2_Router_{random.randint(0, 100000)}'
ClientArray = []

# --- Persistent Data Settings ---
ROUTE_FILE = 'routes.txt'

# Default routes are only used if the file is brand new and empty.
DEFAULT_ROUTES = {
    "VirtualButton1/button": "VirtualButton2/bgcolor",
    "VirtualButton2/button": "VirtualButton1/bgcolor"
}
Spacebrew2Routes = {}
# --- End Persistent Data Settings ---

def save_routes():
    """Save the current routing table to the routes.txt file."""
    try:
        with open(ROUTE_FILE, 'w') as f:
            f.write("# Spacebrew2 Router Routes: Publisher, Subscriber\n")
            for pub, sub in Spacebrew2Routes.items():
                # Write in "publisher_topic,subscriber_topic" format
                f.write(f"{pub},{sub}\n")
        return True
    except Exception as e:
        # This print is kept for non-CLI critical errors
        print(f"Error saving routes to file: {e}")
        return False

def load_routes():
    """
    Load the routing table from routes.txt. 
    If the file doesn't exist, create it with default routes.
    """
    global Spacebrew2Routes
    
    if not os.path.exists(ROUTE_FILE):
        print(f"File '{ROUTE_FILE}' not found. Creating file with default routes.")
        Spacebrew2Routes = DEFAULT_ROUTES.copy() # Use a copy of defaults
        save_routes() # Create the file immediately
        return 

    # If the file exists, attempt to load it
    loaded_routes = {}
    try:
        with open(ROUTE_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(',', 1)
                if len(parts) == 2:
                    pub_topic = parts[0].strip()
                    sub_topic = parts[1].strip()
                    loaded_routes[pub_topic] = sub_topic
        
        Spacebrew2Routes = loaded_routes
        print(f"Routes loaded successfully from '{ROUTE_FILE}'. Total routes: {len(Spacebrew2Routes)}")

    except Exception as e:
        print(f"Error loading routes from file: {e}. Using current routes instead.")
        
class MyCLI(cmd.Cmd):
    def __init__(self, mqtt_client_instance):
        super().__init__()
        self.mqtt_client = mqtt_client_instance
        self.prompt = '>> '
        self.intro = 'Welcome to Spacebrew 2.0. Type "help" for available commands.'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")
    
    def do_quit(self, line):
        """Exit the CLI and stop the MQTT loop."""
        print("Stopping MQTT loop and exiting.")
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()
        return True
    
    def do_routes(self, line):
        """Show the current Spacebrew routing table."""
        if not Spacebrew2Routes:
            print("The routing table is empty.")
            return

        print("--- Current Routes ---")
        for pub, sub in Spacebrew2Routes.items():
            print(f"  {pub} -> {sub}")
        print("----------------------")
        print(f"Total routes: {len(Spacebrew2Routes)}")

    def do_saveroutes(self, line):
        """Save the current routing table to the routes.txt file."""
        if save_routes():
            print(f"✅ Routes successfully saved to '{ROUTE_FILE}'.")
        else:
            print(f"❌ Failed to save routes to '{ROUTE_FILE}'.")
            
    def do_addroute(self, line):
        """
        Add a new route. Usage: addroute <publisher_topic> <subscriber_topic>
        Note: Topics must not contain spaces. Automatically saves on success.
        """
        try:
            parts = line.split()
            if len(parts) != 2:
                raise ValueError("Requires exactly two arguments: publisher and subscriber topic.")

            pub = parts[0].strip()
            sub = parts[1].strip()
            
            # Check if route already exists
            if pub in Spacebrew2Routes and Spacebrew2Routes[pub] == sub:
                 print(f"Route already exists: {pub} -> {sub}")
                 return

            Spacebrew2Routes[pub] = sub
            print(f"✅ Route added: {pub} -> {sub}")
            
            # --- AUTO-SAVE ADDED HERE ---
            if save_routes():
                print(f"✅ Routes automatically saved to '{ROUTE_FILE}'.")
            # ---------------------------
        
        except ValueError as e:
            print(f"Error: {e}")
            print("Usage: addroute <publisher_topic> <subscriber_topic>")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def do_delroute(self, line):
        """
        Delete a route by its publisher topic. Usage: delroute <publisher_topic>
        Automatically saves on success.
        """
        topic = line.strip()
        if not topic:
            print("Usage: delroute <publisher_topic>")
            return
            
        try:
            # Pop the item and store the subscriber topic for display
            sub_topic = Spacebrew2Routes.pop(topic)
            print(f"🗑️ Route deleted: {topic} -> {sub_topic}")
            
            # --- AUTO-SAVE ADDED HERE ---
            if save_routes():
                print(f"✅ Routes automatically saved to '{ROUTE_FILE}'.")
            # ---------------------------
            
        except KeyError:
            print(f"❌ Error: Publisher topic '{topic}' not found in routes.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def do_server(self,line):
        """Show the current broker and port."""
        print(f"Broker: {broker}, Port: {port}")
    
    def do_clients(self,line):
        """Show the names of currently registered clients."""
        if not ClientArray:
            print("No clients are currently registered.")
            return

        print("--- Registered Clients ---")
        for i, client_obj in enumerate(ClientArray):
            try:
                # Use clientName as per previous fix
                client_name = client_obj.clientName
            except AttributeError:
                client_name = "[Name Not Available]"
                
            print(f"{i + 1}. {client_name}")
        print(f"--------------------------")
        print(f"Total: {len(ClientArray)} clients.")

    def do_connection(self, line):
        """Check the current MQTT server connection status."""
        if self.mqtt_client.is_connected():
            print(f"🟢 **Connected** to MQTT Broker at {broker}:{port}")
        else:
            print(f"🔴 **Disconnected** from MQTT Broker at {broker}:{port}")

    def do_testclient(self, line):
        """
        Spawn a test client in a separate process.
        Usage: testclient
        """
        import subprocess
        try:
            # Check if the file exists
            if not os.path.exists("SpacebrewClientTest.py"):
                print("❌ Error: 'SpacebrewClientTest.py' not found in the current directory.")
                return

            print("🚀 Spawning test client...")
            # Run the script in a new process
            # using sys.executable ensures we use the same python interpreter
            subprocess.Popen([sys.executable, "SpacebrewClientTest.py"])
            print("✅ Test client started in background.")
            
        except Exception as e:
            print(f"❌ Error starting test client: {e}")

    def do_publish(self, line):
        """
        Publish an MQTT message. Usage: publish <topic> <message>
        Example: publish VirtualButton1/button 1
        """
        try:
            parts = line.split(' ', 1)
            topic = parts[0].strip()
            message = parts[1].strip()

            if not topic or not message:
                raise ValueError("Missing topic or message.")
            
            result = self.mqtt_client.publish(topic, message, qos=1) 
            status = result[0]
            
            if status == 0:
                print(f"✅ Published: '{message}' to topic '{topic}'")
            else:
                print(f"❌ Failed to publish message to topic {topic}. Status: {status}")

        except IndexError:
            print("Error: Usage is 'publish <topic> <message>'")
        except Exception as e:
            print(f"An error occurred: {e}")

def connect_mqtt(broker_addr, broker_port):
    
    def on_connect(client, userdata, flags, reason_code):
        if reason_code != 0:
            print(f"🔴 Failed to connect to MQTT Broker, return code {reason_code}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    
    try:
        client.connect(broker_addr, broker_port)
        return client
    except Exception as e:
        print(f"Error connecting to broker: {e}")
        sys.exit(1)


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        # Only print received messages to the console
        print(f"\n[RX] Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        
        # --- Registration Logic (Silent) ---
        if msg.topic == "YuxiSpace":
            try:
                # Format: name, desc, pubs(p1:t,p2:t), subs(s1:t,s2:t)
                msg_str = msg.payload.decode()
                
                import re
                # Regex to capture: name, desc, pubs(...), subs(...)
                # This regex handles the format: name, desc, pubs(pub1:type, pub2:type), subs(sub1:type, sub2:type)
                # It is robust to spaces around commas.
                match = re.match(r'^([^,]+),\s*([^,]+),\s*pubs\((.*)\),\s*subs\((.*)\)$', msg_str)
                
                if match:
                    name = match.group(1).strip()
                    desc = match.group(2).strip()
                    pubs_str = match.group(3).strip()
                    subs_str = match.group(4).strip()
                    
                    # Parse pubs and subs lists
                    # They are inside the parens: "pub1:type, pub2:type"
                    pubs = [p.strip() for p in pubs_str.split(',')] if pubs_str else []
                    subs = [s.strip() for s in subs_str.split(',')] if subs_str else []
                    
                    p = [name, desc, pubs, subs]
                else:
                     # Fallback to old split if regex fails (legacy support or simple format)
                     p = msg_str.split(',')
                     # If it was the old format, p[2] and p[3] are just single strings
                     # We wrap them in lists to be consistent
                     if len(p) >= 4:
                         p[2] = [p[2].strip()]
                         p[3] = [p[3].strip()]
                
                if len(p) >= 4:
                    # p[0] is the client name
                    if not any(c.clientName == p[0] for c in ClientArray):
                        tSb = sb2.Spacebrew2Client(p[0],p[1],p[2],p[3]) 
                        ClientArray.append(tSb)
                        print(f"✅ Registered new client: {p[0]}")
                    else:
                        print(f"⚠️  Client rejected: Name '{p[0]}' already exists.")
                
            except Exception as e:
                print(f"[ERROR] Error processing registration: {e}")
        
        # --- Routing Logic (Silent) ---
        for pub, sub in Spacebrew2Routes.items():
            if msg.topic == pub:
                result = client.publish(sub, msg.payload.decode(), qos=1) 
        
        # Restore the CLI prompt after receiving a message
        sys.stdout.write(MyCLI.prompt)
        sys.stdout.flush()

    client.subscribe(s_topic)
    client.on_message = on_message


def run():
    global broker, port
    
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description='Spacebrew 2.0 Router')
    parser.add_argument('--server', type=str, default='localhost', help='MQTT Broker address')
    parser.add_argument('--port', type=int, default=1883, help='MQTT Broker port')
    args = parser.parse_args()
    
    broker = args.server
    port = args.port

    # 1. Load routes from file on startup (creates file if necessary)
    load_routes()
    
    # 2. Connect to MQTT
    client = connect_mqtt(broker, port)
    subscribe(client)
    client.loop_start() 
    
    # 3. Start CLI
    cli = MyCLI(client)
    
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        pass
    finally:
        if client.is_connected():
            client.disconnect()
        client.loop_stop()
        

if __name__ == '__main__':
    run()