import paho.mqtt.client as mqtt
import time

broker = 'localhost'
port = 1883
topic = "YuxiSpace"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

client = mqtt.Client("Test_Duplicate")
client.on_connect = on_connect
client.connect(broker, port)
client.loop_start()

time.sleep(1)

# Register Client A
msg1 = "ClientDuplicate, A client to test duplicates, pubs(p1:bool), subs(s1:bool)"
print(f"Sending 1st registration: {msg1}")
client.publish(topic, msg1)
time.sleep(1)

# Register Client A again (should be rejected)
print(f"Sending 2nd registration (Duplicate): {msg1}")
client.publish(topic, msg1)
time.sleep(1)

client.loop_stop()
client.disconnect()
