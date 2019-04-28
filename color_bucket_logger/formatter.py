import logging
import re

from . import term_mapper

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


def context_color_format_string(format_string, format_attrs):
    '''For extending a format string for logging.Formatter to include attributes with color info.

    ie, '%(process)d %(threadName)s - %(msg)'

    becomes

    '%(_cdl_process)s%(process)d%(_cdl_reset)s %(_cdl_threadName)%(threadName)s%(_cdl_reset)s - %(msg)'

    Note that adding those log record attributes is left to... <FIXME>.
    '''
    format_attrs = find_format_attrs(format_string)
    # TODO: pass in a list of record/logFormatter attributes to be wrapped for colorization

    color_attrs_string = '|'.join([x[1] for x in format_attrs])

    # This looks for log format strings like '%(threadName)s' or '$(process)d, and replaces
    # the format specifier with a version wrapped with log record color attributes.
    #
    # For ex, '%(threadName)s'  -> %(_cdl_threadName)s%(threadName)s%(cdl_reset)
    #
    # When ColorFormatter.format() is called on a LogRecord, this is equilivent to
    # calling 'log_format_string % log_record.__dict__', and uses the normal (but 'old school')
    # string formatting (ie, %s style). 'threadName' is populated automatically by a logging.Logger() class on .log(),
    # but the custom fields like %(_cdl_threadName)s need to be added to the log record
    # we pass to ColorFormatter.format()
    #
    # ColorFormatter.format() actually does this itself, but those attributes could be set else
    # via a logger, a log adapter, a logging Filter attached to the logger, a filter attached
    # to a logging.Handler, or by a logging handler itself. Since our attributes are purely for
    # formatting, we just do it in the ColorFormatter.format()
    # https://docs.python.org/2/library/logging.html#logrecord-attributes
    #
    # THe captured groups 'full_attr' is the entire record attribute from the string, including
    # string formatting/precsion, and padding info. ie '%(process)-10d' is a process pid right justified with
    # a max length of 10 chars.
    #
    # The capture 'attr_name' is just the name of the attr, 'process' or 'message' or 'levelname' for ex. This
    # is extract so it can be used in the name of the color debug logger attribute that will set the color info
    # For '%(process)-10d', that would make 'process' the attr_name, and the color attribute '%(_cdl_process)'
    # color_attrs_string is a sub regex of the attr names to be given color using the re alternate '|' notation.
    re_string = r"(?P<full_attr>%\((?P<attr_name>" + color_attrs_string + r"?)\).*?[dsf])"

    color_format_re = re.compile(re_string)

    replacement = r"%(_cdl_\g<attr_name>)s\g<full_attr>%(_cdl_unset)s"

    # likely needs thread locking
    # exc_info_post = '%(exc_text_sep)s%(exc_text)s%(exc_text_sep)s'
    # format_string = '%s%s' % (format_string, exc_info_post)

    # for match in format_attrs.groups():
    #    print('match: %s' % match)

    format_string2 = color_format_re.sub(replacement, format_string)

    # set the default color at the begining of the format string and add a reset to the end
    format_string = r"%(_cdl_default)s" + format_string2 + r"%(_cdl_reset)s"

    return format_string


def add_default_record_attrs(record, attr_list):
    for attr in attr_list:
        if not hasattr(record, attr):
            setattr(record, attr, None)
    return record


def _apply_colors_to_record(record, colors):
    '''modify LogRecord in place (as side effect) adding _cdl_* attributes'''
    # apply the colors
    for cdl_name, color_value in colors.items():

        # FIXME: revisit setting default idx to a color based on string
        # if cdl_idx == self.DEFAULT_COLOR_IDX:
        #    cdl_idx = _color_by_attr_index

        # FIXME:
        setattr(record, cdl_name, color_value)


class ColorFormatter(logging.Formatter):
    # A little weird...
    @property
    def color_fmt(self):
        if not self._color_fmt:
            self._color_fmt = context_color_format_string(self._base_fmt, self._format_attrs)
        return self._color_fmt

    def __init__(self, fmt=None, default_color_by_attr=None,
                 color_groups=None, auto_color=False, datefmt=None):
        fmt = fmt or DEFAULT_FORMAT
        logging.Formatter.__init__(self, fmt, datefmt=datefmt)
        self._base_fmt = fmt
        self._color_fmt = None

        self._format_attrs = find_format_attrs(self._base_fmt)

        self.color_groups = color_groups or []

        # TODO: be able to set the default color by attr name. Ie, make a record default to the thread or processName
        # self.default_color_by_attr = default_color_by_attr or 'process'
        # the name of the record attribute to check for a default color
        # self.default_attr_string = '_cdl_%s' % self.default_color_by_attr

        self.color_mapper = term_mapper.TermColorMapper(fmt=self._base_fmt,
                                            default_color_by_attr=default_color_by_attr,
                                            color_groups=self.color_groups,
                                            format_attrs=self._format_attrs,
                                            auto_color=auto_color)

    def __repr__(self):
        buf = 'ColorFormatter(fmt="%s", datefmt="%s", auto_color=%s)' % (self._base_fmt,
                                                                         self.datefmt,
                                                                         self.color_mapper.auto_color)
        return buf

    def _pre_format(self, record):
        '''render time and exception info to be a string

        Modifies record by side effect.'''
        # import pprint
        # pprint.pprint(record.__dict__)
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        record.exc_text_sep = '\n'
        # record.exc_text = ''
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

        # for py3.2+ compat
        record = add_default_record_attrs(record, ['stack_info'])
        if not hasattr(record, 'stack_depth'):
            setattr(record, 'stack_depth', '')

        # Figure out what each log records color will be and return
        # a dict key'ed by a string of form '%_cdl_' + the log record attr name
        colors = self.color_mapper.get_colors_for_record(record)

        # _apply_colors_to_record(record, colors)

        # Create a context dict of the log records attributes (the __dict__ of
        # the LogRecord() plus all of the color map items from the 'colors' dict.
        # This avoids having to modify the LogRecord() instance in place.
        record_context = {}
        record_context.update(record.__dict__)
        record_context.update(colors)
        record_context['message'] = record.getMessage()

        # Format the main part of the log message first
        s = self._format(record, record_context)

        # Then append the formatted exception info if there is any
        if record_context.get('exc_text', None):
            s = s + self._format_exception(record_context)

            # 'logging' Formatter() nullifies record.exc_text after it is rendered
            # so duplicate here
            record.exc_text = None
        return s

    # Note that self._format here is more or less the same as py3's Formatter.formatMessage()
    # and self.color_fmt is similar to py3's Formatter._style, but neither are used here
    # for py2 compat.
    def _format(self, record, record_context):

        # record.message = record.getMessage()

        # s = self.color_fmt % record.__dict__
        s = self.color_fmt % record_context
        return s
