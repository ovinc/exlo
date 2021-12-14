"""Tests for the exlo module."""

# Standard library
from exlo import Equipment
from exlo.general import EQUIPMENT


def test_components():
    """Check that components listed in each equipment exist."""
    for equip_name in EQUIPMENT:
        equipment = Equipment(equip_name)
        equipment.check_components()
