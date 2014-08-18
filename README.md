Accuracy assessment sampler for QGIS
===============

## Status
QGIS plugin is still in development.

You can download a functioning sampling script for doing random stratified sampling from the "script" folder, or by clicking [here for the latest version from master](https://raw.githubusercontent.com/ceholden/accuracy_sampler/master/script/sample_map.py).

## Dependencies
Main dependencies:

    QGIS (2.0.1 or newer)
    Python (2.7.5 or newer, but not Python 3)
    GDAL (1.10.0 or newer)

Python dependencies:

    numpy>=1.7.0
    gdal>=1.10.0
    docopt>=0.6.0

If you have QGIS already installed on your system, you most likely already have everything but the [`docopt`](https://github.com/docopt/docopt) module installed. Luckily, `docopt` is easily available from the [Python Package Index (`pip`)](https://pypi.python.org/pypi/docopt). If you don't have or don't want to use `pip`, `docopt` is very easy to install as it is just one single script file. Simply [download the `docopt.py` script from here](https://raw.githubusercontent.com/docopt/docopt/master/docopt.py) and place it next to the Python script you're running, or somewhere in your `PYTHONPATH`.
