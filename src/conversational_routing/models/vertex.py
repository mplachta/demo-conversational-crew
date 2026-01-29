import os
import base64
import json
from google.oauth2 import service_account
from crewai import LLM

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
sa_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")

with open("/tmp/vertex_credentials.json", "w") as f:
    f.write(base64.b64decode(sa_base64).decode("utf-8"))
    
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/vertex_credentials.json"

sa_json = base64.b64decode(sa_base64).decode("utf-8")
sa_info = json.loads(sa_json)
vertex_credentials = service_account.Credentials.from_service_account_info(
    sa_info,
    scopes=SCOPES
)

if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

llm = LLM(
    model="gemini-2.5-flash-lite",
    client_params={
        "project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "location": os.getenv("GOOGLE_CLOUD_LOCATION"),
        "credentials": vertex_credentials,
    }
)

embedder_configuration={
    "provider": "google-vertex",
    "config": {
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "location": os.getenv("GOOGLE_CLOUD_LOCATION"),
        "model_name": "gemini-embedding-001",  # or "text-embedding-005", "text-multilingual-embedding-002"
    }
}