/*
  Spacebrew 2.0 - Arduino Client Example

  This sketch demonstrates how to connect an Arduino (e.g., MKR WiFi 1010, Nano
  33 IoT) to a Spacebrew 2.0 server using MQTT.

  Hardware Required:
  - Arduino with WiFiNINA support (MKR WiFi 1010, Nano 33 IoT, etc.)
  - Pushbutton connected to pin 2
  - LED connected to pin 6 (or use built-in LED)

  Libraries Required:
  - WiFiNINA
  - ArduinoMqttClient

  Functionality:
  - Connects to WiFi and the Spacebrew MQTT Broker.
  - Registers as a client with a Publisher (Button) and Subscriber (LED).
  - Publishes "true" or "false" when the button is pressed/released.
  - Turns the LED on/off when receiving "true"/"false" messages.
*/

#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>

// --- Configuration ---
char ssid[] = "YOUR_WIFI_SSID"; // your network SSID (name)
char pass[] = "YOUR_WIFI_PASS"; // your network password

const char broker[] = "192.168.1.100"; // IP address of your Spacebrew Server
                                       // (computer running main.py)
int port = 1883;

// Unique Client Name
const char clientName[] = "ArduinoClient";
const char description[] = "Arduino Button and LED Client";

// --- Pin Definitions ---
const int buttonPin = 2;
const int ledPin = 6;

// --- Global Variables ---
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

int lastButtonState = LOW;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

void setup() {
  // Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  pinMode(buttonPin, INPUT_PULLUP); // Assuming button connects pin to Ground
  pinMode(ledPin, OUTPUT);

  // attempt to connect to Wifi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(5000);
  }

  Serial.println("You're connected to the network");
  Serial.println();

  // You can provide a unique ID to the MQTT client here if needed
  mqttClient.setId(clientName);

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1)
      ;
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  // --- Spacebrew Registration ---
  // Format: Name, Description, pubs(p1:t, p2:t), subs(s1:t, s2:t)
  // We register:
  // Publisher: "button" (boolean)
  // Subscriber: "led" (boolean)

  String regMsg = String(clientName) + ", " + description +
                  ", pubs(button:boolean), subs(led:boolean)";

  Serial.print("Sending Registration: ");
  Serial.println(regMsg);

  mqttClient.beginMessage("YuxiSpace");
  mqttClient.print(regMsg);
  mqttClient.endMessage();

  // --- Subscribe to Topics ---
  // We need to subscribe to "ClientName/SubscriberName"
  String subTopic = String(clientName) + "/led";

  Serial.print("Subscribing to topic: ");
  Serial.println(subTopic);

  mqttClient.onMessage(onMqttMessage); // Set callback function
  mqttClient.subscribe(subTopic);
}

void loop() {
  // call poll() regularly to allow the library to send/receive MQTT messages
  mqttClient.poll();

  // --- Button Logic ---
  int reading = digitalRead(buttonPin);

  // Check for button state change (with simple debounce logic if needed,
  // but for simplicity we just check state change here assuming clean signal or
  // simple logic)

  // Note: INPUT_PULLUP means LOW when pressed, HIGH when released.
  // Let's invert it so Pressed = HIGH (true)
  int currentButtonState = (reading == LOW) ? HIGH : LOW;

  if (currentButtonState != lastButtonState) {
    // State changed
    lastButtonState = currentButtonState;

    String msg = (currentButtonState == HIGH) ? "true" : "false";

    // Publish to "ClientName/button"
    String pubTopic = String(clientName) + "/button";

    Serial.print("Publishing message: ");
    Serial.print(msg);
    Serial.print(" to topic: ");
    Serial.println(pubTopic);

    mqttClient.beginMessage(pubTopic);
    mqttClient.print(msg);
    mqttClient.endMessage();

    delay(50); // Simple debounce delay
  }
}

void onMqttMessage(int messageSize) {
  // we received a message, print out the topic and contents
  String topic = mqttClient.messageTopic();
  String payload = "";

  while (mqttClient.available()) {
    payload += (char)mqttClient.read();
  }

  Serial.print("Received a message with topic '");
  Serial.print(topic);
  Serial.print("', length ");
  Serial.print(messageSize);
  Serial.print(" bytes: ");
  Serial.println(payload);

  // --- Handle Message ---
  // Check if it's for our LED
  if (topic.endsWith("/led")) {
    if (payload == "true" || payload == "1" || payload == "on") {
      digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(ledPin, LOW);
    }
  }
}
