from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import base64

"""

This is the default implementation of Signature .
You can find the same sample of code at the Crypto.
Signature.PKCS1_v1_5 .
This is the recomended way to sign and verify
in the PyCrypto module.

"""
def sign(msg,private_key_path):
    key = RSA.importKey(open(private_key_path).read())
    h = SHA.new(msg)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    sign = base64.b64encode(signature) # encode dta to easily manipulated
    return sign

def verify(msg,public_key_path,signature):
    sign= base64.b64decode(signature) # decode the data
    key = RSA.importKey(open(public_key_path).read())
    h = SHA.new(msg)
    verifier = PKCS1_v1_5.new(key)
    if verifier.verify(h, sign):
        print "The signature is authentic."
    else:
        print "The signature is not authentic."

if __name__ == '__main__':
    print "Sign func:"
    signature = sign("lalaaaaa","../private_key.pem")
    print "Verify func:"
    verify("lalaaaaa","../public_key.pem",signature)
