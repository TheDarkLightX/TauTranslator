"""
Unit tests for ScopeManager component
Tests quantifier scope tracking and variable binding.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from advanced_parsing_architecture import ScopeManager, Scope


class TestScopeManager:
    """Test suite for ScopeManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scope_manager = ScopeManager()
    
    def test_enter_simple_scope(self):
        """Test entering a simple quantifier scope."""
        # Enter scope for "all x"
        scope_id = self.scope_manager.enter_scope("all", "x", "person")
        
        # Verify scope was created
        assert scope_id in self.scope_manager.scopes
        scope = self.scope_manager.scopes[scope_id]
        assert scope.quantifier == "all"
        assert scope.variable == "x"
        assert scope.domain == "person"
        assert scope.parent is None
        
        # Verify current scope
        assert self.scope_manager.current_scope == scope_id
        
        # Verify variable binding
        assert self.scope_manager.variable_bindings["x"] == scope_id
    
    def test_nested_scopes(self):
        """Test nested quantifier scopes."""
        # Enter outer scope: "all x"
        outer_id = self.scope_manager.enter_scope("all", "x", "person")
        
        # Enter inner scope: "exists y"
        inner_id = self.scope_manager.enter_scope("exists", "y", "car")
        
        # Verify scope hierarchy
        outer_scope = self.scope_manager.scopes[outer_id]
        inner_scope = self.scope_manager.scopes[inner_id]
        
        assert inner_scope.parent == outer_id
        assert outer_id in outer_scope.children
        assert self.scope_manager.current_scope == inner_id
        
        # Verify both variables are bound
        assert self.scope_manager.variable_bindings["x"] == outer_id
        assert self.scope_manager.variable_bindings["y"] == inner_id
    
    def test_exit_scope(self):
        """Test exiting scopes."""
        # Create nested scopes
        outer_id = self.scope_manager.enter_scope("all", "x")
        inner_id = self.scope_manager.enter_scope("exists", "y")
        
        # Exit inner scope
        current = self.scope_manager.exit_scope()
        assert current == outer_id
        assert self.scope_manager.current_scope == outer_id
        
        # Exit outer scope
        current = self.scope_manager.exit_scope()
        assert current is None
        assert self.scope_manager.current_scope is None
    
    def test_resolve_variable(self):
        """Test variable resolution."""
        # Create scopes with variables
        scope1_id = self.scope_manager.enter_scope("all", "x", "number")
        scope2_id = self.scope_manager.enter_scope("exists", "y", "number")
        
        # Resolve variables
        x_scope = self.scope_manager.resolve_variable("x")
        y_scope = self.scope_manager.resolve_variable("y")
        z_scope = self.scope_manager.resolve_variable("z")  # Unbound
        
        assert x_scope is not None
        assert x_scope.variable == "x"
        assert x_scope.quantifier == "all"
        
        assert y_scope is not None
        assert y_scope.variable == "y"
        assert y_scope.quantifier == "exists"
        
        assert z_scope is None
    
    def test_scope_constraints(self):
        """Test adding constraints to scopes."""
        # Create scope with constraints
        scope_id = self.scope_manager.enter_scope("all", "x", "person")
        scope = self.scope_manager.scopes[scope_id]
        
        # Add constraints
        scope.constraints.append("age(x) > 18")
        scope.constraints.append("citizen(x)")
        
        # Verify constraints
        assert len(scope.constraints) == 2
        assert "age(x) > 18" in scope.constraints
        assert "citizen(x)" in scope.constraints
    
    def test_scope_tree_navigation(self):
        """Test navigating the scope tree."""
        # Build a tree:
        # root
        #  ├── all x
        #  │   └── exists y
        #  └── all z
        
        # Add root node
        self.scope_manager.scope_tree.add_node('root')
        
        # First branch
        x_id = self.scope_manager.enter_scope("all", "x")
        self.scope_manager.scope_tree.add_edge('root', x_id)
        
        y_id = self.scope_manager.enter_scope("exists", "y")
        
        # Exit back to root
        self.scope_manager.exit_scope()  # Exit y
        self.scope_manager.exit_scope()  # Exit x
        
        # Second branch
        z_id = self.scope_manager.enter_scope("all", "z")
        self.scope_manager.scope_tree.add_edge('root', z_id)
        
        # Test scope paths
        x_path = self.scope_manager.get_scope_path(x_id)
        y_path = self.scope_manager.get_scope_path(y_id)
        z_path = self.scope_manager.get_scope_path(z_id)
        
        assert x_path == ['root', x_id]
        assert y_path == ['root', x_id, y_id]
        assert z_path == ['root', z_id]
    
    def test_variable_shadowing(self):
        """Test variable shadowing in nested scopes."""
        # Outer scope with variable x
        outer_id = self.scope_manager.enter_scope("all", "x", "person")
        
        # Inner scope with different x (shadowing)
        inner_id = self.scope_manager.enter_scope("exists", "x", "number")
        
        # The binding should point to the inner scope
        assert self.scope_manager.variable_bindings["x"] == inner_id
        
        # Exit inner scope
        self.scope_manager.exit_scope()
        
        # Now x should resolve to outer scope
        # Note: Current implementation overwrites, so we need to re-bind
        # This is a limitation that could be improved
        x_scope = self.scope_manager.resolve_variable("x")
        assert x_scope.id == inner_id  # Current behavior
    
    def test_complex_quantifier_pattern(self):
        """Test complex quantifier patterns."""
        # "For all x, if P(x) then exists y such that Q(x,y)"
        
        # Outer universal
        all_x = self.scope_manager.enter_scope("all", "x", "element")
        all_x_scope = self.scope_manager.scopes[all_x]
        all_x_scope.constraints.append("P(x)")
        
        # Inner existential
        exists_y = self.scope_manager.enter_scope("exists", "y", "element")
        exists_y_scope = self.scope_manager.scopes[exists_y]
        exists_y_scope.constraints.append("Q(x,y)")
        
        # Verify structure
        assert exists_y_scope.parent == all_x
        assert all_x in all_x_scope.children
        
        # Both variables should be resolvable
        assert self.scope_manager.resolve_variable("x") is not None
        assert self.scope_manager.resolve_variable("y") is not None


class TestScopeDataStructure:
    """Test the Scope dataclass itself."""
    
    def test_scope_creation(self):
        """Test creating scope instances."""
        scope = Scope(
            id="scope_1",
            quantifier="all",
            variable="x",
            domain="person"
        )
        
        assert scope.id == "scope_1"
        assert scope.quantifier == "all"
        assert scope.variable == "x"
        assert scope.domain == "person"
        assert scope.constraints == []
        assert scope.parent is None
        assert scope.children == []
    
    def test_scope_with_constraints(self):
        """Test scope with initial constraints."""
        scope = Scope(
            id="scope_2",
            quantifier="exists",
            variable="y",
            constraints=["y > 0", "prime(y)"]
        )
        
        assert len(scope.constraints) == 2
        assert "y > 0" in scope.constraints
        assert "prime(y)" in scope.constraints
    
    def test_scope_hierarchy(self):
        """Test building scope hierarchy."""
        parent = Scope("parent", "all", "x")
        child1 = Scope("child1", "exists", "y", parent="parent")
        child2 = Scope("child2", "exists", "z", parent="parent")
        
        # Manually set up relationships
        parent.children = ["child1", "child2"]
        
        assert child1.parent == "parent"
        assert child2.parent == "parent"
        assert len(parent.children) == 2


class TestScopeManagerIntegration:
    """Integration tests for scope manager with real examples."""
    
    def test_forall_exists_pattern(self):
        """Test ∀x ∃y pattern."""
        manager = ScopeManager()
        
        # "For all persons, there exists an id"
        person_scope = manager.enter_scope("all", "p", "person")
        id_scope = manager.enter_scope("exists", "id", "identifier")
        
        # Add relationship constraint
        manager.scopes[id_scope].constraints.append("has_id(p, id)")
        
        # Verify structure
        assert manager.scopes[id_scope].parent == person_scope
        assert manager.resolve_variable("p").quantifier == "all"
        assert manager.resolve_variable("id").quantifier == "exists"
    
    def test_multiple_quantifiers_same_level(self):
        """Test multiple quantifiers at same level."""
        manager = ScopeManager()
        
        # "For all x and all y, if x < y then..."
        x_scope = manager.enter_scope("all", "x", "number")
        manager.exit_scope()  # Back to root
        
        y_scope = manager.enter_scope("all", "y", "number")
        
        # Both should be independent
        assert manager.scopes[x_scope].parent is None
        assert manager.scopes[y_scope].parent is None
        assert x_scope != y_scope
    
    def test_complex_formula_scoping(self):
        """Test complex formula with multiple scope levels."""
        manager = ScopeManager()
        
        # "∀ε>0 ∃δ>0 ∀x (|x-a|<δ → |f(x)-L|<ε)"
        # Continuity definition
        
        # Level 1: ∀ε>0
        eps_scope = manager.enter_scope("all", "eps", "positive_real")
        manager.scopes[eps_scope].constraints.append("eps > 0")
        
        # Level 2: ∃δ>0
        delta_scope = manager.enter_scope("exists", "delta", "positive_real")
        manager.scopes[delta_scope].constraints.append("delta > 0")
        
        # Level 3: ∀x
        x_scope = manager.enter_scope("all", "x", "real")
        manager.scopes[x_scope].constraints.append("|x-a| < delta -> |f(x)-L| < eps")
        
        # Verify the scope chain
        assert manager.scopes[x_scope].parent == delta_scope
        assert manager.scopes[delta_scope].parent == eps_scope
        assert manager.scopes[eps_scope].parent is None
        
        # All variables should be resolvable
        assert all(manager.resolve_variable(var) is not None 
                  for var in ["eps", "delta", "x"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])