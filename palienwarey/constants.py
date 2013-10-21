# -*- coding: utf-8 -*-
import logging

# USB protocol related constants
SEND_REQUEST_TYPE = 0x21
SEND_REQUEST = 0x09
SEND_VALUE = 0x202
SEND_INDEX = 0x00
READ_REQUEST_TYPE = 0xa1
READ_REQUEST = 0x01
READ_VALUE = 0x101
READ_INDEX = 0x00

# USB state replies
STATE_BUSY = 0x11
STATE_READY = 0x10
STATE_UNKNOWN_COMMAND = 0x12

# USB packet constants
DATA_LENGTH = 9
START_BYTE = 0x02
FILL_BYTE = 0x00
STATUS_OK = 0x10

# How many color modes might be set for a given zone
ZONE_MAX_CONFIGURATIONS = 0xf
# Propietary extension to the protocol: Using the sum of all zones does not
# work reliably with the Alienware 14 2013, so this zone is just an alias for
# indicating commands to be run on all non-group and non-power zones.
ALL_ZONES_UID = 0xffffff

# Max allowed speed for theme tempo
MAX_SPEED = 0xffff
# Wait in seconds before sending a command
WAIT_FOR_OK_SLEEP = 0.01
# Number of tries waiting for OK (~5 seconds)
WAIT_FOR_OK_MAX_TRIES = 500

# Zone commands
CMD_END_STORAGE = 0x00
CMD_SET_MORPH = 0x01
CMD_SET_PULSE = 0x02
CMD_SET_COLOR = 0x03
CMD_END_LOOP = 0x04
CMD_TRANSMIT_EXECUTE = 0x05
CMD_GET_STATUS = 0x06
CMD_RESET = 0x07
CMD_SET_MODE = 0x08
CMD_SAVE = 0x09
CMD_BATTERY_STATE = 0x0F
CMD_SET_SPEED = 0x0E

# Available modes
MODE_VERSION_1 = (
    (0x01, 'Load on boot', 'boot'),
    (0x02, 'Stand By', 'standby'),
    (0x05, 'AC Power', 'ac'),
    (0x06, 'charging', 'charging'),
    (0x07, 'Sleeping on battery', 'batsleep'),
    (0x08, 'Battery Power', 'batpower'),
    (0x09, 'Low Battery', 'batlow'),
)
MODE_VERSION_2 = (
    (0x01, 'Load on boot', 'boot'),
    (0x02, 'Stand By', 'standby'),
    (0x05, 'AC Power', 'ac'),
    (0x06, 'charging', 'charging'),
    (0x07, 'Low Battery', 'batlow'),
    (0x08, 'Battery Power', 'batpower'),
)

# Global commands
RESET_TOUCH_CONTROLS = 0x01
RESET_SLEEP_LIGHTS_ON = 0x02
RESET_ALL_LIGHTS_OFF = 0x03
RESET_ALL_LIGHTS_ON = 0x04

# Hello, Dell
VENDOR_ID = 0x187c

# Daemon protocol related
DEFAULT_HOST = ''
DEFAULT_PORT = 6587  # AW
HEADER_LENGTH = 6

# Possible addresses for leds
LEDS_TO_SCAN = (0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80, 0x100, 0x200,
                0x400, 0x800, 0x1000, 0x2000, 0x4000, 0x8000, 0x10000, 0x20000,
                0x40000, 0x80000, 0x100000, 0x200000, 0x400000, 0x800000)

# Possible program exit codes
SUCCESS = 0
ERROR_DEVICE_NOT_FOUND = 11
ERROR_DEVICE_CANNOT_TAKE_OVER = 12
ERROR_DEVICE_TIMEOUT = 13
ERROR_NO_DAEMON = 14
ERROR_UNKNOWN_COMMAND = 15
ERROR_BAD_COLOR = 16
ERROR_BAD_HEADER = 31
ERROR_BAD_METHOD = 32
ERROR_BAD_ARGUMENTS = 33
ERROR_BAD_REQUEST_JSON = 34
ERROR_CANNOT_CONNECT = 41
ERROR_BAD_HEADER = 42
ERROR_BAD_RESPONSE_JSON = 43
ERROR_CANNOT_SEND_DATA = 44

# Status codes to error messages
MESSAGES_MAP = {
    SUCCESS: '',
    ERROR_DEVICE_NOT_FOUND: 'Device not found',
    ERROR_DEVICE_CANNOT_TAKE_OVER: 'Cannot take over device',
    ERROR_DEVICE_TIMEOUT: 'Device timeout',
    ERROR_NO_DAEMON: 'No daemon running',
    ERROR_UNKNOWN_COMMAND: 'Unknown command',
    ERROR_BAD_COLOR: 'Invalid color',
    ERROR_BAD_HEADER: 'Invalid header provided within the request',
    ERROR_BAD_REQUEST_JSON: 'Invalid JSON data provided within the request',
    ERROR_BAD_METHOD: 'Invalid JSON method provided within the request',
    ERROR_BAD_ARGUMENTS: 'Wrong arguments for the current method',
    ERROR_CANNOT_CONNECT: 'Cannot connect to daemon.',
    ERROR_BAD_HEADER: 'Invalid header replied from daemon',
    ERROR_BAD_RESPONSE_JSON: 'Invalid JSON data replied by daemon',
    ERROR_CANNOT_SEND_DATA: 'Cannot send data to daemon',
}

# Command strings to command uids
STRING_CMD_MAP = {
    'c': CMD_SET_COLOR,
    'color': CMD_SET_COLOR,
    'm': CMD_SET_MORPH,
    'morph': CMD_SET_MORPH,
    'p': CMD_SET_PULSE,
    'pulse': CMD_SET_PULSE
}

# Reset strings to reset contants
STRING_RESET_MAP = {
    'touchpad': RESET_TOUCH_CONTROLS,
    'sleep': RESET_SLEEP_LIGHTS_ON,
    'off': RESET_ALL_LIGHTS_OFF,
    'on': RESET_ALL_LIGHTS_ON
}

# Log level strings to logging constants
STRING_LOG_LEVEL_MAP = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warn': logging.WARN,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# All available log formatters by name
LOG_FORMATTERS = {
    'simple': '%(levelname)s %(module)s:%(lineno)s %(message)s',
    'verbose': ('%(levelname)s %(asctime)s %(module)s.%(funcName)s:%(lineno)s'
                ' %(message)s')
}
