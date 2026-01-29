import os
from crewai import LLM

llm = LLM(
    model="gpt-4o",
    client_params={
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
)

embedder_configuration = {
    "provider": "openai",
    "config": {"model_name": "text-embedding-ada-002"}
}