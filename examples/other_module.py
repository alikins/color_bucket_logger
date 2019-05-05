
import logging
log = logging.getLogger(__name__)

log.info('foo bar mod scope%s %s', 'aaa', 'bbb')


def func3():
    log.warning('func3 warning dfdfd')
