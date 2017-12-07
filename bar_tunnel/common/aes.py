from Crypto import Random
from Crypto.Cipher import AES
from binascii import unhexlify
import base64

def aes_encrypt(skey, m):
    '''
    Encrypt given message with shared key.
    '''
    iv = '\x00' * 16
    stream = AES.new(skey, AES.MODE_CFB, iv)
    #ciphertext_b64 =  base64.b64encode(stream.encrypt(m))
    return stream.encrypt(m)

def aes_decrypt(skey, c):
    '''
    Decrypt given message with shared key.
    '''
    #plaintext64 =  base64.b64encode(c)
    iv = '\x00' * 16
    stream=AES.new(skey, AES.MODE_CFB, iv)
    return stream.decrypt(c)
