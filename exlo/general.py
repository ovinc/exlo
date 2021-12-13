"""General definitions for the exlo package"""


# Standard library imports
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from copy import copy
import json

# Non standard imports
from dateutil.parser import parse
from tzlocal import get_localzone

# Log data and config
import exlo_data
DATA_FOLDER = Path(exlo_data.__file__).parent


# ============================= General Classes ==============================


class JsonData:
    """Base class for data stored in json files (e.g. equipment, users etc.)"""

    filename = None  # file (str) in which data is stored (define in subclass)

    def __init__(self, name):
        """Create object by getting attributes in json file"""

        self.file = DATA_FOLDER / self.filename

        data = self._from_json(self.file)

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


CONFIG = JsonData._from_json(DATA_FOLDER / 'config.json')
LOCAL_TIMEZONE = get_localzone()  # pytz object with local timezone info

COMPONENTS = JsonData._from_json(DATA_FOLDER / 'components.json')
EQUIPMENT = JsonData._from_json(DATA_FOLDER / 'equipment.json')
USERS = JsonData._from_json(DATA_FOLDER / 'users.json')