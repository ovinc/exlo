"""exlo initialization"""

from importlib_metadata import version

from .logging import Logger
from .misc import User, Project, Component, Equipment

__author__ = "Olivier Vincent"
__version__ = version("exlo")
