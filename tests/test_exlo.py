"""Tests for the exlo module."""

# Standard library
from exlo import Setup
from exlo.general import SETUPS


def test_components():
    """Check that components listed in each setup exist."""
    for setup_name in SETUPS:
        setup = Setup(setup_name)
        setup.check_components()
