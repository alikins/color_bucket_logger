# From https://github.com/python/cpython/blob/master/Lib/logging/__init__.py
# https://github.com/python/cpython/commit/cb65b3a4f484ce71dcb76a918af98c7015513025
# (git master branch post 3.8)
# Copyright 2001-2019 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.

import logging
import re
from string import Template
from string import Formatter as StrFormatter

log = logging.getLogger(__name__)
_str_formatter = StrFormatter()


class PercentStyle(object):

    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'
    validation_pattern = re.compile(r'%\(\w+\)[#0+ -]*(\*|\d+)?(\.(\*|\d+))?[diouxefgcrsa%]', re.I)

    attrs_pattern_str = r'(?P<full_attr>%\((?P<attr_name>.*?)\).*?[dsf])'
    attrs_pattern = re.compile(attrs_pattern_str)

    named_fields_pattern = r'''(?P<full_attr>%\((?P<attr_name>.*?)\)(?P<conversion_flag>[#0+ -]*)(?P<field_width>\*|\d+)?(?P<precision>\.(\*|\d+))?(?P<conversion_type>[diouxefgcrsa%]))'''

    def __init__(self, fmt):
        self._fmt = fmt or self.default_format

        self._base_fmt = self._fmt
        self._color_fmt = None
        self._format_attrs = self.find_format_attrs(self._base_fmt)

    def context_color_format_string(self, format_string, format_attrs):
        """For extending a format string for :py:class:`logging.Formatter` to include attributes with color info.

        ie::

            '%(process)d %(threadName)s - %(msg)'

        becomes::

            '%(_cdl_process)s%(process)d%(_cdl_reset)s %(_cdl_threadName)%(threadName)s%(_cdl_reset)s - %(msg)'
        """

        format_attrs = self.find_format_attrs(format_string)

        color_attrs_string = '|'.join([x[1] for x in format_attrs])

        # This looks for log format strings like '%(threadName)s' or '%(process)d, and replaces
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

        format_string2 = color_format_re.sub(replacement, format_string)

        # set the default color at the begining of the format string and add a reset to the end
        format_string = r"%(_cdl_default)s" + format_string2 + r"%(_cdl_reset)s"

        return format_string

    @property
    def color_fmt(self):
        if not self._color_fmt:
            self._color_fmt = self.context_color_format_string(self._base_fmt, self._format_attrs)
        return self._color_fmt

    def usesTime(self):
        return self._fmt.find(self.asctime_search) >= 0

    def validate(self):
        """Validate the input format, ensure it matches the correct style"""
        if not self.validation_pattern.search(self._fmt):
            raise ValueError("Invalid format '%s' for '%s' style" % (self._fmt, self.default_format[0]))

    def _format(self, record_context):
        return self.color_fmt % record_context

    def format(self, record):
        try:
            return self._format(record)
        except KeyError as e:
            raise ValueError('Formatting field not found in record: %s' % e)

    def find_format_attrs(self, format_string):
        format_attrs = self.attrs_pattern.findall(format_string)

        return format_attrs


# TODO: rename, and/or subclass the py3 classes
class StrFormatStyle(PercentStyle):
    default_format = '{message}'
    asctime_format = '{asctime}'
    asctime_search = '{asctime'

    fmt_spec = re.compile(r'^(.?[<>=^])?[+ -]?#?0?(\d+|{\w+})?[,_]?(\.(\d+|{\w+}))?[bcdefgnosx%]?$', re.I)
    field_spec = re.compile(r'^(\d+|\w+)(\.\w+|\[[^]]+\])*$')

    uber_format_pattern = r'(?P<full_attr>{(?P<attr_name>\d+|\w+)[:]?' + \
                        r'(?P<modifiers>(?P<align>.?[<>=^]?)(?P<sign>[+ -]?)' + \
                        r'#?0?(?P<width>\d+|{\w+})?[,_]?(\.(\d+|{\w+}))?' + \
                        r'(?P<conversion_type>[bcdefgnosx%])?)})'

    def find_format_attrs(self, format_string):
        attrs_pattern = re.compile(self.uber_format_pattern)

        format_attrs = attrs_pattern.findall(format_string)
        return format_attrs

    def context_color_format_string(self, format_string, format_attrs):
        format_attrs = self.find_format_attrs(format_string)

        color_attrs_string = '|'.join([x[1] for x in format_attrs])

        # See notes for PercentStyle
        re_string = r"(?P<full_attr>{(?P<attr_name>" + color_attrs_string + r")(:[=+<\d]+[dsf]?)?})+"

        color_format_re = re.compile(re_string)

        replacement = r"{_cdl_\g<attr_name>}\g<full_attr>{_cdl_unset}"

        format_string2 = color_format_re.sub(replacement, format_string)

        # set the default color at the begining of the format string and add a reset to the end
        format_string = r"{_cdl_default}" + format_string2 + r"{_cdl_reset}"

        return format_string

    def _format(self, record_context):
        return self.color_fmt.format(**record_context)

    def validate(self):
        """Validate the input format, ensure it is the correct string formatting style"""
        fields = set()
        try:
            for _, fieldname, spec, conversion in _str_formatter.parse(self._fmt):
                if fieldname:
                    if not self.field_spec.match(fieldname):
                        raise ValueError('invalid field name/expression: %r' % fieldname)
                    fields.add(fieldname)
                if conversion and conversion not in 'rsa':
                    raise ValueError('invalid conversion: %r' % conversion)
                if spec and not self.fmt_spec.match(spec):
                    raise ValueError('bad specifier: %r' % spec)
        except ValueError as e:
            raise ValueError('invalid format: %s' % e)
        if not fields:
            raise ValueError('invalid format: no fields')


class StringTemplateStyle(PercentStyle):
    default_format = '${message}'
    asctime_format = '${asctime}'
    asctime_search = '${asctime}'

    def __init__(self, fmt):
        self._fmt = fmt or self.default_format
        self._tpl = Template(self._fmt)

    def usesTime(self):
        fmt = self._fmt
        return fmt.find('$asctime') >= 0 or fmt.find(self.asctime_format) >= 0

    def validate(self):
        pattern = Template.pattern
        fields = set()
        for m in pattern.finditer(self._fmt):
            d = m.groupdict()
            if d['named']:
                fields.add(d['named'])
            elif d['braced']:
                fields.add(d['braced'])
            elif m.group(0) == '$':
                raise ValueError('invalid format: bare \'$\' not allowed')
        if not fields:
            raise ValueError('invalid format: no fields')

    def _format(self, record):
        return self._tpl.substitute(**record.__dict__)


BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"

_STYLES = {
    '%': (PercentStyle, BASIC_FORMAT),
    '{': (StrFormatStyle, '{levelname}:{name}:{message}'),
    '$': (StringTemplateStyle, '${levelname}:${name}:${message}'),
}
