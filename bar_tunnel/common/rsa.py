from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random

"""
This is nit the write way to encrypt and decrypt data
with the RSA key but it s works for now :)

"""
def read_file(path):
    f = open(path)   # Make a new file in output mode >>>
    text = f.read()  # Read entire file into a string >>> text 'Hello\nworld\n'
    return text

def encryption(public_key,message):
    public_key_object = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(public_key_object)
    ciphertext = cipher.encrypt(message)
    #encrypt_message_b64 =  base64.b64encode(encrypt_message)
    return ciphertext

def decryption(private_key,ciphertext):
    #encrypt_message=  base64.b64encode(encrypted_message_b64)
    private_key_object = RSA.importKey(private_key)
    cipher = PKCS1_OAEP.new(private_key_object)
    decrypted_message = cipher.decrypt(ciphertext)
    return decrypted_message

def encrypt(public_key,plaintext):
    h = SHA.new(plaintext)
    public_key_object = RSA.importKey(public_key)
    cipher = PKCS1_v1_5.new(public_key_object)
    ciphertext = cipher.encrypt(plaintext+h.digest())
    #ciphertext_b64 =  base64.b64encode(ciphertext)
    return ciphertext

def decrypt(private_key , ciphertext):
    #ciphertext=  base64.b64encode(ciphertext_b64)
    private_key_object = RSA.importKey(private_key)
    dsize = SHA.digest_size
    sentinel = Random.new().read(15+dsize)      # Let's assume that average data length i

    cipher = PKCS1_v1_5.new(private_key_object)
    plaintext = cipher.decrypt(ciphertext, sentinel)

    digest = SHA.new(plaintext[:-dsize]).digest()
    if digest==plaintext[-dsize:]:                # Note how we DO NOT look for the sentinel
        print "Decryption was correct."
        return plaintext , True
    else:
        print "Decryption was not correct."
        return plaintext , False



if __name__ == "__main__":

    message = "PAranoia is total awareness" # Can decrypt with 4096 bit key almost 430 and with 2048 almost 225
    print message
    public_key = read_file('/home/bar/Desktop/bar_tunnel/keys/public_key.pem')
    private_key = read_file('/home/bar/Desktop/bar_tunnel/keys/private_key.pem')
    print public_key , private_key
    ciphertext = encrypt(public_key,message)
    print "Encrypt : " + ciphertext
    decrypt = decrypt(private_key , ciphertext)
    print "Decrypt : " , decrypt
