# -*- coding: utf-8 -*-
import argparse
import sys

from . import lsdclient
from .constants import (
    ERROR_DEVICE_NOT_FOUND, ERROR_UNKNOWN_COMMAND, ERROR_BAD_COLOR)
from .defines import get_machine
from .logconf import logger, set_log_level, set_log_formatter, log_error_code
from .lsdaemon import DEFAULT_HOST, DEFAULT_PORT, SUCCESS
from .parse import AppendZoneAction, parse_prepare_zones_cmd_set
from .protocol import send


__all__ = ['lsd', 'main']


def lsd(machine, zones=None, modes=None, speed=0, save=False,
        override_groups=False, daemon=False, repl=False,
        log_level='info', verbosity='simple',
        host=DEFAULT_HOST, port=DEFAULT_PORT):
    set_log_level(log_level)
    set_log_formatter(verbosity)

    try:
        zones = parse_prepare_zones_cmd_set(machine, zones, override_groups)
    except KeyError as e:
        logger.error(e.message)
        return log_error_code(ERROR_UNKNOWN_COMMAND)
    except ValueError as e:
        logger.error(e.message)
        return log_error_code(ERROR_BAD_COLOR)

    if repl:
        try:
            from ipdb import set_trace
        except ImportError:
            from pdb import set_trace
        set_trace()

    if not daemon:
        logger.info('Not using daemon, executing commands directly.')
        return send(machine, zones, modes, speed, save)
    else:
        response = lsdclient.ping(host, port)
        if response['success']:
            logger.info('Using daemon at port: %s' % port)
            response = lsdclient.send(host, port, {
                'zones': zones,
                'modes': modes,
                'speed': speed,
                'save': save
            })
            if not response['code'] == SUCCESS:
                logger.error(response['message'])
            return log_error_code(response['code'])
        else:
            return log_error_code(response['code'])


def main():
    parser = argparse.ArgumentParser(description='Alienware lights control')
    parser.add_argument('-l', '--log-level', default='info',
                        choices=['debug', 'info', 'warn', 'error', 'critical'],
                        help='Set logging level.')
    parser.add_argument('-o', '--override-groups', action='store_true',
                        help='Override groups for single specified zones.')
    parser.add_argument('-d', '--daemon', action='store_true',
                        default=False, help='Use the daemon.')
    parser.add_argument('-i', '--host', default=DEFAULT_HOST,
                        help='lsdaemon host (defaults localhost).')
    parser.add_argument('-p', '--port', action='store', default=DEFAULT_PORT,
                        help='lsdaemon port (defaults to %s.' % DEFAULT_PORT)
    parser.add_argument('-r', '--repl', default=False, action='store_true',
                        help='Get into the command repl.')
    parser.add_argument('-t', '--speed', default=0, type=int,
                        help='Set theme tempo (speed).')
    parser.add_argument('-s', '--save', action='store_true', default=False,
                        help='Save changes permanently.')
    parser.add_argument('-v', '--verbosity', choices=['simple', 'verbose'],
                        default='simple', help='Set verbosity of logs.')

    try:
        machine = get_machine()
    except EnvironmentError:
        return log_error_code(ERROR_DEVICE_NOT_FOUND)

    # Parse all modes and add switches for them.
    for i, mode in enumerate(machine['modes']):
        alias = mode['alias']
        alias_flag = '--mode-' + alias if alias is not None else None
        parser.add_argument(
            '-m%s' % i, alias_flag, action='append_const', dest='modes',
            const=mode['uid'], metavar='COMMAND', help=mode['name'])

    # Parse all zones and add switches for them.
    for i, zone in enumerate(machine['zones']):
        alias = zone['alias']
        alias_flag = '--' + alias if alias is not None else None
        parser.add_argument(
            '-z%s' % i, alias_flag, nargs='+', action=AppendZoneAction,
            dest='zones', const=zone['uid'], metavar='COMMAND',
            help=zone['name'])

    args = vars(parser.parse_args())

    return lsd(machine, **args)


if __name__ == '__main__':
    sys.exit(main())
