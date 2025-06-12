Feature: Educational TAU Autocomplete
  As a user learning TAU language
  I want context-aware suggestions with educational hints
  So that I can write formal specifications correctly

  Background:
    Given I have the TAU autocomplete engine initialized
    And I am editing in TAU language mode

  Scenario: Basic keyword suggestions with hints
    When I type "alw"
    Then I should see suggestion "always" with category "temporal"
    And the suggestion should have hint "Temporal operator: specifies an invariant property that holds at all times"
    And the suggestion should have example "always (x > 0)"

  Scenario: Quantifier suggestions with templates
    When I type "for"
    Then I should see suggestion "forall" with category "quantifier"
    And the suggestion should have template "forall $var : $condition"
    And the suggestion should have hint "Universal quantification: states a property holds for all values"
    And the suggestion should have example "forall x : x > 0 -> f(x) > 0"

  Scenario: Context-aware suggestions after solve
    Given I have typed "solve "
    When I continue typing
    Then I should see suggestions for equation patterns
    And suggestions should include "{$var}:$type" with hint "Type annotation for solver"
    And suggestions should include "$var = $expr" with hint "Simple equation"
    And suggestions should include "$eq1 && $eq2" with hint "System of equations"

  Scenario: Temporal index suggestions
    Given I have typed "x["
    When I continue typing
    Then I should see suggestion "t" with hint "Current time"
    And I should see suggestion "t-1" with hint "Previous time step"
    And I should see suggestion "t+1" with hint "Next time step"

  Scenario: Stream rule suggestions
    When I type "r "
    Then I should see template "r $output[t] = $input[t]"
    And the suggestion should have hint "Stream processing rule"
    And the suggestion should have example "r output[t] = input1[t] & input2[t]"

  Scenario: Progressive learning - beginner mode
    Given my learning level is set to "beginner"
    When I type "="
    Then I should only see basic comparison operators
    And each suggestion should have detailed explanations
    And examples should be simple

  Scenario: Progressive learning - advanced mode
    Given my learning level is set to "advanced"
    When I type "for"
    Then I should see advanced quantifier patterns
    And suggestions should include nested quantifiers
    And examples should show complex use cases