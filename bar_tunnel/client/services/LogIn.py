from twisted.internet import ssl, reactor , defer
import socket

#Our repositories
from  bar_tunnel.protocols.Listener import  ListenerFactory
from  bar_tunnel.protocols.ClientToBar0 import  ClientToBar0Factory
from  bar_tunnel.protocols.BarWebProxy import BarWebProxyFactory
from  bar_tunnel.protocols.ClientToBarServer import ClientToBarServerFactory
from bar_tunnel.client.Filter import *


##### Redirect to TOR Network imports
from argparse import Namespace
import base64
import random

#Our Repos
from bar_tunnel.client.services.Services import baseService
import bar_tunnel.common.generate_keys as gen

import urllib2


class LogInService(baseService):

    # Find Free port for the Listener Protocol at a specifiv range of ports.Specify the tries do you want
    def find_free_port(self,  low ,  up , tries):
        counter = 0
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                _port = random.randint(low, up)
                s.bind(("localhost", _port))
                return s.getsockname()[1]
            except:
                counter += 1

            if counter > tries:
                print "cannot find a free port within range " + str(low) + " to " + str(up)
                return -1

            #Collecting the information
            #Attention! From some reason(i don t find it yet) the program take as global
            #variable the args.listenport and i thats the way it pass this variable to
            #the other functions
    def service(self ,args):
        nym = args.nym
        pk = self.read_file(args.pk.name)

        #Obtain the public params M , m , Nmin , Nmax
            #Optional

        # (a)Compute hi = hash(nym||||pki)
        # (b)Use the public system params M , m , Nmin , Nmax to find the cluster
        cluster = self.compute_cluster(nym,pk) # We compute the Bar server not the Cluster

        # (c)Select a new bridge pair keys for the current session
        gen.generate_rsa_bridge_key(4096)
        bridge_pk = self.read_file(self.dirc(__file__, "../../../keys" , "/bridge_private_key.pem"))

        # (d)Send the IPi , bridge key Bari.Clusteri
        #if args.listenport == 0: args.listenport = self.find_free_port(7000,7100,20)
        #if args.listenport == -1: exit(1) # if the find_free_port function returns -1 means that haven t find a free port within range
        IP = urllib2.urlopen('http://ip.42.pl/raw').read() + ":" + str(args.listenport)
        args.IP = IP

        #Returning information
        args_info = Namespace()
        args_info.service = args.service
        args_info.nym = nym
        args_info.pk = pk
        args_info.bridge_pk = bridge_pk
        args_info.IP = IP
        args_info.listenport = args.listenport
        args_info.proxyport = args.proxyport
        args_info.cluster = cluster
        args_info.serverport = args.serverport
        args_info.bar0 = args.bar0

        return args_info

def bar_server_conn(bar0_factory):
    # Getting the IP and the port of the BAR server(Bar0 sending the IP:port of the available BAR Server)
    BAR_SERVER = bar0_factory.bar_server.split(":")[0]
    BAR_SERVER_PORT = int(bar0_factory.bar_server.split(":")[1])

    bar_server_data = "LogIn||||" + str(bar0_factory.login_args.IP)
    bar_server_factory = ClientToBarServerFactory(bar_server_data , "empty_defer")

    listener_factory = ListenerFactory(reactor, bar_server_factory,bar0_factory.login_args)

    listener_factory.set_bar_server_host(BAR_SERVER)
    listener_factory.set_bar_server_port(BAR_SERVER_PORT)

    bar_server_factory.set_listener(listener_factory)
    listener = reactor.listenTCP(bar0_factory.login_args.listenport, listener_factory)

    #Proxy LIstener for Browser connection over HTTP
    proxyFaxtory = BarWebProxyFactory()
    proxyFaxtory.set_pseudonym(bar0_factory.login_args.nym)
    proxyFaxtory.set_public_key(bar0_factory.login_args.pk)
    proxyFaxtory.set_bar_server(bar0_factory.bar_server)
    proxy = reactor.listenTCP(bar0_factory.login_args.proxyport, proxyFaxtory)

    print 'Proxy on %s.' % (proxy.getHost())
    print 'Listening on %s.' % (listener.getHost())
    #tor_conn(bar_server_factory,BAR_SERVER,BAR_SERVER_PORT)
    reactor.connectTCP(BAR_SERVER,BAR_SERVER_PORT,bar_server_factory)

def login_conn(data_to_send,login_args):
    d = defer.Deferred()
    d.addCallback(bar_server_conn)# put the bar_server_conn function to a callback ,which will run when the data is ready when the BAR0 response with the IP:port combination
    base = baseService()
    factory = ClientToBar0Factory(data_to_send,d,login_args)
    base.TLS_TOR_conn(login_args.bar0,login_args.serverport).connect(factory)

def login_service(args):
    login = LogInService()
    login_fil = LogInFilterer()
    login_args = login.service(args)
    login_conn(login_fil.format(login_args),login_args)
    reactor.run()
