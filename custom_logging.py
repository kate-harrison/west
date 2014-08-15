import logging

# Many thanks to https://docs.python.org/2/howto/logging-cookbook.html

# Colored logging thanks to
# http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output




class ColoredFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    #The background is set with 40 plus the number of the color, and the foreground with 30

    #These are the sequences need to get colored ouput
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"


    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

        self.COLORS = {
            'WARNING': self.YELLOW,
            'INFO': self.WHITE,
            'DEBUG': self.BLUE,
            'CRITICAL': self.YELLOW,
            'ERROR': self.RED
        }


    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in self.COLORS:
            levelname_color = self.COLOR_SEQ % (30 + self.COLORS[levelname]) + \
                              levelname + self.RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def get_colored_formatter():
    def formatter_message(message, use_color = True):
        if use_color:
            message = message.replace("$RESET",
                                      ColoredFormatter.RESET_SEQ).replace(
                "$BOLD", ColoredFormatter.BOLD_SEQ)
        else:
            message = message.replace("$RESET", "").replace("$BOLD", "")
        return message


    #FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s (
    # $BOLD%(filename)s$RESET:%(lineno)d)"
    # FORMAT = "[$BOLD%(name)-10s$RESET][%(levelname)-18s]  %(message)s (" \
    #          "$BOLD%(filename)s$RESET:%(lineno)d)"
    FORMAT = "[%(levelname)s] [$BOLD%(name)s$RESET]  %(message)s (" \
             "$BOLD%(filename)s$RESET:%(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    color_formatter = ColoredFormatter(COLOR_FORMAT)
    return color_formatter



base_logger = logging.getLogger("base")
base_logger.setLevel(logging.DEBUG)

_ch = logging.StreamHandler()
#_formatter = logging.Formatter("[%(levelname)s] %(name)s @ %(asctime)s: %("
#                               "message)s")
_formatter = get_colored_formatter()
_ch.setFormatter(_formatter)
base_logger.addHandler(_ch)

_all_loggers = [base_logger]

def getModuleLogger(obj):
    module_name = obj.__class__.__name__
    #base_logger.getLogger(module_name)
    new_logger = logging.getLogger(module_name)
    new_logger.setLevel(logging.DEBUG)
    new_logger.addHandler(_ch)
    _all_loggers.append(new_logger)
    return new_logger

def changeLogLevel(new_log_level):
    for logger in _all_loggers:
        logger.setLevel(new_log_level)

def disableLogging():
    changeLogLevel(logging.CRITICAL)

def enableDebugLogging():
    changeLogLevel(logging.DEBUG)

def enableWarningLogging():
    changeLogLevel(logging.WARNING)

def enableErrorLogging():
    changeLogLevel(logging.ERROR)

def getCurrentLogLevel():
    return base_logger.getEffectiveLevel()
