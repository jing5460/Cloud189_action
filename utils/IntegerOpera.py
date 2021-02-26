r"""
Calculation to overflow.
"""


import ctypes


def int_overflow(val: int) -> int:
    r"""模拟 Integer 数值溢出"""
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def unsigned_right_shift(n, i):
    r""" 实现 Python 无符号右移"""

    # 数字小于0，则转为32位无符号uint
    if n < 0:
        n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i < 0:
        return -int_overflow(n << abs(i))
    # print(n)
    return int_overflow(n >> i)


def left_shift(n, i):
    return int_overflow(n << i)


def xor(n, i):
    return int_overflow(n ^ i)
