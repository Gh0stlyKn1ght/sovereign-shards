"""Context window budget management.

Keeps the conversation within token limits by summarizing old turns.
Estimates tokens as chars/4 (good enough for local models).
"""

from __future__ import annotations

# Conservative default for small local models on USB hardware
DEFAULT_MAX_TOKENS = 4096
CHARS_PER_TOKEN = 4  # rough estimate


def estimate_tokens(text: str) -> int:
    """Estimate token count from character length."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
    """Estimate total tokens across all messages."""
    return sum(estimate_tokens(m.get("content", "")) for m in messages)


def trim_context(
    messages: list[dict[str, str]],
    max_tokens: int = DEFAULT_MAX_TOKENS,
    keep_system: bool = True,
    keep_last_n: int = 4,
) -> list[dict[str, str]]:
    """Trim conversation to fit within token budget.

    Strategy:
    1. Always keep system message(s) at the front.
    2. Always keep the last N messages.
    3. Summarize/drop middle messages until we fit.
    """
    if not messages:
        return messages

    total = estimate_messages_tokens(messages)
    if total <= max_tokens:
        return messages

    # Split into system, middle, and tail
    system_msgs = []
    rest = []
    for m in messages:
        if m.get("role") == "system" and keep_system and not rest:
            system_msgs.append(m)
        else:
            rest.append(m)

    if len(rest) <= keep_last_n:
        return messages  # can't trim further without losing recent context

    tail = rest[-keep_last_n:]
    middle = rest[:-keep_last_n]

    # Compress middle into a single summary message
    summary_parts = []
    for m in middle:
        role = m.get("role", "?")
        content = m.get("content", "")
        # Take first 200 chars of each message
        snippet = content[:200].replace("\n", " ")
        if len(content) > 200:
            snippet += "..."
        summary_parts.append(f"[{role}] {snippet}")

    summary = "[CONTEXT SUMMARY — older messages compressed]\n" + "\n".join(summary_parts)
    summary_msg = {"role": "system", "content": summary}

    result = system_msgs + [summary_msg] + tail

    # If still too big, just keep system + tail
    if estimate_messages_tokens(result) > max_tokens:
        result = system_msgs + tail

    return result
