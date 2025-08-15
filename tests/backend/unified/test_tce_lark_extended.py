from backend.unified.translators.tce_lark_translator import TceLarkTranslator
from backend.unified.core.result_enhanced import Success

tx = TceLarkTranslator()


def test_previous_value_rule():
    ce = "always previous door equals 0."
    res = tx.translate(ce, "CONTROLLED_ENGLISH", "TAU")
    assert isinstance(res, Success)
    assert res.value == "always (door[t-1] = 0)"


def test_conditional_rule():
    ce = "if fireAlarm then 0 else 1."
    res = tx.translate(ce, "CONTROLLED_ENGLISH", "TAU")
    assert isinstance(res, Success)
    assert res.value == "(fireAlarm ? 0 : 1)"


def test_and_rule():
    ce = "doorClosed and motorRunning."
    res = tx.translate(ce, "CONTROLLED_ENGLISH", "TAU")
    assert isinstance(res, Success)
    assert res.value == "(doorClosed & motorRunning)"


def test_or_rule():
    ce = "overload or emergency."
    res = tx.translate(ce, "CONTROLLED_ENGLISH", "TAU")
    assert isinstance(res, Success)
    assert res.value == "(overload | emergency)" 