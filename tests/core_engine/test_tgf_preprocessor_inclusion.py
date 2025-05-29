import pytest
from pathlib import Path
from tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor

# Helper to normalize Lark output for easier comparison
def normalize_lark_output(text: str) -> str:
    """Normalizes Lark grammar output for consistent comparison."""
    # Split into lines, strip whitespace from each line, filter out empty lines, then sort.
    stripped_lines = [line.strip() for line in text.strip().splitlines()]
    non_empty_lines = [line for line in stripped_lines if line]
    sorted_lines = sorted(non_empty_lines)
    return "\n".join(sorted_lines)

class TestTgfPreprocessorInclusion:
    def test_simple_file_inclusion(self, tmp_path: Path):
        """Tests basic @use "filename.tgf" functionality."""
        # Create mock TGF files
        child_tgf_content = """
child_rule: CHILD_TOKEN;
@use char classes CHILD_CHAR_CLASS.
        """
        (tmp_path / "child.tgf").write_text(child_tgf_content, encoding='utf-8')
    
        main_tgf_content = """
@use "child.tgf"
main_rule: MAIN_TOKEN child_rule;"""
        main_tgf_file = tmp_path / "main.tgf"
        main_tgf_file.write_text(main_tgf_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=main_tgf_file)
        actual_lark_output = preprocessor.to_lark()

        expected_lark_output_str = f"""
// TGF Directive: @use "child.tgf"
// >>> Start Include: {tmp_path.resolve() / 'child.tgf'} (from main.tgf)
child_rule: CHILD_TOKEN
// TGF Directive: @use char classes CHILD_CHAR_CLASS.
// <<< End Include: {tmp_path.resolve() / 'child.tgf'}
main_rule: MAIN_TOKEN child_rule""" 
            
        actual_normalized = normalize_lark_output(actual_lark_output)

        expected_lines_from_fstring = expected_lark_output_str.strip().splitlines()
        processed_expected_lines_sorted = sorted([line.strip() for line in expected_lines_from_fstring if line.strip()])
        expected_normalized = normalize_lark_output("\n".join(processed_expected_lines_sorted))

        assert actual_normalized == expected_normalized
        assert "child.tgf" in preprocessor.included_files
        assert "CHILD_CHAR_CLASS" in preprocessor._char_classes_used

    def test_relative_paths_sibling_and_subdir(self, tmp_path: Path):
        """Tests @use with './sibling.tgf' and 'subdir/child.tgf'."""
        # Create directory structure and files
        (tmp_path / "subdir").mkdir()

        sibling_tgf_content = "sibling_rule: SIBLING_TOKEN;"
        (tmp_path / "sibling.tgf").write_text(sibling_tgf_content, encoding='utf-8')

        child_tgf_content = "child_rule: CHILD_TOKEN;"
        (tmp_path / "subdir" / "child.tgf").write_text(child_tgf_content, encoding='utf-8')

        main_tgf_content = """
@use "./sibling.tgf"
@use "subdir/child.tgf"
main_rule: sibling_rule child_rule;
        """
        main_tgf_file = tmp_path / "main.tgf"
        main_tgf_file.write_text(main_tgf_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=main_tgf_file)
        actual_lark_output = preprocessor.to_lark()

        resolved_sibling_path = (tmp_path / "sibling.tgf").resolve()
        resolved_child_path = (tmp_path / "subdir" / "child.tgf").resolve()

        expected_lark_output = f"""
// TGF Directive: @use "./sibling.tgf"
// >>> Start Include: {resolved_sibling_path} (from main.tgf)
sibling_rule: SIBLING_TOKEN
// <<< End Include: {resolved_sibling_path}
// TGF Directive: @use "subdir/child.tgf"
// >>> Start Include: {resolved_child_path} (from main.tgf)
child_rule: CHILD_TOKEN
// <<< End Include: {resolved_child_path}
main_rule: sibling_rule child_rule
        """
        assert normalize_lark_output(actual_lark_output) == normalize_lark_output(expected_lark_output)
        assert "./sibling.tgf" in preprocessor.included_files
        assert "subdir/child.tgf" in preprocessor.included_files

    def test_relative_path_parent_dir(self, tmp_path: Path):
        """Tests @use with '../common.tgf'."""
        # Create directory structure: tmp_path/common_files/common.tgf
        #                            tmp_path/grammar_dir/main.tgf
        common_files_dir = tmp_path / "common_files"
        common_files_dir.mkdir()
        grammar_dir = tmp_path / "grammar_dir"
        grammar_dir.mkdir()

        common_tgf_content = "common_rule: COMMON_TOKEN;"
        (common_files_dir / "common.tgf").write_text(common_tgf_content, encoding='utf-8')

        main_tgf_content = """
@use "../common_files/common.tgf"
main_rule: common_rule MAIN_TOKEN;
        """
        main_tgf_file = grammar_dir / "main.tgf"
        main_tgf_file.write_text(main_tgf_content, encoding='utf-8')

        # The base_dir_for_includes for TgfPreprocessor will be grammar_dir if not specified,
        # as it's the parent of main_tgf_file.
        preprocessor = TGFPreprocessor(initial_input=main_tgf_file)
        actual_lark_output = preprocessor.to_lark()

        resolved_common_path = (common_files_dir / "common.tgf").resolve()

        expected_lark_output = f"""
// TGF Directive: @use "../common_files/common.tgf"
// >>> Start Include: {resolved_common_path} (from main.tgf)
common_rule: COMMON_TOKEN
// <<< End Include: {resolved_common_path}
main_rule: common_rule MAIN_TOKEN
        """
        assert normalize_lark_output(actual_lark_output) == normalize_lark_output(expected_lark_output)
        assert "../common_files/common.tgf" in preprocessor.included_files

    def test_nested_file_inclusion(self, tmp_path: Path):
        """Tests nested @use directives (main -> child -> grandchild)."""
        # Create mock TGF files
        grandchild_tgf_content = "grandchild_rule: GRANDCHILD_TOKEN;"
        (tmp_path / "grandchild.tgf").write_text(grandchild_tgf_content, encoding='utf-8')

        child_tgf_content = """
@use "grandchild.tgf"
child_rule: CHILD_TOKEN grandchild_rule;
        """
        (tmp_path / "child.tgf").write_text(child_tgf_content, encoding='utf-8')

        main_tgf_content = """
@use "child.tgf"
main_rule: MAIN_TOKEN child_rule;
        """
        main_tgf_file = tmp_path / "main.tgf"
        main_tgf_file.write_text(main_tgf_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=main_tgf_file)
        actual_lark_output = preprocessor.to_lark()

        resolved_main_path = main_tgf_file.resolve()
        resolved_child_path = (tmp_path / "child.tgf").resolve()
        resolved_grandchild_path = (tmp_path / "grandchild.tgf").resolve()

        expected_lark_output = f"""
// TGF Directive: @use "child.tgf"
// >>> Start Include: {resolved_child_path} (from {main_tgf_file.name})
// TGF Directive: @use "grandchild.tgf"
// >>> Start Include: {resolved_grandchild_path} (from {resolved_child_path.name})
grandchild_rule: GRANDCHILD_TOKEN
// <<< End Include: {resolved_grandchild_path}
child_rule: CHILD_TOKEN grandchild_rule
// <<< End Include: {resolved_child_path}
main_rule: MAIN_TOKEN child_rule
        """

        assert normalize_lark_output(actual_lark_output) == normalize_lark_output(expected_lark_output)
        assert "child.tgf" in preprocessor.included_files
        assert "grandchild.tgf" in preprocessor.included_files

    def test_missing_included_file_raises_error(self, tmp_path: Path):
        """Tests that FileNotFoundError is raised for a missing @use target file."""
        main_tgf_content = """
@use "non_existent_child.tgf"
main_rule: MAIN_TOKEN;
        """
        main_tgf_file = tmp_path / "main.tgf"
        main_tgf_file.write_text(main_tgf_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=main_tgf_file)

        expected_missing_path = (tmp_path / "non_existent_child.tgf").resolve()
        expected_error_msg = f"Included file not found: {expected_missing_path} (referenced in {main_tgf_file.name})"

        with pytest.raises(FileNotFoundError) as excinfo:
            preprocessor.to_lark()
        
        assert str(excinfo.value) == expected_error_msg
        assert "non_existent_child.tgf" in preprocessor.included_files # Records the attempt

    def test_circular_dependency(self, tmp_path: Path):
        """Tests handling of circular dependencies (a -> b -> a)."""
        # Create mock TGF files
        file_a_content = """
a_rule: A_TOKEN;
@use "b.tgf"
final_a_rule: END_A;
        """
        file_a = tmp_path / "a.tgf"
        file_a.write_text(file_a_content, encoding='utf-8')

        file_b_content = """
b_rule: B_TOKEN;
@use "a.tgf"
final_b_rule: END_B;
        """
        file_b = tmp_path / "b.tgf"
        file_b.write_text(file_b_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=file_a)
        actual_lark_output = preprocessor.to_lark()

        resolved_a_path = file_a.resolve()
        resolved_b_path = file_b.resolve()

        expected_lark_output = f"""
a_rule: A_TOKEN
// TGF Directive: @use "b.tgf"
// >>> Start Include: {resolved_b_path} (from a.tgf)
b_rule: B_TOKEN
// TGF Directive: @use "a.tgf"
// !!! SKIPPING already included file: {resolved_a_path} (referenced in b.tgf)
final_b_rule: END_B
// <<< End Include: {resolved_b_path}
final_a_rule: END_A
        """

        assert normalize_lark_output(actual_lark_output) == normalize_lark_output(expected_lark_output)
        assert "b.tgf" in preprocessor.included_files
        # "a.tgf" will also be in included_files because b.tgf attempts to include it.
        assert "a.tgf" in preprocessor.included_files 

    def test_idempotency_diamond_dependency(self, tmp_path: Path):
        """Tests that a common file included via multiple paths is processed only once (diamond dependency)."""
        # Create mock TGF files
        common_tgf_content = "common_rule: COMMON_TOKEN;"
        common_file = tmp_path / "common.tgf"
        common_file.write_text(common_tgf_content, encoding='utf-8')

        file_a_content = """
@use "common.tgf"
a_rule: A_TOKEN common_rule;
        """
        file_a = tmp_path / "a.tgf"
        file_a.write_text(file_a_content, encoding='utf-8')

        file_b_content = """
@use "common.tgf"
b_rule: B_TOKEN common_rule;
        """
        file_b = tmp_path / "b.tgf"
        file_b.write_text(file_b_content, encoding='utf-8')

        main_tgf_content = """
@use "a.tgf"
@use "b.tgf"
main_rule: a_rule b_rule;
        """
        main_file = tmp_path / "main.tgf"
        main_file.write_text(main_tgf_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=main_file)
        actual_lark_output = preprocessor.to_lark()

        resolved_common_path = common_file.resolve()
        resolved_a_path = file_a.resolve()
        resolved_b_path = file_b.resolve()

        expected_lark_output = f"""
// TGF Directive: @use "a.tgf"
// >>> Start Include: {resolved_a_path} (from main.tgf)
// TGF Directive: @use "common.tgf"
// >>> Start Include: {resolved_common_path} (from a.tgf)
common_rule: COMMON_TOKEN
// <<< End Include: {resolved_common_path}
a_rule: A_TOKEN common_rule
// <<< End Include: {resolved_a_path}
// TGF Directive: @use "b.tgf"
// >>> Start Include: {resolved_b_path} (from main.tgf)
// TGF Directive: @use "common.tgf"
// !!! SKIPPING already included file: {resolved_common_path} (referenced in b.tgf)
b_rule: B_TOKEN common_rule
// <<< End Include: {resolved_b_path}
main_rule: a_rule b_rule
        """

        assert normalize_lark_output(actual_lark_output) == normalize_lark_output(expected_lark_output)
        assert "common.tgf" in preprocessor.included_files
        assert "a.tgf" in preprocessor.included_files
        assert "b.tgf" in preprocessor.included_files

    def test_directives_from_included_file_affect_parent(self, tmp_path: Path):
        """Tests that directives from an included file affect parent/subsequent processing."""
        child_content = """
@trim _ .
@use char classes MY_SPECIAL_CLASS .
child_rule: CHILD _ TOKEN;
        """
        child_file = tmp_path / "child_directives.tgf"
        child_file.write_text(child_content, encoding='utf-8')

        main_content = """
@use "child_directives.tgf"
main_rule: MAIN _ TOKEN child_rule;
// This should use MY_SPECIAL_CLASS implicitly if @use char classes worked
another_rule: ANOTHER MY_SPECIAL_CLASS TOKEN;
        """
        main_file = tmp_path / "main.tgf"
        main_file.write_text(main_content, encoding='utf-8')

        preprocessor = TGFPreprocessor(initial_input=main_file)
        actual_lark_output = preprocessor.to_lark()

        resolved_child_path = child_file.resolve()

        expected_lark_output = f"""
// TGF Directive: @use "child_directives.tgf"
// >>> Start Include: {resolved_child_path} (from main.tgf)
// TGF Directive: @trim _ .
// TGF Directive: @use char classes MY_SPECIAL_CLASS .
child_rule: CHILD TOKEN
// <<< End Include: {resolved_child_path}
main_rule: MAIN TOKEN child_rule
// TGF Comment: // This should use MY_SPECIAL_CLASS implicitly if @use char classes worked
another_rule: ANOTHER MY_SPECIAL_CLASS TOKEN
        """

        assert normalize_lark_output(actual_lark_output) == normalize_lark_output(expected_lark_output)
        assert "_" in preprocessor._whitespace_rules
        assert "MY_SPECIAL_CLASS" in preprocessor._char_classes_used
        assert "child_directives.tgf" in preprocessor.included_files

    # TODO: Add more tests:
    # - @use in a file that itself was @use'd from a string input
