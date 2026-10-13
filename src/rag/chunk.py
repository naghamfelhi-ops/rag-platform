import re
from pathlib import Path

import pandas as pd
import yaml

from src.rag.ingest import load_config

OUT = Path("data/processed/chunks.parquet")


def chunk_markdown(text, source, max_chars=1500, overlap=200, min_chars=100):
    sections = re.split(r"\n(?=#{1,3} )", text)
    chunks = []
    for sec in sections:
        if not sec.strip():
            continue
        title = sec.splitlines()[0].lstrip("# ").strip()
        start = 0
        while start < len(sec):
            piece = sec[start:start + max_chars]
            if len(piece.strip()) >= min_chars:
                chunks.append({"text": piece.strip(), "source": source, "title": title})
            start += max_chars - overlap
    return chunks


def run():
    cfg = load_config()
    c = cfg["chunking"]
    rows = []
    for repo in cfg["corpus"]["repos"]:
        base = Path("data/raw") / repo["name"]
        for f in sorted((base / repo["docs_path"]).rglob("*.md")):
            text = f.read_text(encoding="utf-8", errors="ignore")
            source = f"{repo['name']}/{f.relative_to(base / repo['docs_path']).as_posix()}"
            rows += chunk_markdown(text, source, c["max_chars"], c["overlap"], c["min_chars"])
    df = pd.DataFrame(rows).drop_duplicates(subset="text").reset_index(drop=True)
    df.insert(0, "chunk_id", df.index)
    df.to_parquet(OUT, index=False)
    print(f"{len(df)} chunks sauvegardés dans {OUT}")


if __name__ == "__main__":
    run()