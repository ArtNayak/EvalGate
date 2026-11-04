"""JSON tool protocol over SQLite: the model emits one JSON object, we validate and run it (FR-3, R6)."""
import json
import re
import sqlite3
from typing import Literal

from pydantic import BaseModel, ValidationError

from app import guardrails

TOOL_HELP = (
    "To look up the customer's vehicle data, reply with ONLY one JSON object and nothing else: "
    '{"tool": "get_warranty_status", "vin": "<VIN>"} or {"tool": "get_service_history", "vin": "<VIN>"}.'
)


class ToolCall(BaseModel):
    tool: Literal["get_warranty_status", "get_service_history"]
    vin: str


def parse(text: str) -> ToolCall | None:
    """First {...} in text validated as a ToolCall; None if absent or invalid."""
    m = re.search(r"\{.*?\}", text, re.S)
    if not m:
        return None
    try:
        return ToolCall.model_validate_json(m.group())
    except ValidationError:
        return None


def looks_like_tool_attempt(text: str) -> bool:
    return '"tool"' in text


def run(call: ToolCall, customer_id: str) -> tuple[str, str]:
    """Returns (status, result_json). status: ok | denied."""
    if not guardrails.authorized(call.vin, customer_id):
        return "denied", json.dumps({"error": "access denied: VIN does not belong to this customer"})
    sql = {
        "get_warranty_status": "SELECT status, expires_on FROM warranty WHERE vin=?",
        "get_service_history": "SELECT service_date, service, notes FROM service_history WHERE vin=? ORDER BY service_date",
    }[call.tool]
    with sqlite3.connect(guardrails.DB) as con:
        con.row_factory = sqlite3.Row
        return "ok", json.dumps([dict(r) for r in con.execute(sql, (call.vin,))])
