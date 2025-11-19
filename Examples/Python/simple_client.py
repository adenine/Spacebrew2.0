import time
import random
import sys
from paho.mqtt import client as mqtt_client

# =============================================================================
# Spacebrew 2.0 - Simple Python Client Example
# =============================================================================
# This script demonstrates how to create a Spacebrew client that:
# 1. Connects to the Spacebrew Server (MQTT Broker)
# 2. Registers itself with a Name, Description, Publishers, and Subscribers
# 3. Publishes data to a topic
# 4. Listens for data on a topic
# =============================================================================

# --- Configuration ---
BROKER = 'localhost'
PORT = 1883

# Generate a unique client name to avoid collisions
# In a real app, you might want a fixed name, but for testing, random is safer.
CLIENT_NAME = f"SimpleClient_{random.randint(0, 1000)}"
DESCRIPTION = "A simple example client demonstrating publishers and subscribers."

# --- Publishers and Subscribers ---
# Format: "name:type"
# Types can be: string, boolean, range, or custom types.
# Publishers: Data this client SENDS to Spacebrew.
PUBLISHERS = [
    "button:boolean",   # Sends true/false
    "slider:range"      # Sends 0-1023
]

# Subscribers: Data this client RECEIVES from Spacebrew.
SUBSCRIBERS = [
    "led:boolean",      # Receives true/false
    "text:string"       # Receives text
]

# --- MQTT Setup ---
client = mqtt_client.Client(CLIENT_NAME)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to Spacebrew Server at {BROKER}:{PORT}")
        
        # --- Registration ---
        # The registration string format is:
        # Name, Description, pubs(p1:t, p2:t), subs(s1:t, s2:t)
        
        pubs_str = ", ".join(PUBLISHERS)
        subs_str = ", ".join(SUBSCRIBERS)
        
        registration_msg = f"{CLIENT_NAME}, {DESCRIPTION}, pubs({pubs_str}), subs({subs_str})"
        
        print(f"📤 Sending Registration: {registration_msg}")
        client.publish("YuxiSpace", registration_msg)
        
        # --- Subscribe to Input Topics ---
        # We need to subscribe to the topics we defined in SUBSCRIBERS.
        # The Spacebrew Router routes messages to: "ClientName/SubscriberName"
        for sub in SUBSCRIBERS:
            sub_name = sub.split(':')[0] # Extract name from "name:type"
            topic = f"{CLIENT_NAME}/{sub_name}"
            client.subscribe(topic)
            print(f"👂 Listening on topic: {topic}")
            
    else:
        print(f"🔴 Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"\n[RX] Received `{msg.payload.decode()}` on `{msg.topic}`")
    # Add your custom logic here to handle incoming messages
    # e.g., if msg.topic == f"{CLIENT_NAME}/led": turn_on_led()

client.on_connect = on_connect
client.on_message = on_message

# --- Main Loop ---
def run():
    try:
        print(f"🚀 Starting {CLIENT_NAME}...")
        client.connect(BROKER, PORT)
        client.loop_start() # Start background thread for MQTT
        
        # Keep the script running and publish some example data
        while True:
            # Example: Simulate a button press every 5 seconds
            print(f"📤 Publishing 'true' to {CLIENT_NAME}/button")
            client.publish(f"{CLIENT_NAME}/button", "true")
            
            time.sleep(2.5)
            
            print(f"📤 Publishing 'false' to {CLIENT_NAME}/button")
            client.publish(f"{CLIENT_NAME}/button", "false")
            
            time.sleep(2.5)
            
    except KeyboardInterrupt:
        print("\nStopping client...")
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    run()
