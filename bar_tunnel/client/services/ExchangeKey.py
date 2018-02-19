from twisted.internet import reactor

#Our repositories
from  bar_tunnel.protocols.ClientToBar0 import ClientToBar0Factory

from argparse import Namespace
import requests
import json

import base64

#Our Repos
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.client.services.Services import baseService
from bar_tunnel.client.Filter import ExchangeFilterer
from bar_tunnel.common import signature
import bar_tunnel.common.rsa as rsa

class ExchangeKeyService(baseService):

    DOMAIN = "bar0.cs.unipi.gr"

    #Collecting the information
    def service(self ,args):
        db_client = DatabaseOperationClient()


        url = 'http://'+ self.DOMAIN +'/bar/public_client/'
        r = requests.get(url)
        public_users = json.loads(r.content)

        #Variables of args
        nymi = args.nym
        nymj = args.fnym

        pki = self.read_file(self.dirc(__file__, "../../../keys" , "/public_key.pem"))

        pkj=""
        for public_user in public_users:
            if public_user.get("nym") == nymj:
                pkj = str(public_user.get("pk"))
                break

        if not pkj:
            print "The user not exist.Is not register!"
            exit(1)

        lij = self.gen_key()
        kij = self.gen_key()
        private_key = self.dirc(__file__, "../../../keys" , "/private_key.pem")

        exchange_staff = nymi + "||||" + pki + "||||" + pkj + "||||" + kij + "||||" + lij

        ##### (a)If the entry is validate
        # Choose a random label lij and a key kij
        db_client.check_update_nym(nymj,pkj,lij,kij)

        # Sign
        sij = signature.sign(exchange_staff,private_key)

        #CAnt make his block of code a function , problem with the lenght of the plaintext "too long"
        plaintext = nymi +"||||"+ pki +"||||"+ pkj +"||||"+ kij +"||||"+ lij +"||||"+ sij

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
            nymi = decrypted_message.split("||||")[0]
            pki = decrypted_message.split("||||")[1]
            pkj = decrypted_message.split("||||")[2]
            kij = decrypted_message.split("||||")[3]
            lij = decrypted_message.split("||||")[4]
            sij = decrypted_message.split("||||")[5]
            verification_data = nymi +"||||"+ pki +"||||"+ pkj +"||||"+ kij +"||||"+ lij
            if (signature.verify(verification_data,self.dirc(__file__, "../../../keys" , "/private_key.pem"),sij) ):
                db_client.check_update_nym(nymi,pki,lij,kij)
        else:
            print "Wrong key or data!"


    def get_exchange_keys(self,nym):
        # use domain name insted(django project)

        url = 'http://' + self.DOMAIN+ '/bar/exchange_client?nym=' + nym

        r = requests.get(url)
        exchange_keys = json.loads(r.content)
        if len(exchange_keys) == 0:
            print "Nobody want to contact with you! :P "
        return exchange_keys

#Communication method -Establish connection with bar0 over TLS/SSL protocol
def exchange_key_conn(data_to_send,exchange_args):
    base= baseService()
    factory = ClientToBar0Factory(data_to_send,"empty_defer","") # without a defer
    base.TLS_TOR_conn(exchange_args.bar0,exchange_args.serverport).connect(factory)

def exchange_key_service(args):
    exchange_key = ExchangeKeyService()
    exchange_key_fil = ExchangeFilterer()
    exchange_key_conn(exchange_key_fil.format( exchange_key.service(args) ) , args )
    reactor.run()
