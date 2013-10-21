# -*- coding: utf-8 -*-
import json
import socket

from .constants import (ERROR_CANNOT_CONNECT, ERROR_BAD_HEADER,
                        ERROR_BAD_RESPONSE_JSON, ERROR_CANNOT_SEND_DATA)
from .logconf import logger
from .lsdaemon import DEFAULT_HOST, DEFAULT_PORT, HEADER_LENGTH, protocol


__all__ = ['ERROR_CANNOT_CONNECT', 'ERROR_BAD_HEADER',
           'ERROR_BAD_RESPONSE_JSON', 'ERROR_CANNOT_SEND_DATA',
           'send_request', 'ping', 'send']


def send_request(host=DEFAULT_HOST, port=DEFAULT_PORT, method='ping',
                 args=None):
    """
    Sends requests to lsdaemon and returns the loaded JSON response.
    """
    # A request is a string with the form 'METHOD JSON_ARGS'.
    if args is not None:
        json_args = json.dumps(args)
        data = method + ' ' + json_args
    else:
        data = method

    # The header just contains the size of request in hex.
    header = "%.6x" % len(data)
    request = header + data

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except socket.error:
        return protocol.response(ERROR_CANNOT_CONNECT)

    try:
        sock.send(request)
    except Exception as e:
        logger.exception(e)
        return protocol.response(ERROR_CANNOT_SEND_DATA)

    try:
        # The response is pretty much like the request: a header with the
        # length of the payload in hex and the payload.
        length = int(sock.recv(HEADER_LENGTH), 16)
    except ValueError:
        return protocol.response(ERROR_BAD_HEADER)

    try:
        # Consume the payload and return.
        return json.loads(sock.recv(length))
    except ValueError:
        return protocol.response(ERROR_BAD_RESPONSE_JSON)


def ping(host, port):
    """
    Simple wrapper around send_request for sending ping requests.
    """
    return send_request(host, port, 'ping')


def send(host, port, args):
    """
    Simple wrapper around send_request for sending device requests.
    """
    return send_request(host, port, 'send', args)
