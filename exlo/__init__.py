"""exlo initialization"""

from importlib_metadata import version

from .general import DATA_FOLDER, CONFIG, LOCAL_TIMEZONE
from .general import COMPONENTS, EQUIPMENT, USERS

from .logging import Logger

__author__ = "Olivier Vincent"
__version__ = version("exlo")
