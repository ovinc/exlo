"""General definitions for the exlo package"""


# Standard library imports
from pathlib import Path
import json

# Non standard imports
from tzlocal import get_localzone

# Log data and config
import exlo_data
DATA_FOLDER = Path(exlo_data.__file__).parent


# ----------------------------------------------------------------------------
# ============================= General Classes ==============================
# ----------------------------------------------------------------------------


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

    # ======================== JSON loading / saving =========================

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

    # ======================== Misc. private methods =========================

    def _update_name(self, new_name):
        """Change name of category in its own JSON file.

        For example, change name of one component in components.json
        Used by change_name_to() methods;
        """
        data = self.all_data

        # Prevent use of existing name ---------------------------------------

        if new_name in data:
            raise ValueError(f'{self.category} name "{new_name}" already exists!')

        # Update JSON file ---------------------------------------------------

        data[new_name] = data.pop(self.name)
        self._to_json(self.file, data)

    def _update_logs(self, new_name):
        """Change of name of category (e.g user, setup, project etc.) in logs.json

        Used by change_name_to() methods;
        """
        log_list = self._from_json(LOGS_FILE)  # list of dicts

        for log_data in log_list:
            if log_data[self.category] == self.name:
                log_data[self.category] = new_name

        self._to_json(LOGS_FILE, log_list)

    # ============================ Public methods ============================

    def change_name_to(self, new_name):
        """Update name of category in all places where it needs to be changed.

        For example for category 'setup', this method will update the name of
        the setup in
        - setups.json
        - logs.json

        Input
        -----
        new_name: str

        Example
        -------
        Setup('Optic1').change_name_to('Optic1-Old')
        """
        self._update_name(new_name)
        self._update_logs(new_name)


# ----------------------------------------------------------------------------
# =============================== Misc. Config ===============================
# ----------------------------------------------------------------------------

config_filename = 'config.json'
users_filename = 'users.json'
projects_filename = 'projects.json'
components_filename = 'components.json'
setups_filename = 'setups.json'

# ----------------------------------------------------------------------------
# ============================= Misc. Constants ==============================
# ----------------------------------------------------------------------------

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

LOGS_FILE = DATA_FOLDER / CONFIG['log file']
