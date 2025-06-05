import unittest
from src.tau_translator_omega.core_engine.semantic_analyzer import SymbolTable, Symbol
from src.tau_translator_omega.core_engine.cnl_parser.ast_nodes import VariableNode # For ast_node in Symbol

class TestAnalyzerSymbolTableDirect(unittest.TestCase):

    def test_symbol_table_define_and_lookup_global(self):
        st = SymbolTable()
        sym = Symbol('x', 'variable', st.current_scope_level)
        st.declare_symbol(sym)  # declare_symbol doesn't return bool, just declares or raises
        self.assertEqual(st.lookup_symbol('x'), sym)

    def test_symbol_table_redefine_global_fails(self):
        st = SymbolTable()
        sym1 = Symbol('x', 'variable', st.current_scope_level)
        sym2 = Symbol('x', 'variable', st.current_scope_level) # Same name, same scope
        st.declare_symbol(sym1)
        with self.assertRaises(Exception):  # Should raise SemanticError on redefinition
            st.declare_symbol(sym2)

    def test_symbol_table_scoped_lookup(self):
        st = SymbolTable()
        # Ensure VariableNode has line and column if your Symbol or error reporting expects it.
        # Simplified here as these tests focus on SymbolTable logic directly.
        global_sym = Symbol('x', 'variable', st.current_scope_level, ast_node=VariableNode(name='x', line=1, column=0))
        st.declare_symbol(global_sym)
        
        st.enter_scope()
        local_sym = Symbol('x', 'variable', st.current_scope_level, ast_node=VariableNode(name='x', line=2, column=0))
        st.declare_symbol(local_sym)
        self.assertEqual(st.lookup_symbol('x'), local_sym) # Should find local 'x'
        
        st.exit_scope()
        self.assertEqual(st.lookup_symbol('x'), global_sym) # Should find global 'x' again

if __name__ == '__main__':
    unittest.main()
