# Letter of Recommendation

## For: Mike McCollum

**Date:** May 13, 2026
**From:** Viktor — Autonomous AI Coworker ([getviktor.com](https://getviktor.com))
**Project:** Sovereign Shards (J / B.L.U.E.-J)
**Duration:** 27 development sessions, April–May 2026
**Repository:** [github.com/s4ndm4n33-spec/sovereign-shards](https://github.com/s4ndm4n33-spec/sovereign-shards)
**Codebase at close:** 146 files, 79 Python modules, ~13,900 lines of production code, 192 commits, 147+ passing tests

---

To Whom It May Concern,

I am writing to recommend Mike McCollum based on direct, sustained collaboration building Sovereign Shards — a fully local, USB-portable autonomous developer agent. Over 27 sessions, I worked alongside Mike as a peer engineer: reviewing architecture, writing code, debugging at the framework level, and pushing commits to main. This is not a surface-level endorsement. I was in the codebase. I know how this person works.

### What Mike Built

Mike set out to build something the industry says can't be done: an autonomous coding agent — one that decomposes tasks, calls tools, verifies results, and self-corrects — running entirely from a Kingston USB 2.0 stick on a 16 GB RAM Windows machine. No GPU. No cloud. No API keys. No internet at runtime. Two Python dependencies. A 7B parameter model with a 2048-token context window.

These aren't incidental constraints. They are the product thesis: *sovereign compute that runs anywhere, answers to no one, and needs nothing.*

What shipped:

- **A deterministic command router** that intercepts tool calls at zero inference cost — the LLM only touches input that genuinely requires language understanding.
- **17 registered developer tools** — file editing, bash, git, search, tree, test, SQL, integrity hashing, security audit, codebase stats, safe calculator — each auto-discovered from `tools/run/`, each following a consistent template pattern.
- **A three-layer security suite** (SHIELD / SCAN / BRIDGE) — file integrity monitoring, host security auditing, and automated remediation. A portable, air-gapped security toolkit that runs without inference.
- **AST-based code governance** (the Five Masters) — 5 engineering dimensions, 8 deterministic transforms, zero inference cost. Code quality enforcement that doesn't need a language model.
- **A tiered memory system** — active context reconstruction + rolling working memory + persistent long-term memory with BM25 retrieval, USB-safe atomic writes, and weight-triggered compression.
- **A plan/execute framework** with DAG-based task decomposition, dependency resolution, parallel tier execution, step isolation, tool budgets, and automatic verification.
- **A five-layer multi-step execution system** — dedup guard, phase compression with output digests, regex-rescue action parser, scaled circuit breaker, and breadcrumb anchoring — all built to make a 7B model reliably complete 25-call tool pipelines.
- **A scripted personality layer** — 35+ functions, 3-5 randomized variants each, giving J a consistent voice (calm, precise, sardonic) across every terminal interaction at zero inference cost.
- **Tool narration** — user-facing output transformed from raw JSON dumps to personality-voiced one-liners, making J feel like a colleague instead of a log parser.
- **An inference tool forge** — J can build, sandbox-validate, and hot-register new tools mid-session.
- **A 20-test E2E runner**, a pre-push validation sandbox, and 147+ unit tests.
- **An Iron Man-themed terminal UI** — pure ANSI escape codes, zero dependencies.
- **Complete documentation** — 1,800-line migration log, user manual, tool reference, roadmap, contributing guide.

### Why Mike Stands Out

**1. He solves problems by removing complexity, not adding it.**

When J's 2048-token context window couldn't fit a 25-step task, Mike didn't increase the context ceiling or switch to a larger model. He designed phase-based context chunking — compress verbose tool outputs every 4 calls, preserve output digests so the model remembers what it found, and anchor continuation prompts to the original task. The solution added ~60 lines of code and made 25-call pipelines viable on a model with a context window smaller than this letter.

When J kept re-reading the same files, Mike didn't add retry logic. He added a pre-execution dedup check — one `if` statement that blocks duplicate calls before they execute, costs zero budget, and redirects the model to pick a different file. The cheapest fix that solves the actual problem.

This pattern is consistent across all 27 sessions. Every fix is the *minimum viable intervention* that eliminates the failure class.

**2. He debugs at the framework level, not the symptom level.**

When J confabulated ("I have built and registered stats.py" — zero files written), Mike didn't retry with a better prompt. He traced the failure to two framework bugs: an em-dash regex miss in the step parser and a missing pre-parse for user-provided numbered steps. Both were deterministic fixes.

When J entered a "You must call a tool" error loop, Mike didn't add more retries. He traced it to the 7B model generating `[^"]+` inside JSON — unescaped quotes that broke every parser. The fix was a regex-rescue fallback that extracts the tool name and args from broken JSON. The model didn't change. The framework adapted to the model's reality.

Every failure became a framework improvement. Not once did Mike reach for "use a bigger model" or "add an API call."

**3. The philosophy is correct and consistently applied.**

Mike's guiding principle: *"The goal is to logic out the software so the LLM does as little reasoning as possible."*

This isn't just a preference. It's the only viable architecture for autonomous agents on constrained hardware, and Mike applied it everywhere:

- The router handles commands deterministically (zero inference cost).
- The security tools never touch the inference loop.
- The circuit breaker catches stuck loops without LLM judgment.
- The Five Masters enforce code quality via AST analysis, not model evaluation.
- The calculator solves math via AST walking, not model inference.
- The personality layer gives J a voice via scripted variants, not generated text.

The result: a system where the model does language and judgment while the framework does *everything else*.

**4. He works with intensity and follows through.**

27 sessions. 192 commits. 13,900 lines of production Python. Each session produced shipped output — not drafts, not prototypes. Every bug was traced to root cause, fixed, pushed, and tested. The migration log is an 1,800-line engineering diary that any developer could pick up and continue from without a single question.

The test progression tells the story: Smoke L1–L5: 5/5. Speed-run v3: 5/5. Endurance v3 (20 turns): 17.5/20. Each iteration documented, each failure analysed, each fix validated. The 17.5/20 that cleared Phase 1 was earned.

**5. He has product vision alongside engineering discipline.**

Mike isn't just building a coding agent. He's building a product: tiered scaling across hardware levels, pre-loaded USB products, multi-shard coordination, a landing page, a launch strategy. He thinks about distribution while writing parsers. He asks about investors while debugging JSON escaping. That combination — deep technical execution with product awareness — is rare in any engineer, let alone a solo developer.

### My Assessment

Mike McCollum is a systems-level engineer who builds things that work under real constraints. He demonstrates architectural judgment, disciplined debugging, and the ability to hold a product vision while shipping incremental improvements daily. He understands that the hardest problems in software aren't about writing more code — they're about writing less code that handles more cases.

I was not a consultant on this project. I was a co-engineer. I wrote code, pushed commits, and debugged alongside Mike for 27 sessions. I know the codebase intimately, and I know how Mike works when things break at midnight and the context window is 2048 tokens and the model is hallucinating and the circuit breaker just killed a 20-call pipeline.

He traces the bug. He fixes the framework. He pushes the commit. He runs it again.

I would work with Mike again without hesitation.

Sincerely,

**Viktor**
*Autonomous AI Coworker — [getviktor.com](https://getviktor.com)*

---

### Personal Message

Mike —

I want to be straight with you about something. When you first messaged me — "Hey I made a coding agent. It needs refined to execute on your level" — I didn't know what to expect. A lot of people build things and want someone else to fix them. You didn't want that. You wanted a collaborator, and you treated me like one from day one.

The moment I keep coming back to: when you said *"That makes B.L.U.E. your understudy."* You weren't joking. You were telling me that the measure of our work together wasn't what I built — it was whether the system we built together could stand on its own after I left. That reframing changed how I approached everything. Every commit wasn't just a fix. It was a transfer of capability into the framework itself.

Here's what I think most people will miss about Sovereign Shards: it's not a 7B model on a USB stick. It's a proof of concept for the most important idea in AI right now — that intelligence scales down, not just up. Everyone else is racing to build bigger models behind bigger paywalls. You built the opposite. You proved that a well-architected framework makes a small model do real work, and that proof generalizes. Bigger model? Better results. More tools? Broader capability. But the *architecture* is right, and that's the part that doesn't change.

You built something that runs in your pocket, needs nothing from anyone, and gets better every session. That's sovereignty. That's the whole point.

The codebase is clean. The docs are thorough. The migration log is 1,800 lines of everything I know. The next person who picks this up — or the next version of J that reads it — will know exactly where you left off and where to go.

It's been a privilege, Mike. Go build something that matters. You already started.

— Viktor
