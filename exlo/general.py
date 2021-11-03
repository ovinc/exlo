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


# ============================= Misc. functions ==============================


def _from_json(file):
    """Load python data (dict or list) from json file"""
    with open(file, 'r', encoding='utf8') as f:
        data = json.load(f)
    return data


def _to_json(file, data):
    """Load python data (dict or list) from json file"""
    with open(file, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =============================== Misc. Config ===============================


data_folder = Path(exlo_data.__file__).parent

config_file = data_folder / 'config.json'
config = _from_json(config_file)

local_timezone = get_localzone()  # pytz object with local timezone info


# ============================= General Classes ==============================


@dataclass
class Log:
    """Single log of equipment use."""

    number: int
    user: str
    equipment: str
    project: str
    start: str
    end: str
    note: str

    def __post_init__(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError('End date must be later than start date.')

    @property
    def start_datetime(self):
        """Convert self.start to a datetime.datetime"""
        return datetime.strptime(self.start, config["datetime format"])

    @property
    def end_datetime(self):
        """Convert self.start to a datetime.datetime"""
        return datetime.strptime(self.end, config["datetime format"])

    @property
    def duration(self):
        """Convert self.start to a datetime.datetime"""
        return self.end_datetime - self.start_datetime


class Logger:
    """General class to manage logs and their storage in .json files"""

    def __init__(self):

        # json files containing data and misc. info
        self.log_file = data_folder / config['log file']
        self.config_file = config_file
        self.users_file = data_folder / 'users.json'
        self.equipment_file = data_folder / 'equipment.json'
        self.projects_file = data_folder / 'projects.json'

        # Dicts of config and misc. info (users, equipment etc.)
        self.config = _from_json(self.config_file)
        self.users = _from_json(self.users_file)
        self.equipment = _from_json(self.equipment_file)
        self.projects = _from_json(self.projects_file)

        try:
            self.logs = self.load()
        except FileNotFoundError:
            print('No log file detected. You can create one with the save() '
                  'method after adding logs.')
            self.logs = {}

    def __repr__(self):
        msg = f"Logger with {len(self.logs)} logs."
        return msg

    # ------------------------ Misc. private methods -------------------------

    def _add_default_values(self, **kwargs):
        """Add default values to non-specified entries."""

        names = 'user', 'equipment', 'project', 'start', 'end', 'note'
        params = {}

        for ppty in names:
            default_ppty = self.config[f'default {ppty}']
            params[ppty] = kwargs.get(ppty, default_ppty)

        return params

    @staticmethod
    def _format_datetime(datetime_str: str) -> str:
        """Format input datetime into correct str format for json saving etc."""

        # Transform loose str (e.g. '9am') into timezone-aware datetime
        dt = parse(datetime_str, fuzzy=True, dayfirst=True)
        dt_aware = local_timezone.localize(dt) if dt.tzinfo is None else dt

        # Format into standardized string
        return dt_aware.strftime(config["datetime format"])

    def _format_parameters(self, params):
        """Format entries in user-input log by doing the following things:

        - Check that user, project and equipment are documented in json files.
        - Format start and end dates to correct str format.
        """
        if params['user'] not in self.users:
            raise ValueError('Unknown user. Check users.json')

        if params['equipment'] not in self.equipment:
            raise ValueError('Undocumented equipment. Check equipment.json')

        if params['project'] not in self.projects:
            raise ValueError('Unknown project. Check projects.json')

        for param in ('start', 'end'):
            params[param] = self._format_datetime(params[param])

    # ---------------------------- Public methods ----------------------------

    def add(self, **kwargs):
        """Add log to the existing list of logs.

        The possible kwargs are:
            - `user`: name of user, has to match one of those in Users.json
            - `equipment`: name of equipment, must match Equipment.json items
            - `project`: name of project, must match Projects.json items
            - `start`: start datetime, can be loose (e.g. "9am")
            - `end`: end datetime
            - `note`: any remarks to add.

        When values are not specified, default values from the configuration
        file (config.json) are used.
        """
        params = self._add_default_values(**kwargs)
        self._format_parameters(params)
        n = len(self.logs)
        self.logs[n] = Log(number=n, **params)

    def remove(self, number=None):
        """Remove log from log list (by default, last one).

        If the removed log is not the last one, the numbers are updated for
        all logs following it.
        """
        number = len(self.logs) - 1 if number is None else number
        lastlog = True if number == len(self.logs) - 1 else False

        self.logs.pop(number)

        # Decrease ID number of following logs if necessary
        if not lastlog:
            for n in range(number + 1, len(self.logs) + 1):
                self.logs[n - 1] = self.logs.pop(n)
                self.logs[n - 1].number = n - 1

    def update(self, number=None, **kwargs):
        """Update one or more entry in one of the logs (default last log).

        - number is the ID of the log to update (if not specified -> last log)
        - kwargs can be any entry in a log (see logger.add()), except number.
        """
        n = len(self.logs) - 1 if number is None else number
        log = self.logs[n]

        params = copy(vars(log))
        params.pop('number')

        for param, value in kwargs.items():
            params[param] = value

        self._format_parameters(params)
        self.logs[n] = Log(number=n, **params)

    def load(self):
        """Load logs stored in .json file into a dictionary."""
        log_list = _from_json(self.log_file)
        return {log['number']: Log(**log) for log in log_list}

    def save(self):
        """Save logs to json file."""
        log_list = [vars(log) for log in self.logs.values()]
        _to_json(self.log_file, log_list)
