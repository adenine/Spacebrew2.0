import cmd
import sys
import os

class SpacebrewCLI(cmd.Cmd):
    def __init__(self, router, mqtt_service):
        super().__init__()
        self.router = router
        self.mqtt_service = mqtt_service
        self.prompt = '>> '
        self.intro = 'Welcome to Spacebrew 2.0. Type "help" for available commands.'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")
    
    def do_quit(self, line):
        """Exit the CLI and stop the MQTT loop."""
        print("Stopping MQTT loop and exiting.")
        self.mqtt_service.stop()
        # We might need to kill the web server too, but it runs in main thread usually.
        # If CLI is in a thread, we can't easily kill the main thread uvicorn.
        # Usually we just exit the process.
        os._exit(0) 
        return True
    
    def do_routes(self, line):
        """Show the current Spacebrew routing table."""
        if not self.router.routes:
            print("The routing table is empty.")
            return

        print("--- Current Routes ---")
        for pub, sub in self.router.routes.items():
            print(f"  {pub} -> {sub}")
        print("----------------------")
        print(f"Total routes: {len(self.router.routes)}")

    def do_saveroutes(self, line):
        """Save the current routing table to the routes.txt file."""
        if self.router.save_routes():
            print(f"✅ Routes successfully saved.")
        else:
            print(f"❌ Failed to save routes.")
            
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
            
            success, msg = self.router.add_route(pub, sub)
            if success:
                print(f"✅ {msg}")
            else:
                print(f"❌ {msg}")
        
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
            
        success, msg = self.router.delete_route(topic)
        if success:
            print(f"🗑️ {msg}")
        else:
            print(f"❌ {msg}")

    def do_server(self,line):
        """Show the current broker and port."""
        print(f"Broker: {self.mqtt_service.broker}, Port: {self.mqtt_service.port}")
    
    def do_clients(self,line):
        """Show the names of currently registered clients."""
        if not self.router.clients:
            print("No clients are currently registered.")
            return

        print("--- Registered Clients ---")
        for i, client_obj in enumerate(self.router.clients):
            print(f"{i + 1}. {client_obj.clientName}")
        print(f"--------------------------")
        print(f"Total: {len(self.router.clients)} clients.")

    def do_connection(self, line):
        """Check the current MQTT server connection status."""
        if self.mqtt_service.client.is_connected():
            print(f"🟢 **Connected** to MQTT Broker at {self.mqtt_service.broker}:{self.mqtt_service.port}")
        else:
            print(f"🔴 **Disconnected** from MQTT Broker at {self.mqtt_service.broker}:{self.mqtt_service.port}")

    def do_testclient(self, line):
        """
        Spawn a test client in a separate process.
        Usage: testclient
        """
        import subprocess
        try:
            if not os.path.exists("SpacebrewClientTest.py"):
                print("❌ Error: 'SpacebrewClientTest.py' not found in the current directory.")
                return

            print("🚀 Spawning test client...")
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
            
            result = self.mqtt_service.publish(topic, message)
            status = result[0]
            
            if status == 0:
                print(f"✅ Published: '{message}' to topic '{topic}'")
            else:
                print(f"❌ Failed to publish message to topic {topic}. Status: {status}")

        except IndexError:
            print("Error: Usage is 'publish <topic> <message>'")
        except Exception as e:
            print(f"An error occurred: {e}")
