# -*- coding: utf-8 -*-
import collections

from argparse import Action

from .logconf import logger
from .constants import (
    CMD_SET_COLOR, CMD_SET_MORPH, CMD_SET_PULSE, STRING_CMD_MAP,
    CMD_STRING_MAP)


__all__ = ['ALL_ZONES_UID', 'STRING_CMD_MAP', 'AppendZoneAction',
           'parse_color', 'parse_zones_cmd_set', 'merge_zones_cmd_set',
           'group_zone_has_cmd', 'expand_group_zones_cmd_set',
           'prepare_zones_cmd_set', 'parse_prepare_zones_cmd_set']


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


def parse_zones_cmd_set(machine, zones_cmd_set):
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


def merge_zones_cmd_set(machine, zones_cmd_set):
    """
    Merges all same zones commands into single zones.

    Arguments:
      + machine: a machine dict as returned by ``defines.get_machine``.
      + zones_cmd_set: a list of tuples where first element is the uid for the
         zone (or tuple of uids if it's a group) and the second element is an
         iterable with all commands defined as proper data structures.

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
        else:
            merged[idx] += cmd_and_args
    return merged


def group_zone_has_cmd(group, group_uid, group_idx, zones_cmd_set):
    """
    Returns true if zone with uid has a command defined for it.
    """
    for zone_idx, zone_cmd_set in enumerate(zones_cmd_set):
        zone_uid = zone_cmd_set[0]
        # The group will only have overrides when a zone (or group zone)
        # command was defined after it.
        if group_idx >= zone_idx:
            continue
        if not isinstance(zone_uid, collections.Iterable):
            if group_uid == zone_uid:
                return True
        else:
            for single_uid in zone_uid:
                if single_uid == group_uid:
                    return True
    return False


def expand_group_zones_cmd_set(machine, zones_cmd_set, override_groups=False):
    """
    Expand all group zones commands into separated zones.

    Arguments:
      + machine: a machine dict as returned by ``defines.get_machine``.
      + zones_cmd_set: a list of tuples where first element is the uid for the
         zone (or tuple of uids if it's a group) and the second element is an
         iterable with all commands defined as proper data structures.
      + override_groups: when True, single zone commands will override command
         definitions for groups for which it is member.

    Returns the expanded zones_cmd_set.
    """
    expanded = []
    for zone_idx, zone_cmd_set in enumerate(zones_cmd_set):
        uid = zone_cmd_set[0]
        cmd_and_args = zone_cmd_set[1]
        zone = machine['zones_by_uid'][uid]
        if not zone['is_group']:
            expanded.append(zone_cmd_set)
        else:
            for single_uid in uid:
                # For groups we do something fancier when the override_groups
                # is True: we need the group index because a lower index means
                # less priority when overriding commands.
                if override_groups and group_zone_has_cmd(
                        uid, single_uid, zone_idx, zones_cmd_set):
                    continue
                expanded.append((single_uid, cmd_and_args))
    return expanded


def prepare_zones_cmd_set(machine, zones_cmd_set, override_groups=False):
    """
    Alias for merge_zones_cmd_set(expand_group_zones_cmd_set(*args))
    """
    return merge_zones_cmd_set(
        machine, expand_group_zones_cmd_set(
            machine, zones_cmd_set, override_groups))


def parse_prepare_zones_cmd_set(machine, zones_cmd_set, override_groups=False):
    """
    Alias for:
        parse_zones_cmd_set(
            merge_zones_cmd_set(expand_group_zones_cmd_set(*args)))
    """
    return merge_zones_cmd_set(
        machine, expand_group_zones_cmd_set(
            machine, parse_zones_cmd_set(
                machine, zones_cmd_set), override_groups))
