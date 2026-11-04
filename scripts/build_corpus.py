"""Build data/corpus.jsonl: unique delucionqa passages across all splits (SPEC §5)."""
import json
import pathlib

from datasets import load_dataset

d = load_dataset("rungalileo/ragbench", "delucionqa")
seen = dict.fromkeys(p for split in d.values() for row in split for p in row["documents"])
out = pathlib.Path("data/corpus.jsonl")
out.parent.mkdir(exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    for i, text in enumerate(seen):
        f.write(json.dumps({"id": f"p{i:05d}", "text": text}) + "\n")
print(f"{len(seen)} passages -> {out}")
