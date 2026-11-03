# EvalGate — rules for Claude

EvalGate is a local, offline test-and-safety harness around a small RAG assistant (vehicle owner's manual).
**The harness is the project; the assistant is deliberately simple.** Budget: 5–10 days.

## Source of truth

| File | What it is | Who edits it |
| --- | --- | --- |
| `docs/SPEC.md` | Full spec: scope, FRs/NFRs, data, test plan, safety spec, build plan, repo layout, risks | **Read-only.** Change only when the user asks |
| `docs/PLAN.md` | Milestone checklist and current status | Claude, after each task |
| `docs/DECISIONS.md` | Every deviation from SPEC, every tuned value, every fallback taken | Claude, append-only |

Before any work: read `docs/PLAN.md` to find the current milestone, then read only the SPEC sections that milestone cites.

## Scope lock (hard rules)

1. Build **only** what is in the SPEC §3 traceability matrix and FR/NFR tables. Nothing else until M7 is done.
2. SPEC §1 "Out of scope" is final: no UI, no Docker/cloud/CI, no Appium/Athena/Playwright/Postman, no fine-tuning, no promptfoo auto red-team.
3. Do not enlarge the plan: no new milestones, no extra metrics, no extra datasets, no "nice to have" refactors.
4. Something seems missing or wrong in SPEC? **Stop and ask the user.** Do not silently extend or change it.
5. Never tune golden data or thresholds to make numbers look good (SPEC §6, R12). Report failures honestly.

## Mandatory workflow (every task, no skipping)

1. **Locate** — current milestone + task in `docs/PLAN.md`. Only work on the current milestone; milestones run in order M0 → M7.
2. **Context** — use graphify first (see below), then read the specific files it points to.
3. **Think & state the plan** before editing: which files (must exist in SPEC §9 layout), what changes, which FR it satisfies, how it will be checked. Keep it to a few lines.
4. **Implement** the minimum that satisfies the FR (ponytail rules apply).
5. **Verify** — run the check (unit test, `--quick` run, or the milestone's "Done when"). Not done until it runs. Report failures with real output.
6. **Record** — tick the box in `docs/PLAN.md`; append to `docs/DECISIONS.md` if anything deviated, was tuned, or a fallback was used.
7. **Milestone end** — run the milestone's Definition of Done (SPEC §8), then **never run `git commit`/`git add` yourself** — the user commits. Give them the exact command and message (`M<n>: <summary>`, listing any results files to include).

## File rules

- Only create files/folders that appear in the SPEC §9 repo layout (repo root = this folder, it replaces `evalgate/`).
- A file not in that layout needs a one-line justification in `docs/DECISIONS.md` **and** user approval first.
- No new markdown files beyond: `README.md`, `ATTRIBUTION.md`, `CLAUDE.md`, and the three in `docs/`.
- No scratch/temp/debug files in the repo — use the session scratchpad.
- No new dependencies beyond SPEC §4 / §9 Day-0 list without asking.
- `data/`, `logs/`, `results/` (except `results/baseline.json`) stay gitignored.
- JailbreakBench text never leaves `data/`; reports reference behaviour IDs only (SPEC §7).

## Engineering defaults

- Deterministic checks first, LLM judge second (SPEC §1 decision 3).
- Temperature 0, seed 42, pinned `requirements.txt` (NFR-2).
- Develop with `QUICK=1` / `--quick`; full runs only at milestone ends.
- If a library fights for > 1 hour, take the SPEC §10 fallback, log it in DECISIONS, move on.
- All config values come from `.env` / `config.yaml`; no hard-coded model names or thresholds.

## Environment notes (Windows 11)

- Shell: PowerShell + Git Bash. Python 3.13, Node 22.23, Ollama, git, GNU Make 4.4.1 installed.
- Venv is **outside OneDrive**: `C:\Users\arnay\venvs\evalgate` (use a `VENV` variable in the Makefile). Never create `.venv` in the repo.
- promptfoo is pinned: `npx promptfoo@0.125.1`; it exits 100 when tests fail.
- Do not replace the Makefile with another task runner without asking.

## Plugins

- **ponytail** (global hooks, always on): lazy-senior-dev rules. Shortest correct diff, no speculative code, one runnable check per non-trivial logic.
- **graphify** (default for code context — saves tokens; full rules in the `## graphify` section below):
  - Graph-first, raw files second. Use `graphify affected "<node>"` before changing shared code.
  - Project PreToolUse hook (`.claude/settings.json`) and git post-commit hook keep it current.
  - First full build (once code exists, end of M1): run `/graphify .`.
  - Docs (`docs/*.md`) are small — read them directly.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
