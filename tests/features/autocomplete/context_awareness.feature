Feature: Context-Aware Autocomplete
  As a specification writer
  I want suggestions based on my current context
  So that I get relevant help for what I'm trying to write

  Background:
    Given I have the context-aware autocomplete system initialized

  Scenario: Function definition context
    Given I have typed "DEFINE "
    When I continue typing
    Then I should see template suggestions for function definitions
    And suggestions should include "$name($params) := $body"
    And suggestions should be categorized as "definition"

  Scenario: Inside quantifier context
    Given I have typed "forall x : "
    When I continue typing
    Then I should see suggestions for predicates and conditions
    And suggestions should include comparison operators
    And suggestions should include logical operators

  Scenario: After temporal operator
    Given I have typed "always ("
    When I continue typing
    Then I should see suggestions for temporal properties
    And suggestions should include stream references with [t]
    And suggestions should include state transitions

  Scenario: Boolean expression context
    Given I am inside a boolean expression
    When I type "&"
    Then I should see suggestion "&&" with hint "Logical AND"
    And I should not see arithmetic operators

  Scenario: Arithmetic expression context
    Given I am inside an arithmetic expression
    When I type "+"
    Then I should see arithmetic operation patterns
    And I should not see logical operators

  Scenario: Nested context handling
    Given I have typed "always (forall x : "
    When I continue typing
    Then suggestions should reflect both temporal and quantifier context
    And hints should explain the combined construct

  Scenario: Error prevention suggestions
    Given I have an unclosed parenthesis "always (x > 0"
    When I type at the end
    Then I should see suggestion to close parenthesis
    And the suggestion should maintain proper nesting