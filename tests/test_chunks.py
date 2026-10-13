import pandas as pd
import pytest

from src.rag.chunk import OUT, chunk_markdown


def test_chunk_markdown_keeps_source_and_title():
    text = "# Titre\n" + "mot " * 100
    chunks = chunk_markdown(text, "demo/a.md")
    assert chunks and all(c["source"] == "demo/a.md" for c in chunks)
    assert chunks[0]["title"] == "Titre"


@pytest.fixture(scope="module")
def df():
    return pd.read_parquet(OUT)


def test_no_empty_chunk(df):
    assert (df["text"].str.strip().str.len() > 0).all()


def test_no_duplicate_text(df):
    assert not df["text"].duplicated().any()


def test_every_chunk_has_source(df):
    assert df["source"].notna().all() and (df["source"] != "").all()