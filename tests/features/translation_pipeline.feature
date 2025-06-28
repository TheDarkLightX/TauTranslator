Feature: TCE to Tau Translation Pipeline Validation

  As a developer, I want to ensure the translation pipeline accurately converts
  Controlled English (TCE) into canonical Tau code, based on official demos.

  Scenario: Translating a universal and existential quantifier statement
    Given the following multi-line English source text:
      """
      for every X there is some Y such that X is 0 and Y is 0.
      """
    When I translate the text from TCE to Tau
    Then the output should be the following canonical Tau code:
      """
      all X ex Y (X = 0 && Y = 0)
      """
