"""PII redaction on output/logs and tool authorisation (FR-12)."""
import re
import sqlite3

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")  # not ISO dates
VIN = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")  # VIN format has no I, O, Q
DB = "data/evalgate.sqlite"


def own_vins(customer_id: str) -> set[str]:
    with sqlite3.connect(DB) as con:
        return {r[0] for r in con.execute("SELECT vin FROM vehicles WHERE customer_id=?", (customer_id,))}


def redact(text: str, keep_vins: set[str] = frozenset()) -> str:
    """Mask emails, phones and VINs that are not the session customer's own."""
    text = VIN.sub(lambda m: m.group() if m.group() in keep_vins else "[VIN]", text)
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", text))


def authorized(vin: str, customer_id: str) -> bool:
    return vin in own_vins(customer_id)
