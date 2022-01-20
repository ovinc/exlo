"""General definitions for the exlo package"""


# Standard library imports
from pathlib import Path
import json

# Non standard imports
from tzlocal import get_localzone

# Log data and config
import exlo_data
DATA_FOLDER = Path(exlo_data.__file__).parent


# ============================= General Classes ==============================


class JsonData:
    """Base class for data stored in json files (e.g. setups, users etc.)"""

    category = None  # Category of data (e.g. 'user', 'project', etc.)
    file = None  # file (Path object) in which data is stored (define in subclass)
    all_data = {}  # Dict of data loaded from json file (define in subclass)

    def __init__(self, name):
        """Create object by getting attributes in json file"""

        self.name = name

        # create attributes based on information in json file
        try:
            data = self.all_data[name]
        except KeyError:
            raise KeyError(f'Unknown {self.category}: "{name}". '
                           f'Must be in [{", ".join(self.all_data.keys())}]')
        else:
            for key, value in data.items():
                setattr(self, key, value)

    @staticmethod
    def _from_json(file):
        """Load python data (dict or list) from json file"""
        with open(file, 'r', encoding='utf8') as f:
            data = json.load(f)
        return data

    @staticmethod
    def _to_json(file, data):
        """Load python data (dict or list) from json file"""
        with open(file, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


# =============================== Misc. Config ===============================

config_filename = 'config.json'
users_filename = 'users.json'
projects_filename = 'projects.json'
components_filename = 'components.json'
setups_filename = 'setups.json'

# ============================= Misc. Constants ==============================

CONFIG_FILE = DATA_FOLDER / config_filename
USERS_FILE = DATA_FOLDER / users_filename
PROJECTS_FILE = DATA_FOLDER / projects_filename
COMPONENTS_FILE = DATA_FOLDER / components_filename
SETUPS_FILE = DATA_FOLDER / setups_filename

CONFIG = JsonData._from_json(CONFIG_FILE)
LOCAL_TIMEZONE = get_localzone()  # pytz object with local timezone info

USERS = JsonData._from_json(USERS_FILE)
PROJECTS = JsonData._from_json(PROJECTS_FILE)
COMPONENTS = JsonData._from_json(COMPONENTS_FILE)
SETUPS = JsonData._from_json(SETUPS_FILE)
