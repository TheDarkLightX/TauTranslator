import pytest
from pathlib import Path
# Adjust these imports based on your actual project structure
from tau_translator_omega.core_engine.parser import GrammarDrivenParser
from tau_translator_omega.core_engine.plugin_manager import Plugin
from tau_translator_omega.core_engine.plugin import PluginEntryPoint # Added import

# Path to the fixture grammar and the source for common.lark
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TEST_FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
MINIMAL_GRAMMAR_FILE_PATH = TEST_FIXTURES_DIR / "grammars" / "minimal_logic_gates.lark"
# Path to the directory containing the original common.lark
COMMON_LARK_SRC_DIR = PROJECT_ROOT / "src" / "tau_translator_omega" / "core_engine" / "cnl_parser" / "grammars"

# Content of logic_gates.tau
LOGIC_GATES_TAU_CONTENT = """\
# Title: Logic Gates
# Description: Implementation of basic logic gates (AND, OR, NOT, XOR) with two inputs.

# Define input files
sbf i1 = ifile(\"input1.in\")
sbf i2 = ifile(\"input2.in\")

# Define output files
sbf o1 = ofile(\"and.out\")
sbf o2 = ofile(\"or.out\")
sbf o3 = ofile(\"not.out\")
sbf o4 = ofile(\"xor.out\")

# AND gate
r o1[t] = i1[t] & i2[t]

# OR gate
r o2[t] = i1[t] | i2[t]

# NOT gate (of first input)
r o3[t] = i1[t]'

# XOR gate
r o4[t] = (i1[t] & i2[t]') | (i1[t]' & i2[t])
"""

@pytest.fixture
def logic_gates_grammar_plugin():
    """Provides a mock Plugin object for the logic_gates grammar."""
    
    # Create a PluginEntryPoint instance suitable for a grammar definition plugin
    ep = PluginEntryPoint(type="grammar_definition")

    # Define the grammar-specific configuration details
    # GrammarDrivenParser will likely look for these in plugin_specific_config
    grammar_details = {
        "formalism": "Lark",
        "grammar_file_path": str(MINIMAL_GRAMMAR_FILE_PATH),
        "import_paths": [str(COMMON_LARK_SRC_DIR)]
    }

    plugin = Plugin(
        # Required fields for Plugin:
        id="minimal-logic-gates-grammar",
        name="Minimal Logic Gates Grammar",
        version="0.1.0",
        description="A minimal Lark grammar for parsing logic_gates.tau example.",
        entry_point=ep, # Corrected: pass PluginEntryPoint instance
        manifest_path=MINIMAL_GRAMMAR_FILE_PATH.parent / "dummy_manifest.json", # Dummy path
        plugin_dir=MINIMAL_GRAMMAR_FILE_PATH.parent.parent, # Dummy path to tests/fixtures/
        manifest_data={ # Minimal manifest_data for a mock
            "id": "minimal-logic-gates-grammar",
            "name": "Minimal Logic Gates Grammar",
            "version": "0.1.0",
            "plugin_type": "grammar_definition",
            "entry_point": {"type": "grammar_definition"} # Data for PluginEntryPoint
        },

        # Optional fields we are setting:
        plugin_type="grammar_definition",
        author="TestFixture",
        license="MIT",
        ilr_versions_supported=[">=0.1.0"], # Corrected from ilr_version_constraint
        tags=["grammar", "lark", "tau", "test"],
        
        # Pass grammar details here:
        plugin_specific_config=grammar_details,

        # Other fields like dependencies, instance will use their defaults
    )
    
    # Manually set the grammar_config attribute as GrammarDrivenParser expects it
    plugin.grammar_config = grammar_details 
    
    return plugin

def test_parse_logic_gates_tau(logic_gates_grammar_plugin):
    """
    Tests that the GrammarDrivenParser can parse the logic_gates.tau content
    using the minimal_logic_gates.lark grammar.
    """
    assert MINIMAL_GRAMMAR_FILE_PATH.exists(), f"Grammar file not found at {MINIMAL_GRAMMAR_FILE_PATH}"
    assert COMMON_LARK_SRC_DIR.joinpath("common.lark").exists(), \
        f"common.lark not found in source directory: {COMMON_LARK_SRC_DIR}"

    parser = GrammarDrivenParser(grammar_plugin=logic_gates_grammar_plugin)
    
    try:
        cst = parser.parse(LOGIC_GATES_TAU_CONTENT)
        assert cst is not None, "Parsing returned None, expected a CST."
        print("\\nParsed CST for logic_gates.tau:")
        print(cst.pretty()) 
    except Exception as e:
        pytest.fail(
            f"Parsing logic_gates.tau failed: {e}\\n"
            f"Grammar: {MINIMAL_GRAMMAR_FILE_PATH}\\n"
            f"Import paths in grammar_config: {logic_gates_grammar_plugin.grammar_config.get('import_paths')}"
        )