"""Chat loop for talking with the Sovereign Shard assistant."""

from __future__ import annotations

from json import dumps, loads
from pathlib import Path
from urllib.request import Request, urlopen

from app.client import OllamaConfig, create_client
from app.session import SessionLogger
from app.system_tools import get_system_snapshot

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")
DEVELOPER_PROMPT = (PROMPTS_DIR / "developer.txt").read_text(encoding="utf-8")
COMBINED_SYSTEM_PROMPT = f"{SYSTEM_PROMPT}\n\n{DEVELOPER_PROMPT}"


def build_history(system_context: str = "") -> list[dict[str, str]]:
    """Build the initial chat history."""
    history = [{"role": "system", "content": COMBINED_SYSTEM_PROMPT}]
    if system_context:
        history.append({"role": "system", "content": system_context})
    return history


def ollama_chat(client: OllamaConfig, messages: list[dict[str, str]]):
    """Send a chat request to the local Ollama server."""
    payload = {
        "model": client.model,
        "messages": messages,
        "stream": True,
        "keep_alive": client.keep_alive,
        "options": {
            "num_predict": client.num_predict,
            "num_ctx": client.num_ctx,
            "num_thread": client.num_thread,
            "temperature": client.temperature,
        },
    }
    request = Request(
        url=f"{client.host}/api/chat",
        data=dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        return urlopen(request, timeout=300)
    except Exception as error:
        raise RuntimeError(f"Connection failed: {error}") from error


def _format_hardware_context() -> str:
    """Create the system context injected into the chat."""
    snapshot = get_system_snapshot()
    if snapshot.get("status") != "ONLINE":
        return "[Sovereign Identity Unavailable]"

    return (
        "\n[Sovereign Identity Verified]\n"
        f"Node: {snapshot['network']['node_name']}\n"
        f"CPU: {snapshot['host_machine']['cpu']}\n"
        f"Memory: {snapshot['live_metrics']['ram_usage_percent']} used of "
        f"{snapshot['host_machine']['ram_total_gb']}GB\n"
        f"Storage: {snapshot['live_metrics']['disk_free_gb']}GB free on local disk.\n"
    )


def _run_turn(
    client: OllamaConfig,
    messages: list[dict[str, str]],
    logger: SessionLogger,
    user_message: str,
) -> str:
    messages.append({"role": "user", "content": user_message})
    logger.append("user", user_message)
    reply = ""

    with ollama_chat(client, messages) as response:
        for line in response:
            if not line:
                continue
            chunk = loads(line.decode("utf-8"))
            if "message" in chunk:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                reply += content
            if chunk.get("done"):
                break

    print()
    messages.append({"role": "assistant", "content": reply})
    logger.append("assistant", reply)
    return reply


def run_chat(initial_message: str | None = None) -> None:
    """Run the interactive chat loop with real-time streaming."""
    client = create_client()
    logger = SessionLogger(model=client.model)
    messages = build_history(_format_hardware_context())

    print(f"--- SOVEREIGN SHARD ONLINE [{logger.session_id}] ---")
    print(f"Model: {client.model}")
    print("Commands: quit, exit, /snapshot")

    if initial_message:
        print("\nJ.: ", end="", flush=True)
        _run_turn(client, messages, logger, initial_message)
        return

    while True:
        user_message = input("\nYou: ").strip()
        if user_message.lower() in {"quit", "exit"}:
            print(f"Session saved to {logger.transcript_path}")
            break
        if not user_message:
            continue
        if user_message == "/snapshot":
            snapshot = dumps(get_system_snapshot(), indent=2)
            print(snapshot)
            logger.append("system", snapshot)
            continue
        try:
            print("\nJ.: ", end="", flush=True)
            _run_turn(client, messages, logger, user_message)
        except RuntimeError as error:
            print(f"\nJ. Error: {error}")
            logger.append("error", str(error))
