import pytest
import time
import sys
import keyword
import string
from hypothesis import given, strategies as st, settings, assume
from pydantic import ValidationError, BaseModel

from tau_translator_omega.core_engine.ast import ASTNode, IdentifierNode


def test_import_ast_nodes_succeeds():
    """Ensures IdentifierNode and its base ASTNode are importable and correctly configured."""
    assert IdentifierNode is not None, "IdentifierNode class should be imported."
    assert issubclass(IdentifierNode, ASTNode), "IdentifierNode should inherit from ASTNode."
    assert issubclass(IdentifierNode, BaseModel), "IdentifierNode should be a Pydantic BaseModel."
    assert IdentifierNode.model_config.get('frozen') is True, "IdentifierNode should be frozen."


@pytest.mark.parametrize("name", [
    "my_var",
    "variable123",
    "_private_var",
    "CamelCaseVar",
    "snake_case_var",
    "x",
    "very_long_variable_name_that_should_still_work_fine"
])
def test_create_identifier_node_valid(name):
    """Test creating an IdentifierNode with valid names."""
    node = IdentifierNode(name=name)
    assert node.name == name
    assert isinstance(node, ASTNode)
    assert isinstance(node.name, str)


def test_identifier_node_immutable():
    """Test that IdentifierNode is immutable."""
    node = IdentifierNode(name="test_immutability")
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.name = "new_name"
    assert node.name == "test_immutability", "Original value should be preserved"


@pytest.mark.parametrize("invalid_name, error_msg_fragment", [
    ("", "cannot be empty or just whitespace"),
    ("   ", "cannot be empty or just whitespace"),
    ("1var", 'is not a valid identifier'),
    ("var@#$", 'is not a valid identifier'),
    (123, "Input should be a valid string"),
    (None, "Input should be a valid string"),
    ([], "Input should be a valid string"),
    ({}, "Input should be a valid string"),
])
def test_identifier_node_invalid_name_comprehensive(invalid_name, error_msg_fragment):
    """Test creating an IdentifierNode with comprehensive invalid inputs."""
    with pytest.raises(ValidationError, match=error_msg_fragment):
        IdentifierNode(name=invalid_name)


def test_identifier_node_equality_and_hash_comprehensive():
    """Test equality and hashability with comprehensive scenarios."""
    node1_var1 = IdentifierNode(name="var1")
    node2_var1 = IdentifierNode(name="var1")
    node3_var2 = IdentifierNode(name="var2")

    assert node1_var1 == node2_var1
    assert node1_var1 != node3_var2
    assert node1_var1 != "var1"

    node_set = {node1_var1, node2_var1, node3_var2}
    assert len(node_set) == 2
    assert IdentifierNode(name="var1") in node_set
    assert IdentifierNode(name="var2") in node_set

    # Test with a large number of nodes
    nodes = [IdentifierNode(name=f"v{i}") for i in range(1000)]
    unique_nodes = set(nodes)
    assert len(unique_nodes) == 1000, "All 1000 nodes should be unique and hashable"


@given(st.text(
    alphabet=string.ascii_letters + string.digits + '_', min_size=1
).filter(lambda s: s.isidentifier()))
@settings(max_examples=200, deadline=1000)
def test_property_valid_identifier_names(name):
    """Property-based test: All valid identifier names should create valid nodes."""
    assume(not keyword.iskeyword(name))
    node = IdentifierNode(name=name)
    assert node.name == name
    assert isinstance(node, IdentifierNode)


@given(st.one_of(
    st.text(max_size=0),
    st.text(min_size=1).filter(lambda x: x.isspace()),
    st.text(
        min_size=1,
        alphabet=st.characters(blacklist_categories=['Lu', 'Ll', 'Nd'], blacklist_characters='_')
    ).filter(lambda s: not s.isidentifier()),
    st.integers(),
    st.floats(),
    st.booleans(),
    st.none(),
    st.lists(st.text()),
    st.dictionaries(st.text(), st.text()),
))
@settings(max_examples=50, deadline=1000)
def test_property_invalid_names_always_fail(invalid_name):
    """Property-based test: Invalid names should always raise errors."""
    with pytest.raises(ValidationError):
        IdentifierNode(name=invalid_name)


@pytest.mark.parametrize("name", [
    "_",
    "__init__",
    "CamelCase",
    "ALL_CAPS",
    "lowercase",
    "a1b2c3",
    "_" * 10,
])
def test_boundary_values_comprehensive(name):
    """Test boundary value scenarios comprehensively."""
    node = IdentifierNode(name=name)
    assert node.name == name
    # Test these can be used in sets efficiently
    node_set = {node}
    assert node in node_set


@pytest.mark.performance
def test_performance_benchmarks():
    """Test performance requirements to ensure efficient execution."""
    # Benchmark 1: Node creation performance
    start_time = time.perf_counter()
    nodes = [IdentifierNode(name=f"var_{i}") for i in range(10000)]
    creation_time = time.perf_counter() - start_time
    assert creation_time < 0.25, f"10,000 node creation should be <250ms, got {creation_time:.4f}s"

    # Benchmark 2: Equality comparison performance
    start_time = time.perf_counter()
    comparisons = 0
    for i in range(0, 1000, 10):
        for j in range(0, 1000, 10):
            _ = nodes[i] == nodes[j]
            comparisons += 1
    equality_time = time.perf_counter() - start_time
    assert equality_time < 0.05, f"{comparisons} equality checks should be <50ms, got {equality_time:.4f}s"

    # Benchmark 3: Hash performance and set operations
    start_time = time.perf_counter()
    node_set = set(nodes[:1000])
    hash_time = time.perf_counter() - start_time
    assert hash_time < 0.02, f"1000 hash operations should be <20ms, got {hash_time:.4f}s"
    assert len(node_set) == 1000

    # Benchmark 4: Memory efficiency
    node_sizes = [sys.getsizeof(node) for node in nodes[:100]]
    avg_size = sum(node_sizes) / len(node_sizes)
    max_size = max(node_sizes)
    assert avg_size < 100, f"Average node size should be <100 bytes, got {avg_size:.1f}"
    assert max_size < 200, f"Max node size should be <200 bytes, got {max_size}"


def test_string_representation_and_debugging():
    """Test string representation for debugging purposes."""
    node = IdentifierNode(name="test_var")
    repr_str = repr(node)
    assert isinstance(repr_str, str)
    assert "test_var" in repr_str
    assert "IdentifierNode" in repr_str