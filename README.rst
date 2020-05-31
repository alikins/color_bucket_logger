===================
color_bucket_logger
===================


.. image:: https://img.shields.io/pypi/v/color_bucket_logger.svg
        :target: https://pypi.python.org/pypi/color_bucket_logger

.. image:: https://img.shields.io/travis/alikins/color_bucket_logger.svg
        :target: https://travis-ci.org/alikins/color_bucket_logger

.. image:: https://readthedocs.org/projects/color-bucket-logger/badge/?version=latest
        :target: https://color-bucket-logger.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/alikins/color_bucket_logger/shield.svg
     :target: https://pyup.io/repos/github/alikins/color_bucket_logger/
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

Usage
-----

Examples
--------

Basic config colorized by logger name::

    import logging

    import color_bucket_logger

    log = logging.getLogger('example')
    log.setLevel(logging.DEBUG)

    log_format = '%(asctime)s %(process)s %(levelname)s %(name)s %(funcName)s -- %(message)s'

    # Use logger name for the primary color of each entry
    formatter = color_bucket_logger.ColorFormatter(fmt=log_format, default_color_by_attr='name')

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    # basicConfig will add our handler to the root logger
    # Note 'handlers' arg is py3 only
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

Color Group Examples
--------------------

Example uses of color_groups::

    # color almost everything by logger name
    color_groups = [('name', ['filename', 'module', 'lineno', 'funcName', 'pathname'])]

    color_groups = [
        ('process', ['default', 'message']),
        ('process', ['processName', 'process']),
        ('thread', ['default', 'threadName', 'message', 'unset', 'processName', 'exc_text']),
        ('thread', ['threadName', 'thread']),
        ]

    # color logger name, filename and lineno same as the funcName
    color_groups = [('funcName', ['default', 'message', 'unset', 'name', 'filename', 'lineno'])]

    # color message same as debug level
    color_groups = [('levelname', ['levelname', 'levelno'])]

    # color funcName, filename, lineno same as logger name
    color_groups = [('name', ['funcName', 'filename', 'lineno'])]

    # color groups can be based on non standard 'extra' attributes or log record
    # attibutes created from filters. In this example, a 'task' attributes.
    color_groups = [('task', ['task_uuid', 'task'])]

    # color default, msg and playbook/play/task by the play
    color_groups = [('play', ['default','message', 'unset', 'play', 'task'])]

License
-------

* Free software: MIT license


Features
--------

* TODO
