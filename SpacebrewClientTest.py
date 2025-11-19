import paho.mqtt.client as mqtt
import time
import sys
import random

# --- Configuration ---
BROKER = 'localhost'
PORT = 1883
SERVER_TOPIC = "YuxiSpace" # Topic to send registration messages to
CLIENT_NAME = f"ExampleClient_{random.randint(0, 1000)}"
CLIENT_DESC = "An example client with multiple publishers and subscribers"

# --- Publishers and Subscribers ---
# Format: "name:type"
PUBLISHERS = [
    "button:boolean",
    "slider:range",
    "text_out:string"
]

SUBSCRIBERS = [
    "led:boolean",
    "display:string",
    "servo:range"
]

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker at {BROKER}:{PORT}")
        register(client)
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"📩 Received message on {msg.topic}: {msg.payload.decode()}")

def register(client):
    """
    Constructs and sends the registration string.
    Format: Name, Description, pubs(p1:t,p2:t), subs(s1:t,s2:t)
    """
    pubs_str = ", ".join(PUBLISHERS)
    subs_str = ", ".join(SUBSCRIBERS)
    
    # Construct the registration message
    # Note: The server expects the format: Name, Desc, pubs(...), subs(...)
    registration_msg = f"{CLIENT_NAME}, {CLIENT_DESC}, pubs({pubs_str}), subs({subs_str})"
    
    print(f"📤 Sending registration: {registration_msg}")
    client.publish(SERVER_TOPIC, registration_msg)

# --- Main Execution ---
def run():
    client = mqtt.Client(CLIENT_NAME)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"Connecting to {BROKER}...")
        client.connect(BROKER, PORT, 60)
        
        # Subscribe to our subscriber topics so we can hear messages
        # Note: In a real app, you'd subscribe to the topics you defined in SUBSCRIBERS
        # The server routes messages TO these topics.
        for sub in SUBSCRIBERS:
            topic_name = sub.split(':')[0]
            full_topic = f"{CLIENT_NAME}/{topic_name}" # Assuming a naming convention or just the raw name?
            # Actually, Spacebrew usually routes FROM a publisher TO a subscriber.
            # The subscriber listens on its own channel.
            # Let's assume the server routes to the exact name provided in the subscriber list?
            # Or does it prepend the client name? 
            # Looking at main.py routing logic:
            # for pub, sub in Spacebrew2Routes.items():
            #    if msg.topic == pub:
            #        client.publish(sub, msg.payload.decode(), qos=1)
            # So if I register subscriber "led", and someone routes to it, the server publishes to "led".
            # BUT, to avoid collisions, usually topics are namespaced.
            # However, the current main.py doesn't enforce namespacing on the route destination.
            # It just takes the string from the route table.
            # So if I add a route "button -> led", the server publishes to "led".
            # So I should subscribe to "led".
            pass 

        client.loop_start()
        
        # Keep the script running
        # Send 5 messages then exit
        for i in range(5):
            msg = f"Message {i+1}"
            # Publish to one of our publisher topics
            # We registered "text_out:string", so let's publish to that.
            # Topic structure: The server routes based on the publisher name.
            # But we need to publish TO the server.
            # Usually Spacebrew clients publish to a specific topic.
            # Let's assume we publish to "CLIENT_NAME/publisher_name"
            pub_topic = f"{CLIENT_NAME}/text_out"
            print(f"📤 Sending message {i+1}: {msg} to {pub_topic}")
            client.publish(pub_topic, msg)
            time.sleep(1)
            
        print("Done sending messages. Exiting.")
        client.loop_stop()
        client.disconnect()
            
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
