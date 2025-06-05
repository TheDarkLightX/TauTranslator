Feature: Translation API Behavior
  As an API user
  I want to interact with the translation service
  So that I can integrate Tau translation into my applications

  Background:
    Given the API server is running
    And I have a valid API key
    And the default headers are set

  @api @authentication
  Scenario: Successful authentication with valid API key
    When I send a GET request to "/api/health"
    Then the response status should be 200
    And the response should contain "healthy"

  @api @authentication
  Scenario: Failed authentication with invalid API key
    Given I have an invalid API key
    When I send a GET request to "/api/health"
    Then the response status should be 401
    And the response should contain "unauthorized"

  @api @translation
  Scenario: Translate TCE to TAU via API
    Given I have the request body:
      """
      {
        "input": "define predicate is_valid(x) as x > 0.",
        "from": "TCE",
        "to": "TAU"
      }
      """
    When I send a POST request to "/api/translate"
    Then the response status should be 200
    And the response should contain "is_valid(x) := x > 0"
    And the response should have field "success" equal to true

  @api @translation
  Scenario: Translate TAU to TCE via API
    Given I have the request body:
      """
      {
        "input": "is_valid(x) := x > 0",
        "from": "TAU",
        "to": "TCE"
      }
      """
    When I send a POST request to "/api/translate"
    Then the response status should be 200
    And the response should contain "define predicate is_valid(x) as x > 0."
    And the response should have field "success" equal to true

  @api @validation
  Scenario: Validate correct TCE syntax
    Given I have the request body:
      """
      {
        "input": "x = 5.",
        "language": "TCE"
      }
      """
    When I send a POST request to "/api/validate"
    Then the response status should be 200
    And the response should have field "valid" equal to true

  @api @validation
  Scenario: Detect invalid TCE syntax
    Given I have the request body:
      """
      {
        "input": "x = 5",
        "language": "TCE"
      }
      """
    When I send a POST request to "/api/validate"
    Then the response status should be 200
    And the response should have field "valid" equal to false
    And the response should have field "errors" containing "period"

  @api @batch
  Scenario: Batch translation of multiple inputs
    Given I have the request body:
      """
      {
        "inputs": [
          {"input": "x = 5.", "from": "TCE", "to": "TAU"},
          {"input": "y > 10.", "from": "TCE", "to": "TAU"},
          {"input": "z and w.", "from": "TCE", "to": "TAU"}
        ]
      }
      """
    When I send a POST request to "/api/translate/batch"
    Then the response status should be 200
    And the response should have field "results" with length 3
    And the response results[0] should contain "x = 5"
    And the response results[1] should contain "y > 10"
    And the response results[2] should contain "z & w"

  @api @error_handling
  Scenario: Handle malformed request gracefully
    Given I have the request body:
      """
      {
        "invalid": "request"
      }
      """
    When I send a POST request to "/api/translate"
    Then the response status should be 400
    And the response should contain "missing required field"

  @api @rate_limiting
  Scenario: Rate limiting prevents excessive requests
    Given I make 100 requests in 1 second to "/api/translate"
    Then at least one response status should be 429
    And the rate limit response should contain "too many requests"

  @api @websocket
  Scenario: Real-time translation via WebSocket
    Given I connect to WebSocket endpoint "/ws/translate"
    When I send WebSocket message:
      """
      {
        "type": "translate",
        "input": "x = 5.",
        "from": "TCE",
        "to": "TAU"
      }
      """
    Then I should receive WebSocket message containing "x = 5"
    And the WebSocket message should have field "type" equal to "result"