import logging
import threading

flog = logging.getLogger('foo')
blog = logging.getLogger('bar')
blog.setLevel(logging.DEBUG)

# import logging_tree
# logging_tree.printout()


class ExampleException(Exception):
    pass


def log_stuff():
    flog.debug('First debug message')
    flog.info('fi')
    flog.warn('Some warning')
    flog.warn('Some warning')

    blog.warn('Some warning')
    blog.debug('First debug message')
    blog.debug('Second debug message')

    blog.debug('A debug message')


def log_more_stuff():
    flog.warn('Some warning')
    flog.warn('Some warning')
    blog.warn('Some warning')

    # use the root logger
    logging.debug('A debug message')


def log_thread_msg(thread_msg):
    flog.warn(thread_msg)
    blog.info(thread_msg)
    logging.debug(thread_msg)


# to test nested exceptions, esp on py3
def throw_deep_exc(msg=None):
    try:
        try:
            37 / 0
        except ZeroDivisionError as outer_e:
            flog.exception(outer_e)
            try:
                doesnt_exist.append(1)  # noqa
            except NameError as inner_e:
                flog.exception(inner_e)
                raise ExampleException(msg)
    except Exception as e:
        flog.exception(e)
        blog.exception(e)


def gen_log_events(thread_msg=None):
    log_stuff()

    log_more_stuff()

    # Generate log messages that reference the thread we expect it to come from
    log_thread_msg(thread_msg)

    throw_deep_exc('This example is raise as an example of log.exception() handling')

    log_more_stuff()


def run():
    import logging_tree
    logging_tree.printout()

    gen_log_events()


def run_threaded(thread_count=2):
    threads = []
    thread_time_increment = 0.001  # seconds
    main_thread = threading.currentThread()

    for i in range(thread_count):
        interval = thread_time_increment * i
        # interval = 0
        t = threading.Timer(interval=interval,
                            function=gen_log_events,
                            # Timers use auto created threadname 'Thread-$count', where count starts at 1,
                            # hence the +1 here.
                            args=('msg from thread #%s' % (i + 1,),))
        # An example of threads where they have a vague unuseful threadName
        # For ex, when there are 10 threads all named 'helper'
        named_thread = threading.Thread(target=gen_log_events, name='VagueThreadName',
                             args=('msg from vague thread #%s' % i,))
        threads.append(t)
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
