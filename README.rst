======
eparse
======


.. image:: https://img.shields.io/pypi/v/eparse.svg
        :target: https://pypi.python.org/pypi/eparse

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
        :target: https://opensource.org/licenses/MIT
        :alt: License: MIT


Description
===========
Excel spreadsheet crawler and table parser for data extraction
and querying

* TODO


Installation
============
To install eparse, you can use pip and the latest version on PyPI:

.. code-block:: bash

   $ pip install eparse

Or you can clone this repo and install from source:

.. code-block:: bash

   $ git clone https://github.com/ChrisPappalardo/eparse.git
   $ cd eparse
   $ pip install .


Usage
=====
eparse is intended to be used from the command-line.  You can view
supported commands and usage with `--help` as follows:

.. code-block:: bash

   $ eparse --help
   Usage: eparse [OPTIONS] COMMAND [ARGS]...

   excel parser

   Options:
     -i, --input TEXT   input dir(s) or file(s)
     -o, --output TEXT  output destination
     -d, --debug        use debug mode
     -l, --loose        find tables loosely
     -r, --recursive    find files recursively
     -t, --truncate     truncate dataframe output
     -v, --verbose      increase output verbosity
     --help             Show this message and exit.

   Commands:
     parse  parse table(s) found in sheet for target(s)
     query  query eparse output
     scan   scan for excel files in target


Scan
----
To scan one or more directories for Excel files with descriptive
information, you can use the `scan` command like so:

.. code-block:: bash

    $ eparse -v -i <path_to_files> scan

Increase the verbosity with additional flags, such as `-vvv`, for
more descriptive information about the file(s), including sheet names.


Parse
-----
Excel files can be parsed as follows:

.. code-block:: bash

    $ eparse -v -i <path_to_files> parse

This mode will list each table found in each Excel file to the command-line.
This mode is useful for initial discovery for parseable data.

eparse uses a simple algorithm for identifying tables.  Table "corners"
are identified as cells that contain empty cells above and to the right
(or sheet boundaries).  A densely or sparsely populated 2x2 table must
follow in order for data to be extracted in relation to that cell.
eparse will automatically adjust for rowspan labels and empty table
corners and the dense vs. sparse criterion can be controlled with
the `--loose` flag.

eparse was written to accomodate various types of output formats and
endpoints, including `to_null`, `to_stdout`, and `to_sqlite3`.

to_null
^^^^^^^
This mode is useful for validating files and generating descriptive
info, and is the default.  The command above with `-v` is an example
of this mode, which lists out the tables found.

to_stdout
^^^^^^^^^
This mode is good for viewing data extracted from Excel files in the
console.  For example, you could view all tables found in `Sheet1`
with the following command:

.. code-block:: bash

    $ eparse -i <path_to_files> -o to_stdout parse -s "Sheet1"

eparse uses `pandas.DataTable <https://github.com/pandas-dev/pandas>`_
to handle table data.  You can view larger tables without truncation
using the `-t` flag as follows:

.. code-block:: bash

    $ eparse -t -i <path_to_files> -o to_stdout parse -s "Sheet1"

Data in table format is useful for human viewing, but a serialized
form is better for data interfacing.  Serialize your output with
the `-z` flag as follows:

.. code-block:: bash

    $ eparse -t -i <path_to_files> -o to_stdout parse -z

Each cell of extracted table data is serialized as follows:

* row - 0-indexed table row number
* column - 0-indexed table column number
* value - the value of the cell as a `str`
* type - the implied python `type` of the data found
* c_header - the column header
* r_header - the row header
* excel_RC - the RC reference from the spreadsheet (e.g. B10)
* sheet - the name of the sheet
* f_name - the name of the file

to_sqlite3
^^^^^^^^^^
eparse uses the `peewee <https://github.com/coleifer/peewee>`_
package for ORM and database integration.  The
`eparse/interfaces.py <eparse/interfaces.py>`_ module contains a
`ExcelParse` model that provides data persistence and a common
interface.

To create a `SQLite3 <https://github.com/sqlite/sqlite>`_ database
with your parsed Excel data, use the following command:

.. code-block:: bash

    $ mkdir .files
    $ eparse -i <path_to_files> -o to_sqlite3 parse

This command will automatically generate a unique database filename
using the `uuid` python package in the `.files/` sub-directory of
the working directory.  You may need to create this directory before
running this command, as shown.


query
-----
Once you have stored parsed data, you can begin to query it using the
`peewee` ORM.  This can be done with the tool or directly with the
database.

For example, query distinct column header names from a generated
`SQLite3` database as follows:

.. code-block:: bash

    $ eparse -o to_stdout query -i from_sqlite3 .files/<db_file> -m get_c_header
                   c_header  Total Rows  Data Types  Distinct Values
      0             ABC-col         150           2               76
      1             DEF-col        3981           3               15
      2             GHI-col          20           1                2
      ..                ...         ...         ...              ...

This command will give descriptive information of each distinct c_header
found, including total rows, unique data types, and distinct values.

You can also get raw un-truncated data as follows, which is the default
behavior:

.. code-block:: bash

    $ eparse -t -o to_stdout query -i from_sqlite3 .files/<db_file>

Filtering data on content is easy.  Use the `--filter` option as follows:

.. code-block:: bash

    $ eparse -t -o to_stdout query -i from_sqlite3 .files/<db_file> --filter f_name "somefile.xlsx"

The above command will filter all rows from an Excel file named
`somefile.xlsx`. You can use any of the following `django`-style
filters:

* `__eq` equals X
* `__lt` less than X
* `__lte` less than or equal to X
* `__gt` greater than X
* `__gte` greater than or equal to X
* `__ne` not equal to X
* `__in` X is in
* `__is` is X
* `__like` like expression, such as `%somestr%`, case sensitive
* `__ilike` like expression, such as `%somestr%`, case insensitive
* `__regexp` regular expression matching such as `^.*?foo.*?$`

Filters are applied to the ORM fields like so:

* `--filter row__gte 4` all extracted table rows >= 5
* `--filter f_name__ilike "%foo%"` all data from filenames with "foo"
* `--filter value__ne 100` all data with values other than 100

Queried data can even be stored into a new database for creating
curated data subsets, as follows:

.. code-block:: bash

    $ eparse -t -o to_sqlite3 query -i from_sqlite3 .files/<db_file>


Contributing
============
As an open-source project, contributions are always welcome. Please see `Contributing <CONTRIBUTING.rst>`_ for more information.


License
=======
eparse is licensed under the `MIT License <https://opensource.org/licenses/MIT>`_. See the `LICENSE <LICENSE>`_ file for more details.


Contact
=======
Thanks for your support of eparse. Feel free to contact me at `cpappala@gmail.com <mailto:cpappala@gmail.com>`_ or connect with me on `Github <https://www.linkedin.com/in/chris-a-pappalardo/>`_.
