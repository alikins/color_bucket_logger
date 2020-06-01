"""The logging Formatters
"""

import logging
import re

from . import term_mapper
from . import styles

DEFAULT_FORMAT = ("""%(asctime)-15s"""
                  """ %(levelname)-0.1s"""
                  # If log records are coming from multiproceses into a single handler (say, via a multiprocess queue
                  # based handler), it is useful to see the process info with a different color per process.
                  # Assume we only need 3 digits for worker process number, if you see this wrap, but the '-4s' below
                  # to '-5s'. This is fixed width just to make the results easier to read for the normal case
                  # (everything before 'name' should be the same width for each log item show...)
                  # """ %(processName)-4s %(_cdl_process)spid=%(process)-5d%(_cdl_unset)s"""
                  """ %(processName)-4s pid=%(process)-5d"""
                  # truncate thread name to 2 chars, we use 2char names or the process filter does MainThread/MT elsewhere
                  """ %(threadName)-2s"""
                  # """ %(thread)d"""
                  # """[tid: \033[32m%(thread)d$RESET tname:\033[32m%(threadName)s]$RESET """
                  """ %(name)s"""
                  """ """
                  """%(funcName)s"""
                  """ """
                  """%(filename)s"""
                  """ """
                  """%(lineno)d"""
                  """ - %(message)s""")
#                  """%(_cdl_reset)s""")


def find_format_attrs(format_string):
    attrs_re_string = r"(?P<full_attr>%\((?P<attr_name>" + r'.*' + r"?)\).*?[dsf])"

    attrs_re = re.compile(attrs_re_string)
    format_attrs = attrs_re.findall(format_string)

    return format_attrs


# TODO: If there are common fields that should not default to None,
#       add them here
def default_attr_value(attr):
    if attr == 'stack_depth':
        return ''
    return None


# This could just return a dict of default values instead of
# modifying the record.
def get_default_record_attrs(record_context, attr_list):
    """Add default values to a log record_context for each attr in attr_list

    Return a dict of {record_attr_name: some_default_value}.
    For example, a record_context with no 'stack_info' item would cause
    the return to be {'stack_info': None}.

    For now, the default value is always None."""

    defaults_for_attrs = {}
    for attr in attr_list:
        if attr not in record_context:
            defaults_for_attrs[attr] = default_attr_value(attr)
    return defaults_for_attrs


class ColorFormatter(logging.Formatter):
    """Base color bucket formatter"""

    def __init__(self, fmt=None, default_color_by_attr=None,
                 color_groups=None, auto_color=False, datefmt=None, style=None):
        fmt = fmt or DEFAULT_FORMAT
        kwargs = dict(fmt=fmt, datefmt=datefmt)

        # py2 logging.Formatter will error on a 'style' keyword of course,
        # but it's needed for py3.
        # TODO: Unless we stop using the logging.Formatter base class at all, which
        #       may be more reasonable at this point.
        if style:
            kwargs['style'] = style
        logging.Formatter.__init__(self, **kwargs)

        # assue % style if not specified. py2 will not specifiy
        style_name = style or '%'

        # Override the 'style' set in logging.Formatter.__init__ (for py3)
        self._style = styles._STYLES[style_name][0](fmt)
        self._base_fmt = fmt

        self.color_groups = color_groups or []

        # TODO: be able to set the default color by attr name. Ie, make a record default to the thread or processName
        # self.default_color_by_attr = default_color_by_attr or 'process'
        # the name of the record attribute to check for a default color
        # self.default_attr_string = '_cdl_%s' % self.default_color_by_attr

        self.color_mapper = term_mapper.TermColorMapper(fmt=self._base_fmt,
                                                        default_color_by_attr=default_color_by_attr,
                                                        color_groups=self.color_groups,
                                                        format_attrs=self._style._format_attrs,
                                                        auto_color=auto_color)

    def __repr__(self):
        buf = '%s(fmt="%s", datefmt="%s", auto_color=%s, color_mapper.default_color_by_attr=%s)' % \
            (self.__class__.__name__,
             self._base_fmt,
             self.datefmt,
             self.color_mapper.auto_color,
             self.color_mapper.default_color_by_attr)
        return buf

    def _pre_format(self, record):
        '''Render time and exception info to be a string

        Modifies :py:class:`logging.LogRecord` record by side effect, updating asctime, exc_text attrs.'''
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        record.exc_text_sep = '\n'
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
            record.exc_text_sep = '\n'

    def _format_exception(self, record_context):
        exc_text_post = '%(exc_text_sep)s%(_cdl_exc_text)s%(exc_text)s%(_cdl_reset)s%(exc_text_sep)s' % record_context

        return exc_text_post

    # format is based on from stdlib python logging.LogFormatter.format()
    # It's kind of a pain to customize exception formatting, since it
    # just appends the exception string from formatException() to the formatted message.
    def format(self, record):
        self._pre_format(record)

        # Create a context dict of the log records attributes (the __dict__ of
        # the LogRecord() plus all of the color map items from the 'colors' dict.
        # This avoids having to modify the LogRecord() instance in place.
        record_context = {}
        record_context.update(record.__dict__)

        # 'stack_info' attr always added for py2/py3 compat
        new_defaults_for_attrs = get_default_record_attrs(record_context, ['stack_info'] + [x[1] for x in self._style._format_attrs])
        record_context.update(new_defaults_for_attrs)

        # Need the pre color rendered message early so we can use it as a color group
        record_context['_cdl_xmessage'] = record.getMessage()

        # Figure out what each log records color will be and return
        # a dict key'ed by a string of form '%_cdl_' + the log record attr name
        colors = self.color_mapper.get_colors_for_record(record_context, self._style._format_attrs)

        record_context.update(colors)

        # Re render
        record_context['message'] = record.getMessage()

        # Format the main part of the log message first
        s = self._style._format(record_context)

        # Then append the formatted exception info if there is any
        if record_context.get('exc_text', None):
            s = s + self._format_exception(record_context)

            # 'logging' Formatter() nullifies record.exc_text after it is rendered
            # so duplicate here
            record.exc_text = None
        return s


class TermFormatter(ColorFormatter):
    """Formatter for terminals that colorizes attributes based on their value

    Parameters
    ----------
    fmt : str
        A :py:class:`logging.Formatter` style log format string
    default_color_by_attr : str, optional
        The name of the log record attribute whose color will
        used by default for other records if they do not have
        a color set (by either 'auto_color' or by 'color_groups')
    color_groups : iterable, optional
        Define when a attribute should use the same color as another attribute.

        For example, to make the 'processName' and 'message' attributes
        use the same color as 'process'.

        color_groups is a list of tuples. The first element of each
        tuple is the "leader" attribute, and the second element is
        a list of "follower" attributes.

        For the 'process' and 'processName' example::

            color_groups=[('process', ['processName', 'message']]
    auto_color : boolean, optional
        If true, automatically calculate and use colors for each attribute.
        Defaults to False
    datefmt : str, optional
        Date format string as used by :py:class:`logging.Formatter`
    """

    def __init__(self, fmt=None, default_color_by_attr=None,
                 color_groups=None, auto_color=False, datefmt=None,
                 color_mapper=None):

        super(TermFormatter, self).__init__(fmt=fmt,
                                            default_color_by_attr=default_color_by_attr,
                                            color_groups=color_groups,
                                            auto_color=auto_color,
                                            datefmt=datefmt)

        self.color_mapper = term_mapper.TermColorMapper(fmt=fmt,
                                                        default_color_by_attr=default_color_by_attr,
                                                        color_groups=color_groups,
                                                        format_attrs=self._style._format_attrs,
                                                        auto_color=auto_color)
