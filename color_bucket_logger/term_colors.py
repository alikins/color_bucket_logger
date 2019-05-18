
# hacky ansi color stuff
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

NUMBER_OF_BASE_COLORS = 8

#: Used to determine what color index we start from.
#: The xterm256 colors 0-8 and 8-16 are normal and bright term colors, 16-231 is from a 6x6x6 rgb cube
#: 232-255 are the grays (white to gray to black)
#: +2 is to skip black and very dark blue as valid color.
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

ALL_COLORS = {}
ALL_COLORS.update(BASE_COLORS)
ALL_COLORS.update(THREAD_COLORS)

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = BASE_COLORS.keys()

RESET_SEQ_IDX = 256
ALL_COLORS[RESET_SEQ_IDX] = RESET_SEQ

DEFAULT_COLOR = WHITE
DEFAULT_COLOR_IDX = 257
ALL_COLORS[DEFAULT_COLOR_IDX] = ALL_COLORS[DEFAULT_COLOR]
