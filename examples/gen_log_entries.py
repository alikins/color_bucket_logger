import logging


flog = logging.getLogger('foo')
blog = logging.getLogger('bar')
blog.setLevel(logging.DEBUG)

# import logging_tree
# logging_tree.printout()


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


def run():
    import logging_tree
    logging_tree.printout()

    log_stuff()

    log_more_stuff()
