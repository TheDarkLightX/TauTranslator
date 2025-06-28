import pytest
import json
import shutil
from pathlib import Path
from tau_translator_omega.core_engine.parsers.grammar_driven_parser import GrammarDrivenParser
from tau_translator_omega.core_engine.grammar_processing import TGFGrammarService
from tau_translator_omega.infrastructure.grammar_io import GrammarRepository
from returns.result import Success
from lark import Tree

# Path to the fixture grammar and the source for common.lark
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
MINIMAL_GRAMMAR_FILE_PATH = FIXTURES_DIR / "grammars" / "minimal_logic_gates.lark"
LOGIC_GATES_TAU_PATH = FIXTURES_DIR / "cnl_tau_sources" / "logic_gates.tau"
COMMON_LARK_FILE_PATH = PROJECT_ROOT / "src" / "tau_translator_omega" / "core_engine" / "parsers" / "cnl_parser" / "grammars" / "common.lark"

def test_parse_logic_gates_tau(tmp_path):
    """
    Tests that the GrammarDrivenParser can parse the logic_gates.tau content
    using the minimal_logic_gates.lark grammar via the modern API.
    """
    # 1. Setup a temporary grammar environment
    temp_grammar_dir = tmp_path / "grammars"
    temp_grammar_dir.mkdir()
    temp_config_file = tmp_path / "grammar-files.json"

    # Copy necessary grammar files to the temporary location
    shutil.copy(MINIMAL_GRAMMAR_FILE_PATH, temp_grammar_dir)
    shutil.copy(COMMON_LARK_FILE_PATH, temp_grammar_dir)

    # 2. Create the grammar configuration file
    grammar_config = [
        {
            "id": "minimal-logic-gates-grammar",
            "name": "Minimal Logic Gates Grammar",
            "filename": "minimal_logic_gates.lark",
            "isActive": True, # Set this grammar as active for the test
            # "transformer_class": "tau_translator_omega.core_engine.cnl_parser.logic_gates_transformer.LogicGatesTransformer"
        }
    ]
    with open(temp_config_file, 'w') as f:
        json.dump(grammar_config, f)

    # 3. Instantiate the services and parser
    repo = GrammarRepository(grammar_dir=temp_grammar_dir, config_file=temp_config_file)
    service = TGFGrammarService(repository=repo)
    parser = GrammarDrivenParser(grammar_service=service)

    # 4. Assert that the parser initialized correctly
    assert parser.initialization_error_reason is None, f"Parser failed to initialize: {parser.initialization_error_reason}"
    assert parser.lark_parser is not None, "Lark parser instance was not created"

    # 5. Read the source content and perform the parsing
    source_code = LOGIC_GATES_TAU_PATH.read_text()
    result = parser.parse(source_code)

    # 6. Assertions to verify successful parsing
    assert result.success, f"Parsing failed: {result.error}"
    assert result.ast is not None, "Parsing produced a None AST."

    # Since no transformer is specified (or the specified one is missing/commented out),
    # the AST should be a raw Lark Tree.
    raw_ast = result.ast
    assert isinstance(raw_ast, Tree), f"Expected a Lark Tree, got {type(raw_ast)}"
    assert raw_ast.data == 'start', f"Expected root of the tree to be 'start', got {raw_ast.data}"
        # e.g., isinstance(first_rule.expression, BinaryOperation) and check operands/operator

    # Further detailed checks can be added based on the expected transformed AST structure.


TAU_TGF_CONTENT = """\
# To view the license please visit https://github.com/IDNI/tau-lang/blob/main/LICENSE.txt
@use char classes eof, space, digit, xdigit, alpha, alnum, punct, printable.

@enable productions charvar.

# 
start                  => rr _.

# TODO (LOW) maybe rename rr to program, rr_gssot or similar
rr                     => rec_relations _ wff:main _ '.'.
rec_relations          => (_ rec_relation _ '.')*. 
rec_relation           => ref _ ":=" _ (capture | ref | wff | bf).
ref                    => sym [offsets] ref_args
                                                [ _ "fallback" __ fp_fallback ].
fp_fallback            => "first":first_sym | "last":last_sym
                        | capture | ref | wff | bf.
ref_args               => '(' [ (_ bf:ref_arg) (_ ',' _ ref_arg)* ] _ ')'.

library                => ((_ (wff_rule | bf_rule):rule)*):rules.
wff_rule               => wff:wff_matcher _ "::=" _ wff:wff_body _ '.'.
bf_rule                => bf :bf_matcher  _  ":=" _ bf :bf_body  _ '.'.

builder                => _ builder_head _ builder_body _ '.'.
builder_head           => '(' _ capture (__ capture)* _ ')'.
builder_body           => ("=:"  _ bf) :bf_builder_body
                        | ("=::" _ wff):wff_builder_body.

tau_constant_source    => rec_relations _ main _ [ '.' _ ].

# 
wff                    => ('(' _ wff _ ')')                  :wff_parenthesis
                        | (("sometimes" | "<>")  _ wff)      :wff_sometimes
                        | (("always"    | "[]")  _ wff)      :wff_always
                        | (wff _ '?' _ wff _ ':' _ wff)      :wff_conditional
                        | ("all"     __ q_vars  __ wff)      :wff_all
                        | ("ex"      __ q_vars  __ wff)      :wff_ex
                        | ref                                :wff_ref
                        |                                     constraint
                        | (wff   _ "->"  _ wff)              :wff_imply
                        | (wff   _ "<-"  _ wff)              :wff_rimply
                        | (wff   _ "<->" _ wff)              :wff_equiv
                        | (wff   _ "||"  _ wff)              :wff_or
                        | (wff   _ '^'   _ wff)              :wff_xor
                        | (wff   _ "&&"  _ wff)              :wff_and
                        | ('!'   _ wff)                      :wff_neg
                        | 'T'                                :wff_t
                        | 'F'                                :wff_f.
"""

BITVECTOR_TGF_CONTENT = """\
# To view the license please visit https://github.com/IDNI/tau-lang/blob/main/LICENSE.txt

@use char classes space, alpha, digit.

@enable productions charvar.

start  => _ bitvector _.
bitvector => _uint
           | _int
           | _ulong
           | _long
           | _bits.
sign      => minus | plus.
minus     => '-'.
plus      => ['+'].
_int      => sign _ _unsigned.
_long     => sign _ _unsigned _ 'l'.
_uint     => [plus] _ _unsigned _ 'u'.
_ulong    => [plus] _ _unsigned _ "ul".
_unsigned => digit (_digit)*.
_bits     => _bit (_ _bit)* 'b'.
_bit      => '0':zero | '1':one.
"""

@pytest.fixture
def official_tau_grammar_files(tmp_path):
    """
    Sets up a temporary directory with official Tau grammar files (tau.tgf, bitvector.tgf)
    and common.lark, along with a grammar-files.json configuration.
    """
    temp_grammar_dir = tmp_path / "grammars"
    temp_grammar_dir.mkdir()
    temp_config_file = tmp_path / "grammar-files.json"

    # Write official grammar files
    (temp_grammar_dir / "tau.tgf").write_text(TAU_TGF_CONTENT)
    (temp_grammar_dir / "bitvector.tgf").write_text(BITVECTOR_TGF_CONTENT)

    # Copy common.lark (ensure COMMON_LARK_FILE_PATH is defined globally)
    shutil.copy(COMMON_LARK_FILE_PATH, temp_grammar_dir)

    # Create grammar configuration
    grammar_config_data = [
        {
            "id": "official-tau-grammar",
            "name": "Official Tau Grammar",
            "filename": "tau.tgf",
            "isActive": True,
            # No transformer_class specified, expect raw Lark Tree
        }
    ]
    with open(temp_config_file, 'w') as f:
        json.dump(grammar_config_data, f)

    return temp_grammar_dir, temp_config_file

def test_parse_logic_gates_with_official_tau_grammar(official_tau_grammar_files):
    """
    Tests that GrammarDrivenParser can parse logic_gates.tau content
    using the official tau.tgf grammar.
    """
    temp_grammar_dir, temp_config_file = official_tau_grammar_files

    # Instantiate services and parser
    repo = GrammarRepository(grammar_dir=temp_grammar_dir, config_file=temp_config_file)
    service = TGFGrammarService(repository=repo)
    parser = GrammarDrivenParser(grammar_service=service)

    # Assert parser initialized correctly
    assert parser.initialization_error_reason is None, f"Parser failed to initialize: {parser.initialization_error_reason}"
    assert parser.lark_parser is not None, "Lark parser instance was not created"

    # Read source content and perform parsing (ensure LOGIC_GATES_TAU_PATH is defined globally)
    source_code = LOGIC_GATES_TAU_PATH.read_text()
    result = parser.parse(source_code, grammar_id="official-tau-grammar")

    # Assertions
    assert result.success, f"Parsing failed: {result.error}"
    assert result.ast is not None, "Parsing produced a None AST."

    raw_ast = result.ast
    assert isinstance(raw_ast, Tree), f"Expected a Lark Tree, got {type(raw_ast)}"
    assert raw_ast.data == 'start', f"Expected root of the tree to be 'start', got {raw_ast.data}"
