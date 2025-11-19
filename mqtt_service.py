import sys
import random
from paho.mqtt import client as mqtt_client
import re
import asyncio

class SpacebrewMQTT:
    def __init__(self, router, broker='localhost', port=1883):
        self.router = router
        self.broker = broker
        self.port = port
        self.client_id = f'Spacebrew2_Router_{random.randint(0, 100000)}'
        self.client = mqtt_client.Client(self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Callbacks for external services (e.g., WebService broadcasting)
        self.on_route_activity = None 
        self.on_client_message = None

    def connect(self):
        try:
            self.client.connect(self.broker, self.port)
            return True
        except Exception as e:
            print(f"Error connecting to broker: {e}")
            sys.exit(1)

    def start(self):
        self.client.loop_start()
        self.client.subscribe("#") # Subscribe to all topics

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, topic, message):
        return self.client.publish(topic, message, qos=1)

    def on_connect(self, client, userdata, flags, reason_code):
        if reason_code != 0:
            print(f"🔴 Failed to connect to MQTT Broker, return code {reason_code}")
        else:
            print(f"✅ Connected to MQTT Broker at {self.broker}:{self.port}")

    def on_message(self, client, userdata, msg):
        # Print received message
        try:
            payload_str = msg.payload.decode()
        except:
            payload_str = str(msg.payload)
            
        print(f"\n[RX] Received `{payload_str}` from `{msg.topic}` topic")
        
        # 1. Registration Logic
        if msg.topic == "YuxiSpace":
            self.handle_registration(payload_str)
        
        # 2. Routing Logic
        if msg.topic in self.router.routes:
            sub_topic = self.router.routes[msg.topic]
            self.client.publish(sub_topic, payload_str, qos=1)
            
            # Notify listener (WebService) about route activity
            if self.on_route_activity:
                self.on_route_activity(msg.topic, sub_topic)

        # 3. Forward to Web Clients (if applicable)
        if self.on_client_message:
            self.on_client_message(msg.topic, payload_str)

        # Restore CLI prompt (if running CLI in same process, though CLI handles its own prompt usually)
        # sys.stdout.write(">> ")
        # sys.stdout.flush()

    def handle_registration(self, msg_str):
        try:
            # Format: name, desc, pubs(p1:t,p2:t), subs(s1:t,s2:t)
            match = re.match(r'^([^,]+),\s*([^,]+),\s*pubs\((.*)\),\s*subs\((.*)\)$', msg_str)
            
            if match:
                name = match.group(1).strip()
                desc = match.group(2).strip()
                pubs_str = match.group(3).strip()
                subs_str = match.group(4).strip()
                
                pubs = [p.strip() for p in pubs_str.split(',')] if pubs_str else []
                subs = [s.strip() for s in subs_str.split(',')] if subs_str else []
            else:
                 # Fallback to old split
                 p = msg_str.split(',')
                 if len(p) >= 4:
                     name = p[0].strip()
                     desc = p[1].strip()
                     pubs = [p[2].strip()]
                     subs = [p[3].strip()]
                 else:
                     return # Invalid format

            success, message = self.router.register_client(name, desc, pubs, subs)
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️  {message}")

        except Exception as e:
            print(f"[ERROR] Error processing registration: {e}")
