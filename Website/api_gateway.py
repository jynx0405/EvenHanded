from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from endpoints.compare_urls import router as url_router
from endpoints.compare_topic import router as topic_router
import os

app = FastAPI(title="Even Handed Backend")

# Add CORS so the client can easily communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url_router)
app.include_router(topic_router)

# Serve the static website we just built
# It checks both the current directory and the parent directory so you can move it freely.
client_path_local = os.path.join(os.path.dirname(__file__), "client")
client_path_up = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client")
client_path = client_path_local if os.path.exists(client_path_local) else client_path_up

@app.get("/api-status")
def status():
    return {"message": "Even Handed Backend API Running 🚀"}

if os.path.exists(client_path):
    app.mount("/", StaticFiles(directory=client_path, html=True), name="client")