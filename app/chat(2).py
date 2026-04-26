"""Chat loop for talking with the J. J."""

from json import JSONDecodeError, dumps, loads
from pathlib import Path
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.client import OllamaConfig, create_client


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")
DEVELOPER_PROMPT = (PROMPTS_DIR / "developer.txt").read_text(encoding="utf-8")
COMBINED_SYSTEM_PROMPT = f"{SYSTEM_PROMPT}\n\n{DEVELOPER_PROMPT}"


def build_history() -> list[dict[str, str]]:
    """Build the initial chat history."""
    return [{"role": "system", "content": COMBINED_SYSTEM_PROMPT}]


def ollama_chat(
    client: OllamaConfig,
    messages: list[dict[str, str]],
):
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
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama returned HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(
            "Could not reach Ollama. Make sure the Ollama app is running."
        ) from error
    
def ensure_gpu_is_active(client: OllamaConfig) -> None:
    """Stop the app if Ollama is not reporting GPU use."""
    if not client.require_gpu:
        return

    result = subprocess.run(
        ["ollama", "ps"],
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    model_name = client.model.lower()

    for line in output.splitlines():
        lowered_line = line.lower()
        if model_name in lowered_line:
            if "gpu" in lowered_line:
                return
            raise RuntimeError(
                "Ollama is running the model without GPU acceleration."
            )

    raise RuntimeError(
        "Could not confirm GPU use from 'ollama ps'."
    )


def run_chat(system_context: str = "") -> None:
    """Run the interactive chat loop with real-time streaming."""
    client = create_client()
    messages = build_history()
    if system_context:
        messages.append({"role": "system", "content": system_context})
    
    checked_gpu = False
    print("J. is online through Ollama. Type 'quit' to exit.")

    while True:
        user_message = input("\nYou: ").strip()
        if user_message.lower() in {"quit", "exit"}:
            print("J.: Session ended.")
            break

        if not user_message:
            print("J.: Please say something, if you would be so kind.")
            continue

        messages.append({"role": "user", "content": user_message})
        
        try:
            # We start the line for J.'s response
            print("\nJ.: ", end="", flush=True)
            full_reply = ""
            
            # Open the live connection from ollama_chat
            with ollama_chat(client, messages) as response:
                for line in response:
                    if line:
                        # Decode the JSON chunk sent by Ollama
                        chunk = loads(line.decode("utf-8"))
                        
                        if "message" in chunk:
                            content = chunk["message"]["content"]
                            # Print each word immediately as it's generated
                            print(content, end="", flush=True)
                            full_reply += content
                        
                        if chunk.get("done"):
                            break
            
            print() # Move to a new line when he's finished
            messages.append({"role": "J", "content": full_reply})

            if not checked_gpu:
                ensure_gpu_is_active(client)
                checked_gpu = True
                
        except RuntimeError as error:
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            print(f"\nJ. Error: {error}")
            continue
