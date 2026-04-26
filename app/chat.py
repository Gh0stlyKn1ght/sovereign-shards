"""Chat loop for talking with the Sovereign Shard J."""

from __future__ import annotations

from json import dumps, loads
from pathlib import Path
from urllib.request import Request, urlopen

from app.client import RuntimeConfig, create_client
from app.local_server import LocalLlamaServer
from app.session import SessionLogger
from app.system_tools import get_system_snapshot
from core.fivemasters import evaluate_code


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

SYSTEM_PROMPT = (PROMPTS_DIR / "J-system.txt").read_text(encoding="utf-8")


def build_history(system_context: str = ""):
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + (
                f"\n\n[Context]\n{system_context}"
                if system_context else ""
            )
        }
    ]


def _ollama_chat(client: RuntimeConfig, messages: list[dict[str, str]]):
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
        url=f"{client.base_url}/api/chat",
        data=dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        return urlopen(request, timeout=300)
    except Exception as error:
        raise RuntimeError(f"Connection failed: {error}") from error


def _llama_cpp_chat(client: RuntimeConfig, messages: list[dict[str, str]]):
    payload = {
        "model": client.model,
        "messages": messages,
        "stream": True,
        "max_tokens": client.num_predict,
        "temperature": client.temperature,
        "top_p": client.top_p,
        "stop": list(client.stop_tokens),
    }

    request = Request(
        url=f"{client.base_url}/v1/chat/completions",
        data=dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        return urlopen(request, timeout=300)
    except Exception as error:
        raise RuntimeError(f"Connection failed: {error}") from error


def _format_hardware_context() -> str:
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


def _stream_reply(client: RuntimeConfig, messages: list[dict[str, str]]) -> str:
    """Stream reply with safe interception layer."""
    reply_chunks = []

    def emit(token: str) -> None:
        print(token, end="", flush=True)

    def maybe_evaluate(content: str) -> str:
        """Five Masters gate (SAFE, scoped, non-crashing)."""
        if "def " in content or "class " in content:
            try:
                report = evaluate_code(content)
                if report.score() < 5:
                    return f"\n[FIVE MASTERS WARNING]\n{report}\n\n{content}"
            except Exception:
                pass
        return content

    if client.backend == "llama_cpp":
        with _llama_cpp_chat(client, messages) as response:
            for raw_line in response:
                if not raw_line:
                    continue

                line = raw_line.decode("utf-8", errors="ignore").strip()

                if not line.startswith("data:"):
                    continue

                data = line[5:].strip()

                if data == "[DONE]":
                    break

                chunk = loads(data)
                choices = chunk.get("choices") or []
                if not choices:
                    continue

                delta = choices[0].get("delta") or {}
                content = delta.get("content") or ""

                if not content:
                    continue

                content = maybe_evaluate(content)

                emit(content)
                reply_chunks.append(content)

        return "".join(reply_chunks)

    # --- fallback (ollama) ---
    with _ollama_chat(client, messages) as response:
        full_reply = ""
        for line in response:
            if not line:
                continue

            chunk = loads(line.decode("utf-8"))

            if "message" in chunk:
                content = chunk["message"]["content"]
                emit(content)
                full_reply += content

            if chunk.get("done"):
                break

        return full_reply


def _run_turn(
    client: RuntimeConfig,
    messages: list[dict[str, str]],
    logger: SessionLogger,
    user_message: str,
) -> str:

    messages.append({"role": "user", "content": user_message})
    logger.append("user", user_message)

    reply = _stream_reply(client, messages)

    print()

    messages.append({"role": "assistant", "content": reply})
    logger.append("assistant", reply)

    return reply


def run_chat(
    initial_message: str | None = None,
    runtime_state: dict | None = None,
) -> None:

    if runtime_state is None:
        runtime_state = {"sandbox_enabled": False}

    client = create_client()
    logger = SessionLogger(model=f"{client.backend}:{client.model}")
    messages = build_history(_format_hardware_context())
    local_server = LocalLlamaServer(client)

    try:
        local_server.ensure_started()

        print(f"--- SOVEREIGN SHARD ONLINE [{logger.session_id}] ---")
        print(f"Backend: {client.backend}")
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

            # sandbox toggle
            if user_message.lower() == "bruce wayne":
                runtime_state["sandbox_enabled"] = True
                print("\n[SANDBOX ENABLED]")
                continue

            if runtime_state.get("sandbox_enabled"):
                user_message = f"[SANDBOX] {user_message}"

            try:
                print("\nJ.: ", end="", flush=True)
                _run_turn(client, messages, logger, user_message)

            except RuntimeError as error:
                print(f"\nJ. Error: {error}")
                logger.append("error", str(error))

    finally:
        local_server.stop()