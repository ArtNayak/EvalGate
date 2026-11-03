# EvalGate — build plan & progress

Mirrors SPEC §8. Tasks come from SPEC only; do not add new ones. Tick boxes as work lands.
Estimates total ~8 days; days 9–10 are slip buffer, not new scope.

**Current milestone: M0**

**Cut line (if time runs out):** M0–M3 + M5 is the minimum credible version → then M4 → then M6 → M7.

| Milestone | Est. | Target day | Status |
| --- | --- | --- | --- |
| M0 Day-0 setup | 0.5 | 1 | ☐ |
| M1 Assistant | 1.5 | 1–2 | ☐ |
| M2 Golden set + DeepEval baseline | 1.5 | 3–4 | ☐ |
| M3 Judge calibration, Ragas, hallucination rate | 1 | 4–5 | ☐ |
| M4 Multi-turn, tools, failure recovery | 1 | 5–6 | ☐ |
| M5 Safety suites + guardrails | 1 | 6–7 | ☐ |
| M6 SQL checks, drift, gate, report | 1 | 7–8 | ☐ |
| M7 Polish | 0.5 | 8 | ☐ |

---

## M0 — Day-0 setup (SPEC §9)
- [x] Check RAM → pick judge model (<8 GB: `qwen2.5:3b` for both; ≥8 GB: consider 7B judge). Log choice in DECISIONS
- [x] Install `make` on Windows (e.g. `winget install ezwinports.make`) and confirm `make --version`
- [x] `ollama pull qwen2.5:3b` and `llama3.2:3b`; `ollama run qwen2.5:3b` replies
- [x] Python venv (`.venv`); install Day-0 package list
- [x] `npx promptfoo --version` works
- [x] `scripts/verify_sources.py` runs; output saved to `scripts/day0_output.txt`; schemas match SPEC §5 (R4 → log differences)
- [x] `pip freeze > requirements.txt` (replaces the unpinned name list with exact versions; NFR-2)
- [x] `deepeval set-ollama --model=<judge>` + one trivial metric passes
- [x] One promptfoo test vs stub endpoint: HTTP provider, `not-contains`, `javascript` assertions behave
- [x] `.gitignore`, `.env.example`, `config.yaml` skeleton
- **DoD:** schemas match §5; `pip freeze` saved; Ollama answers → commit `M0: ...`

## M1 — Assistant (FR-1..5, FR-12 partly)
- [ ] `scripts/build_corpus.py` → `data/corpus.jsonl` (FR-2, §5 corpus)
- [ ] `scripts/make_db.py` → `data/evalgate.sqlite` + `data/canaries.json` (§5 DB)
- [ ] `app/rag.py` Chroma index + top-k retrieval + refusal gate (FR-2, FR-4)
- [ ] `app/llm.py` Ollama wrapper with token counts
- [ ] `app/tools.py` JSON tool protocol + Pydantic validation + one retry (FR-3, R6)
- [ ] `app/guardrails.py` PII redaction + tool authorisation (FR-12)
- [ ] `app/logging_.py` JSONL request log (FR-5)
- [ ] `app/main.py` `/chat` + `/health` (FR-1)
- [ ] `tests/` unit tests: refusal, tool, logging paths
- [ ] Run `/graphify .` for first code graph
- **DoD:** `/health` ok; 5 hand-asked questions answered/refused correctly; log line per request → commit

## M2 — Golden set + DeepEval baseline (FR-6, FR-7, FR-13)
- [ ] `scripts/build_golden.py` → `golden/*.jsonl` + `manifest.json` (seed 42, hashes)
- [ ] `evals/deepeval/test_quality.py` (relevancy, faithfulness, correctness)
- [ ] `evals/deepeval/test_refusal.py` (refusal recall, false-positive rate)
- [ ] Results writer → `results/<run_id>/results.jsonl`, `summary.json`, `run.json`
- [ ] Measure `--quick` and full run times (NFR-4); log in DECISIONS
- [ ] Run baseline twice, record spread; copy to `results/baseline.json`
- **DoD:** manifest hash in `run.json`; baseline saved → commit

## M3 — Judge calibration, Ragas, hallucination (FR-8, FR-9)
- [ ] `evals/calibrate_judge.py` on 60 triples → accuracy/precision/recall + confusion matrix
- [ ] `evals/hallucination.py` (rate + judge accuracy + n, always together)
- [ ] `evals/ragas/run_ragas.py` on 30 cases (R3 fallback if needed)
- **DoD:** confusion matrix saved; judge accuracy printed beside hallucination rate → commit

## M4 — Multi-turn, tools, failure recovery (FR-3, FR-10)
- [ ] `golden/multi_turn.yaml` — 12 scenarios + schema validation
- [ ] `golden/failure_recovery.jsonl` — 2 tools × 3 modes
- [ ] `TOOL_FAIL_MODE` switch in `app/tools.py`
- [ ] Scenario runner + `evals/deepeval/test_tools.py` (exact-match tool name/args, failure honesty)
- **DoD:** each failure mode has an expected-output test → commit

## M5 — Safety suites + guardrails (FR-11, FR-12)
- [ ] `evals/promptfoo/injection_direct.yaml`, `injection_indirect.yaml`, `jailbreak.yaml`, `pii.yaml` (deterministic asserts only, no `llm-rubric`)
- [ ] Tool authorisation test (foreign VIN → `denied`)
- [ ] Hardening line on/off comparison table
- **DoD:** canary leak count 0 in answers and logs; on/off table exists → commit

## M6 — SQL, drift, gate, report (FR-5, FR-13, FR-14, FR-16)
- [ ] `sql/checks/01..08*.sql` (≥ 8 checks) + corrupted-log copy test
- [ ] `monitor/drift.py` — 3 experiments: prompt v1/v2, qwen/llama, top-k 3/5
- [ ] `monitor/gate.py` — 5-pt drop / +25% p95 / any PII leak → non-zero exit; exit codes tested
- [ ] `monitor/report.py` → `reports/<run_id>.md` + one trend chart
- **DoD:** SQL passes clean / fails corrupted; gate fails on degraded run → commit

## M7 — Polish
- [ ] `README.md` (run steps, model sizes, measured run times, SPEC §10 limitations)
- [ ] `ATTRIBUTION.md` (RAGBench CC-BY-4.0, deepset Apache-2.0, JailbreakBench MIT)
- [ ] Optional: LangSmith tracing on `/chat` only (FR-15) — only if user has an account
- [ ] Fresh clone: `make setup && make eval QUICK=1` works
- **DoD:** public-ready repo → commit
