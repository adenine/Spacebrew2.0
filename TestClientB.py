import time
from paho.mqtt import client as mqtt_client

# --- Configuration ---
BROKER = 'localhost'
PORT = 1883
CLIENT_NAME = "TestClientB"
DESCRIPTION = "Test client with one publisher/subscriber per type"

# One publisher and one subscriber per type, so type-restricted routing
# can be exercised against TestClientA (or itself).
PUBLISHERS = [
    "toggle:boolean",
    "level:range",
    "name:string",
    "data:json",
]
SUBSCRIBERS = [
    "toggle:boolean",
    "level:range",
    "name:string",
    "data:json",
]

client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, CLIENT_NAME)

# Last Will: if this client's connection drops uncleanly, the broker
# publishes this on our behalf so the router can deregister us.
client.will_set("YuxiSpace/leave", payload=CLIENT_NAME, qos=1)


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"Failed to connect, return code {rc}")
        return

    pubs_str = ", ".join(PUBLISHERS)
    subs_str = ", ".join(SUBSCRIBERS)
    registration_msg = f"{CLIENT_NAME}, {DESCRIPTION}, pubs({pubs_str}), subs({subs_str})"
    client.publish("YuxiSpace", registration_msg)
    print(f"Registered {CLIENT_NAME}")


client.on_connect = on_connect

if __name__ == "__main__":
    client.connect(BROKER, PORT)
    client.loop_start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.publish("YuxiSpace/leave", CLIENT_NAME).wait_for_publish()
        client.loop_stop()
        client.disconnect()
