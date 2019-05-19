
DEFAULT_COLOR_BY_ATTR = 'name'


class BaseColorMapper(object):
    # default_color_groups is:
    #  ('attr', list_of_attrs_to_use 'attr''s color
    default_color_groups = [
        # color almost everything by logger name
        # ('name', ['filename', 'module', 'lineno', 'funcName', 'pathname']),
        # ('process', ['processName', 'thread', 'threadName']),
        # ('_cdl_default', ['asctime']),
        # ('levelname', ['levelname', 'levelno'])
    ]
    # custom_attrs are attributes we have specific methods for finding instead of the
    # generic get_color_name. For ex, 'process' is found via get_process_color()
    custom_attrs = ['levelname', 'levelno', 'process', 'processName', 'thread', 'threadName', 'exc_text']
    high_cardinality = set(['asctime', 'created', 'msecs', 'relativeCreated', 'args', 'message'])

    def __init__(self, fmt=None, default_color_by_attr=None,
                 color_groups=None, format_attrs=None,
                 auto_color=False):
        self._fmt = fmt
        self.color_groups = color_groups or []

        self.group_by = []
        # self.group_by = self.default_color_groups[:]
        # self.group_by.extend(self.color_groups)
        # self.group_by = self.color_groups

        self.default_color_by_attr = default_color_by_attr or DEFAULT_COLOR_BY_ATTR
        self.default_attr_string = '_cdl_%s' % self.default_color_by_attr

        # make sure the defaut color attr is in the group_by list
        if self.default_color_by_attr:
            self.group_by.insert(0, (self.default_color_by_attr, [self.default_color_by_attr]))

        self.group_by.extend(self.color_groups)

        # self._format_attrs = format_attrs

        self.auto_color = auto_color
        # import pprint
        # pprint.pprint(('color_groups', color_groups))

    def get_thread_color(self, thread_id):
        '''return color idx for thread_id'''
        return 0

    def get_name_color(self, name, perturb=None):
        '''return color idx for 'name' string'''
        return 0

    def get_level_color(self, levelname, levelno):
        '''return color idx for logging levelname and levelno'''
        return 0

    def get_process_colors(self, record):
        '''return a tuple of pname_color, pid_color, tname_color, tid_color idx for process record'''
        return 0, 0, 0, 0
        # return pname_color, pid_color, tname_color, tid_color

    def get_colors_for_attr(self, record):
        return {}
