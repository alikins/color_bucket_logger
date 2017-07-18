#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `color_debug` package."""

import pytest

import logging

from color_debug import color_debug


class BufHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.buf = []
        self.record_buf = []

    def emit(self, record):
        try:
            msg = self.format(record)
            self.buf.append(msg)
            self.record_buf.append(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_find_format_attrs():
    format_string = 'foo %(process)d blip'
    res = color_debug.find_format_attrs(format_string)
    assert ('%(process)d', 'process') in res


def test_find_format_attrs_precision():
    format_string = '%(levelname)-0.1s %(threadName)-2s %(process)-5d %(lineno)d'
    res = color_debug.find_format_attrs(format_string)
    assert ('%(levelname)-0.1s', 'levelname') in res
    assert ('%(process)-5d', 'process') in res
    assert ('%(threadName)-2s', 'threadName') in res
    assert ('%(lineno)d', 'lineno') in res


def setup_logger(color_groups=None, fmt=None):
    color_groups = color_groups or [('name', ['name', 'levelname'])]
    fmt = fmt or '%(levelname)s %(name)s %(message)s'
    formatter = color_debug.ColorFormatter(fmt=fmt,
                                           default_color_by_attr='name',
                                           color_groups=color_groups)
    logger = logging.getLogger(__name__ + '.test_logger')
    logger.setLevel(logging.DEBUG)
    handler = BufHandler(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, handler, formatter


def test_get_name_color():
    logger, handler, formatter = setup_logger(color_groups=[('name', ['name', 'levelname'])],
                                              fmt='%(levelname)s %(name)s %(message)s')
    logger.debug('foooooooo')

    for record in handler.record_buf:
        print(record.__dict__)
        assert hasattr(record, '_cdl_name')


def test_init(response):
    """Just init the class"""
    formatter = color_debug.ColorFormatter()
    assert isinstance(formatter, color_debug.ColorFormatter)


def test_null_handler(response):
    nh = logging.NullHandler()
    formatter = color_debug.ColorFormatter()
    nh.setFormatter(formatter)
