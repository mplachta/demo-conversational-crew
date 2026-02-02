import os
from crewai import LLM

llm = LLM(
    model="gemini/gemini-2.5-flash-lite",
    client_params={
        "api_key": os.getenv("GEMINI_API_KEY"),
    }
)

embedder_configuration = {
    "provider": "google-generativeai",
    "config": {"model_name": "gemini-embedding-001"}
}