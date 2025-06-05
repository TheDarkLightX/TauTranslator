"""
BDD Step Definitions for API Features
====================================

Implements the step definitions for API-related BDD scenarios.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import json
import requests
import websocket
import time
from collections import defaultdict

# Load API feature scenarios
scenarios('../features/api/api_behavior.feature')


# Fixtures
@pytest.fixture
def api_context():
    """Context object to store API interaction state."""
    return {
        'base_url': 'http://localhost:8000',
        'headers': {},
        'api_key': None,
        'request_body': None,
        'response': None,
        'responses': [],
        'websocket': None,
        'ws_messages': []
    }


# Background steps
@given('the API server is running')
def ensure_api_server(api_context):
    """Ensure API server is accessible."""
    try:
        response = requests.get(f"{api_context['base_url']}/health", timeout=2)
        assert response.status_code in [200, 401], "API server not responding properly"
    except requests.exceptions.RequestException:
        pytest.skip("API server not running")


@given('I have a valid API key')
def set_valid_api_key(api_context):
    """Set valid API key for authentication."""
    api_context['api_key'] = 'valid-test-api-key-12345'
    api_context['headers']['Authorization'] = f"Bearer {api_context['api_key']}"


@given('I have an invalid API key')
def set_invalid_api_key(api_context):
    """Set invalid API key for authentication testing."""
    api_context['api_key'] = 'invalid-api-key'
    api_context['headers']['Authorization'] = f"Bearer {api_context['api_key']}"


@given('the default headers are set')
def set_default_headers(api_context):
    """Set default headers for API requests."""
    api_context['headers'].update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })


# Request setup steps
@given(parsers.parse('I have the request body:\n{body}'))
def set_request_body(api_context, body):
    """Set request body from multiline string."""
    api_context['request_body'] = json.loads(body)


# Request execution steps
@when(parsers.parse('I send a {method} request to "{endpoint}"'))
def send_request(api_context, method, endpoint):
    """Send HTTP request to API endpoint."""
    url = f"{api_context['base_url']}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(
                url, 
                headers=api_context['headers'],
                timeout=5
            )
        elif method.upper() == 'POST':
            response = requests.post(
                url,
                headers=api_context['headers'],
                json=api_context['request_body'],
                timeout=5
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        api_context['response'] = response
        api_context['responses'].append(response)
        
    except requests.exceptions.RequestException as e:
        # Store error response for verification
        api_context['response'] = type('MockResponse', (), {
            'status_code': 0,
            'text': str(e),
            'json': lambda: {'error': str(e)}
        })


@given(parsers.parse('I make {count:d} requests in {seconds:d} second to "{endpoint}"'))
def make_rapid_requests(api_context, count, seconds, endpoint):
    """Make multiple rapid requests for rate limiting tests."""
    url = f"{api_context['base_url']}{endpoint}"
    api_context['responses'] = []
    
    start_time = time.time()
    for _ in range(count):
        if time.time() - start_time > seconds:
            break
            
        try:
            response = requests.post(
                url,
                headers=api_context['headers'],
                json={'input': 'x = 5.', 'from': 'TCE', 'to': 'TAU'},
                timeout=1
            )
            api_context['responses'].append(response)
        except:
            pass  # Ignore errors in rate limit testing
            
    time.sleep(0.1)  # Small delay to ensure rate limit kicks in


# WebSocket steps
@given(parsers.parse('I connect to WebSocket endpoint "{endpoint}"'))
def connect_websocket(api_context, endpoint):
    """Connect to WebSocket endpoint."""
    ws_url = api_context['base_url'].replace('http://', 'ws://') + endpoint
    
    try:
        api_context['websocket'] = websocket.create_connection(
            ws_url,
            header={"Authorization": api_context['headers'].get('Authorization', '')}
        )
    except Exception as e:
        pytest.skip(f"WebSocket connection failed: {e}")


@when(parsers.parse('I send WebSocket message:\n{message}'))
def send_websocket_message(api_context, message):
    """Send message through WebSocket."""
    if not api_context['websocket']:
        pytest.fail("No WebSocket connection")
        
    api_context['websocket'].send(message)
    
    # Wait for response
    try:
        response = api_context['websocket'].recv()
        api_context['ws_messages'].append(json.loads(response))
    except:
        api_context['ws_messages'].append({})


# Response verification steps
@then(parsers.parse('the response status should be {status_code:d}'))
def verify_response_status(api_context, status_code):
    """Verify HTTP response status code."""
    assert api_context['response'] is not None, "No response received"
    assert api_context['response'].status_code == status_code, \
        f"Expected status {status_code}, got {api_context['response'].status_code}"


@then(parsers.parse('the response should contain "{text}"'))
def verify_response_contains(api_context, text):
    """Verify response contains expected text."""
    assert api_context['response'] is not None, "No response received"
    response_text = api_context['response'].text
    assert text.lower() in response_text.lower(), \
        f"Response should contain '{text}', got: {response_text}"


@then(parsers.parse('the response should have field "{field}" equal to {value}'))
def verify_response_field_bool(api_context, field, value):
    """Verify response JSON field has expected boolean value."""
    assert api_context['response'] is not None, "No response received"
    response_json = api_context['response'].json()
    
    # Convert string to appropriate type
    if value.lower() == 'true':
        expected = True
    elif value.lower() == 'false':
        expected = False
    else:
        expected = value
        
    assert field in response_json, f"Field '{field}' not in response"
    assert response_json[field] == expected, \
        f"Field '{field}' should be {expected}, got {response_json[field]}"


@then(parsers.parse('the response should have field "{field}" containing "{text}"'))
def verify_response_field_contains(api_context, field, text):
    """Verify response JSON field contains expected text."""
    assert api_context['response'] is not None, "No response received"
    response_json = api_context['response'].json()
    
    assert field in response_json, f"Field '{field}' not in response"
    field_value = str(response_json[field])
    assert text in field_value, \
        f"Field '{field}' should contain '{text}', got: {field_value}"


@then(parsers.parse('the response should have field "{field}" with length {length:d}'))
def verify_response_field_length(api_context, field, length):
    """Verify response JSON field has expected length."""
    assert api_context['response'] is not None, "No response received"
    response_json = api_context['response'].json()
    
    assert field in response_json, f"Field '{field}' not in response"
    assert len(response_json[field]) == length, \
        f"Field '{field}' should have length {length}, got {len(response_json[field])}"


@then(parsers.parse('the response {field} should contain "{text}"'))
def verify_response_indexed_field(api_context, field, text):
    """Verify indexed response field contains text."""
    assert api_context['response'] is not None, "No response received"
    response_json = api_context['response'].json()
    
    # Parse field like "results[0]"
    if '[' in field and ']' in field:
        base_field, index = field.split('[')
        index = int(index.rstrip(']'))
        
        assert base_field in response_json, f"Field '{base_field}' not in response"
        assert len(response_json[base_field]) > index, \
            f"Field '{base_field}' doesn't have index {index}"
        
        value = str(response_json[base_field][index])
        assert text in value, \
            f"Field '{field}' should contain '{text}', got: {value}"


# Rate limiting verification
@then(parsers.parse('at least one response status should be {status_code:d}'))
def verify_any_response_status(api_context, status_code):
    """Verify at least one response has expected status."""
    statuses = [r.status_code for r in api_context['responses']]
    assert status_code in statuses, \
        f"Expected at least one {status_code} response, got: {statuses}"


@then(parsers.parse('the rate limit response should contain "{text}"'))
def verify_rate_limit_response(api_context, text):
    """Verify rate limit response contains expected text."""
    rate_limited = [r for r in api_context['responses'] if r.status_code == 429]
    assert rate_limited, "No rate limited responses found"
    
    for response in rate_limited:
        if text.lower() in response.text.lower():
            return
            
    pytest.fail(f"Rate limit responses don't contain '{text}'")


# WebSocket verification
@then(parsers.parse('I should receive WebSocket message containing "{text}"'))
def verify_websocket_message_contains(api_context, text):
    """Verify WebSocket message contains expected text."""
    assert api_context['ws_messages'], "No WebSocket messages received"
    
    message_texts = [json.dumps(m) for m in api_context['ws_messages']]
    combined = ' '.join(message_texts)
    
    assert text in combined, \
        f"WebSocket messages should contain '{text}', got: {combined}"


@then(parsers.parse('the WebSocket message should have field "{field}" equal to "{value}"'))
def verify_websocket_field(api_context, field, value):
    """Verify WebSocket message field has expected value."""
    assert api_context['ws_messages'], "No WebSocket messages received"
    
    latest_message = api_context['ws_messages'][-1]
    assert field in latest_message, f"Field '{field}' not in WebSocket message"
    assert latest_message[field] == value, \
        f"Field '{field}' should be '{value}', got '{latest_message[field]}'"