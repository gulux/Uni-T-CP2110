import struct
import time
from .UTHID import UTHID


class UT171A(UTHID):
    """UT171A specific class, e.g. formatting data, protocol"""

    def __init__(self):
        UTHID.__init__(self)
        '''The more required bytes at positions are defined the faster read_data can skip distorted messages.
        The tuple with more than one value signals the position of the message length Byte in the message. If only one
        length is allowed, add a bogus value for that purpose.'''
        self.protocol = (0xab,), (0xcd,), (0x11, 0x17, 0x05, 0x04, 0x06, 0x08), (0x00,), (0x02,)

    @staticmethod
    def format_data(data, units=False, flags=False):
        """specific formatting for UT-171A"""
        lendat = len(data)
        val1 = None
        val2 = None
        val3 = None

        meas_unit: str = ''
        aux_unit: str = ''
        meas_type: int = -1
        meas_factor = 1
        if lendat >= 21:
            # the main value
            val1, = struct.unpack('<f', d[9:13])
            # auxiliary value
            val2, = struct.unpack('<f', d[15:19])
        if lendat == 27:
            val3, = struct.unpack('<f', d[21:25])
        '''what was measured?'''
        if units:
            meas_type: int = d[7]
            if meas_type == 0xA:
                meas_unit = "Ohm"
                if d[8] >= 2:
                    meas_factor *= 1000
                if d[8] >= 5:
                    meas_factor *= 1000
            elif meas_type == 0x2:
                meas_unit = "V/DC"
            elif meas_type == 0x3:
                meas_unit = "V/AC"
                aux_unit = "kHz"
            elif meas_type == 0x5:
                meas_unit = "mV/DC"
            elif meas_type == 0x6:
                meas_unit = "mV/AC"
                aux_unit = "kHz"
            elif meas_type == 0xb:
                meas_unit = "diode"
            elif meas_type == 0x14:
                meas_unit = "mA/DC"
            elif meas_type == 0x15:
                meas_unit = "mA/AC"
            elif meas_type == 0x11:
                meas_unit = "µA/DC"
            elif meas_type == 0x12:
                meas_unit = "µA/AC"
            elif meas_type == 0x17:
                meas_unit = "A/DC"
            elif meas_type == 0x18:
                meas_unit = "A/AC"
            elif meas_type == 0xf:
                meas_unit = "Hz"
            else:
                meas_unit = str(meas_type)
        '''evaluate display hints, bitwise'''
        display = ""
        if flags:
            scrn: int = data[5]
            # if scrn & 0x01:
            #    display += "kHz?"
            if scrn & 0x04:
                display += "BatLow "
            # if scrn & 0x08:
            #     display += "USB "
            if scrn & 0x80:
                display += "Hold "
        formatted = "{:8.4f} {:s} ".format(val1 * meas_factor, meas_unit)
        if meas_type in (0x3, 0x6):
            formatted += ", {:8.4f} {:s} ".format(val2, aux_unit)
        if flags:
            formatted += "{:s}".format(display)
        return formatted


if __name__ == "__main__":
    ut171A = None
    try:
        ut171A = UT171A()
        ut171A.connect()
        t_start = time.time()
        for t, d in ut171A.read_data():
            # print(UTHID.format_data(d))
            print("{:04.2f}  {:s}".format(t - t_start, UT171A.format_data(d, units=True, flags=True)))

    except KeyboardInterrupt:
        pass
    finally:
        if ut171A is not None:
            ut171A.pause()
            ut171A.disable_uart()
