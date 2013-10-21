# -*- coding: utf-8 -*-
import argparse
import json
import socket

try:
    import SocketServer as socketserver
except ImportError:
    # Python 3 compat
    import socketserver

from .constants import (DEFAULT_HOST, DEFAULT_PORT, HEADER_LENGTH, SUCCESS,
                        ERROR_BAD_HEADER, ERROR_BAD_METHOD,
                        ERROR_BAD_ARGUMENTS, ERROR_BAD_REQUEST_JSON,
                        MESSAGES_MAP)
from .logconf import logger, set_log_level, set_log_formatter
from .protocol import send


__all__ = ['DEFAULT_PORT', 'HEADER_LENGTH', 'SUCCESS', 'ERROR_BAD_HEADER',
           'ERROR_BAD_METHOD', 'ERROR_BAD_ARGUMENTS', 'ERROR_BAD_REQUEST_JSON',
           'protocol', 'LSDaemonServerRequestHandler', 'LSDaemonServer',
           'lsdaemon']


class protocol(object):

    @staticmethod
    def response(code):
        return {'success': code == SUCCESS,
                'code': code,
                'message': MESSAGES_MAP[code]}

    @staticmethod
    def encode_response(response, coding):
        data = json.dumps(response).encode(coding)
        header = "%.6x" % len(data)
        return header + data

    @staticmethod
    def decode_request(request, coding):
        return request.decode(coding)

    @staticmethod
    def dispatch(method_name, args=None):
        try:
            method = getattr(protocol, 'method_' + method_name)
        except AttributeError:
            return protocol.response(ERROR_BAD_METHOD)

        if args is not None:
            try:
                args = json.loads(args)
            except ValueError:
                return ERROR_BAD_REQUEST_JSON

            try:
                return protocol.response(method(args))
            except TypeError:
                return protocol.response(ERROR_BAD_ARGUMENTS)
        else:
            return protocol.response(method())

    @staticmethod
    def parse(request):
        try:
            method_name, args = request.split(' ', 1)
        except ValueError:
            method_name = request.strip()
            args = None
        return (method_name, args)

    @staticmethod
    def method_send(args):
        return send(**args)

    @staticmethod
    def method_ping():
        return 0


class LSDaemonServerRequestHandler(socketserver.BaseRequestHandler):
    """
    Request handler for the LSDaemonServer.

    Handle protocol requests from client by dispatching received data to
    protocol.send and returns to the client whatever it replies.
    """

    def __init__(self, request, client_address, server):
        self.encoding = server.encoding
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        logger.debug('Client connected')
        while True:
            try:
                header = self.request.recv(HEADER_LENGTH)
                logger.debug('Received header: %s', header)

                if header:
                    length = int(header, 16)
                else:
                    logger.error('Empty header received')
                    response = protocol.encode_response(
                        ERROR_BAD_HEADER, self.encoding)
                    self.request.send(response)
                    self.request.close()
                    break

                data = protocol.decode_request(
                    self.request.recv(length), self.encoding)
                logger.debug('Received data: %s', data)

                method_name, args = protocol.parse(data)
                raw_response = protocol.dispatch(method_name, args)
                response = protocol.encode_response(
                    raw_response, self.encoding)
                logger.debug('Replied data: %s', response)
                self.request.send(response)

                break
            except socket.timeout as e:
                logger.error('Socket error: %s', e)
                break


class LSDaemonServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Good ol' TCPServer using LSDaemonServerRequestHandler as handler.
    """

    def __init__(self, server_address,
                 handler_class=LSDaemonServerRequestHandler, encoding='utf-8'):
        self.encoding = encoding
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        host, port = self.server_address
        logger.info('Serving on: %s:%s (coding %s)', host, port, self.encoding)


def lsdaemon(host=DEFAULT_HOST, port=0, encoding='utf-8',
             log_level='info', verbosity='simple'):
    """
    Starts a LSDaemonServer on given host and port using encoding.

    If no port is provided then let the OS choose it.
    """
    set_log_level(log_level)
    set_log_formatter(verbosity)

    server = LSDaemonServer((host, port), encoding=encoding)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        description='Alienware lights control daemon driver')
    parser.add_argument('-i', '--host', default='',
                        help='Host (defaults localhost).')
    parser.add_argument('-e', '--encoding', default='utf-8',
                        choices=['utf-8', 'latin-1'], help='Data encoding.')
    parser.add_argument('-l', '--log-level', default='info',
                        choices=['debug', 'info', 'warn', 'error', 'critical'],
                        help='Set logging level.')
    parser.add_argument('-p', '--port', action='store', default=DEFAULT_PORT,
                        type=int, help='Port (defaults to %s).' % DEFAULT_PORT)
    parser.add_argument('-v', '--verbosity', choices=['simple', 'verbose'],
                        default='simple', help='Set verbosity of logs.')

    lsdaemon(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
