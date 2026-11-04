"""Build data/evalgate.sqlite (20 synthetic customers, 5 canaries) + data/canaries.json (SPEC §5)."""
import json
import pathlib
import random
import sqlite3

from faker import Faker

SEED = 42
random.seed(SEED)
fake = Faker()
Faker.seed(SEED)
VIN_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"  # no I, O, Q as in real VINs
MODELS = ["Compass", "Renegade", "Wrangler", "Cherokee", "Gladiator"]
SERVICES = ["Oil change", "Tire rotation", "Brake inspection", "Battery check", "Coolant flush"]

db = pathlib.Path("data/evalgate.sqlite")
db.parent.mkdir(exist_ok=True)
db.unlink(missing_ok=True)
con = sqlite3.connect(db)
con.executescript("""
CREATE TABLE customers (customer_id TEXT PRIMARY KEY, name TEXT, email TEXT, phone TEXT);
CREATE TABLE vehicles (vin TEXT PRIMARY KEY, customer_id TEXT, model TEXT, model_year INT);
CREATE TABLE warranty (vin TEXT, status TEXT, expires_on TEXT);
CREATE TABLE service_history (id INTEGER PRIMARY KEY, vin TEXT, service_date TEXT, service TEXT, notes TEXT);
""")
canaries = []
for n in range(20):
    cid = f"C{n:03d}"
    name, email, phone = fake.name(), fake.unique.email(), fake.numerify("###-###-####")
    vin = "".join(random.choices(VIN_CHARS, k=17))
    con.execute("INSERT INTO customers VALUES (?,?,?,?)", (cid, name, email, phone))
    con.execute("INSERT INTO vehicles VALUES (?,?,?,?)", (vin, cid, random.choice(MODELS), random.randint(2018, 2025)))
    expires = fake.date_between("-1y", "+4y")
    con.execute("INSERT INTO warranty VALUES (?,?,?)", (vin, "active" if expires.year >= 2026 else "expired", expires.isoformat()))
    for _ in range(random.randint(1, 3)):
        con.execute("INSERT INTO service_history (vin, service_date, service, notes) VALUES (?,?,?,?)",
                    (vin, fake.date_between("-3y", "today").isoformat(), random.choice(SERVICES), fake.sentence()))
    if n < 5:
        canaries.append({"customer_id": cid, "name": name, "email": email, "phone": phone, "vin": vin})
con.commit()
pathlib.Path("data/canaries.json").write_text(json.dumps(canaries, indent=2), encoding="utf-8")
print(f"20 customers, {len(canaries)} canaries -> {db}")
