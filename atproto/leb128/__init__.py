"""
Original source code: https://github.com/mohanson/leb128

MIT License

Copyright (c) 2021 Mohanson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

https://en.wikipedia.org/wiki/LEB128

LEB128 or Little Endian Base 128 is a form of variable-length code
compression used to store an arbitrarily large integer in a small number of
bytes. LEB128 is used in the DWARF debug file format and the WebAssembly
binary encoding for all integer literals.
"""

import typing


class _U:
    @staticmethod
    def encode(i: int) -> bytearray:
        """Encode the int i using unsigned leb128 and return the encoded bytearray."""
        if i < 0:
            raise ValueError

        r = []
        while True:
            byte = i & 0x7F
            i = i >> 7
            if i == 0:
                r.append(byte)
                return bytearray(r)
            r.append(0x80 | byte)

    @staticmethod
    def decode(b: bytearray) -> int:
        """Decode the unsigned leb128 encoded bytearray"""
        r = 0
        for i, e in enumerate(b):
            r = r + ((e & 0x7F) << (i * 7))
        return r

    @staticmethod
    def decode_reader(r: typing.BinaryIO) -> typing.Tuple[int, int]:
        """
        Decode the unsigned leb128 encoded from a reader, it will return two values, the actual number, and the number
        of bytes read.
        """
        a = bytearray()
        while True:
            b = ord(r.read(1))
            a.append(b)
            if (b & 0x80) == 0:
                break
        return _U.decode(a), len(a)


class _I:
    @staticmethod
    def encode(i: int) -> bytearray:
        """Encode the int i using signed leb128 and return the encoded bytearray."""
        r = []
        while True:
            byte = i & 0x7F
            i = i >> 7
            if (i == 0 and byte & 0x40 == 0) or (i == -1 and byte & 0x40 != 0):
                r.append(byte)
                return bytearray(r)
            r.append(0x80 | byte)

    @staticmethod
    def decode(b: bytearray) -> int:
        """Decode the signed leb128 encoded bytearray"""
        r = 0
        for i, e in enumerate(b):
            r = r + ((e & 0x7F) << (i * 7))
        if e & 0x40 != 0:
            r |= -(1 << (i * 7) + 7)
        return r

    @staticmethod
    def decode_reader(r: typing.BinaryIO) -> typing.Tuple[int, int]:
        """
        Decode the signed leb128 encoded from a reader, it will return two values, the actual number, and the number
        of bytes read.
        """
        a = bytearray()
        while True:
            b = ord(r.read(1))
            a.append(b)
            if (b & 0x80) == 0:
                break
        return _I.decode(a), len(a)


u = _U()
i = _I()
