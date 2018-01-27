from twisted.internet import ssl, reactor , defer

#Our repositories
from  bar_tunnel.protocols.ClientToBar0 import ClientToBar0Protocol , ClientToBar0Factory

from argparse import Namespace
import requests
import json

import base64

from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random

#Our Repos
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.client.services.Services import baseService
from bar_tunnel.client.Filter import ExchangeFilterer
from bar_tunnel.common import signature
import bar_tunnel.common.rsa as rsa
import bar_tunnel.common.rsa as rsa_block
from bar_tunnel.common import aes
import urllib2


class ExchangeKeyService(baseService):

            #Collecting the information
    def service(self ,args):
        db_client = DatabaseOperationClient()

        DOMAIN = "195.251.225.87" + ":2400" # use domain name insted(django project)

        url = 'http://'+ DOMAIN +'/bar/public_client/'
        r = requests.get(url)
        public_users = json.loads(r.content)

        #Variables of args
        nymi = args.nym
        nymj = args.fnym

        pki = self.read_file(self.dirc(__file__, "../../../keys" , "/public_key.pem"))

        pkj=""
        for public_user in public_users:
            if public_user.get("nym") == nymj:
                pkj = public_user.get("pk")
                break

        if not pkj:
            print "The user not exist.Is not register!"
            exit(1)

        lij = self.gen_key()
        kij = self.gen_key()
        private_key = self.dirc(__file__, "../../../keys" , "/private_key.pem")

        exchange_staff = nymi + "||||" + pki + "||||" + pkj + "||||" + lij + "||||" + kij

        ##### (a)If the entry is validate
        # Choose a random label lij and a key kij
        db_client.check_update_nym(nymj,pkj,lij,kij)

        # Sign
        sij = signature.sign(exchange_staff,private_key)

        #New variables to fit the restriction of encrypt for the example
        #sij = "this is the signature"
        #pki = "My pk"

        #CAnt make his block of code a function , problem with the lenght of the plaintext "too long"
        plaintext = nymi +"||||"+ pki +"||||"+ kij +"||||"+ lij +"||||"+ sij

        cij = ""
        block = plaintext
        while len(block) > 0:
            if len(block) >= 200:
                enc_block = rsa.encrypt(pkj, block[:200])
                cij += enc_block + "////"

            else:
                enc_block = rsa.encrypt(pkj, block)
                cij += enc_block
            block = block[200:]


        # Generate
        #cij = rsa.encrypt(pkj ,plaintext) # We can t encrypt string with 225 or more characters

        args_info = Namespace()
        args_info.service = args.service
        args_info.nymj = nymj
        args_info.cij = base64.b64encode(cij)

        return args_info

    def decrypt_exchange_messages(self,nymi):
        exchange_keys = self.get_exchange_keys(nymi)
        private_key = self.read_file(self.dirc(__file__, "../../../keys" , "/private_key.pem"))
        for exchange_key in exchange_keys:
            cij = exchange_key.get("cij")
            self.decrypt_message(cij,private_key)


    def decrypt_message(self,encrypt_message_b64,private_key):
        db_client = DatabaseOperationClient()
        cij =  base64.b64decode(encrypt_message_b64)

        decrypted_message = ""
        for encrypt_message in cij.split('////'):
            de_block, correct_decrypt = rsa.decrypt(private_key, encrypt_message)
            decrypted_message += de_block[:200]
        if correct_decrypt:
            nymj = decrypted_message.split("||||")[0]
            pkj = decrypted_message.split("||||")[1]
            kij = decrypted_message.split("||||")[2]
            lij = decrypted_message.split("||||")[3]
            sij = decrypted_message.split("||||")[4]
            print "THere is the data " , nymj , pkj , kij , lij , sij , decrypted_message
            #if (signature.verify(decrypted_message,self.dirc(__file__, "../../../keys" , "/private_key.pem"),sij) ):
            db_client.check_update_nym(nymj,pkj,lij,kij)
        else:
            print "Wrong key or data!"


    def get_exchange_keys(self,nym):
        DOMAIN = "195.251.225.87" + ":2400"  # use domain name insted(django project)

        url = 'http://' + DOMAIN + '/bar/exchange_client?nym=' + nym

        r = requests.get(url)
        exchange_keys = json.loads(r.content)
        if len(exchange_keys) == 0:
            print "Nobody want to contact with you! :P "
        return exchange_keys


def exchange_key_conn(data_to_send,exchange_args):
    base= baseService()
    factory = ClientToBar0Factory(data_to_send,"empty_defer","") # without a defer
    base.TLS_TOR_conn(exchange_args.bar0,exchange_args.serverport).connect(factory)

def exchange_key_service(args):
    exchange_key = ExchangeKeyService()
    exchange_key_fil = ExchangeFilterer()
    exchange_key_conn(exchange_key_fil.format( exchange_key.service(args) ) , args )
    reactor.run()
