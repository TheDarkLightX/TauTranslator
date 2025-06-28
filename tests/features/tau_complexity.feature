Feature: Tau Language Complexity Translation

  Scenario: Translating a simple "always" statement
    Given the natural language input is:
      """
      always the input is greater than 10
      """
    When the system translates the input to Tau
    Then the resulting Tau expression should be "always (i[t] > 10)"

  Scenario: Translating a statement with implication and streams
    Given the natural language input "if the input stream is greater than the threshold stream then the output stream is 1"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "i[t] > t[t] -> o[t] = 1"

  Scenario: Translating a statement with universal quantification (for all)
    Given the natural language input "for all x, x is positive"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "all x (x > 0)"

  Scenario: Translating a statement combining "always" and "sometimes"
    Given the natural language input "always sometimes the input is less than 0"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "always (sometimes (i[t] < 0))"

  Scenario: Translating a nested temporal statement
    Given the natural language input "always (the input is greater than 5 and sometimes the input is less than 10)"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "always (i[t] > 5 and sometimes (i[t] < 10))"

  Scenario: Translating a bitwise negation formula
    Given the natural language input "the output is the bitwise negation of the input"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "o[t] = i[t]'"

  Scenario: Translating a value interval check
    Given the natural language input "the value is between the lower bound and the upper bound"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "lower_bound <= value <= upper_bound"

  Scenario: Translating a statement with existential quantification (exists)
    Given the natural language input "there exists an x such that x is greater than the input"
    When the system translates the input to Tau
    Then the resulting Tau expression should be "ex x (x > i[t])"

  Scenario: Translating an ambiguous statement with boolean logic
    Given the natural language input "A user is valid if their account is active and they have either a verified email or a phone number."
    When the system translates the input to Tau
    Then the resulting Tau expression should be "(user.account.active and (user.email.verified or user.phone.verified)) -> user.valid"

  Scenario: Translating a Tau expression back to natural language
    Given the Tau expression "always (price > 100 -> demand = 'low')"
    When the system translates the Tau to natural language
    Then the resulting natural language text should be "If the price is always greater than 100, then the demand is always 'low'."
