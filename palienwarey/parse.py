# -*- coding: utf-8 -*-
import collections

from argparse import Action

from .logconf import logger
from .constants import (
    CMD_SET_COLOR, CMD_SET_MORPH, CMD_SET_PULSE, STRING_CMD_MAP,
    CMD_STRING_MAP)


__all__ = ['ALL_ZONES_UID', 'STRING_CMD_MAP', 'AppendZoneAction',
           'parse_color', 'parse_cmd', 'parse_zones',
           'flatten_group_zones', 'merge_zones', 'parse']


class AppendZoneAction(Action):
    """
    Argument parser for zone definitions.

    It appends all zone options in a dictionary whose keys matches the index
    of the zone for the current used machine.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])
        items = getattr(namespace, self.dest)
        items.append((self.const, ' '.join(values)))


def parse_color(color, first=True):
    """
    Parses 6 digit rgb color strings into a representation accepted by
    the USB protocol.

    If first is True, then the returned tuple is elegible for single colors,
    pulse colors and the first color of a morph. Else the color is returned in
    such form that is elegible for the destination color of a morph.

    Returns a tuple.
    """
    num_digits = len(color)
    if num_digits != 6:
        raise ValueError(
            'Invalid number of digits (must be 6, %s given)' % num_digits)

    r = int(int(color[0:2], 16)/16)
    g = int(int(color[2:4], 16)/16)
    b = int(int(color[4:6], 16)/16)

    if first:
        return (r * 16 + g, b * 16)
    else:
        return (r, g * 16 + b)


def parse_cmd(command):
    """
    Parse command string.

    Arguments:
      + command: is a string representing the command, where each argument is
        separated by ":". Example: "morph:ff00cc:cc00ff".

    Raises:
      + KeyError: if command is invalid.
      + ValueError: if colors are invalid.

    Returns a tuple, where the first element is the protocol function to send
    the request, and the remainder is the list of parsed arguments. Note
    parsed arguments don't include, device, zone or mode.
    """
    _ = command.split(":")
    cmd_str = _[0]
    args = _[1:]

    cmd = STRING_CMD_MAP[cmd_str]

    if cmd in [CMD_SET_COLOR, CMD_SET_PULSE]:
        if len(args) > 1:
            raise ValueError('This command supports up to one color per call')
        args[0] = parse_color(args[0])
    elif cmd == CMD_SET_MORPH:
        if len(args) > 2:
            raise ValueError('This command supports up to two colors per call')
        args[0] = parse_color(args[0])
        args[1] = parse_color(args[1], False)

    return (cmd,) + tuple(args)


def _zone_can(zone, cmd):
    warn_msg = 'Zone "%s" (uid: %s) cannot %s, skipping'
    can = (cmd == CMD_SET_COLOR or
           (cmd == CMD_SET_MORPH and zone['can_morph']) or
           (cmd == CMD_SET_PULSE and zone['can_pulse']))
    if not can:
        uid_fmt = '0x%.4x'
        uid = zone['uid']
        if not zone['is_group']:
            uid_str = uid_fmt % uid
        else:
            uid_str = ', '.join([uid_fmt % suid for suid in uid])
        logger.warn(warn_msg, zone['name'], uid_str, CMD_STRING_MAP[cmd])
    return can


def parse_zones(machine, zones_cmd_set):
    """
    Parses all zones commands defined in strings to data structures.

    Arguments:
      + machine: a machine dict as returned by ``defines.get_machine``.
      + zones_cmd_set: a tuple of tuples where first element is the uid for
         the zone (or tuple of uids if it's a group) and the second element is
         a string with all the commands to be applied to it.

    Returns a list of tuples where first element is the uid for the zone (or
    tuple of uids if it's a group) and the second element is an iterable with
    all commands defined as proper data structures.
    """
    parsed = []
    for uid, cmd_list in zones_cmd_set:
        zone = machine['zones_by_uid'].get(uid)

        if zone is None:
            logger.warn('Unrecognized zone %x, skipping', zone)
            continue

        for cmd in cmd_list.split():
            cmd_and_args = parse_cmd(cmd)
            cmd_const = cmd_and_args[0]
            if not _zone_can(zone, cmd_const):
                continue
            parsed.append((uid, cmd_and_args))
    return parsed


def flatten_group_zones(machine, zones_cmd_set):
    """
    Flattens all group definitions into single zones.

    Important thing to note, this fn is idempotent.
    """
    acc = []
    for uid, zone_cmd in zones_cmd_set:
        zone = machine['zones_by_uid'].get(uid)
        if zone["is_group"]:
            for z in uid:
                acc.append((z, zone_cmd))
        else:
            acc.append((uid, zone_cmd))
    return acc


def merge_zones(machine, zones_cmd_set, cascade=False):
    """
    Merges all same zones commands into single zones.

    Arguments:
      + machine: a machine dict as returned by ``defines.get_machine``.
      + zones_cmd_set: a list of tuples where first element is the uid for the
         zone (or tuple of uids if it's a group) and the second element is an
         iterable with all commands defined as proper data structures.
      + cascade: when True, commands for zones get overriden by latter ones
         instead of being appended in the same loop.

    Returns the merged zones_cmd_set.
    """
    merged = []
    uid_idx = {}
    for zone_cmds in zones_cmd_set:
        uid = zone_cmds[0]
        cmd_and_args = list(zone_cmds[1:])
        idx = uid_idx.get(uid)
        if idx is None:
            merged.append([uid] + cmd_and_args)
            idx = len(merged) - 1
            uid_idx[uid] = idx
        elif cascade:
            merged[idx] = [uid] + cmd_and_args
        else:
            merged[idx] += cmd_and_args
    return merged


def parse(machine, zones_cmd_set, cascade=False):
    """
    Parses the list of zones with commands in string format.

    Arguments:
      + machine: a machine dict as returned by ``defines.get_machine``.
      + zones_cmd_set: a list of tuples where first element is the uid for the
         zone (or tuple of uids if it's a group) and the second element is an
         iterable with all commands defined as proper data structures.
      + cascade: when True, commands for zones get overriden by latter ones
         instead of being appended in the same loop.

    Returns a list ready to be sent to the USB device.
    """
    parsed = parse_zones(machine, zones_cmd_set)
    flat = flatten_group_zones(machine, parsed)
    return merge_zones(machine, flat, cascade)
