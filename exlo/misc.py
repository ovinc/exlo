"""Misc. classes for the exlo package (User, Component, Setup, Project."""


# local imports
from .general import JsonData, LOGS_FILE
from .general import USERS, PROJECTS, COMPONENTS, SETUPS
from .general import USERS_FILE, PROJECTS_FILE, COMPONENTS_FILE, SETUPS_FILE


# ============================= General Classes ==============================


class UnknownComponent(Exception):
    """Custom exception raised when component listed in setup is unknown"""
    pass


class User(JsonData):
    """Class to decribe and manage user information"""

    category = 'user'
    file = USERS_FILE
    all_data = USERS


class Project(JsonData):
    """Class to decribe and manage project information"""

    category = 'project'
    file = PROJECTS_FILE
    all_data = PROJECTS


class Component(JsonData):
    """Class to decribe and manage component information"""

    category = 'component'
    file = COMPONENTS_FILE
    all_data = COMPONENTS

    def change_name_to(self, new_name):
        """Update name of component in all places where it needs to be changed.

        Will change the name of the component in
        - components.json
        - setups.json

        Input
        -----
        new_name: str

        Example
        -------
        Component('Microscope').change_name_to('Stereoscope')
        """
        # Check name does not already exist and update components.json -------

        self._update_name(new_name)

        # Update setups.json -------------------------------------------------

        for setup_data in SETUPS.values():
            comps = setup_data['components']
            if self.name in comps:
                new_comps = [new_name if c == self.name else c for c in comps]
                setup_data['components'] = new_comps

        self._to_json(SETUPS_FILE, SETUPS)


class Setup(JsonData):
    """Class to decribe and manage setup information"""

    category = 'setup'
    file = SETUPS_FILE
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
