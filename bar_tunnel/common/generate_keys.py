from Crypto.PublicKey import RSA
import os
"""

Isn t complited yet. A must specify the permissions
for the key files .Now is chmod 644 . We want only
the owner of the private key to have access to
the private key for known perpuse.We allready specify
the permissions for the keys folder to chmod 600

And its not the wright way to generate keys

Even though you may choose to  directly use the methods of an RSA key object
to perform the primitive cryptographic operations (e.g. _RSAobj.encrypt),
it is recommended to use one of the standardized schemes instead (like
Crypto.Cipher.PKCS1_v1_5 or Crypto.Signature.PKCS1_v1_5).

"""

def change_directory(ex_file,back,file):
    dir_of_executable = os.path.dirname(ex_file)
    path = os.path.abspath(os.path.join(dir_of_executable, back)) + file
    return path

def generate_rsa_key(bit):
    path_to_private_key = change_directory(__file__,"../../keys","/private_key.pem")

    key = RSA.generate(bit)
    try:
        f = open(path_to_private_key, 'r')
    except IOError:
        f=  open(path_to_private_key,'w')
    f.write(key.exportKey('PEM'))
    f.close()

    path_to_public_key = change_directory(__file__,"../../keys","/public_key.pem")

    try:
        f = open(path_to_public_key, 'r')
    except IOError:
        f=  open(path_to_public_key,'w')

    f.write(key.publickey().exportKey())
    f.close()

def generate_rsa_bridge_key(bit):
    key = RSA.generate(bit)
    try:
        f = open('keys/bridge_private_key.pem', 'r')
    except IOError:
        f = open('keys/bridge_private_key.pem', 'w')

    f.write(key.exportKey('PEM'))
    f.close()

    try:
        f = open('keys/bridge_public_key.pem', 'r')
    except IOError:
        f = open('keys/bridge_public_key.pem', 'w')

    f.write(key.publickey().exportKey())
    f.close()

if __name__ == "__main__":
    generate_rsa_key(2048)
