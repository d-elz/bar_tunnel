from twisted.internet import  reactor , ssl


#Our repositories
from  bar_tunnel.protocols.ClientToBar0 import  ClientToBar0Factory
from bar_tunnel.client.Filter import *


from argparse import Namespace
from bar_tunnel.client.services.Services import baseService

class RegisterService(baseService):

            #Collecting the information
    def service(self ,args):

        # (a) Select  aunique pseudonym nymi and generate a public/private key pair1 pki,ski.
        nym = args.nym
        pk = self.check_pk(args.pk)
        #If you want to generate a user to a specific bar server.
        while self.compute_cluster(nym,pk) != args.barserver:
            pk = self.check_pk(args.pk)

        self.write_file( self.dirc(__file__, "../../../keys" , "/pseudonym" ) , nym )

        # (c)Use this route to send nymi, pki to BAR0.
        args_info = Namespace()
        args_info.service = args.service
        args_info.nym = nym
        args_info.pk = pk

        return args_info


#Communication method -Establish connection with bar0 over TLS/SSL protocol
def register_conn(data_to_send,register_args):
    base= baseService()
    factory = ClientToBar0Factory(data_to_send,"empty_defer","") # without a defer
    base.TLS_TOR_conn(register_args.bar0,register_args.serverport).connect(factory)

def register_service(args):
    register = RegisterService()
    register_fil = RegisterFilterer()
    register_conn(register_fil.format(register.service(args)),args)
    reactor.run()
