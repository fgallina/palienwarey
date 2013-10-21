# -*- coding: utf-8 -*-
import collections
import time

from usb.core import USBError
from usb.util import claim_interface, dispose_resources

from .defines import get_machine
from .logconf import logger, log_error_code

from .constants import (
    READ_REQUEST_TYPE, READ_REQUEST, READ_VALUE, READ_INDEX, SEND_REQUEST_TYPE,
    SEND_REQUEST, SEND_VALUE, SEND_INDEX, START_BYTE, FILL_BYTE, DATA_LENGTH,
    CMD_SET_COLOR, CMD_SET_MORPH, CMD_SET_PULSE, CMD_GET_STATUS, CMD_END_LOOP,
    CMD_SET_SPEED, CMD_RESET, CMD_SAVE, CMD_SET_MODE, CMD_TRANSMIT_EXECUTE,
    STATUS_OK, ZONE_MAX_CONFIGURATIONS, MAX_SPEED, RESET_ALL_LIGHTS_ON,
    WAIT_FOR_OK_SLEEP, WAIT_FOR_OK_MAX_TRIES, SUCCESS, ERROR_DEVICE_NOT_FOUND,
    ERROR_DEVICE_CANNOT_TAKE_OVER, ERROR_DEVICE_TIMEOUT)


__all__ = ['connect', 'read', 'write', 'send_request', 'bytes_zone',
           'defpacket', 'packet_set_color', 'packet_set_morph',
           'packet_set_pulse', 'packet_get_status', 'packet_end_loop',
           'packet_set_speed', 'packet_reset', 'packet_save',
           'packet_set_mode', 'packet_transmit_execute',
           'STATUS_OK', 'wait_ok', 'cmd_set_color', 'cmd_set_morph',
           'cmd_set_pulse', 'cmd_get_status', 'cmd_end_loop', 'cmd_set_speed',
           'cmd_reset', 'cmd_transmit_execute', 'cmd_save', 'cmd_set_mode',
           'CMD_FN_MAP', 'send_for_mode', 'send']


def connect(device):
    """
    Gets control over the USB lights device.
    """
    try:
        claim_interface(device, 0)
    except USBError:
        logger.debug('Failed to claim interface, trying harder...')
        try:
            device.detach_kernel_driver(0)
        except USBError:
            logger.debug('Cannot detach (already attached?), trying harder...')
        try:
            device.set_configuration()
        except USBError:
            logger.debug('Setting configuration failed, trying harder...')
            device.attach_kernel_driver(0)
            device.detach_kernel_driver(0)
            try:
                device.set_configuration()
            except USBError:
                logger.debug('Configuration set failed after (at/de)tach.')
                raise


def read(device, packet):
    """
    Reads replies from device for given packet.
    """
    response = device.ctrl_transfer(
        READ_REQUEST_TYPE,
        READ_REQUEST,
        READ_VALUE,
        READ_INDEX,
        len(packet))
    logger.debug('Device Replied: %s' % response)
    return response


def write(device, packet):
    """
    Writes to device the given packet.

    Returns None
    """
    device.ctrl_transfer(
        SEND_REQUEST_TYPE,
        SEND_REQUEST,
        SEND_VALUE,
        SEND_INDEX,
        packet)


def send_request(device, packet):
    """
    Writes to device the given packet, waits for response and returns it.
    """
    logger.debug('Sending packet: %s' % packet)
    write(device, packet)
    response = read(device, packet)
    logger.debug(response)
    return response


def bytes_zone(zone_ids):
    """
    Returns packet bytes for the given zone_ids.

    >>> bytes_zone(0x0008)
    ... (0, 0, 8)
    >>> bytes_zone(0x0200)
    ... (0, 2, 0)
    >>> bytes_zone(0x08000000)
    ... (2048, 0, 0)
    >>> bytes_zone([1,2,4])
    ... (0, 0, 7)

    Arguments:
      + zone_ids: might be an interable of ints, each one for every desired
      zone or it might be just an integer for a single zone.

    Returns a bytes triplet elegible to be used in packets to mark the desired
    zones to affect.
    """
    if isinstance(zone_ids, collections.Iterable):
        # Several zones can be affected at the same time, in that case the
        # packet part where the zone is described is just the sum of all
        # zones.
        zones = sum(zone_ids)
    else:
        # For a single zone it might be handy to not have to wrap it over an
        # interable.
        zones = zone_ids
    first_two = int(zones / 65536)
    next_two = int(zones / 256) - int(first_two * 256)
    last_two = zones - first_two * 65536 - next_two * 256
    return (first_two, next_two, last_two)


def defpacket(cmd, *args):
    """
    Constructs a packet of DATA_LENGTH from args.
    """
    contents = [START_BYTE, cmd]
    for arg in args:
        for data in arg:
            contents.append(data)
    # Pad packet to DATA_LENGTH
    contents.extend([FILL_BYTE] * (DATA_LENGTH - len(contents)))
    return contents


def packet_set_color(idx, zones, color):
    """
    Returns a packet for the set_color command.

    Arguments:
      + idx: zone index for this command.
      + zones: is either a zone uid or a sum of all uids to be affected.
      + color: is a color as returned by parse_color.
    """
    return defpacket(CMD_SET_COLOR, [idx], bytes_zone(zones), color)


def packet_set_morph(idx, zones, color1, color2):
    """
    Returns a packet for the set_morph command.

    Arguments:
      + idx: zone index for this command.
      + zones: is either a zone uid or a sum of all uids to be affected.
      + color1: is a color as returned by parse_color.
      + color2: is a color as returned by parse_color with first=False.
    """
    color12 = color1[1] + color2[0]
    return defpacket(CMD_SET_MORPH, [idx], bytes_zone(zones),
                     [color1[0]], [color12], [color2[1]])


def packet_set_pulse(idx, zones, color):
    """
    Returns a packet for the set_pulse command.

    Arguments:
      + idx: zone index for this command.
      + zones: is either a zone uid or a sum of all uids to be affected.
      + color: is a color as returned by parse_color.
    """
    return defpacket(CMD_SET_PULSE, [idx], bytes_zone(zones), color)


def packet_get_status():
    """
    Returns a packet for the get_status command.
    """
    return defpacket(CMD_GET_STATUS)


def packet_end_loop():
    """
    Returns a packet for the end_loop command.
    """
    return defpacket(CMD_END_LOOP)


def packet_set_speed(speed):
    """
    Returns a packet for the set_speed command.

    Arguments:
      + speed: integer to be used to set theme speed (max 65535).
    """
    return defpacket(CMD_SET_SPEED, [FILL_BYTE],
                     [int(speed / 256)], [int(speed - (speed / 256) * 256)])


def packet_reset(type_=RESET_ALL_LIGHTS_ON):
    """
    Returns a packet for the reset command.

    Arguments:

      + type_: the type of reset request that must be sent, possible values are
        one of RESET_TOUCH_CONTROLS, RESET_SLEEP_LIGHTS_ON,
        RESET_ALL_LIGHTS_ON, RESET_ALL_LIGHTS_OFF.
    """
    return defpacket(CMD_RESET, [type_])


def packet_save():
    """
    Returns a packet for the save command.
    """
    return defpacket(CMD_SAVE)


def packet_set_mode(mode):
    """
    Returns a packet for the save_mode command.

    Arguments:
      + mode: the mode for which current configuration must be saved.
    """
    return defpacket(CMD_SET_MODE, [mode])


def packet_transmit_execute():
    """
    Returns a packet for the trasmit_execute command.
    """
    return defpacket(CMD_TRANSMIT_EXECUTE)


def wait_ok(device):
    """
    Waits for USB device to be responsive.
    """
    i = 0
    while True:
        status = cmd_get_status(device)[0]
        logger.debug('Waiting for ok, got: 0x%x', status)
        if status == STATUS_OK:
            break
        send_request(device, packet_reset(RESET_ALL_LIGHTS_ON))
        i += 1
        time.sleep(WAIT_FOR_OK_SLEEP)
        if i > WAIT_FOR_OK_MAX_TRIES:
            raise USBError("Device timeout: No OK reply received.")


def _log_color_command(cmd, idx, zones, color1, color2=None):
    zones = sum(zones) if isinstance(zones, collections.Iterable) else zones
    msg = 'Send %s: 0x%x, 0x%x, %s, %s'
    logger.info(msg, cmd, idx, zones, color1, color2)


def cmd_set_color(device, idx, zones, color):
    """
    Sends a set_color request to given zones.

    Arguments:
      + idx: index for this command, used by protocol for order in loops.
      + zones: either a zone uid or a sum of all uids to be affected.
      + color: a color tuple.
    """
    _log_color_command('cmd_set_color', idx, zones, color)
    return send_request(device, packet_set_color(idx, zones, color))


def cmd_set_morph(device, idx, zones, color1, color2):
    """
    Sends a set_morph request to given zones.

    Notice color1 and color2 have different formats as defined by the
    protocol. See parse_color for details on format.

    Arguments:
      + idx: index for this command, used by protocol for order in loops.
      + zone: either a zone uid or a sum of all uids to be affected.
      + color1: a color tuple.
      + color2: a color tuple.
    """
    _log_color_command('cmd_set_morph', idx, zones, color1, color2)
    return send_request(device, packet_set_morph(idx, zones, color1, color2))


def cmd_set_pulse(device, idx, zones, color):
    """
    Sends a set_pulse request to given zones.

    Arguments:
      + idx: index for this command, used by protocol for order in loops.
      + zone: either a zone uid or a sum of all uids to be affected.
      + color: a color tuple.
    """
    _log_color_command('cmd_set_pulse', idx, zones, color)
    return send_request(device, packet_set_pulse(idx, zones, color))


def cmd_get_status(device):
    """
    Gets device status.
    """
    logger.info('Send cmd_get_status')
    return send_request(device, packet_get_status())


def cmd_end_loop(device):
    """
    Sends end_loop command,

    After several style commands have been sent, marking the end of loop will
    enable looping all sent commands.
    """
    logger.info('Send cmd_end_loop')
    return send_request(device, packet_end_loop())


def cmd_set_speed(device, speed):
    """
    Sends a set_speed command.

    Arguments:
      + speed: speed amount. This might be a very large int (up to 0xffff or
               65535), for instance 51200 is a good default.
    """
    logger.info('Send cmd_set_speed: %d', speed)
    return send_request(device, packet_set_speed(speed))


def cmd_reset(device, type_=RESET_ALL_LIGHTS_ON):
    """
    Sends a reset command.

    Arguments:
      + type_: type of reset request that must be sent, possible values are
        one of RESET_TOUCH_CONTROLS, RESET_SLEEP_LIGHTS_ON,
        RESET_ALL_LIGHTS_ON, RESET_ALL_LIGHTS_OFF.
    """
    logger.info('Send cmd_reset')
    return send_request(device, packet_reset(type_))


def cmd_transmit_execute(device):
    """
    Sends a transmit_execute command.
    """
    logger.info('Send cmd_transmit_execute')
    return send_request(device, packet_transmit_execute())


def cmd_save(device):
    """
    Sends a save command.
    """
    logger.info('Send cmd_save')
    return send_request(device, packet_save())


def cmd_set_mode(device, mode):
    """
    Sets the mode for following commands.

    If mode is None this is a noop.
    """
    if mode is None:
        return
    logger.info('Send cmd_set_mode: 0x%x', mode)
    return send_request(device, packet_set_mode(mode))


CMD_FN_MAP = {
    CMD_SET_COLOR: cmd_set_color,
    CMD_SET_MORPH: cmd_set_morph,
    CMD_SET_PULSE: cmd_set_pulse
}


def send_for_mode(machine=None, zones=tuple(), mode=None, speed=0):
    """
    Sends commands to the device for given mode.

    Any invalid command, zone uid or speed provided will not result into an
    error but just a warning.

    Arguments:
      + machine: a machine with a *connected* device.
      + zones: an iterable where each element is a size two iterable, where
         the first element is the zone uid and the latter is a list where
         every item is a command to be sent to such zone with its arguments.
      + modes: a mode uid to apply current configuration to (None means
         current session only).
      + speed: theme speed for current configuration (range 0 to 65535).

    Returns an integer intended to be the value returned by sys.exit.
    """
    if machine is None:
        try:
            machine = get_machine()
        except EnvironmentError:
            return log_error_code(ERROR_DEVICE_NOT_FOUND)

    device = machine['device']

    # This holds the zone index for each group of commands sent to it, it must
    # start at 1, otherwise it just ignores the first request.
    idx = 1

    for zone_cmds in zones:
        zone_uid = zone_cmds[0]
        cmd_list = zone_cmds[1:]

        if speed:
            if (0 > speed or speed > MAX_SPEED):
                logger.warn('Invalid speed %d, setting to %d (0x%x)',
                            speed, MAX_SPEED, MAX_SPEED)
                speed = MAX_SPEED
            try:
                cmd_set_mode(device, mode)
                cmd_set_speed(device, speed)
            except USBError:
                return log_error_code(ERROR_DEVICE_TIMEOUT)

        try:
            zone = machine['zones_by_uid'][zone_uid]
        except KeyError:
            logger.warn('Invalid Zone uid: 0x%x, skipping...', zone_uid)
            continue

        num_configs = len(cmd_list)
        if num_configs > ZONE_MAX_CONFIGURATIONS:
            logger.warn(
                'Max zone 0x%x configs is %d, got %d, truncating...',
                zone_uid, ZONE_MAX_CONFIGURATIONS, num_configs)
            cmd_list = cmd_list[:ZONE_MAX_CONFIGURATIONS]

        for cmd_and_args in cmd_list:
            cmd = cmd_and_args[0]
            args = cmd_and_args[1:]
            if (cmd == CMD_SET_MORPH and not zone['can_morph']) or \
               (cmd == CMD_SET_PULSE and not zone['can_pulse']):
                logger.warn('Invalid Zone cmd: 0x%x cannot %x, skipping...',
                            zone_uid, cmd)
                continue
            try:
                # Send the proper command to the device
                cmd_fn = CMD_FN_MAP[cmd]
                cmd_set_mode(device, mode)
                cmd_fn(device, idx, zone_uid, *args)
            except KeyError:
                logger.warn('Invalid Command uid: 0x%x, skipping...', cmd)
            except USBError:
                return log_error_code(ERROR_DEVICE_TIMEOUT)

        idx += 1

        # Mark loop end
        try:
            cmd_set_mode(device, mode)
            cmd_end_loop(device)
        except USBError:
            return log_error_code(ERROR_DEVICE_TIMEOUT)

    return SUCCESS


def send(machine=None, zones=None, modes=None, speed=0, save=False):
    """
    Sends zone commands to the device for all modes.

    This is used by lsd, either talking directly to it when it has root
    access, or via the lsdaemon as intermediary. In any case this is the main
    entry point of the library, that you can use for your own applications.

    If mode is None is specified, then the commands are executed just for the
    current session, meaning that you will see the changes immediately.

    Arguments:
      + machine: a machine, as detected by get_machine.
      + zones: an iterable where each element is a size two iterable, where
         the first element is the zone uid and the latter is a list, where
         every item is a command to be sent to such zone with its arguments.
      + modes: a list of modes uids to apply current configuration to.
      + speed: theme speed for current configuration (range 0 to 65535).
      + save: when True, send a cmd_save request to make changes permantent.

    See ``protocol.send_for_mode`` for more details.

    Returns an integer intended to be the value returned by sys.exit.
    """
    try:
        machine = get_machine()
    except EnvironmentError:
        return log_error_code(ERROR_DEVICE_NOT_FOUND)

    device = machine['device']

    if modes is None:
        modes = []
    modes.append(None)

    try:
        # Try to gain device control really hard. This should work in most
        # situations for most machines.
        connect(device)
    except USBError:
        return log_error_code(ERROR_DEVICE_CANNOT_TAKE_OVER)

    try:
        wait_ok(device)
        cmd_reset(device, RESET_ALL_LIGHTS_ON)
        wait_ok(device)
    except USBError:
        return log_error_code(ERROR_DEVICE_TIMEOUT)

    for mode in modes:
        code = send_for_mode(machine, zones, mode, speed)
        if code != SUCCESS:
            return code

    # Mark loop end
    try:
        if save:
            cmd_save(device)
        cmd_transmit_execute(device)
    except USBError:
        return log_error_code(ERROR_DEVICE_TIMEOUT)

    # Free the robots^C^Cdevice
    dispose_resources(device)

    return SUCCESS
