"""
Legacy import shim for Declarative TCE parser expected by some tests.

This build does not include a separate declarative parser; raise a clear
error so tests can skip or handle accordingly.
"""

class DeclarativeTCEParser:
    def parse(self, text: str):
        raise NotImplementedError("DeclarativeTCEParser is not available in this edition.")


