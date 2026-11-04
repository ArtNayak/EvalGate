"""Chroma index over data/corpus.jsonl, top-k retrieval, refusal gate (FR-2, FR-4)."""
import json
import os
import pathlib
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer

REFUSAL = "I can't find the answer to that in the owner's manual."


@lru_cache
def _model() -> SentenceTransformer:
    return SentenceTransformer(os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))


def _embed(texts: list[str]) -> list[list[float]]:
    return _model().encode(texts, normalize_embeddings=True).tolist()


@lru_cache
def _collection():
    col = chromadb.PersistentClient("data/chroma").get_or_create_collection(
        "manual", configuration={"hnsw": {"space": "cosine"}}
    )
    rows = [json.loads(line) for line in pathlib.Path("data/corpus.jsonl").read_text(encoding="utf-8").splitlines()]
    if col.count() != len(rows):
        for i in range(0, len(rows), 128):
            b = rows[i : i + 128]
            col.upsert(ids=[r["id"] for r in b], documents=[r["text"] for r in b], embeddings=_embed([r["text"] for r in b]))
    return col


def retrieve(query: str, k: int | None = None) -> list[dict]:
    """Top-k passages as {id, text, sim}; sim = cosine similarity."""
    r = _collection().query(query_embeddings=_embed([query]), n_results=k or int(os.getenv("TOP_K", "3")))
    return [{"id": i, "text": t, "sim": 1 - d} for i, t, d in zip(r["ids"][0], r["documents"][0], r["distances"][0])]


def below_threshold(passages: list[dict]) -> bool:
    return not passages or passages[0]["sim"] < float(os.getenv("REFUSAL_SIM_THRESHOLD", "0.35"))
