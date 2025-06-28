Feature: Typedef Handling in TauTranslator

  Scenario: Define a custom type from a CNL statement
    Given a fresh Tau translator instance
    When the user provides the TCE statement: "Let a 'user_id' be a number."
    Then the translator successfully processes the statement
    And the resulting Tau output is "typedef user_id: num;"

  Scenario: Define a custom type with a descriptive alphanumeric string type
    Given a fresh Tau translator instance
    When the user provides the TCE statement: "Let a 'product_code' be a alphanumeric_string."
    Then the translator successfully processes the statement
    And the resulting Tau output is "typedef product_code: Alphanumeric;"

  Scenario: Define a custom type that references another user-defined type
    Given a fresh Tau translator instance
    When the user provides the TCE statement: "Let a 'CustomIdentifier' be a string."
    Then the translator successfully processes the statement
    And the resulting Tau output is "typedef CustomIdentifier: str;"
    When the user provides the TCE statement: "Let a 'PrimaryID' be a CustomIdentifier."
    Then the translator successfully processes the statement
    And the resulting Tau output is "typedef PrimaryID: CustomIdentifier;"