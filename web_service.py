from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import os
import sys

# Models
class RouteModel(BaseModel):
    pub: str
    sub: str

class PublishModel(BaseModel):
    topic: str
    message: str

# WebSocket Managers
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

class WebClientManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    def subscribe(self, websocket: WebSocket, topic: str):
        if websocket in self.active_connections:
            self.active_connections[websocket].add(topic)

    async def broadcast(self, topic: str, message: str):
        for ws, subs in self.active_connections.items():
            if topic in subs:
                try:
                    await ws.send_json({"topic": topic, "message": message})
                except Exception:
                    pass

class SpacebrewWebServer:
    def __init__(self, router, mqtt_service, host="0.0.0.0", port=8088):
        self.router = router
        self.mqtt_service = mqtt_service
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.templates = Jinja2Templates(directory="templates")
        self.manager = ConnectionManager()
        self.web_client_manager = WebClientManager()
        self.loop = None # Will capture loop on startup

        self.setup_routes()
        self.setup_callbacks()

    def setup_callbacks(self):
        # Register callbacks with MQTT service
        # Note: These callbacks will be called from MQTT thread, so we need threadsafe execution
        
        def on_route_activity(pub, sub):
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self.manager.broadcast({"pub": pub, "sub": sub}), 
                    self.loop
                )

        def on_client_message(topic, message):
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self.web_client_manager.broadcast(topic, message),
                    self.loop
                )

        self.mqtt_service.on_route_activity = on_route_activity
        self.mqtt_service.on_client_message = on_client_message

    def setup_routes(self):
        app = self.app

        @app.on_event("startup")
        async def startup_event():
            self.loop = asyncio.get_running_loop()

        @app.get("/")
        async def read_root(request: Request):
            return self.templates.TemplateResponse("index.html", {
                "request": request,
                "broker": self.mqtt_service.broker,
                "port": self.mqtt_service.port
            })

        @app.get("/webclient")
        async def web_client_page(request: Request):
            return self.templates.TemplateResponse("web_client.html", {"request": request})

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.manager.disconnect(websocket)

        @app.websocket("/ws/client")
        async def websocket_client_endpoint(websocket: WebSocket):
            await self.web_client_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_json()
                    cmd = data.get("cmd")
                    
                    if cmd == "register":
                        msg = data.get("message")
                        if msg:
                            self.mqtt_service.publish("YuxiSpace", msg)
                            
                    elif cmd == "publish":
                        topic = data.get("topic")
                        payload = data.get("message")
                        if topic and payload:
                            self.mqtt_service.publish(topic, payload)
                            
                    elif cmd == "subscribe":
                        topic = data.get("topic")
                        if topic:
                            self.web_client_manager.subscribe(websocket, topic)
                            
            except WebSocketDisconnect:
                self.web_client_manager.disconnect(websocket)

        @app.get("/api/status")
        async def get_status():
            # Check MQTT connection
            connected = self.mqtt_service.client.is_connected()
            return {"connected": connected}

        @app.get("/api/clients")
        async def get_clients():
            return self.router.get_clients_data()

        @app.get("/api/routes")
        async def get_routes():
            return self.router.routes

        @app.post("/api/routes")
        async def add_route(route: RouteModel):
            success, msg = self.router.add_route(route.pub, route.sub)
            return {"message": msg}

        @app.delete("/api/routes")
        async def delete_route(pub: str):
            success, msg = self.router.delete_route(pub)
            if success:
                return {"message": msg}
            raise HTTPException(status_code=404, detail=msg)

        @app.post("/api/publish")
        async def publish_message(data: PublishModel):
            self.mqtt_service.publish(data.topic, data.message)
            return {"message": "Published"}

        @app.post("/api/save")
        async def save_routes_api():
            if self.router.save_routes():
                return {"message": "Routes saved"}
            raise HTTPException(status_code=500, detail="Failed to save routes")

        @app.post("/api/testclient")
        async def spawn_test_client_api():
            import subprocess
            try:
                if not os.path.exists("SpacebrewClientTest.py"):
                     raise HTTPException(status_code=404, detail="Test client script not found")
                subprocess.Popen([sys.executable, "SpacebrewClientTest.py"])
                return {"message": "Test client spawned"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def start(self):
        print(f"🚀 Starting Web Interface at http://{self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="error")
