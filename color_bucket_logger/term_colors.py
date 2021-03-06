'''256 color terminal handling

ALL_COLORS is a dict mapping color indexes to the ANSI escape code.
ALL_COLORS is essentially a "palette".

Note that ALL_COLORS is a dict that (mostly) uses integers as the keys.
Yeah, that is weird. In theory, the keys could also be other identifiers,
although that isn't used much at the moment. So, yeah, could/should just
be a list/array.

Also note that the ordering of the color indexes is fairly arbitrary.
It mostly follows the order of the ANSI escape codes. But it is
important to note that the order doesn't mean much. For example,
the colors for index 154 and 155 may or may not be related in any way.

This module also defines some convience names for common keys of
ALL_COLORS.

The first 8 terminal colors:
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE

The terminal reset index:
    RESET_SEQ_INDEX

The default color index:
    DEFAULT_COLOR_IDX
'''

# hacky ansi color stuff
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

NUMBER_OF_BASE_COLORS = 8

ALL_COLORS = {}

# See https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit

#: Used to determine what color index we start from.
#:
#: The xterm256 color indexes are:
#:
#:   0-7 normal term colors
#:
#:   8-15 bright term colors
#:
#:   16-231 are the rest from a 6x6x6 (216 color) rgb cube
#:
#:   16, 17 are black and very dark blue so they are skipped since they are hard to read.
#:
#:   232-255 are the grays (white to gray to black) and are skipped and why END_OF_THREAD_COLORS is 231.
RGB_COLOR_OFFSET = 16 + 2

# FIXME: needs to learn to support dark/light themes
START_OF_THREAD_COLORS = RGB_COLOR_OFFSET
END_OF_THREAD_COLORS = 231
NUMBER_OF_THREAD_COLORS = END_OF_THREAD_COLORS - RGB_COLOR_OFFSET

BASE_COLORS = dict((color_number, color_seq) for
                   (color_number, color_seq) in [(x, "\033[38;5;%dm" % x) for x in range(NUMBER_OF_BASE_COLORS)])
# \ x 1 b [ 38 ; 5; 231m
THREAD_COLORS = dict((color_number, color_seq) for
                     (color_number, color_seq) in [(x, "\033[38;5;%dm" % x) for x in range(START_OF_THREAD_COLORS, END_OF_THREAD_COLORS)])

ALL_COLORS.update(BASE_COLORS)
ALL_COLORS.update(THREAD_COLORS)

#: The number of total colors when excluded and skipped colors
#: are considered. The color mappers use this to know what
#: number to modulus (%) by to figure out the color bucket.
NUMBER_OF_ALL_COLORS = len(ALL_COLORS) - RGB_COLOR_OFFSET

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = BASE_COLORS.keys()

#: Some named colors that map to the first 8 terminal colors
NAMED_COLOR_IDXS = {'BLACK': BLACK,
                    'RED': RED,
                    'GREEN': GREEN,
                    'YELLOW': YELLOW,
                    'BLUE': BLUE,
                    'MAGENTA': MAGENTA,
                    'CYAN': CYAN,
                    'WHITE': WHITE
                    }

#: The index for a 'reset'
RESET_SEQ_IDX = 256
ALL_COLORS[RESET_SEQ_IDX] = RESET_SEQ

#: The index for the default 'default' color
DEFAULT_COLOR_IDX = 257

#: The default color (white)
DEFAULT_COLOR = NAMED_COLOR_IDXS['WHITE']
ALL_COLORS[DEFAULT_COLOR_IDX] = ALL_COLORS[DEFAULT_COLOR]
