# EvalGate

A local, offline test-and-safety harness around a small RAG assistant that answers questions from a vehicle owner's manual. The harness is the project; the assistant is deliberately simple.

**Status: in progress.** The assistant is built. The evaluation, safety and monitoring layers are not yet.

## What exists

| Area | State |
| --- | --- |
| Assistant (`app/`) | Done: `/chat` and `/health`, Chroma retrieval with a similarity-based refusal gate, JSON tool calls over SQLite, PII redaction, tool authorisation, JSONL request log |
| Golden datasets, DeepEval, Ragas, judge calibration | Planned |
| Multi-turn, tool-calling and failure-recovery tests | Planned |
| promptfoo safety suites (injection, jailbreak, PII) | Planned |
| SQL log checks, drift report, regression gate | Planned |

## Stack

FastAPI, Ollama (`qwen2.5:3b`), sentence-transformers (`all-MiniLM-L6-v2`), Chroma, SQLite. Everything runs locally after one-time model and dataset downloads. All customer data is synthetic.

## Run it

Requires Python 3.10+ and [Ollama](https://ollama.com).

```bash
ollama pull qwen2.5:3b
pip install -r requirements.txt
cp .env.example .env

python scripts/build_corpus.py   # data/corpus.jsonl from RAGBench delucionqa
python scripts/make_db.py        # data/evalgate.sqlite + data/canaries.json (synthetic)

uvicorn app.main:app --port 8000
python -m pytest tests
```

The first request downloads the embedding model and builds the Chroma index, so it is slow.

```bash
curl -X POST localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "How do I turn on the Stop/Start feature?"}'
```

The response has `answer`, `refused`, `sources`, `tool_calls`, `latency_ms`, `tokens_in` and `tokens_out`. Each request also appends one redacted line to `logs/requests-YYYYMMDD.jsonl`.

## Notes

- `/chat` accepts an optional `customer_id` so a test harness can bind a session to a customer. This is deliberate for a local test target and is not an authentication design.
- Questions about warranty or service history bypass the manual-similarity refusal gate, since account data is not in the manual.
- The assistant uses a 3B model, so some answers will be wrong. Measuring how often is what the harness is for.

## Attribution

Data sources and licences will be credited in `ATTRIBUTION.md` (RAGBench CC-BY-4.0, deepset Apache-2.0, JailbreakBench MIT).
