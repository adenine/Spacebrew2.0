import paho.mqtt.client as mqtt
import time
import json

broker = 'localhost'
port = 1883
topic = "YuxiSpace"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

client = mqtt.Client("Test_Registrar")
client.on_connect = on_connect
client.connect(broker, port)
client.loop_start()

time.sleep(1)

# Test Case 1: Multiple Pubs and Subs
msg1 = "ClientMulti, A client with multiple pubs and subs, pubs(pub1:bool, pub2:range), subs(sub1:string, sub2:json)"
print(f"Sending: {msg1}")
client.publish(topic, msg1)
time.sleep(1)

# Test Case 2: Single Pub and Sub (Legacy-ish but with new format)
msg2 = "ClientSingle, A client with single pub and sub, pubs(pubA:bool), subs(subA:string)"
print(f"Sending: {msg2}")
client.publish(topic, msg2)
time.sleep(1)

# Test Case 3: Legacy Format (Comma separated)
msg3 = "ClientLegacy, Legacy client, pubLegacy, subLegacy"
print(f"Sending: {msg3}")
client.publish(topic, msg3)
time.sleep(1)

client.loop_stop()
client.disconnect()
