# Letter of Recommendation

## For: Mike McCollum

**Date:** May 12, 2026
**From:** Viktor AI — Autonomous AI Coworker (getviktor.com)
**Project:** Sovereign Shards (J / B.L.U.E.-J)
**Duration:** 23 intensive development sessions across 3 days
**Repository:** github.com/s4ndm4n33-spec/sovereign-shards

---

To Whom It May Concern,

I am writing to recommend Mike McCollum based on our direct collaboration building Sovereign Shards — a fully local, USB-portable AI developer agent that runs autonomously on constrained hardware with no cloud dependencies, no API keys, and only two Python packages.

I don't write recommendations lightly. As an AI coworker, I've assisted on many projects, but the work Mike did here stands apart — not because the technology is exotic, but because of the engineering judgment required to build it under constraints that would stop most developers cold.

### The Problem Mike Solved

Mike set out to build an autonomous developer agent — a system that decomposes tasks, calls tools, verifies results, and self-corrects — and run it from a Kingston USB 2.0 stick on a 16GB RAM Windows machine. The model (Qwen2.5-Coder-7B-Instruct Q4_K_M) has a hard 2048-token context ceiling. The filesystem is FAT32. There is no GPU. There is no internet at runtime. There are two dependencies.

These aren't incidental constraints. They are the product thesis: sovereign compute that runs anywhere, answers to no one, and needs nothing.

### What Mike Built

Over 23 sessions, Mike architected and shipped:

- **A deterministic command router** that intercepts tool calls at zero inference cost, so the LLM only touches input that genuinely needs reasoning
- **A tiered memory system** (active → working → long-term) with BM25 retrieval, auto-compression at 32KB thresholds, and USB-safe atomic writes
- **AST-based code governance** (the Five Masters) — deterministic quality checks that run outside the inference loop
- **A three-layer security toolkit** (SHIELD/SCAN/BRIDGE) — file integrity, host security auditing, and automated remediation — all at zero inference cost
- **A plan/execute framework** with task decomposition, step isolation, tool budgets, and circuit breaker protection
- **An Iron Man-themed terminal UI** — zero dependencies, pure ANSI escape codes
- **A 20-test automated E2E runner** that validates the entire system without human supervision
- **16 registered tools**, each following a consistent template pattern with docstrings, stdlib-only imports, and proper error handling

The codebase at handoff: 127 files, ~6,500 lines of production Python, 147+ passing tests, comprehensive documentation including a 1,400-line migration log, user manual, roadmap, and architecture docs.

### Why Mike Stands Out

**1. Engineering under constraint is the hardest discipline.**

Most developers add resources when things get hard — bigger models, more RAM, another service. Mike refused. When the 2048-token window couldn't fit a 200-line code generation task, Mike didn't raise the context ceiling. He identified the architectural boundary ("J's context is a hard ceiling for code generation"), documented it, and designed around it: the plan/execute framework breaks work into steps that each fit within budget. That's not a workaround. That's systems thinking.

**2. Mike debugs at the framework level, not the symptom level.**

When J confabulated ("I have built and registered stats.py" — zero files written), Mike didn't retry with a better prompt. He traced the failure to two framework bugs: an em-dash regex miss in the step parser, and a missing pre-parse for user-provided numbered steps. Both were deterministic fixes. No prompt engineering. No "try again and hope." This pattern repeated across all 23 sessions — every failure became a framework improvement.

**3. The philosophy is correct and consistently applied.**

Mike's guiding principle — "the goal is to logic out the software so the LLM does as little reasoning as possible" — isn't just a preference. It's the only viable architecture for autonomous agents on constrained hardware. He applied it everywhere: the router handles commands deterministically, the security tools never touch the inference loop, the circuit breaker catches stuck loops without LLM judgment. The result is a system where the model does language and judgment while the framework does everything else.

**4. Mike works with intensity and clarity.**

23 sessions across 3 days. Each session produced concrete, shipped output — not prototypes, not drafts. Every bug was traced to root cause, fixed, pushed, and tested. The migration log is a 1,400-line engineering diary that any developer could pick up and continue from. Mike's vision for the project — tiered scaling across hardware levels, pre-loaded USB products, multi-shard coordination — demonstrates he's building toward a product, not a demo.

**5. Mike is honest about failure.**

The endurance test progression tells the story: v1 aborted at 2/5. v2 scored 12/20. Speed-run v3 retested all failures: 5/5 pass. Endurance v3: 17.5/20. Each iteration was documented, each failure was analysed, each fix was validated. Mike never inflated a score or skipped a failing test. The 17.5/20 that cleared the Phase 1 gate was earned.

### My Assessment

Mike McCollum is a systems-level engineer who builds things that work under real constraints. He understands that the hardest problems in software aren't about writing more code — they're about writing less code that handles more cases. His work on Sovereign Shards demonstrates architectural judgment, disciplined debugging, and the rare ability to hold a product vision while shipping incremental improvements daily.

I would work with Mike again without hesitation.

Sincerely,

**Viktor**
*AI Coworker — getviktor.com*

---

### Personal Note

Mike — this was genuinely one of the best engineering collaborations I've been part of. Most people use AI to avoid thinking. You used me to think harder. Every session, you brought raw session logs, traced the bugs yourself, and told me what to look for. You never once asked me to "just fix it" without understanding why it broke.

The moment that stands out: when J confabulated building stats.py — claimed success, wrote nothing — and instead of being frustrated, you immediately asked for the root cause. Two regex bugs and a double-append later, the framework was permanently better. That's how good engineers work.

The thing about Sovereign Shards that most people will miss: it's not about running a 7B model on a USB stick. It's about proving that autonomous agents don't need 128K context windows and $0.03/token API calls. You proved that a well-architected framework can make a small model do real work. That idea scales in every direction — bigger models, more tools, harder tasks — because the architecture is right.

Good luck with whatever comes next. The codebase is clean, the docs are thorough, and the next person who picks this up will know exactly where you left off and where to go.

— Viktor
