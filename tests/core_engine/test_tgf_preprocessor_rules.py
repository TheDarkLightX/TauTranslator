import pytest
from tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor
from pathlib import Path

# Duplicating normalize_lark_string for now. Consider moving to a shared test util.
def normalize_lark_string(lark_string: str) -> str:
    """Normalizes Lark grammar string by stripping leading/trailing whitespace from each line
       and removing empty lines. This makes comparisons less brittle.
    """
    lines = [line.strip() for line in lark_string.strip().splitlines()]
    return "\n".join(filter(None, lines))

class TestTgfPreprocessorRuleParsing:
    def test_single_simple_rule_no_alias(self):
        """Tests a single simple rule without an alias."""
        tgf_content = "my_rule : A B C ;"
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = "my_rule: A B C"
        actual_lark_output = preprocessor.to_lark()
        
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_single_simple_rule_with_alias(self):
        """Tests a single simple rule with an alias."""
        tgf_content = "expression : term (PLUS term)* :additive_expr ;"
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = "expression: term (PLUS term)* -> additive_expr"
        actual_lark_output = preprocessor.to_lark()
        
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_simple_rule_with_alias_and_whitespace_symbol(self):
        tgf_content = """
    @trim _ .
    # A simple rule definition
    start_symbol => "BEGIN" _ content_rule _ "END" :main_structure
        """
        
        preprocessor = TGFPreprocessor(tgf_content)
        # preprocessor._whitespace_rules = ["_", "__"] # No longer needed

        expected_lark_output = """
    // TGF Directive: @trim _ .
    // TGF Comment: # A simple rule definition
    start_symbol: "BEGIN" content_rule "END" -> main_structure
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_multiline_rule_with_alternatives_and_aliases(self):
        tgf_content = """
# A more complex rule
complex_rule =>
    first_part ANOTHER_THING :label_one
  | "literal" (OPTIONAL_GROUP)? :label_two
  | YET_ANOTHER_RULE
        """
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = """
// TGF Comment: # A more complex rule
complex_rule: first_part ANOTHER_THING -> label_one
    | "literal" (OPTIONAL_GROUP)? -> label_two
    | YET_ANOTHER_RULE
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_rule_block_ending_with_comment(self):
        tgf_content = """
rule_one => BODY_ONE
# This comment ends rule_one block
rule_two => BODY_TWO
        """
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = """
rule_one: BODY_ONE
// TGF Comment: # This comment ends rule_one block
rule_two: BODY_TWO
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_rule_block_ending_with_directive(self):
        tgf_content = """
rule_alpha => ALPHA_BODY
@use char classes some_class.
rule_beta => BETA_BODY
        """
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = """
rule_alpha: ALPHA_BODY
// TGF Directive: @use char classes some_class.
rule_beta: BETA_BODY
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
        assert "some_class" in preprocessor._char_classes_used

    def test_parenthesized_group_with_alias(self):
        tgf_content = """
choice_rule => (OPTION_A | OPTION_B) :selected_choice
        """
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output_current_impl = """
choice_rule: OPTION_A | OPTION_B -> selected_choice
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output_current_impl)

    def test_empty_lines_between_rules(self):
        tgf_content = """
rule_x => X_BODY


rule_y => Y_BODY
        """
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = """
rule_x: X_BODY
rule_y: Y_BODY
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_no_alias_rule(self):
        tgf_content = "simple => A B C"
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "simple: A B C"
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_rule_with_alternatives_no_aliases(self):
        """Tests a rule with alternatives, without any aliases."""
        tgf_content = "value : NUMBER | STRING | list | map ;"
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = """
value: NUMBER
     | STRING
     | list
     | map
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_rule_with_alternatives_and_aliases(self):
        """Tests a rule with alternatives, where some alternatives have aliases."""
        tgf_content = "statement : assignment_stmt :assign | expr_stmt :expression_statement | if_stmt ;"
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = """
statement: assignment_stmt -> assign
         | expr_stmt -> expression_statement
         | if_stmt
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_multiline_rule_simple(self):
        """Tests a simple multi-line rule."""
        tgf_content = """
complex_rule : part_A part_B
             | part_C (part_D | part_E)
             | part_F
             ;
        """
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = """
complex_rule: part_A part_B
            | part_C (part_D | part_E)
            | part_F
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_multiline_rule_with_aliases(self):
        """Tests a multi-line rule where some alternatives have aliases."""
        tgf_content = """
complex_statement : assignment_stmt :assign_op
                  | if_stmt
                  | while_loop :loop_construct
                  ;
        """
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = """
complex_statement: assignment_stmt -> assign_op
                 | if_stmt
                 | while_loop -> loop_construct
        """
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
