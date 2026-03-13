import os

from daily_update import generate_ai_explanation


def test_generate_ai_explanation_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = generate_ai_explanation("sample-table")
    assert result is None


def test_generate_ai_explanation_with_missing_package(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ImportError("openai not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    result = generate_ai_explanation("sample-table")
    assert result is None
