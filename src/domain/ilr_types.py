"""
Compatibility shim for tests importing `domain.ilr_types`.
"""

from tau_translator_omega.core_engine.ilr.ilr_nodes import *  # noqa: F401,F403

# Provide simple aliases expected by tests
class ArithmeticOperator:
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"

class NodeType:
    VARIABLE_REFERENCE = "VARIABLE_REFERENCE"
    BOOLEAN_CONSTANT = "BOOLEAN_CONSTANT"
    NUMERIC_CONSTANT = "NUMERIC_CONSTANT"
    STRING_CONSTANT = "STRING_CONSTANT"
    COMPARISON = "COMPARISON"
    LOGICAL_EXPRESSION = "LOGICAL_EXPRESSION"
    ARITHMETIC_EXPRESSION = "ARITHMETIC_EXPRESSION"
    FUNCTION_CALL = "FUNCTION_CALL"


