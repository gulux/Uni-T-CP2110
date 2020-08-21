import time
import unittest

from ..UT171A import UT171A


class UT171AByteGen(UT171A):

    def __init__(self):
        UT171A.__init__(self)
        self._ba = ""

    def set_bytes(self, ba):
        self._ba = ba

    def read_raw(self):
        """ overrides UTHID.read_raw()"""
        ba = bytearray.fromhex(self._ba)
        for a in ba:
            time.sleep(0.01)
            self._deq.appendleft(a)


class UT171AMessagesTestCases(unittest.TestCase):

    def setUp(self):
        self.ut171a = UT171AByteGen()
        self.ut171a.connect()

    def test_Good(self):
        self.ut171a.set_bytes("ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03")
        cnt = 0
        try:
            for t, d in self.ut171a.read_data():
                if cnt == 0:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03"))
                elif cnt == 1:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03"))
                else:
                    self.fail("too many lines returned")
                cnt += 1
            if cnt == 0:
                self.fail("no lines returned")
            elif cnt == 1:
                self.fail("too few lines returned")
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    def test_short(self):
        """2nd line 1Byte less"""
        self.ut171a.set_bytes("ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03")
        cnt = 0
        try:
            for t, d in self.ut171a.read_data():
                if cnt == 0:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03"))
                elif cnt == 1:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03"))
                else:
                    self.fail("too many lines returned")
                cnt += 1
            if cnt == 0:
                self.fail("no lines returned")
            elif cnt == 1:
                self.fail("too few lines returned")
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    def test_wrong_chksum(self):
        """2nd line wrong checksum less"""
        self.ut171a.set_bytes("ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d f0 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03")
        cnt = 0
        try:
            for t, d in self.ut171a.read_data():
                if cnt == 0:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03"))
                elif cnt == 1:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03"))
                else:
                    self.fail("too many lines returned")
                cnt += 1
            if cnt == 0:
                self.fail("no lines returned")
            elif cnt == 1:
                self.fail("too few lines returned")
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    def test_bogus_data(self):
        """additional bytes around correct messages"""
        self.ut171a.set_bytes("ff ef ee 00 00 ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03\
                     ff ef ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03\
                     ff  ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03 ff ee bc")
        cnt = 0
        try:
            for t, d in self.ut171a.read_data():
                if cnt == 0:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03"))
                elif cnt == 1 or cnt == 2:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03"))
                else:
                    self.fail("too many lines returned")
                cnt += 1
            if cnt == 0:
                self.fail("no lines returned")
            elif cnt == 1:
                self.fail("too few lines returned")
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    def test_broken_message(self):
        """messages interrupted and new messages started"""
        self.ut171a.set_bytes("ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38\
                        ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40\
                        ab cd 11 00 02 08 01 02 01 01 9b f2 3a 3d 40 00 4f\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03\
                        ab cd 11 00 02 08 01 02 01 9b ")
        cnt = 0
        try:
            for t, d in self.ut171a.read_data():
                if cnt == 0:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03"))
                elif cnt == 1:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03"))
                else:
                    self.fail("too many lines returned")
                cnt += 1
            if cnt == 0:
                self.fail("no lines returned")
            elif cnt == 1:
                self.fail("too few lines returned")
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    def test_long(self):
        """test long messages"""
        self.ut171a.set_bytes("ab cd 17 00 02 09 03 03 03 85 13 68 43 20 01 ad b3 4c 3d 30 13 d3 26 68 43 5f 05\
                        ab cd 17 00 02 09 03 03 03 fe 16 68 43 20 01 ae b4 4c 3d 30 13 b9 29 68 43 c6 05")
        cnt = 0
        try:
            for t, d in self.ut171a.read_data():
                if cnt == 0:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 17 00 02 09 03 03 03 85 13 68 43 20 01 ad b3 4c 3d 30 13 d3 26 68 43 5f 05"))
                elif cnt == 1:
                    self.assertEqual(d, bytearray.fromhex(
                        "ab cd 17 00 02 09 03 03 03 fe 16 68 43 20 01 ae b4 4c 3d 30 13 b9 29 68 43 c6 05"))
                else:
                    self.fail("too many lines returned")
                cnt += 1
            if cnt == 0:
                self.fail("no lines returned")
            elif cnt == 1:
                self.fail("too few lines returned")
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    def test_times(self):
        """messages interrupted and new messages started"""
        self.ut171a.set_bytes("ab cd 11 00 02 08 01 02 01 13 e0 3b 3d 40 00 64 d0 39 3d 74 03\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 ab\
                        cd 11 00 02 08 01 02 01 01 9b f2 3a 3d 40 00 4f 00\
                        ab cd 11 00 02 08 01 02 01 9b f2 3a 3d 40 00 4f b9 38 3d e0 03")
        t_start = time.time()
        try:
            ta = []
            for t, d in self.ut171a.read_data():
                ta.append(t - t_start)
            self.assertTrue(len(ta) == 2, "too many lines returned")
            # reading each byte takes ~0.09 s low: 71 high: 92
            self.assertTrue(0.65 < ta[1] - ta[0] < 0.90)
        except TimeoutError as toe:
            pass


if __name__ == '__main__':
    unittest.main()
