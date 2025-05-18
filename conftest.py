"""Pytest configuration file."""
import os
import pytest


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--thread-count",
        action="store",
        default=None,
        help="Number of threads to use for thread tests",
    )


@pytest.fixture(scope="session")
def thread_count(request):
    """Get thread count from command line or environment variable."""
    # Command line option takes precedence
    cli_value = request.config.getoption("--thread-count")
    if cli_value is not None:
        return int(cli_value)
    
    # Fall back to environment variable
    env_value = os.environ.get("THREAD_COUNT")
    if env_value is not None:
        return int(env_value)
    
    # Default value if nothing is specified
    return None
