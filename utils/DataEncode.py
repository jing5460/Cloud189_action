r"""
I don't know what is this, so I translated it.
If you know what those that start with "__" are, Please tell me :)
"""

import rsa
import hmac
import hashlib
from utils.IntegerOpera import unsigned_right_shift, int_overflow, left_shift, xor


def __ka_BytesBool(a: bytes, b: bool) -> list:
    iArr = []
    alen = len(a)
    length = unsigned_right_shift(alen, 2)
    length += (alen & 3) != 0

    ilen = length + 1 if b else length
    for i in range(ilen):
        if i == length:
            iArr.append(alen)
        else:
            iArr.append(0)
    for i2 in range(alen):
        i3 = unsigned_right_shift(i2, 2)
        iArr[i3] = iArr[i3] | ((a[i2] & -1) << ((i2 & 3) << 3))

    return iArr


def __ka_ListBool(a: list, b: bool) -> bytes:
    i2 = 0
    length = len(a) << 2
    if b:
        i2 = a[len(a) - 1]
        if i2 > length or i2 <= 0:
            return bytes()
    else:
        i2 = length

    bArr = []
    for i3 in range(i2):
        t1 = unsigned_right_shift(i3, 2)
        t2 = unsigned_right_shift(a[t1], ((i3 & 3) << 3))
        bArr.append(t2 & 255)

    return bytes(bArr)


def __kb_List2(a: list, b: list) -> list:
    length = len(a) - 1
    if length < 1:
        return a
    if len(b) < 4:
        iArr3 = [0, 0, 0, 0]
        iArr3[0:len(b)] = b[:]
        b = iArr3
    i2 = int(52 / (length + 1)) + 6
    i3 = a[length]
    i4 = 0
    while True:
        i5 = i2 - 1
        if i2 <= 0:
            return a
        i4 -= 1640531527
        i6 = unsigned_right_shift(i4, 2) & 3
        i7 = i3
        i8 = 0
        while i8 < length:
            i9 = i8 + 1
            i10 = a[i9]
            temp1 = int_overflow(unsigned_right_shift(i7, 5) ^ left_shift(i10, 2))
            temp2 = int_overflow(unsigned_right_shift(i10, 3) ^ left_shift(i7, 4))
            temp3 = int_overflow(int_overflow(i10 ^ i4) + int_overflow(i7 ^ b[int_overflow((i8 & 3) ^ i6)]))
            i7 = int_overflow(int_overflow(int_overflow(temp1 + temp2) ^ temp3) + a[i8])
            a[i8] = i7
            i8 = i9
        i11 = a[0]
        temp1 = int_overflow(unsigned_right_shift(i7, 5) ^ left_shift(i11, 2))
        temp2 = int_overflow(unsigned_right_shift(i11, 3) ^ left_shift(i7, 4))
        temp3 = int_overflow(i11 ^ i4)
        temp4 = int_overflow(b[int_overflow((i8 & 3) ^ i6)] ^ i7)
        i3 = int_overflow(int_overflow(int_overflow(temp1 + temp2) ^ int_overflow(temp3 + temp4)) + a[length])
        a[length] = i3
        i2 = i5


def __kb_Bytes2(a: bytes, b: bytes) -> bytes:
    return __ka_ListBool(__kb_List2(__ka_BytesBool(a, True), __ka_BytesBool(b, False)), False)


def __ka_List2(a: list, b: list) -> list:
    length = len(a) - 1
    if length < 1:
        return a
    if len(b) < 4:
        iArr3 = [0, 0, 0, 0]
        iArr3[0:len(b)] = b[:]
        b = iArr3
    i2 = a[0]
    i3 = int_overflow((int(52 / (length + 1)) + 6) * -1640531527)
    while i3 != 0:
        i4 = int_overflow(unsigned_right_shift(i3, 2) & 3)
        i5 = i2
        i6 = length
        while i6 > 0:
            i7 = a[i6 - 1]
            temp1 = int_overflow(xor(i5, i3) + xor(i7, b[xor((i6 & 3), i4)]))
            temp2 = xor(unsigned_right_shift(i7, 5), (i5 << 2))
            temp3 = xor(unsigned_right_shift(i5, 3), (i7 << 4))
            temp4 = int_overflow(temp2 + temp3)
            i5 = int_overflow(a[i6] - xor(temp1, temp4))
            a[i6] = i5
            i6 -= 1
        i8 = a[length]
        temp1 = xor(unsigned_right_shift(i8, 5), left_shift(i5, 2))
        temp2 = xor(unsigned_right_shift(i5, 3), left_shift(i8, 4))
        temp3 = int_overflow(temp1 + temp2)
        temp4 = xor(temp3, int_overflow(xor(i5, i3) + xor(b[xor((i6 & 3), i4)], i8)))
        i2 = int_overflow(a[0] - temp4)
        a[0] = i2
        i3 = int_overflow(i3 + 1640531527)
    return a


def __ka_Bytes2(a: bytes, b: bytes) -> bytes:
    return __ka_ListBool(__ka_List2(__ka_BytesBool(a, False), __ka_BytesBool(b, False)), True)


def encodeHex(string: str, key: str) -> str:
    kbBB_ret = __kb_Bytes2(string.encode("utf-8"), key.encode("utf-8"))
    return kbBB_ret.hex().upper()


def decodeHex(data: str, key: str) -> str:
    kaBB_ret = __ka_Bytes2(bytes.fromhex(data), key.encode("utf-8"))
    return str(kaBB_ret, "utf-8")


def rsa_encode(publicKey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{publicKey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    return rsa.encrypt(f'{string}'.encode(), pubkey).hex()


def md5(string: str) -> str:
    return hashlib.md5(string.encode("utf-8")).hexdigest()


def hmac_sha1(string: str, key: str):
    hmac_code = hmac.new(key.encode("utf-8"), string.encode("utf-8"), "sha1")
    return hmac_code.hexdigest()
