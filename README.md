csv_util.py
-----------

csv_util.py contains a single Python class `Csv` which I use for reading, manipulating, and writing comma-separated value spreadsheet files.

There are already excellent tools for doing this (e.g. [pandas](http://pandas.pydata.org/pandas-docs/stable/io.html#io-read-csv-table)) but they can be overkill for just wanting to read in and out a simple text spreadsheet file. The code here utilises the standard library `csv` module but adds handy features and makes it a bit simpler to use. Also more aimed at numerical/scientific files (e.g. it automatically converts to integers or floats where it can).

Contributions or suggestions welcome.

Released under the MIT License, so you're free to do whatever you like with it.
