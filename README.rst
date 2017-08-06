===========
color_debug
===========


.. image:: https://img.shields.io/pypi/v/color_debug.svg
        :target: https://pypi.python.org/pypi/color_debug

.. image:: https://img.shields.io/travis/alikins/color_debug.svg
        :target: https://travis-ci.org/alikins/color_debug

.. image:: https://readthedocs.org/projects/color-debug/badge/?version=latest
        :target: https://color-debug.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/alikins/color_debug/shield.svg
     :target: https://pyup.io/repos/github/alikins/color_debug/
     :alt: Updates


Python logging Formatter for colorizing logs per thread, process, logger name, or any record attribute

Using this logging formatter to make log records that share a common attribute share a color
automatically.

For example, a process with three threads could show the log entries for each thread in a different
color. The same can be done per process, or per logger name. Any log record attribute can be used
to choose the color used for the log entry.

The entire log record, the particular log field ('level' or 'process' for ex.), or a group of
fields can be colorized based on an attribute value.

For example, the fields for 'thread', 'threadName', 'process', 'processName' could be colorized
based on the thread id.

License
-------

* Free software: MIT license


Features
--------

* TODO
