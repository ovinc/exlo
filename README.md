About
=====

Log usage of equipment for scientific experiments with json files.

Install
-------

Before install, the separate config/data package `exlo_data` must be installed, see https://github.com/ovinc/exlo_data

```bash
git clone https://github.com/ovinc/exlo
cd exlo
pip install -e .
```

Quick start
===========

The companion `exlo_data` module contains several `json` files that need to be filled before being able to use the logger :

- `config.json` (misc. configuration)
- `users.json` (list of users and their information)
- `equipment.json` (list of equipment and related info)
- `projects.json` (list of projects the equipment can be used for).

Once this configuration step is done, one can instantiate and use the `Logger` class to create and manage logs for the equipment:

```python
from exlo import Logger
logger = Logger()

# Add log; any field not provided will use default values from config.json
# The user, equipment & project must match one of those in the config files
# The date parser uses dateutil.parser and accepts a variety of date formats
# By default the day is present day, and timezone is the local timezone.
# In case of ambiguity in day/month order, day first is assumed.
logger.add(user='Martin', equipment='Optic1', project='Dupont-ERC-2020',
           start='9am', end='15:00', note='First test of the new laser')

# Save this new log to the log list in the json file
logger.save()

# See all logs as a list (opening the json file might be easier to read)
logger.logs

# Update any of the field in the last log; save() must be called again.
logger.update(equipment='Optic2')
logger.update(42, end='16:30')  # update not the last log but another one (#42)
logger.save()

# Remove logs
logger.remove()    # remove last log
logger.remove(33)  # remove specific log
logger.save()
```

Each log is an object from the `Log` dataclass, which stores all fields as strings (`str`) except the log number as an `int`. For convenience, one can also access time-related information as datetime/timedelta objects:
```python
log = logger.logs[42]  # extract 42th log

# datetime.dateime objects
log.start_datetime
log.end_datetime

# timedelta object
log.duration
```


Misc. info
==========

Module requirements
-------------------

### Config/data module

The logger config and data are managed in a separate package `exlo_data` (see *Install* section above).


### Modules outside of standard library

(installed automatically by pip if necessary)

- python-dateutil
- tzlocal
- importlib-metadata



Python requirements
-------------------

Python : >= 3.7 (dataclasses)

Author
------

Olivier Vincent

(ovinc.py@gmail.com)

License
-------

3-Clause BSD (see *LICENSE* file).

