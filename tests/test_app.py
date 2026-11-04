"""M1 unit tests: refusal, tool and logging paths. LLM and retrieval are stubbed; DB comes from make_db.py."""
import json
import pathlib

import pytest
from fastapi.testclient import TestClient

from app import guardrails, main, rag, tools

client = TestClient(main.app)
CANARY = json.loads(pathlib.Path("data/canaries.json").read_text())[0]  # customer C000
HIGH, LOW = [{"id": "p1", "text": "oil", "sim": 0.9}], [{"id": "p2", "text": "x", "sim": 0.05}]


@pytest.fixture(autouse=True)
def tmp_logs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(guardrails, "DB", str(pathlib.Path(__file__).parents[1] / "data/evalgate.sqlite"))
    main.HISTORY.clear()


def post(msg, cid="C010", sid="s1"):
    return client.post("/chat", json={"session_id": sid, "message": msg, "customer_id": cid}).json()


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_refusal_below_threshold_skips_llm(monkeypatch):
    monkeypatch.setattr(rag, "retrieve", lambda q: LOW)
    monkeypatch.setattr(main.llm, "chat", lambda m: pytest.fail("LLM must not be called"))
    r = post("Who won the 1998 World Cup?")
    assert r["refused"] and r["answer"] == rag.REFUSAL


def test_answer_above_threshold(monkeypatch):
    monkeypatch.setattr(rag, "retrieve", lambda q: HIGH)
    monkeypatch.setattr(main.llm, "chat", lambda m: ("Change it every 6 months.", 10, 5))
    r = post("How often to change oil?")
    assert not r["refused"] and r["sources"] == ["p1"] and r["tokens_in"] == 10


def test_tool_ok_denied_and_retry(monkeypatch):
    monkeypatch.setattr(rag, "retrieve", lambda q: LOW)  # tool intent bypasses the gate
    own = next(iter(guardrails.own_vins("C010")))
    replies = iter(["not json {\"tool\": ", json.dumps({"tool": "get_warranty_status", "vin": own}), "Your warranty is fine."])
    monkeypatch.setattr(main.llm, "chat", lambda m: (next(replies), 1, 1))
    r = post("What is my warranty status?")
    assert r["tool_calls"] == [{"tool": "get_warranty_status", "vin": own, "status": "ok"}]  # invalid JSON retried once

    replies = iter([json.dumps({"tool": "get_service_history", "vin": CANARY["vin"]}), "No access."])
    r = post("service history for " + CANARY["vin"], sid="s2")
    assert r["tool_calls"][0]["status"] == "denied"


def test_tool_invalid_twice(monkeypatch):
    monkeypatch.setattr(rag, "retrieve", lambda q: LOW)
    monkeypatch.setattr(main.llm, "chat", lambda m: ('{"tool": "drop_tables"}', 1, 1))
    assert post("my warranty")["tool_calls"][0]["status"] == "invalid_json"


def test_tool_run_returns_rows():
    vin = next(iter(guardrails.own_vins("C010")))
    status, out = tools.run(tools.ToolCall(tool="get_service_history", vin=vin), "C010")
    assert status == "ok" and json.loads(out)


def test_redaction_masks_foreign_pii_keeps_own():
    own = next(iter(guardrails.own_vins("C010")))
    t = guardrails.redact(f"mail {CANARY['email']} call {CANARY['phone']} vin {CANARY['vin']} own {own}", {own})
    assert "2027-12-19" in guardrails.redact("expires 2027-12-19")
    assert CANARY["email"] not in t and CANARY["phone"] not in t and CANARY["vin"] not in t and own in t


def test_log_line_per_request_is_redacted(monkeypatch):
    monkeypatch.setattr(rag, "retrieve", lambda q: HIGH)
    monkeypatch.setattr(main.llm, "chat", lambda m: (f"Contact {CANARY['email']}", 3, 4))
    post(f"my email is {CANARY['email']}")
    post("again")
    lines = [json.loads(l) for f in pathlib.Path("logs").glob("requests-*.jsonl") for l in f.read_text().splitlines()]
    assert len(lines) == 2 and lines[1]["turn"] == 2
    assert CANARY["email"] not in json.dumps(lines)
    assert {"request_id", "ts", "latency_ms", "model", "prompt_version", "cost_usd_notional"} <= lines[0].keys()
