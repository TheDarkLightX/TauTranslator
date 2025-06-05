"""
Pytest-BDD Configuration
=======================

Configuration for BDD tests using pytest-bdd.
"""

import pytest
from pathlib import Path


def pytest_configure(config):
    """Configure pytest for BDD testing."""
    config.addinivalue_line(
        "markers", 
        "core: Core functionality tests"
    )
    config.addinivalue_line(
        "markers", 
        "translation: Translation-related tests"
    )
    config.addinivalue_line(
        "markers", 
        "bidirectional: Bidirectional translation tests"
    )
    config.addinivalue_line(
        "markers", 
        "error_handling: Error handling tests"
    )
    config.addinivalue_line(
        "markers", 
        "nlp: Natural language processing tests"
    )
    config.addinivalue_line(
        "markers", 
        "streams: Stream processing tests"
    )
    config.addinivalue_line(
        "markers", 
        "arithmetic: Arithmetic operation tests"
    )
    config.addinivalue_line(
        "markers", 
        "api: API-related tests"
    )
    config.addinivalue_line(
        "markers", 
        "parser: Parser-related tests"
    )
    config.addinivalue_line(
        "markers", 
        "semantic: Semantic analysis tests"
    )
    config.addinivalue_line(
        "markers", 
        "performance: Performance-related tests"
    )
    config.addinivalue_line(
        "markers", 
        "integration: Integration tests"
    )


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Get test data directory."""
    return project_root / "tests" / "data"


@pytest.fixture(scope="session")
def fixtures_dir(project_root):
    """Get fixtures directory."""
    return project_root / "tests" / "fixtures"


# Hook to generate BDD test report
def pytest_bdd_after_scenario(request, feature, scenario):
    """Hook called after each scenario."""
    # Could add custom reporting here
    pass


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Hook called when a step fails."""
    # Could add enhanced error reporting here
    print(f"\nBDD Step Failed: {step.name}")
    print(f"  Feature: {feature.name}")
    print(f"  Scenario: {scenario.name}")
    print(f"  Error: {exception}")


# Custom pytest options for BDD
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--bdd-strict",
        action="store_true",
        default=False,
        help="Fail on undefined steps"
    )
    parser.addoption(
        "--bdd-showsteps",
        action="store_true",
        default=False,
        help="Show all available step definitions"
    )