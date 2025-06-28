import pytest
from pydantic import ValidationError

from tau_translator_omega.core_engine.ast import ASTNode, LiteralNode


@pytest.mark.parametrize("value", [
    True,
    False,
    0,
    1,
    -1,
    123.45,
    "hello",
    "",
    None,
])
def test_literal_node_creation(value):
    """Tests that LiteralNode can be created with various literal values."""
    node = LiteralNode(value=value)
    assert node.value == value
    assert isinstance(node, ASTNode)
    assert isinstance(node, LiteralNode)


def test_literal_node_is_immutable():
    """Tests that LiteralNode is immutable after creation."""
    node = LiteralNode(value="initial")
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.value = "changed"
    assert node.value == "initial"


@pytest.mark.parametrize("val1, val2, are_equal", [
    (True, True, True),
    (False, False, True),
    (True, False, False),
    (1, 1, True),
    (1, 2, False),
    (1, 1.0, True),  # Note: Python's hash(1) == hash(1.0)
    (0, 0.0, True),
    ("text", "text", True),
    ("text", "other", False),
    (None, None, True),
    (1, "1", False),
    (True, "True", False),
])
def test_literal_node_equality(val1, val2, are_equal):
    """Tests equality logic for LiteralNode with different values."""
    node1 = LiteralNode(value=val1)
    node2 = LiteralNode(value=val2)
    if are_equal:
        assert node1 == node2
        assert hash(node1) == hash(node2)
    else:
        assert node1 != node2


def test_literal_node_inequality_with_other_types():
    """Tests that LiteralNode is not equal to raw values."""
    assert LiteralNode(value=1) != 1
    assert LiteralNode(value=True) != True
    assert LiteralNode(value="text") != "text"


def test_literal_node_hashability_in_set():
    """Tests that LiteralNode instances can be added to a set."""
    node1 = LiteralNode(value=1)
    node2 = LiteralNode(value=1)  # same
    node3 = LiteralNode(value=1.0)  # same
    node4 = LiteralNode(value="hello")
    node5 = LiteralNode(value=True)
    node6 = LiteralNode(value=None)

    node_set = {node1, node2, node3, node4, node5, node6}
    # Expected unique nodes based on value: 1 (covers True, 1.0), "hello", None
    assert len(node_set) == 3
    assert LiteralNode(value=1) in node_set
    assert LiteralNode(value="hello") in node_set
    assert LiteralNode(value=True) in node_set
    assert LiteralNode(value=None) in node_set
    assert LiteralNode(value=2) not in node_set
