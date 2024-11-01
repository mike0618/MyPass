from os import urandom
from hashlib import pbkdf2_hmac
from binascii import hexlify, unhexlify
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


def derivekey(key_word, salt: bytes = b""):
    if not salt:
        salt = urandom(8)
    return pbkdf2_hmac("sha256", key_word.encode("utf8"), salt, 1000), salt


def encrypt(plainpw, key_word):
    dk = derivekey(key_word)
    if not dk:
        return False
    key, salt = dk
    aes = AESGCM(key)
    iv = urandom(12)
    plainpw = plainpw.encode("utf8")
    cipherpw = aes.encrypt(iv, plainpw, None)
    return f'{hexlify(salt).decode("utf8")}-{hexlify(iv).decode("utf8")}-{hexlify(cipherpw).decode("utf8")}'


def decrypt(cipherpw, key_word):
    salt, iv, cipherpw = map(unhexlify, cipherpw.split("-"))
    dk = derivekey(key_word, salt)
    if not dk:
        return 404
    key, _ = dk
    aes = AESGCM(key)
    try:
        plainpw = aes.decrypt(iv, cipherpw, None)
    except InvalidTag:
        return 404
    return plainpw.decode("utf8")
