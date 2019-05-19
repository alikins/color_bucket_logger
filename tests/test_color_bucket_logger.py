#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `color_bucket_logger` package."""
import logging
import logging.config
import sys
import threading

import logging_tree
import pytest

try:
    from logging import NullHandler
except ImportError:
    # no NullHandler on py2.6, so use our own
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

import color_bucket_logger

min_log_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
    },
    'filters': {},
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'blip':
            {'level': logging.DEBUG},
    }
}

testlog = logging.getLogger(__name__)
testlog.debug('testlog ping')


def delete_log_tree(log_node):
    for child in log_node[2]:
        delete_log_tree(child)
    log_node[1].handlers = []


def teardown_config():
    logging.getLogger('tests.test_color_bucket_logger').handlers = []
    lt = logging_tree.tree()
    delete_log_tree(lt)
    logging.config.dictConfig(min_log_config)


def setup_logger(color_groups=None, fmt=None,
                 formatter_class=None, auto_color=False,
                 default_color_by_attr=None):
    formatter_class = formatter_class or color_bucket_logger.ColorFormatter
    color_groups = color_groups or [('name', ['name', 'levelname'])]

    fmt = fmt or '%(levelname)s %(name)s %(message)s'
    formatter = formatter_class(fmt=fmt,
                                default_color_by_attr=default_color_by_attr or 'name',
                                color_groups=color_groups,
                                auto_color=auto_color)

    logger = logging.getLogger(__name__ + '.test_logger')
    logger.disabled = False
    logger.setLevel(logging.DEBUG)
    handler = BufHandler(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, handler, formatter


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
        except Exception:
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


def other_logger():
    logger = logging.getLogger(__name__ + '.test_logger.other')
    logger.disabled = False
    logger.setLevel(logging.DEBUG)

    logger.debug('Other Logger %s', 'TheOL')
    logger.error('We have a problem')


def test_term_formatter_no_args():
    formatter = color_bucket_logger.TermFormatter()

    logger = logging.getLogger(__name__ + '.test_logger')
    logger.disabled = False
    logger.setLevel(logging.DEBUG)

    handler = BufHandler(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.debug('default termFormatter no args %s', 'blip')
    other_logger()
    logger.critical('I think you chew too loudly')
    logging_tree.printout()

    # The default is to colorize by logger name, so setup two
    # loggers, and assert they got expected color therefore different
    other_exp = '\x1b[38;5;53m'
    too_loudly_exp = '\x1b[38;5;70m'

    for logged_item in handler.buf:
        testlog.debug('logged_item: %s', logged_item)
        if 'other_logger' in logged_item:
            assert other_exp in logged_item
        if 'too loudly' in logged_item:
            assert too_loudly_exp in logged_item


def test_get_name_color():
    logger, handler, formatter = setup_logger(color_groups=[('name', ['name', 'levelname'])],
                                              fmt='levelname=%(levelname)s name=%(name)s message=%(message)s')
    logger.debug('foo%s', 'blip')

    for record in handler.record_buf:
        # The _cdl_* attrs should NOT be set on the record now
        assert not hasattr(record, '_cdl_name')

    for logged_item in handler.buf:
        # the expected rendered output include term escape codes
        expected_levelname = 'levelname=\x1b[38;5;70mDEBUG\x1b[38;5;70m'
        expected_message = 'message=\x1b[38;5;70mfooblip\x1b[38;5;70m\x1b[0m'
        testlog.debug('logged_item: %s', logged_item)
        assert expected_levelname in logged_item
        assert expected_message in logged_item


def test_default_color_by_just_message():
    logger, handler, formatter = setup_logger(color_groups=[],
                                              default_color_by_attr='message',
                                              fmt='levelname=%(levelname)s name=%(name)s message=%(message)s')
    logger.debug('some msg 0')
    logger.debug('some other msg 2')
    logger.info('some other msg 2')
    logger.debug('some_msg1')
    logger.info('some_msg1')
    logger.error('some_msg1')

    for logged_item in handler.buf:
        testlog.debug('logged_item: %s', logged_item)
        expected_default = '\x1b[38;5;113m'
        other_expected_default = '\x1b[38;5;52m'
        if 'some_msg1' in logged_item:
            assert expected_default in logged_item
        if 'some other msg 2' in logged_item:
            assert other_expected_default in logged_item


def test_get_thread_color():
    logger, handler, formatter = setup_logger(color_groups=[('name', ['name', 'message']),
                                                            ('thread', ['thread']),
                                                            ('levelname', ['levelname', 'levelno'])],
                                              auto_color=True,
                                              fmt='levelname=%(levelname)s tid=%(thread)d tname=%(threadName)s pid=%(process)d proccess=%(processName)s name=%(name)s message=%(message)s')

    logger.debug('foo%s', 'blip')

    def log_from_thread(msg):
        logger.debug('thread debug: %s', msg)
        logger.info('thread info: %s', msg)
        logger.warning('thread warning: %s', msg)

    # log some stuff from a thread
    some_thread = threading.Thread(target=log_from_thread,
                            args=('msg from some thread #%s' % '1SomeThread',))
    some_thread.daemon = True
    some_thread.start()

    logger.debug('from main sssssssss')

    some_thread.join()

    logger.debug('after thread join')

    for record in handler.record_buf:
        # The _cdl_* attrs should NOT be set on the record now
        assert not hasattr(record, '_cdl_name')

    for logged_item in handler.buf:
        # the expected rendered output include term escape codes
        # expected_levelname = 'levelname=\x1b[38;5;99mDEBUG\x1b[38;5;99m'
        # expected_message = 'message=\x1b[38;5;99mfooblip\x1b[38;5;99m\x1b[0m'
        testlog.debug('logged_item: %s', logged_item)
        # assert expected_levelname in logged_item
        # assert 'name=tests.test_color_bucket_logger.test_logger' in logged_item
        assert '=\x1b[38;5;70mtests.test_color_bucket_logger.test_logger' in logged_item
        # assert expected_message in logged_item


def break_stuff():
    37 / 0


def test_exception_formatter():
    logger, handler, formatter = setup_logger(color_groups=[('name', ['name', 'message']),
                                                            ('thread', ['thread']),
                                                            ('levelname', ['levelname', 'levelno'])],
                                              auto_color=True,
                                              fmt='levelname=%(levelname)s tid=%(thread)d tname=%(threadName)s pid=%(process)d proccess=%(processName)s name=%(name)s message=%(message)s')

    logger.debug('test_exception_formatter')

    try:
        break_stuff()
    except ZeroDivisionError as exc:
        logger.error('Hit an exception, 37/0 isnt ok I suppose')
        logger.exception(exc)

    for record in handler.record_buf:
        # The _cdl_* attrs should NOT be set on the record now
        assert not hasattr(record, '_cdl_name')

    for logged_item in handler.buf:
        testlog.debug('logged_item: %s', logged_item)
        assert '=\x1b[38;5;70mtests.test_color_bucket_logger.test_logger' in logged_item


def test_created_time():
    # teardown_config()
    logger, handler, formatter = setup_logger(
                                              auto_color=True,
                                              fmt='created=%(created)f rel=%(relativeCreated)d levelname=%(levelname)s name=%(name)s message=%(message)s')

    logger.debug('test created time')
    logger.debug('a little bit latter')

    for logged_item in handler.buf:
        testlog.debug('logged_item: %s', logged_item)
        assert 'created=' in logged_item
        assert 'rel='in logged_item


def test_extra_attrs():
    logger, handler, formatter = setup_logger(
                                              auto_color=True,
                                              fmt='levelname=%(levelname)s name=%(name)s an_extra=%(an_extra)s message=%(message)s')

    logger.debug('test non default args', extra={'an_extra': 'eggggstra'})

    for logged_item in handler.buf:
        testlog.debug('logged_item: %s', logged_item)
        assert 'an_extra=' in logged_item
        assert 'eggggstra'in logged_item

@pytest.fixture(params=[color_bucket_logger.ColorFormatter,
                        color_bucket_logger.TermFormatter])
def formatter_class(request):
    # _config()
    return request.param


def test_stuff(formatter_class):
    teardown_config()
    logging_tree.printout()

    # All of the default log record attributes
    fmt_string = 'logger %(levelname)s %(asctime)s %(created)f %(msecs)d %(relativeCreated)d %(filename)s %(funcName)s ' + \
        '%(levelno)s %(module)s %(pathname)s %(process)d %(processName)s' + \
        '%(thread)d %(threadName)s %(name)s %(message)s'
    logger, handler, formatter = setup_logger(color_groups=[('name', ['name', 'levelname'])],
                                              fmt=fmt_string,
                                              auto_color=True,
                                              formatter_class=formatter_class)

    sfmt = 'slogger %(levelname)s %(filename)s %(process)d' + \
        '%(thread)d %(name)s %(message)s'
    slogger, shandler, formatter = setup_logger(color_groups=[('name', ['name', 'message']),
                                                              ('thread', ['process', 'filename'])],
                                                fmt=sfmt,
                                                auto_color=False,
                                                formatter_class=formatter_class)

    logging_tree.printout()

    logger.debug('D: %s', '_debug')
    logger.info('I: %s', '_info')
    logger.warning('W: %s', '_warn')

    slogger.debug('foo1')
    slogger.info('foo2')
    slogger.error('foo4')

#    for record in handler.record_buf:
#        print(record.message)

    for logged_item in handler.buf:
        sys.stdout.write('%s\n' % logged_item)

    for logged_item in shandler.buf:
        sys.stdout.write('%s\n' % logged_item)


def test_color_formatter_empty_init(response):
    """Just init the class"""
    formatter = color_bucket_logger.ColorFormatter()
    assert isinstance(formatter, color_bucket_logger.ColorFormatter)


def test_term_formatter_empty_init(response):
    """Just init the class"""
    formatter = color_bucket_logger.TermFormatter()
    assert isinstance(formatter, color_bucket_logger.TermFormatter)


def test_null_handler(response):
    nh = NullHandler()
    formatter = color_bucket_logger.ColorFormatter()
    nh.setFormatter(formatter)
