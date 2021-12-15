"""Misc. classes for the exlo package (User, Component, Setup, Project."""


# Standard library imports
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from copy import copy
import json

# local imports
from .general import JsonData
from .general import USERS, PROJECTS, COMPONENTS, SETUPS


# ============================= General Classes ==============================


class UnknownComponent(Exception):
    """Custom exception raised when component listed in setup is unknown"""
    pass


class User(JsonData):
    """Class to decribe and manage user information"""

    category = 'user'
    filename = 'users.json'
    all_data = USERS


class Project(JsonData):
    """Class to decribe and manage project information"""

    category = 'project'
    filename = 'projects.json'
    all_data = PROJECTS


class Component(JsonData):
    """Class to decribe and manage component information"""

    category = 'component'
    filename = 'components.json'
    all_data = COMPONENTS


class Setup(JsonData):
    """Class to decribe and manage setup information"""

    category = 'setup'
    filename = 'setups.json'
    all_data = SETUPS

    def check_components(self):
        """Verify that the components listed in the setup exist."""
        unknown_components = []
        for component in self.components:
            if component not in COMPONENTS:
                unknown_components.append(component)

        if len(unknown_components) > 0:
            raise UnknownComponent(f'In setup "{self.name}": '
                                   f'{unknown_components}')
