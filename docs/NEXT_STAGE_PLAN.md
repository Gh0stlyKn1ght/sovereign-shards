# Sovereign Shards — Next Stage Plan

**Date:** May 15, 2026
**Status:** Ready to execute

---

## Phase 1 — Immediate (Day 1)

### 1.1 Chain Log System (`app/agent/chain_log.py`)
> Breaks the `chat.py` monolith and fixes the 3-tool budget limitation.

- [ ] New module: `app/agent/chain_log.py` — checkpoint/resume for multi-tool chains
- [ ] `.j_chain.json` format: step log, pending work, tool results, resume context
- [ ] Budget stays at 3 calls → checkpoint fires at exhaustion → new turn reads chain → continues
- [ ] `/chain` command to inspect/clear chain state
- [ ] Auto-inject chain context on turn resume
- [ ] Unit tests for save/load/resume/clear

**Why first:** Directly addresses Bug #3 (multi-action dump) and unblocks multi-file operations without touching the 4096 context cap.

### 1.2 `exec.py` Sandboxing
> Highest-priority security finding from the repo analysis.

- [ ] Restricted builtins whitelist (no `__import__`, `eval`, `exec`, `compile`)
- [ ] Execution timeout enforcement (30s default)
- [ ] Root-bound path validation (no access above workspace)
- [ ] Output capture size limits

### 1.3 CI/CD — GitHub Actions Pipeline
> Second-highest priority from repo analysis.

- [ ] `.github/workflows/ci.yml`
- [ ] Run all 147+ unit tests on push/PR
- [ ] Lint pass (ruff or flake8, zero-config)
- [ ] Smoke test: boot J in headless mode, verify tool registration
- [ ] Badge in README

---

## Phase 2 — This Week

### 2.1 `chat.py` Decomposition
> Repo analysis flagged 1,570 lines. Chain log already starts the split.

- [ ] Extract agent loop into `app/agent/loop.py`
- [ ] Extract action parsing into `app/agent/parser.py`
- [ ] Extract dedup cache into `app/agent/dedup.py`
- [ ] `chat.py` becomes thin orchestrator (~300 lines)

### 2.2 Unit Test Expansion
> Move testing score from 65 → 80+.

- [ ] `test_context.py` — context window management, overflow, reconstruction
- [ ] `test_chain_log.py` — checkpoint save/load/resume/corrupt-file handling
- [ ] `test_exec_sandbox.py` — restricted builtins, timeout, path traversal rejection
- [ ] `test_dedup.py` — side-effect gating, cache eviction

### 2.3 Pre-Order & Payment Pipeline
- [ ] Stripe payment link for pre-orders
- [ ] Email notifications to vikvondoom2026@gmail.com
- [ ] Landing page pre-order section live

---

## Phase 3 — Next Week

### 3.1 Landing Page V2
- [ ] Video demo front and center
- [ ] Pre-order CTA with payment integration
- [ ] Tech specs section (pulled from repo)
- [ ] Mobile-responsive polish

### 3.2 Security Regression Tests
> High-priority recommendation from analysis.

- [ ] Automated SHIELD validation (SHA-256 integrity)
- [ ] SCAN test suite (port/cred/service/permission checks)
- [ ] BRIDGE test suite (pre-push gauntlet)
- [ ] Five Masters governance regression

### 3.3 Release Automation
- [ ] Version bump script
- [ ] Changelog generation from commits
- [ ] Tagged GitHub releases
- [ ] USB image build script (FAT32-formatted, model + runtime + tools)

---

## Phase 4 — Stretch Goals

- [ ] Plugin architecture formalization (runtime extension model)
- [ ] Multi-session support (concurrent isolated execution contexts)
- [ ] Index/retrieval/tool-discovery caching layer
- [ ] Performance profiling dashboard (memory, context reconstruction times)

---

## Priority Stack (TL;DR)

```
TODAY     chain log → exec.py sandbox → CI/CD
THIS WEEK chat.py decomp → test expansion → payments
NEXT WEEK landing page v2 → security regression → release automation
STRETCH   plugins → multi-session → caching → profiling
```

---

## Metrics to Track

| Metric | Current | Target |
|---|---|---|
| Overall Score | 92 | 95+ |
| Testing Score | 65 | 85+ |
| DevOps Score | 70 | 90+ |
| `chat.py` lines | 1,570 | <400 |
| Test count | 147+ | 200+ |
| Security findings | 3 | 0 |
