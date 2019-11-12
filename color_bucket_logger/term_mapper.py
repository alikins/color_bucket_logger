from . import mapper
from . import term_colors


class TermColorMapper(mapper.BaseColorMapper):
    #: A fixed map of logging level to color used by the
    #: default get_level_color()
    LEVEL_COLORS = {'TRACE': term_colors.BLUE,
                    'SUBDEBUG': term_colors.BLUE,
                    'DEBUG': term_colors.BLUE,
                    'INFO': term_colors.GREEN,
                    'SUBWARNING': term_colors.YELLOW,
                    'WARNING': term_colors.YELLOW,
                    'ERROR': term_colors.RED,
                    # bold red?
                    'CRITICAL': term_colors.RED}

    NUMBER_OF_COLORS = term_colors.NUMBER_OF_ALL_COLORS

    # TODO: tie tid/threadName and process/processName together so they start same color
    #       so MainProcess, the first pid/processName are same, and maybe MainThread//first tid
    # DOWNSIDE: requires tracking all seen pid/process/tid/threadName ? that could be odd with multi-processes with multi instances
    #           of the Formatter
    # TODO: make so a given first ProcessName will always start the same color (so multiple runs are consistent)
    # TODO: make 'msg' use the most specific combo of pid/processName/tid/threadName
    # TODO: generalize so it will for logger name as well
    # MAYBE: color hiearchy for logger names? so 'foo.model' and 'foo.util' are related...
    #        maybe split on '.' and set initial color based on hash of sub logger name?
    # SEEALSO: chromalog module does something similar, may be easiest to extend
    # TODO: this could be own class/methods like ContextColor(log_record) that returns color info
    def get_thread_color(self, threadid):
        """Calculate the color index for a threadid (tid) number

        Parameters
        ----------
        threadid : int
            The value of the LogRecord.threadid attribute (the tid)

        Returns
        -------
        int
        The color index to use
        """

        # 220 is useable 256 color term color (forget where that comes from? some min delta-e division of 8x8x8 rgb colorspace?)
        thread_mod = threadid % self.NUMBER_OF_COLORS
        return thread_mod + term_colors.RGB_COLOR_OFFSET

    # TODO: This could special case 'MainThread'/'MainProcess' to pick a good predictable color
    def get_name_color(self, name, perturb=None):
        perturb = perturb or ''
        # perturb = 'dsfadddddd'

        name = '%s%s' % (name, perturb)

        name_hash = sum([ord(x) for x in name])
        name_mod = name_hash % self.NUMBER_OF_COLORS
        return name_mod + term_colors.RGB_COLOR_OFFSET

    def get_level_color(self, levelname, levelno):
        level_color = self.LEVEL_COLORS.get(levelname, None)
        if not level_color:
            level_color = self.LEVEL_COLORS.get(levelno, self.default_color)
        return level_color

    def get_process_colors(self, record_context):
        """Given process/thread info, return reasonable colors for them.

        Roughly:

            - attempts to get a unique color per 'processName'
            - attempts to get a unique color per 'process' (pid)
                - attempt to make those the same for "MainProcess"
                - for any other 'processName', the pname color and the pid color can be different
            - if 'threadName' is "MainThread", make tname_color and tid_color match "MainProcess" pname_color and pid_color
            - other 'threadName' values get a new color and new tid_color

        Notes
        -----
            This doesn't track any state so there is no ordering or prefence to the colors given out.

        Parameters
        ----------
        record_context : :py:class:`dict`
            The log record_context to calculate process colors for

        Returns
        -------
        int, int, int, int
            The color indexes for 'processName', 'process', 'threadName', and 'thread'
        """

        pname = record_context['processName']
        pid = record_context['process']
        tname = record_context['threadName']
        tid = record_context['thread']

        # 'pname' is almost always 'MainProcess' which ends up a ugly yellow. perturb is here to change the color
        # that 'MainProcess' ends up to a nicer light green
        perturb = 'pseudoenthusiastically'

        # combine pid+pname otherwise, all MainProcess will get the same pname
        pid_label = '%s%s' % (pname, pid)
        pname_color = self.get_name_color(pid_label, perturb=perturb)

        if pname == 'MainProcess':
            pid_color = pname_color
        else:
            pid_color = self.get_thread_color(pid)

        if tname == 'MainThread':
            # tname_color = pname_color
            tname_color = pid_color
            tid_color = tname_color
        else:
            tname_color = self.get_name_color(tname)
            tid_color = self.get_thread_color(tid)

        return pname_color, pid_color, tname_color, tid_color

    # TODO: maybe add a Filter that sets a record attribute for process/pid/thread/tid color that formatter would use
    #       (that would let formatter string do '%(theadNameColor)s tname=%(threadName)s %(reset)s %(processColor)s pid=%(process)d%(reset)s'
    #       so that the entire blurb about process info matches instead of just the attribute
    #       - also allows format to just expand a '%(threadName)s' in fmt string to '%(theadNameColor)s%(threadName)s%(reset)s' before regular formatter
    # DOWNSIDE: Filter would need to be attach to the Logger not the Handler
    # def add_color_attrs_to_record(self, record):
    def get_colors_for_record(self, record_context, format_attrs):
        """For a  record_context dict, compute color for each field and return a color dict"""

        _default_color_index = term_colors.DEFAULT_COLOR_IDX
        _color_by_attr_index = _default_color_index
        # 'cdl' is 'context debug logger'. Mostly just an unlikely record name to avod name collisions.
        colors = {'_cdl_default': _default_color_index,
                  '_cdl_unset': _default_color_index,
                  '_cdl_reset': term_colors.RESET_SEQ_IDX}

        # custom_mapppers = levelno, levelno

        # populate the record with values for any _cdl_* attrs we will use
        # could be format_attrs (actually used in format string) + any referenced as color_group keys
        group_by_attrs = [y[0] for y in self.group_by]

        record_format_attrs = [z[1] for z in format_attrs] + ['exc_text']

        # attrs_needing_default = self.default_record_attrs + self.custom_record_attrs
        attrs_needed = group_by_attrs + record_format_attrs
        for attr_needed in attrs_needed:
            cdl_name = '_cdl_%s' % attr_needed
            colors[cdl_name] = _default_color_index

        use_level_color = 'levelname' in group_by_attrs or 'levelno' in group_by_attrs
        # NOTE: the impl here is based on info from justthe LogRecord and should be okay across threads
        #       If this wants to use more global data, beware...
        if use_level_color:
            level_color = self.get_level_color(record_context['levelname'], record_context['levelno'])
            colors['_cdl_levelname'] = level_color

        # set a different color for each logger name. And by default, make filename, funcName, and lineno match.
        use_name_color = 'name' in group_by_attrs or self.auto_color
        if use_name_color:
            module_and_method_color = self.get_name_color(record_context['name'])
            colors['_cdl_name'] = module_and_method_color
            # group mapping should take care of the rest of these once _cdl_name is set

        use_thread_color = False
        for attr in ['process', 'processName', 'thread', 'threadName']:
            if attr in group_by_attrs:
                use_thread_color = True

        if use_thread_color or self.auto_color:
            pname_color, pid_color, tname_color, tid_color = self.get_process_colors(record_context)

            colors['_cdl_process'] = pid_color
            colors['_cdl_processName'] = pname_color
            colors['_cdl_thread'] = tid_color
            colors['_cdl_threadName'] = tname_color
            colors['_cdl_exc_text'] = tid_color

        # fields we don't need to calculate indiv, since they will be a different group
        in_a_group = set()

        # find the color for any group keys before setting colors for group members
        # TODO: extend group keys to let them be tuples
        #       to allow (name, funcName) to get a color for module.function() instead of two sep
        #       sim to module_and_method_color above
        for group in group_by_attrs:
            group_color = colors.get('_cdl_%s' % group, _default_color_index)
            if group in self.custom_attrs or group in in_a_group:
                continue

            # record.message isnt 'rendered' until after the format
            if group == 'message':
                color_idx = self.get_name_color(record_context['_cdl_xmessage'])
            else:
                # default to empty string for non existent record attributes ('extra', etc)
                color_idx = self.get_name_color(record_context.get('group', ''), 'sdsdf')
            colors['_cdl_%s' % group] = color_idx

        for group, members in self.group_by:
            group_color = colors.get('_cdl_%s' % group, _default_color_index)

            for member in members:
                colors['_cdl_%s' % member] = group_color
                if member == 'default':
                    self.default_color_by_attr = group
                    # _color_by_attr_index = colors.get('_cdl_%s' % group, _default_color_index)
                    # _color_by_attr_index = colors[default_attr_string]
                in_a_group.add(member)

        # for everything else, use the name/string to get a color if auto_colors is True
        for needed_attr in attrs_needed:
            if needed_attr in self.custom_attrs or needed_attr in in_a_group \
                    or needed_attr in self.high_cardinality or not self.auto_color:
                continue
            color_idx = self.get_name_color(record_context.get(needed_attr, ''))
            colors['_cdl_%s' % needed_attr] = color_idx

        # set the default color based on computed values, lookup the color
        # mapped to the attr default_color_by_attr  (ie, if 'process', lookup
        # record._cdl_process and set self.default_color to that value
        default_attr_string = '_cdl_%s' % self.default_color_by_attr
        _color_by_attr_index = colors[default_attr_string]

        name_to_color_map = {}
        for cdl_name, cdl_idx in colors.items():
            # FIXME: revisit setting default idx to a color based on string
            if cdl_idx == term_colors.DEFAULT_COLOR_IDX:
                cdl_idx = _color_by_attr_index
            name_to_color_map[cdl_name] = term_colors.ALL_COLORS[cdl_idx]
        return name_to_color_map
