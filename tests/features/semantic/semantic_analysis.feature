Feature: Semantic Analysis and Type Checking
  As a system component
  I want to perform semantic analysis on parsed AST
  So that type errors and semantic issues are caught early

  Background:
    Given the semantic analyzer is initialized
    And the type system is configured
    And the symbol table is empty

  @semantic @types
  Scenario: Type check variable declaration
    Given I have parsed AST for "integer x equals 5."
    When I perform semantic analysis
    Then the symbol "x" should be registered with type "integer"
    And the value "5" should be validated as type "integer"
    And no type errors should be reported

  @semantic @types
  Scenario: Detect type mismatch in assignment
    Given I have parsed AST for "boolean flag equals 42."
    When I perform semantic analysis
    Then a type error should be reported
    And the error should mention "boolean" and "integer" mismatch

  @semantic @symbols
  Scenario: Detect undefined variable usage
    Given I have parsed AST for "y equals x plus 1."
    And variable "x" is not defined
    When I perform semantic analysis
    Then an undefined variable error should be reported for "x"

  @semantic @scope
  Scenario: Handle variable scoping correctly
    Given I have parsed AST for:
      """
      integer x equals 10.
      if true then
        integer x equals 20.
        y equals x.
      end.
      z equals x.
      """
    When I perform semantic analysis
    Then "y" should reference the inner "x" with value 20
    And "z" should reference the outer "x" with value 10

  @semantic @functions
  Scenario: Validate function call arguments
    Given the function "max" is defined with signature "(integer, integer) -> integer"
    And I have parsed AST for "result equals max(5, true)."
    When I perform semantic analysis
    Then a type error should be reported
    And the error should mention argument 2 type mismatch

  @semantic @predicates
  Scenario: Validate predicate arity
    Given the predicate "between" has arity 3
    And I have parsed AST for "between(x, 1)."
    When I perform semantic analysis
    Then an arity error should be reported
    And the error should mention "expected 3 arguments, got 2"

  @semantic @quantifiers
  Scenario: Check quantifier variable binding
    Given I have parsed AST for "Always x such that x > 0 implies exists y such that y equals x squared."
    When I perform semantic analysis
    Then "x" should be bound by universal quantifier
    And "y" should be bound by existential quantifier
    And both variables should have proper scoping

  @semantic @performance
  Scenario: Analyze large AST efficiently
    Given I have parsed AST with 1000 nodes
    When I perform semantic analysis
    Then analysis should complete within 50 milliseconds
    And memory usage should be under 5 MB

  @semantic @warnings
  Scenario: Generate warnings for suspicious patterns
    Given I have parsed AST for "Always x implies x."
    When I perform semantic analysis
    Then a warning should be generated
    And the warning should mention "tautology"

  @semantic @inference
  Scenario: Infer types when not explicitly declared
    Given type inference is enabled
    And I have parsed AST for "x equals 42."
    When I perform semantic analysis
    Then "x" should be inferred as type "integer"
    And no type errors should be reported