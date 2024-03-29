About
=====

Log usage of equipment for scientific experiments with json files.

Install
-------

Before install, the separate config/data package `exlo_data` must be installed, see https://github.com/ovinc/exlo_data

After this, install the `exlo` package with:

```bash
git clone https://github.com/ovinc/exlo
cd exlo
pip install -e .
```

Quick start
===========

## Configuration

The companion `exlo_data` module contains several `json` files that need to be filled before being able to use the logger :

- `config.json` (misc. configuration),
- `users.json` (list of users and their information),
- `components.json` (list of individual pieces of equipment that constitute the *setups* below),
- `setups.json` (list of setups and related info),
- `projects.json` (list of projects the equipment can be used for).

## Logging use of equipment

Once the configuration step is done, one can instantiate and use the `Logger` class to create and manage logs for the equipment:

```python
from exlo import Logger
logger = Logger()

# Add log; any field not provided will use default values from config.json
# The user, setup & project must match one of those in the config files
# The date parser uses dateutil.parser and accepts a variety of date formats
# By default the day is present day, and timezone is the local timezone.
# In case of ambiguity in day/month order, day first is assumed.
logger.add(user='Martin', setup='Optic1', project='Dupont-ERC-2020',
           start='9am', end='15:00', note='First test of the new laser')

# Save this new log to the log list in the json file
logger.save()

# See all logs as a list (opening the json file might be easier to read)
logger.logs

# Update any of the field in the last log; save() must be called again.
logger.update(setup='Optic2')
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

## Export logs to Excel

The `Logger` class has a `to_excel()` method that exports the info on users, projects, components, setups and logs into an Excel file.

The logs are separated for each component, and separate sheets in the Excel file represent the log data corresponding to every component. If a setup contains several components, this means that a log with this setup will be duplicated in all sheets of the corresponding components.

To do the export, just `cd` into the directory where you want the file to be generated and:
```python
from exlo import Logger
logger = Logger()
logger.to_excel()
```
This will generate a file `Logs.xlsx` in the current directory.

Export of logs can also be filtered by date:
```python
logger.to_excel(min_date='Jan 1, 2023', max_date='Dec. 31, 2024')
```
(note that if a log spans before and after the min/max dates, it will be included, i.e. only the end time of the log is considered for the min date, and only the start time of the log is considered for the max date).

It is also possible to specify a path for saving and/or change the filename:
```python
logger.to_excel(savepath='D:/Data/Logs', filename='Log_Data.xlsx')
```

**NOTE:** If `to_excel` generates an error *AttributeError: 'Worksheet' object has no attribute 'write'*, it may be that `xslxwriter` is not installed. This can be fixed with `pip install xlsxwriter`.


## Python objects representing users, projects, components, setups

The users, projects, components and setup are also represented by classes (`User`, `Project`, `Component`, `Setup`, respectively), which define their attributes automatically from the `.json` files:

```python
from exlo import User, Project, Component, Setup

user = User('Martin')
user.status
>>> Postdoc

setup = Setup('Optic1')
setup.components
>>> ["Laser", "Microscope"]
```

The `Setup` class also has a method to check that the listed components are indeed described in the `components.json` file.
```python
setup.check_components()
```
which raises a `UnknownComponent` exception.

## Batch change of names of users, projects, components, setups

It's possible to change the name (identifier) of a user, project, component or setup everywhere in the system at once by using the `change_name_to()` methods of the corresponding classes. For example,
```python
from exlo import User, Project, Component, Setup

User('Cam').change_name_to('Camille')
Project('Dupont-ERC-2020').change_name_to('ERC')
Component('Microscope').change_name_to('Stereoscope')
Setup('Optic1').change_name_to('Optic1-Old')
```
This will change the identifier names anywhere they need to be changed in the JSON files, including *logs.json* (and for components, in the *setups.json* file).

It is probably wise to restart the python console and re-import **exlo** after calling `change_name_to()`, because some variables in memory don't automatically re-load data from the JSON files.


Testing
=======

With `pytest`:
```bash
pytest
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
- tzlocal < 3.0 (typically, 2.1; after this, problems arise due to dropped pytz support)
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

