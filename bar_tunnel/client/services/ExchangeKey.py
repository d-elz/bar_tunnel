from twisted.internet import ssl, reactor , defer

#Our repositories
from  bar_tunnel.protocols.ClientToBar0 import ClientToBar0Protocol , ClientToBar0Factory

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

import urllib2


class ExchangeKeyService(baseService):

            #Collecting the information
    def service(self ,args):
        db_client = DatabaseOperationClient()

        DOMAIN = urllib2.urlopen('http://ip.42.pl/raw').read() + ":2400" # use domain name insted(django project)

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
        sij = "this is the signature"
        pki = "My pk"

        plaintext = nymi +"||||"+ pki +"||||"+ kij +"||||"+ lij +"||||"+ sij

        # Generate
        cij = rsa.encrypt(pkj ,plaintext) # We can t encrypt string with 225 or more characters

        args_info = Namespace()
        args_info.service = args.service
        args_info.nymj = nymj
        args_info.cij = cij

        return args_info



def exchange_key_conn(data_to_send,exchange_args):
    base= baseService()
    factory = ClientToBar0Factory(data_to_send,"empty_defer","") # without a defer
    base.TLS_TOR_conn(exchange_args.bar0,exchange_args.serverport).connect(factory)

def exchange_key_service(args):
    exchange_key = ExchangeKeyService()
    exchange_key_fil = ExchangeFilterer()
    exchange_key_conn(exchange_key_fil.format( exchange_key.service(args) ) , args )
    reactor.run()
