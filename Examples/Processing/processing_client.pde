/*
  Spacebrew 2.0 - Processing Client Example
  
  This sketch demonstrates how to connect a Processing sketch to a Spacebrew 2.0 server using MQTT.
  
  Libraries Required:
  - MQTT (by Joel Gaehwiler) - Install via Sketch > Import Library > Add Library...
  
  Functionality:
  - Connects to the Spacebrew MQTT Broker.
  - Registers as a client with a Publisher (Mouse Click) and Subscriber (Background Color).
  - Publishes "true" when the mouse is pressed.
  - Changes background color when receiving messages.
*/

import mqtt.*;

MQTTClient client;

// --- Configuration ---
String broker = "mqtt://localhost"; // Use "mqtt://127.0.0.1" or IP address
// Note: The library might expect "mqtt://" prefix. If connecting to standard port 1883.

// Unique Client Name
String clientName = "ProcessingClient_" + int(random(10000));
String description = "Processing Mouse and Color Client";

// --- Publishers and Subscribers ---
// We will publish mouse clicks and subscribe to background color changes.
// Format: "name:type"
String[] publishers = { "mouse:boolean" };
String[] subscribers = { "color:string" };

int bgColor = 0;

void setup() {
  size(400, 400);
  background(0);
  
  client = new MQTTClient(this);
  
  // Connect to broker
  // Ensure your Spacebrew server (main.py) is running on port 1883
  client.connect(broker, "processing_client_" + int(random(1000)));
  
  // Note: The connect() function in some libraries is blocking, in others async.
  // We usually wait for a callback or just proceed.
  // For this library, we can subscribe in setup or in a callback.
}

void draw() {
  background(bgColor);
  
  fill(255);
  textAlign(CENTER);
  text("Click to publish 'true' to 'mouse'", width/2, height/2);
  text("Client: " + clientName, width/2, height/2 + 20);
}

void clientConnected() {
  println("✅ Connected to Broker");
  
  // --- Spacebrew Registration ---
  // Format: Name, Description, pubs(p1:t, p2:t), subs(s1:t, s2:t)
  
  String pubsStr = join(publishers, ", ");
  String subsStr = join(subscribers, ", ");
  
  String regMsg = clientName + ", " + description + ", pubs(" + pubsStr + "), subs(" + subsStr + ")";
  
  println("📤 Sending Registration: " + regMsg);
  client.publish("YuxiSpace", regMsg);
  
  // --- Subscribe to Topics ---
  // We need to subscribe to "ClientName/SubscriberName"
  for (String sub : subscribers) {
    String subName = split(sub, ':')[0];
    String topic = clientName + "/" + subName;
    client.subscribe(topic);
    println("👂 Subscribed to: " + topic);
  }
}

void messageReceived(String topic, byte[] payload) {
  String msg = new String(payload);
  println("📩 Received: " + topic + " -> " + msg);
  
  // --- Handle Messages ---
  // Check if it's for our color subscriber
  if (topic.equals(clientName + "/color")) {
    // Expecting hex string like "#FF0000" or simple names if supported by Processing logic
    // For simplicity, let's handle simple commands or just random colors if "random" is sent
    
    if (msg.equals("red")) {
      bgColor = color(255, 0, 0);
    } else if (msg.equals("green")) {
      bgColor = color(0, 255, 0);
    } else if (msg.equals("blue")) {
      bgColor = color(0, 0, 255);
    } else {
      // Try to parse hex? Or just random
      bgColor = color(random(255), random(255), random(255));
    }
  }
}

void connectionLost() {
  println("🔴 Connection lost");
}

void mousePressed() {
  // --- Publish Message ---
  // Publish "true" to "ClientName/mouse"
  String topic = clientName + "/mouse";
  String msg = "true";
  
  client.publish(topic, msg);
  println("📤 Published: " + msg + " to " + topic);
}

void mouseReleased() {
  // Publish "false"
  String topic = clientName + "/mouse";
  String msg = "false";
  
  client.publish(topic, msg);
  println("📤 Published: " + msg + " to " + topic);
}
