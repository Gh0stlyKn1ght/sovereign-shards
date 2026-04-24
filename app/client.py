"""Client helpers for connecting to a local Ollama server."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class OllamaConfig:
    """Store the settings needed to talk to a local Ollama server."""

    host: str
    model: str
    num_predict: int
    num_ctx: int
    num_thread: int
    temperature: float
    keep_alive: str
    require_gpu: bool


def create_client() -> OllamaConfig:
    """Create and return an Ollama configuration object."""
    load_dotenv()

    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "brain")
    num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "256"))
    num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "1024"))
    num_thread = int(os.getenv("OLLAMA_NUM_THREAD", "2"))
    temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
    keep_alive = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
    require_gpu = os.getenv("REQUIRE_GPU", "false").lower() == "true"

    return OllamaConfig(
        host=host.rstrip("/"),
        model=model,
        num_predict=num_predict,
        num_ctx=num_ctx,
        num_thread=num_thread,
        temperature=temperature,
        keep_alive=keep_alive,
        require_gpu=require_gpu,
    )
