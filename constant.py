import logging
from time import strftime, localtime

# LOG HEADER
LOG_HEADER_ACTION = 0xEA  # 行为日志
LOG_HEADER_ERR = 0xEB  # 错误日志
LOG_HEADER_FLOW = 0xEC  # 流水日志

# FLOW LOG LEVEL
LOG_FLOW_LEVEL_FATAL = 0x01  # Fatal
LOG_FLOW_LEVEL_ERROR = 0x02  # Error
LOG_FLOW_LEVEL_WARN = 0x03  # Warn
LOG_FLOW_LEVEL_INFO = 0x04  # Info
LOG_FLOW_LEVEL_DEBUG = 0x05  # Debug

# FLOW LOG MODE
MODE_BLE = 'BLE模式'
MODE_WIFI = 'WIFI模式'

# LOG CONFIG
LOG_PATH = '/log/' + strftime('%Y%m%d%H%M%S', localtime()) + '.log'
LOG_FORMAT = "%(asctime)s %(levelname)s: %(module)s -> %(funcName)s -> line: %(lineno)d  Message: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
FATAL = 50
FILENAME = LOG_PATH
FILEMODE = 'a'
