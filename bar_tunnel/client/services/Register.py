from twisted.internet import ssl, reactor , defer


#Our repositories
from  bar_tunnel.protocols.ClientToBar0 import  ClientToBar0Factory
from bar_tunnel.client.Filter import *


from argparse import Namespace
from bar_tunnel.client.services.Services import baseService

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
