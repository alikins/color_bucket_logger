#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `color_bucket_logger` package."""

import pytest

import logging
try:
    from logging import NullHandler
except ImportError:
    # no NullHandler on py2.6, so use our own
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

import color_bucket_logger


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
    res = color_bucket_logger.formatter.find_format_attrs(format_string)
    assert ('%(process)d', 'process') in res


def test_find_format_attrs_precision():
    format_string = '%(levelname)-0.1s %(threadName)-2s %(process)-5d %(lineno)d'
    res = color_bucket_logger.formatter.find_format_attrs(format_string)
    assert ('%(levelname)-0.1s', 'levelname') in res
    assert ('%(process)-5d', 'process') in res
    assert ('%(threadName)-2s', 'threadName') in res
    assert ('%(lineno)d', 'lineno') in res


def setup_logger(color_groups=None, fmt=None):
    color_groups = color_groups or [('name', ['name', 'levelname'])]
    fmt = fmt or '%(levelname)s %(name)s %(message)s'
    formatter = color_bucket_logger.ColorFormatter(fmt=fmt,
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
                                              fmt='levelname=%(levelname)s name=%(name)s message=%(message)s')
    logger.debug('foo%s', 'blip')

    for record in handler.record_buf:
        # The _cdl_* attrs should NOT be set on the record now
        assert not hasattr(record, '_cdl_name')

    for logged_item in handler.buf:
        # the expected rendered output include term escape codes
        expected_levelname = 'levelname=\x1b[38;5;97mDEBUG\x1b[38;5;97m'
        expected_message = 'message=\x1b[38;5;97mfooblip\x1b[38;5;97m\x1b[0m'
        assert expected_levelname in logged_item
        assert expected_message in logged_item


def test_stuff():
    fmt_string = '%(levelname)s %(created)s %(filename)s %(funcName)s '
    '%(levelno)s %(module)s %(pathname)s %(process)d '
    '%(thread)d %(name)s %(message)s'
    logger, handler, formatter = setup_logger(color_groups=[('name', ['name', 'levelname'])],
                                              fmt=fmt_string)

    sfmt = '%(levelname)s %(filename)s %(process)d'
    '%(thread)d %(name)s %(message)s'
    slogger, shandler, formatter = setup_logger(color_groups=[('name', ['name', 'levelname'])],
                                                fmt=sfmt)

    logger.debug('D: %s', '_debug')
    logger.info('I: %s', '_info')
    logger.warning('W: %s', '_warn')
    slogger.debug('foo1')
    slogger.info('foo2')
    slogger.error('foo4')

    for record in handler.record_buf:
        print(record.message)


def test_init(response):
    """Just init the class"""
    formatter = color_bucket_logger.ColorFormatter()
    assert isinstance(formatter, color_bucket_logger.ColorFormatter)


def test_null_handler(response):
    nh = NullHandler()
    formatter = color_bucket_logger.ColorFormatter()
    nh.setFormatter(formatter)
