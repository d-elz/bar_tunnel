from twisted.internet import ssl, reactor , defer
from twisted.internet.protocol import Factory, Protocol ,ClientFactory , ServerFactory
from twisted.protocols.basic import NetstringReceiver


#Our repositories
import bar_tunnel.common.generate_keys as gen
from  bar_tunnel.protocols.Listener import ListenerProtocol , ListenerFactory
from  bar_tunnel.protocols.ClientToBarServer import ClientToBarServerProtocol , ClientToBarServerFactory
from  bar_tunnel.protocols.ClientToBar0 import ClientToBar0Protocol , ClientToBar0Factory
from  bar_tunnel.protocols.BarWebProxy import BarWebProxyFactory

from bar_tunnel.client.Filter import *


##### Redirect to TOR Network imports
from txsocksx.client import SOCKS5ClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint , SSL4ClientEndpoint


from argparse import Namespace
import os
import hashlib
#HTTP Reguest
import urllib2
import requests
import json

import base64
import random
from Crypto.Hash import SHA
from Crypto import Random

#Our Repos
from bar_tunnel.common.db import Bardb
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.client.services.Services import baseService
from bar_tunnel.common import aes , rsa
import bar_tunnel.common.generate_keys as gen
from bar_tunnel.common import signature
import bar_tunnel.common.rsa as rsa

import urllib2

from txsocksx.tls import TLSWrapClientEndpoint



class RegisterService(baseService):

            #Collecting the information
    def service(self ,args):
        nym = args.nym
        pk = self.check_pk(args.pk)

        args_info = Namespace()
        args_info.service = args.service
        args_info.nym = nym
        args_info.pk = pk

        return args_info



def register_conn(data_to_send,register_args):
    base= baseService()
    factory = ClientToBar0Factory(data_to_send,"empty_defer","") # without a defer
    base.TLS_TOR_conn(register_args.bar0,register_args.serverport).connect(factory)

def register_service(args):
    register = RegisterService()
    register_fil = RegisterFilterer()
    register_conn(register_fil.format(register.service(args)),args)
    reactor.run()
