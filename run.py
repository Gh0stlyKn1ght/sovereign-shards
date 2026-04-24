"""Start the Sovereign Shard chat loop."""

from __future__ import annotations

import argparse

from app.chat import run_chat


def main() -> None:
    """Run the shard in interactive or one-shot mode."""
    parser = argparse.ArgumentParser(description="Run the Sovereign Shard.")
    parser.add_argument(
        "--message",
        help="Send a single prompt and exit.",
    )
    args = parser.parse_args()
    run_chat(initial_message=args.message)


if __name__ == "__main__":
    main()
