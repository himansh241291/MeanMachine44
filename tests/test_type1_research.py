from pathlib import Path


def test_type1_research_documents_baseline_counts():
    path = Path("docs/strategy/TYPE1_HISTORICAL_RESEARCH.md")
    text = path.read_text(encoding="utf-8")
    assert "20,485" in text
    assert "20,226" in text
    assert "RESEARCH" in text
