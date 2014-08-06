"""
Tequila: a command-line Minecraft server manager written in python

Copyright (C) 2014 Snaipe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from collections import namedtuple
import socket

NetState = {
    '01': 'ESTABLISHED',
    '02': 'SYN_SENT',
    '03': 'SYN_RECV',
    '04': 'FIN_WAIT1',
    '05': 'FIN_WAIT2',
    '06': 'TIME_WAIT',
    '07': 'CLOSE',
    '08': 'CLOSE_WAIT',
    '09': 'LAST_ACK',
    '0A': 'LISTEN',
    '0B': 'CLOSING'
}

NetInfo = namedtuple('NetInfo', [
    'slot',
    'local_address',
    'remote_address',
    'state',
    'queue_usage',
    'uid',
    'timeout'
])

NetAddress = namedtuple('NetAddress', ['host', 'port'])


def _hex_to_dec(s):
    return str(int(s, 16))


class TCP_IPv4(object):

    def __init__(self):
        self.proc_path = '/proc/net/tcp'

    def parse_addr(self, addr):
        arr = addr.split(':')

        ip = '.'.join([
            _hex_to_dec(arr[0][6:8]),
            _hex_to_dec(arr[0][4:6]),
            _hex_to_dec(arr[0][2:4]),
            _hex_to_dec(arr[0][0:2])
        ])
        port = int(_hex_to_dec(arr[1]))

        return NetAddress(ip, port)

    def parse_proc_net_line(self, line):
        arr = [e for e in line.split(' ') if e != '']
        return NetInfo(arr[0][:-1], self.parse_addr(arr[1]), self.parse_addr(arr[2]), NetState[arr[3]], arr[4], arr[7], arr[8])

    def netstat(self):
        with open(self.proc_path, 'r') as proc:
            lines = proc.readlines()
            lines.pop(0)

            status = []
            for line in lines:
                status.append(self.parse_proc_net_line(line))
            return status


class TCP_IPv6(TCP_IPv4):

    def __init__(self):
        super().__init__()
        self.proc_path += '6'

    def parse_addr(self, addr):
        arr = addr.split(':')

        ip = ':'.join([
            _hex_to_dec(arr[0][28:32]),
            _hex_to_dec(arr[0][24:28]),
            _hex_to_dec(arr[0][20:24]),
            _hex_to_dec(arr[0][16:20]),
            _hex_to_dec(arr[0][12:16]),
            _hex_to_dec(arr[0][8:12]),
            _hex_to_dec(arr[0][4:8]),
            _hex_to_dec(arr[0][0:4])
        ])
        port = int(_hex_to_dec(arr[1]))

        return NetAddress(ip, port)

    def parse_proc_net_line(self, line):
        arr = [e for e in line.split(' ') if e != '']
        return NetInfo(arr[0][:-1], self.parse_addr(arr[1]), self.parse_addr(arr[2]), NetState[arr[3]], arr[4], arr[7], arr[8])


def get_open_ports(low=2 << 10, high=(2 << 16) - 1):
    stat = TCP_IPv4().netstat()
    stat.extend(TCP_IPv6().netstat())

    ports = set(range(low, high+1))
    for s in stat:
        if s.state != 'LISTEN':
            continue

        port = s.local_address.port
        if low <= port <= high and port in ports:
            ports.remove(port)

    return sorted(ports)


class socket_connection(object):

    def __init__(self, address):
        self.address = address

    def __enter__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.address)
        return self.sock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()