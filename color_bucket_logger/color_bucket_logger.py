
# TODO: add a Filter or LoggingAdapter that adds a record attribute for parent pid
#       (and maybe thread group/process group/cgroup ?)


# Example uses of color_groups
# color_groups = [
# color almost everything by logger name
#    ('name', ['filename', 'module', 'lineno', 'funcName', 'pathname']),
#    ('process', ['default', 'message']),
#    ('process', ['processName', 'process']),
#    ('thread', ['default', 'threadName', 'message', 'unset', 'processName', 'exc_text']),
#    ('thread', ['threadName', 'thread']),
#
# color logger name, filename and lineno same as the funcName
#   ('funcName', ['default', 'message', 'unset', 'name', 'filename', 'lineno']),
# color message same as debug level
#   ('levelname', ['levelname', 'levelno']),
#
# color funcName, filename, lineno same as logger name
#   ('name', ['funcName', 'filename', 'lineno']),
#
#   ('time_color', ['asctime', 'relativeCreated', 'created', 'msecs']),
#   ('task', ['task_uuid', 'task']),
# color message and default same as funcName
#   ('funcName', ['message', 'unset'])
#
#   ('funcName', ['relativeCreated', 'asctime'])
#
# color default, msg and playbook/play/task by the play
#   ('play', ['default','message', 'unset', 'play', 'task']),
# ]
