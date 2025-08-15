"""UI package init for imports in tests."""

try:
    from .tau_translator_desktop_qt_autocomplete import TauTranslatorQt  # type: ignore # noqa: F401
except Exception:
    # Fallback minimal stub to satisfy imports during headless test collection
    class TauTranslatorQt:  # type: ignore
        pass


