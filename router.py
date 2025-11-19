import os
import Spacebrew2Client as sb2

class SpacebrewRouter:
    def __init__(self, route_file='routes.txt'):
        self.route_file = route_file
        self.routes = {}
        self.clients = []
        self.default_routes = {
            "VirtualButton1/button": "VirtualButton2/bgcolor",
            "VirtualButton2/button": "VirtualButton1/bgcolor"
        }
        self.load_routes()

    def load_routes(self):
        """Load routes from file or create default if not exists."""
        if not os.path.exists(self.route_file):
            print(f"File '{self.route_file}' not found. Creating file with default routes.")
            self.routes = self.default_routes.copy()
            self.save_routes()
            return

        loaded_routes = {}
        try:
            with open(self.route_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        pub_topic = parts[0].strip()
                        sub_topic = parts[1].strip()
                        loaded_routes[pub_topic] = sub_topic
            
            self.routes = loaded_routes
            print(f"Routes loaded successfully from '{self.route_file}'. Total routes: {len(self.routes)}")

        except Exception as e:
            print(f"Error loading routes from file: {e}. Using current routes instead.")

    def save_routes(self):
        """Save current routes to file."""
        try:
            with open(self.route_file, 'w') as f:
                f.write("# Spacebrew2 Router Routes: Publisher, Subscriber\n")
                for pub, sub in self.routes.items():
                    f.write(f"{pub},{sub}\n")
            return True
        except Exception as e:
            print(f"Error saving routes to file: {e}")
            return False

    def add_route(self, pub, sub):
        if pub in self.routes and self.routes[pub] == sub:
            return False, "Route already exists"
        self.routes[pub] = sub
        self.save_routes()
        return True, f"Route added: {pub} -> {sub}"

    def delete_route(self, pub):
        if pub in self.routes:
            sub = self.routes.pop(pub)
            self.save_routes()
            return True, f"Route deleted: {pub} -> {sub}"
        return False, "Route not found"

    def register_client(self, name, desc, pubs, subs):
        # Check for duplicate name
        if any(c.clientName == name for c in self.clients):
            return False, f"Client rejected: Name '{name}' already exists."
        
        new_client = sb2.Spacebrew2Client(name, desc, pubs, subs)
        self.clients.append(new_client)
        return True, f"Registered new client: {name}"

    def get_clients_data(self):
        return [
            {
                "name": c.clientName,
                "description": c.clientDesc,
                "publishers": c.clientPubs,
                "subscribers": c.clientSubs
            }
            for c in self.clients
        ]
