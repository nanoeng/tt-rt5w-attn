#!/usr/bin/env python3
"""Serve a local serial port (the TT demo board, or the fake board's pty) over RFC 2217, so a container, a VM or
another machine can run the HIL backend with  --port rfc2217://<host>:<tcp-port>.

    python3 hil/tools/rfc2217_bridge.py /dev/ttyACM0            # board on this machine, TCP 4000
    python3 hil/tools/rfc2217_bridge.py /tmp/rt5w_hil_tty -p 4001 # fake board (hil/tests/fake_board.py)

Single client at a time; reconnects are accepted. Based on pyserial's serial.rfc2217.PortManager."""
import argparse
import socket
import threading

import serial
import serial.rfc2217


class _LenientSerial(serial.Serial):
    """Pseudo-terminals (fake board) have no modem-control lines; report them as inactive instead of failing."""
    def _safe(self, fn, default=False):
        try:
            return fn()
        except OSError:
            return default

    @property
    def cts(self):
        return self._safe(lambda: serial.Serial.cts.fget(self))

    @property
    def dsr(self):
        return self._safe(lambda: serial.Serial.dsr.fget(self))

    @property
    def ri(self):
        return self._safe(lambda: serial.Serial.ri.fget(self))

    @property
    def cd(self):
        return self._safe(lambda: serial.Serial.cd.fget(self))

    def _update_rts_state(self):
        self._safe(lambda: serial.Serial._update_rts_state(self))

    def _update_dtr_state(self):
        self._safe(lambda: serial.Serial._update_dtr_state(self))


class _Conn:
    """PortManager writes its telnet negotiation through .write(); give it the socket's sendall."""
    def __init__(self, sock):
        self.sock = sock

    def write(self, data):
        self.sock.sendall(data)


def serve(ser, conn):
    mgr = serial.rfc2217.PortManager(ser, _Conn(conn))
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    conn.sendall(b"".join(mgr.escape(data)))
            except (OSError, serial.SerialException):
                break
        stop.set()

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    try:
        while not stop.is_set():
            data = conn.recv(1024)  # noqa
            if not data:
                break
            ser.write(b"".join(mgr.filter(data)))
    finally:
        stop.set()
        t.join(timeout=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("port", help="local serial port or pyserial URL")
    ap.add_argument("-p", "--tcp-port", type=int, default=4000)
    ap.add_argument("--bind", default="0.0.0.0")
    a = ap.parse_args()
    if "://" in a.port:
        ser = serial.serial_for_url(a.port, baudrate=115200, timeout=0.05)
    else:
        ser = _LenientSerial(a.port, baudrate=115200, timeout=0.05)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((a.bind, a.tcp_port))
    srv.listen(1)
    print(f"RFC 2217: {a.port} on {a.bind}:{a.tcp_port}", flush=True)
    while True:
        conn, addr = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print(f"client {addr[0]}:{addr[1]}", flush=True)
        try:
            serve(ser, conn)
        except OSError as e:
            print(f"client closed: {e}", flush=True)
        finally:
            conn.close()


if __name__ == "__main__":
    main()
