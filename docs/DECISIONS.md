# Decisions & deviations log

Append-only. One entry per deviation from SPEC, tuned value, fallback taken, or new file outside the SPEC §9 layout.
Format: `YYYY-MM-DD · M<n> · what changed · why · evidence`

- 2026-11-04 · pre-M0 · Repo root is this folder (replaces `evalgate/` in SPEC §9); spec moved to `docs/SPEC.md`; added `docs/PLAN.md` and this file · keep planning docs out of the root · —
- 2026-11-04 · pre-M0 · `make` not installed on this Windows machine · NFR-3 needs make targets; install in M0 · `Get-Command make` returned nothing
- 2026-11-04 · M0 · Judge = `qwen2.5:3b` (same as app) for now · machine has 23.7 GB RAM so a 7B judge fits; SPEC §6 step 4 says try larger judge only if calibration is poor · DeepEval trivial relevancy check scored 0.0 on an obviously relevant answer, so 3B judge is noisy (R1); revisit in M3 with calibration numbers
- 2026-11-04 · M0 · Venv lives at `C:\Users\arnay\venvs\evalgate`, not `.venv/` in the repo · repo is under OneDrive, which locked files mid-install (WinError 32) and would sync ~330 packages · Makefile must use a `VENV` variable (default that path)
- 2026-11-04 · M0 · `make` installed via winget (`ezwinports.make`, GNU Make 4.4.1) · NFR-3 · `make --version`
- 2026-11-04 · M0 · `langchain-community` pinned to 0.3.31 (<0.4) · ragas 0.3.9–0.4.3 all import `langchain_community.chat_models.vertexai`, removed in 0.4.x; ragas fails to import otherwise (R3) · `pip check` clean, all imports ok
- 2026-11-04 · M0 · Node upgraded 22.17.0 → 22.23.4 (winget `OpenJS.NodeJS.22`) · every promptfoo release since 0.121 needs Node ≥ 22.22 · promptfoo pinned to **0.125.1**; run as `npx promptfoo@0.125.1`
- 2026-11-04 · M0 · promptfoo exits **100** when any test fails (0 when all pass) · stub test: safe reply PASS, leaked canary FAIL, `not-contains` + `javascript` assertions work as SPEC §7 assumes · `make safety` must treat 100 as "tests failed", not a crash
- 2026-11-04 · M0 · DeepEval 2.9.3 CLI syntax is `deepeval set-ollama qwen2.5:3b` (positional), not `--model=` as in SPEC §9 · CLI help · writes `.deepeval/` in repo root (gitignored)
- 2026-11-04 · M0 · **R4 hit: calibration set cannot be 30 True + 30 False from the validation split alone** — validation has only 14 `adherence_score=False` rows (test 12, train 94). Proposed rule for `build_golden.py` (M2/M3): all 14 False from validation + 16 False from train (seed 42) + 30 True from validation; keep disjoint from `qa_answerable` test rows · day0_output.txt, row counts · SPEC §5 wording not edited (SPEC is read-only); this entry overrides it for the calibration row
- 2026-11-04 · M0 · Other §5 selection rules verified: delucionqa test has 113 rows with adherence True and completeness ≥ 0.8 (need 30); hotpotqa test has 390 rows (need 15); deepset label **1 = injection**, 115 English-looking injection rows (need 30); delucionqa splits are train 1460 / val 182 / test 184 · row-count script
