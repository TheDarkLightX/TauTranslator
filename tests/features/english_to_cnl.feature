# Copyright (c) DarkLightX / Dana Edwards

Feature: Grammar-Driven Text Transformation
  As a developer,
  I want to transform structured text using a custom grammar and transformer
  So that I can process formal languages reliably.

  Scenario: Transform a simple math expression using a custom grammar
    Given a custom grammar file "simple_math.ebnf"
    And the grammar is loaded successfully
    When I provide the source text "5 + 5"
    Then the transformed output should be "5 + 5"
