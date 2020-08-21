import time
from collections import deque
from copy import deepcopy
from threading import Thread

import hid
from glibc import ctypes


class UTHID(object):
    """Base class for accessing CP2110 based HID device.
    It defines the basic methods for initialization, connection and reading and writing to the HID device.
    Derive it for other multimeters with different protocol and formatting."""
    # Default Vendor/Product IDs for the CP2110.
    CP2110_VID = 0x10c4
    CP2110_PID = 0xEA80
    RX_TX_MAX = 63  # max number of Bytes to read and write
    GET_SET_UART_CONFIG = 0x50
    GET_SET_UART_ENABLE = 0x41
    DEFAULT_PROTOCOL = (0xab,), (0xcd,), (0x11, 0x17, 0x05, 0x04, 0x06, 0x08)

    def __init__(self):
        try:
            self.device = hid.Device(vid=self.CP2110_VID, pid=self.CP2110_PID)
            self.device.nonblocking = 1
        except Exception:
            raise RuntimeError("device initialization failed")
        self._connected: bool = False
        self._deq: deque = deque('', 50)
        self.enable_uart()
        self.__uart_config_defaults()
        self.protocol = UTHID.DEFAULT_PROTOCOL

    def is_uart_enabled(self):
        rv = self.device.get_feature_report(self.GET_SET_UART_ENABLE, 2)
        return rv[1] == 1

    def enable_uart(self):
        self.__write_config([0x41, 0x01])

    def disable_uart(self):
        self.__write_config([0x41, 0x00])

    def __uart_config_defaults(self):
        """ this refers to 9600, parity=NONE, 8 Bit, hardware Flow Control disabled, stop bits short """
        self.__write_config([0x50, 0x00, 0x00, 0x25, 0x80, 0x00, 0x00, 0x03, 0x00, 0x00])

    def connect(self):
        if self.is_uart_enabled():
            b = bytearray(1)
            for a in bytes.fromhex("AB CD 04 00 0A 01 0F 00"):
                b[0] = a
                self.__write(b)
            self._connected = True
        else:
            raise ConnectionError("uart not enabled")

    def pause(self):
        if self.is_uart_enabled() and self._connected:
            b = bytearray(1)
            for a in bytes.fromhex("AB CD 04 00 0A 00 0E 00"):
                b[0] = a
                self.__write(b)
            self._connected = False

    @staticmethod
    def format_data(data, *args):
        """return hex string"""
        return bytearray.hex(data, ' ')

    def read_raw(self):
        counter = 0
        while self._connected and counter < 1000:
            counter += 1
            b = self.__read(2)[1:2]
            if len(b) > 0:
                self._deq.appendleft(b[0])
                counter = 0
            ' sleep as bytes come from device with a delay of 8-9ms, necessary!'
            time.sleep(0.003)
        else:
            if not self._connected:
                raise Exception("not connected")
            if counter > 999:
                raise TimeoutError("read raw timeout")

    def read_data(self):
        """ generates single readings from the meter as a (timestamp, bytearray) Tuple"""
        if not self._connected:
            self.connect()

        dat: bytearray = bytearray()
        lenmessage: int = -1
        tim: float = 0.0

        def clean_dat(a):
            '''local function'''
            dat.clear()
            self._deq.append(a)

        Thread(target=self.read_raw, daemon=False).start()

        read_fail_counter = 0
        try:
            # for b in self.__read_raw():
            while True and read_fail_counter < 50:
                if len(self._deq) == 0:
                    time.sleep(0.01)
                    read_fail_counter += 1
                    continue

                read_fail_counter = 0

                a = self._deq.pop()

                lendat = len(dat)

                prot = self.protocol[lendat] if lendat < len(self.protocol) else None
                if prot is not None:
                    if a in prot:
                        if lendat == 0:
                            tim = time.time()
                        if len(prot) > 1:
                            lenmessage = a
                        dat.append(a)
                    else:
                        if lendat > 0:
                            clean_dat(a)
                elif lendat == lenmessage + 3:
                    dat.append(a)
                    # checksum
                    chsum_sent = dat[lenmessage + 3] << 8 | dat[lenmessage + 2]
                    chsum_calc = sum(dat[2:lenmessage + 2])
                    if chsum_sent == chsum_calc:
                        yield tim, dat
                    else:
                        print("checksum mismatch! read:", chsum_sent, " calc:", chsum_calc,"  Bytes:", bytearray.hex(dat, ' '))
                        ab_ix = dat.find(0xab, 5)
                        if ab_ix >= 0:
                            # add back to deque bytes until index
                            c = deepcopy(dat[ab_ix:])
                            c.reverse()
                            self._deq.extend(c)

                    lenmessage = -1
                    dat.clear()
                else:
                    dat.append(a)
            else:
                raise TimeoutError("read_data timed out")
        except TimeoutError as toe:
            print(toe)
        except Exception as ex:
            print(ex)
        finally:
            self.pause()

    def __write(self, data):
        """write max 2 Bytes at once"""
        len_bytes = len(data)
        if len_bytes > self.RX_TX_MAX - 1:
            raise RuntimeError("data too long")

        buf = ctypes.create_string_buffer(len_bytes + 1)
        # Store the length of data in buf[0]
        buf[0] = len_bytes
        buf[1:] = data[:len_bytes]
        self.device.write(buf)

    def __write_config(self, data):
        """write configuration with send_feature_report"""
        len_bytes = len(data)
        buf = ctypes.create_string_buffer(len_bytes)
        buf[:len_bytes] = data[:len_bytes]
        self.device.send_feature_report(buf)

    def __read(self, size=None):
        """for UT171A we read max 2 Bytes at once"""
        if size is None:
            size = self.RX_TX_MAX + 1
        return self.device.read(size)
