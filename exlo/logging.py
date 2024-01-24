"""Definitions related to logs / logger"""


# Standard library imports
from datetime import datetime
from dataclasses import dataclass
from copy import copy
from pathlib import Path

# Non standard imports
from dateutil.parser import parse
import pandas as pd

# Local imports
from .general import CONFIG, LOCAL_TIMEZONE, LOGS_FILE, JsonData
from .general import USERS, PROJECTS, COMPONENTS, SETUPS
from .misc import Setup


# ================================ Log class =================================


@dataclass
class Log:
    """Single log of equipment use."""

    number: int
    user: str
    setup: str
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
        return datetime.strptime(self.start, CONFIG["datetime format"])

    @property
    def end_datetime(self):
        """Convert self.start to a datetime.datetime"""
        return datetime.strptime(self.end, CONFIG["datetime format"])

    @property
    def duration(self):
        """Convert self.start to a datetime.datetime"""
        return self.end_datetime - self.start_datetime


# =============================== Logger class ===============================


class Logger:
    """General class to manage logs and their storage in .json files"""

    def __init__(self):

        self.config = CONFIG
        self.users = USERS
        self.projects = PROJECTS
        self.components = COMPONENTS
        self.setups = SETUPS

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

        names = 'user', 'setup', 'project', 'start', 'end', 'note'
        params = {}

        for ppty in names:
            default_ppty = self.config[f'default {ppty}']
            params[ppty] = kwargs.get(ppty, default_ppty)

        return params

    @staticmethod
    def _parse_datetime(datetime_str: str) -> datetime:
        """Transform loose str (e.g. '9am') into timezone-aware datetime"""
        dt = parse(datetime_str, fuzzy=True, dayfirst=True)
        dt_aware = LOCAL_TIMEZONE.localize(dt) if dt.tzinfo is None else dt
        return dt_aware

    @staticmethod
    def _format_datetime(dt_aware: datetime) -> str:
        """Format tz-aware datetime into correct str format for json saving etc."""
        return dt_aware.strftime(CONFIG["datetime format"])

    def _format_parameters(self, params):
        """Format entries in user-input log by doing the following things:

        - Check that user, project and setup are documented in json files.
        - Format start and end dates to correct str format.
        """
        if params['user'] not in self.users:
            raise ValueError('Unknown user. Check users.json')

        if params['setup'] not in self.setups:
            raise ValueError('Undocumented setup. Check setups.json')

        if params['project'] not in self.projects:
            raise ValueError('Unknown project. Check projects.json')

        for param in ('start', 'end'):
            dt_str_in = params[param]
            dt_aware = self._parse_datetime(dt_str_in)
            dt_str_out = self._format_datetime(dt_aware)
            params[param] = dt_str_out

    # ---------------------------- Public methods ----------------------------

    def add(self, **kwargs):
        """Add log to the existing list of logs.

        The possible kwargs are:
            - `user`: name of user, has to match one of those in Users.json
            - `setup`: name of setup, must match setups.json items
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
        log_list = JsonData._from_json(LOGS_FILE)
        return {log['number']: Log(**log) for log in log_list}

    def save(self):
        """Save logs to json file."""
        log_list = [vars(log) for log in self.logs.values()]
        JsonData._to_json(LOGS_FILE, log_list)

    def to_excel(
        self,
        savepath='.',
        filename='Logs.xlsx',
        min_date=None,
        max_date=None,
    ):
        """Export logs to Excel file with sheets corresponding to components.

        Parameters
        ----------
        - savepath (str or path object): directory in which to save data
        - filename (str): name of Excel file to generate
        - min_date (str): if not None, consider only logs with end >= min_date
        - max_date (str): if not None, consider only logs with start <= max_date
        """
        folder = Path(savepath)
        folder.mkdir(exist_ok=True)
        savefile = folder / filename

        def filter_dates(data):
            """return pandas data only within input min and max dates"""
            if min_date is not None:
                dt_end = pd.to_datetime(data['end'])
                dt_min = self._parse_datetime(min_date)
                data = data[dt_end >= dt_min]
            if max_date is not None:
                dt_start = pd.to_datetime(data['start'])
                dt_max = self._parse_datetime(max_date)
                data = data[dt_start <= dt_max]
            return data

        columns = (
            'user',
            'project',
            'setup',
            'start',
            'end',
            'duration',
            'number',
            'note',
        )

        all_data = {}

        for component in self.components:

            data = {column: [] for column in columns}

            for log in self.logs.values():

                setup = Setup(log.setup)

                if component in setup.components:

                    for column in columns:
                        column_data = getattr(log, column)
                        if column == 'duration':
                            column_data = str(column_data)
                        data[column].append(column_data)

            all_data[component] = data

        with pd.ExcelWriter(savefile, datetime_format='[h]:mm') as writer:

            info = {
                '(Info) - Components': self.components,
                '(Info) Setups': self.setups,
                '(Info) Users': self.users,
                '(Info) Projects': self.projects,
            }

            for info_name, info_data in info.items():

                pd.DataFrame(info_data).to_excel(
                    writer,
                    sheet_name=info_name,
                    startrow=2,
                )

                # Add title in first cell
                writer.sheets[info_name].write(0, 0, info_name)

            # hack to save datetimes correctly (see https://stackoverflow.com/
            # questions/46523178/formatting-timedelta64-when-using-pandas-to-excel)
            # t0 = pd.Timestamp('1900-01-01')

            for component, data in all_data.items():

                component_data = pd.DataFrame(data).sort_values('start')
                component_data_final = filter_dates(component_data)

                name = f'(Data) {component}'
                component_data_final.to_excel(
                    writer,
                    sheet_name=name,
                    index=False,
                    startrow=2,
                )

                # Add title in first cell
                writer.sheets[name].write(0, 0, name)
