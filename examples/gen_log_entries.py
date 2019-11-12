import logging
import logging.config
import os
import signal
import threading
import uuid

import yaml

flog = logging.getLogger('foo')
blog = logging.getLogger('bar')
blog.setLevel(logging.DEBUG)

LOGGING_TREE = False
try:
    import logging_tree
    LOGGING_TREE = True
except ImportError:
    print("Could not import logging_tree, but thats ok")


class ExampleException(Exception):
    pass


def log_setup(log_config_file):

    with open(log_config_file, 'r') as log_config_fd:
        log_config = yaml.safe_load(log_config_fd)

    logging.config.dictConfig(log_config)


def show_setup():
    if not LOGGING_TREE:
        return

    if not os.environ.get('CBL_LOGGING_TREE'):
        return

    logging_tree.printout()


def log_stuff(extra=None):
    flog.debug('First debug message', extra=extra)
    flog.info('This is a record with format strings: %s', 'blip', extra=extra)
    flog.debug('This is a record with format strings: %s', 'baz', extra=extra)
    flog.warn('Some warning', extra=extra)
    flog.warn('Some warning', extra=extra)

    blog.warn('Some warning')
    blog.debug('First debug message')
    blog.debug('Second debug message', extra=extra)

    blog.debug('A debug message', extra=extra)


def log_more_stuff(extra=None):
    flog.warn('Some warning')
    flog.warn('Some warning', extra=extra)
    blog.warn('Some warning', extra=extra)

    # use the root logger
    logging.debug('A debug message', extra=extra)

    flog.critical('uh oh', extra=extra)


def log_thread_msg(thread_msg, extra=None):
    flog.warn(thread_msg, extra=extra)
    blog.info(thread_msg)
    logging.debug(thread_msg, extra=extra)


# to test nested exceptions, esp on py3
def throw_deep_exc(msg=None, extra=None):
    try:
        try:
            37 / 0
        except ZeroDivisionError as outer_e:
            flog.exception(outer_e, extra=extra)
            try:
                doesnt_exist.append(1)  # noqa
            except NameError as inner_e:
                flog.exception(inner_e, extra=extra)
                raise ExampleException(msg)
    except Exception as e:
        flog.exception(e, extra=extra)
        blog.exception(e, extra=extra)


def gen_log_events(thread_msg=None, throw_exc=False, stop_event=None):
    if stop_event and stop_event.isSet():
        return

    # time_low is just the first 32 bits of the uuid, close enough
    extra = {'tsx_id': uuid.uuid4().time_low}
    log_stuff(extra=extra)

    log_more_stuff(extra=extra)

    # Generate log messages that reference the thread we expect it to come from
    log_thread_msg(thread_msg, extra=extra)

    try:
        raise ExampleException('This is an expected example exception to demo log.exception()')
    except ExampleException as exc:
        flog.exception(exc, extra=extra)

    if throw_exc:
        throw_deep_exc('This example is raise as an example of log.exception() handling',
                       extra=extra)

    # a different tsx_id
    extra = {'tsx_id': uuid.uuid4().time_low}
    log_more_stuff(extra=extra)


def run(throw_exc=False):
    gen_log_events(thread_msg='Just the main thread', throw_exc=throw_exc)


def run_threaded(thread_count=2, throw_exc=False):
    threads = []
    timers = []
    thread_time_increment = 0.001  # seconds
    main_thread = threading.currentThread()

    stop_event = threading.Event()

    def fire_event(signum, frame):
        # logging.info(“Event fired”)
        stop_event.set()
        for timer in timers:
            timer.cancel()

    signal.signal(signal.SIGINT, fire_event)

    for i in range(thread_count):
        interval = thread_time_increment * i
        # interval = 0
        t = threading.Timer(interval=interval,
                            function=gen_log_events,
                            # Timers use auto created threadname 'Thread-$count', where count starts at 1,
                            # hence the +1 here.
                            args=('msg from thread #%s' % (i + 1,),
                                  throw_exc,
                                  stop_event))
        # An example of threads where they have a vague unuseful threadName
        # For ex, when there are 10 threads all named 'helper'
        named_thread = threading.Thread(target=gen_log_events, name='VagueThreadName',
                             args=('msg from vague thread #%s' % i, stop_event))
        timers.append(t)
        threads.append(named_thread)
        t.daemon = True
        named_thread.daemon = True
        t.start()
        named_thread.start()

    for t in threading.enumerate():
        if t is main_thread:
            continue
        # logging.debug('joining %s', t.getName())
        t.join()
