from __future__ import annotations

import os
import pytest
from backend.unified.services.nli_onnx import OnnxNliReranker


def test_nli_onnx_adapter_lexical_fallback(tmp_path):
    fake = tmp_path / "model.onnx"
    # do not create file -> should fallback
    rr = OnnxNliReranker(str(fake))
    best, reasons = rr.rerank("blue elephants exist", ["There exists x such that elephant(x)", "foo bar"])
    assert best.startswith("There exists")
    assert any("lexical" in r.lower() for r in reasons)


def test_nli_onnx_adapter_session_loaded_if_present(tmp_path):
    # if onnxruntime not installed or file invalid, still fallback gracefully
    fake = tmp_path / "model.onnx"
    fake.write_bytes(b"not an onnx model")
    rr = OnnxNliReranker(str(fake))
    best, reasons = rr.rerank("if payment approved then order shipped", ["for every u if login then profile", "if payment is approved then order is shipped"]) 
    assert isinstance(best, str)
    assert reasons


