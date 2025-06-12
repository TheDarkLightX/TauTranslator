Feature: Educational TCE (Controlled English) Autocomplete
  As a user learning to write specifications
  I want controlled English patterns that map to TAU
  So that I can write formal specifications in natural language

  Background:
    Given I have the TCE autocomplete engine initialized
    And I am editing in TCE language mode

  Scenario: Basic controlled patterns
    When I type "for all"
    Then I should see pattern "for all $objects such that $condition"
    And the pattern should show TAU equivalent "forall $objects : $condition"
    And it should have hint "Universal quantification in controlled English"

  Scenario: Temporal controlled patterns
    When I type "it is always"
    Then I should see pattern "it is always the case that $property"
    And the pattern should show TAU equivalent "always ($property)"
    And it should have hint "Temporal invariant property"

  Scenario: Existence patterns
    When I type "there exists"
    Then I should see pattern "there exists $object such that $property"
    And the pattern should show TAU equivalent "exists $object : $property"
    And it should have example "there exists x such that x > 0"

  Scenario: Conditional patterns
    When I type "if"
    Then I should see pattern "if $condition then $consequence"
    And the pattern should show TAU equivalent "$condition -> $consequence"
    And it should have hint "Logical implication"

  Scenario: Stream patterns in English
    When I type "output at"
    Then I should see pattern "output at time t equals $expression"
    And the pattern should show TAU equivalent "output[t] = $expression"
    And it should have hint "Stream value at current time"

  Scenario: Finding solutions in English
    When I type "find"
    Then I should see pattern "find a value for $var such that $condition"
    And the pattern should show TAU equivalent "solve $var = $condition"
    And it should have example "find a value for x such that x squared equals 4"

  Scenario: TCE to TAU learning mode
    Given I have learning mode enabled
    When I complete a TCE pattern
    Then I should see the TAU translation highlighted
    And I should see an explanation of the mapping
    And related TAU constructs should be suggested