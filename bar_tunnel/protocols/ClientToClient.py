from twisted.internet import ssl, reactor , defer
from twisted.internet.protocol import Factory, Protocol ,ClientFactory , ServerFactory
from twisted.protocols.basic import NetstringReceiver
import bar_tunnel.common.generate_keys as gen

##### Redirect to TOR Network imports
from txsocksx.client import SOCKS5ClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint , SSL4ClientEndpoint

from txtorcon import endpoints as tor_endpoint
##### SSL - TLS import
from txsocksx.tls import TLSWrapClientEndpoint

import time
import optparse
import os

# Server Host:port
CLIENT_HOST = "127.0.0.1"
CLIENT_PORT = 6882



class ClientToClientProtocol(Protocol):

    def __init__(self , data ):
        self.data = data

    def connectionMade(self):
        peer = self.transport.getPeer()
        host = self.transport.getHost()
        print "~~ Connected to Client at " +str(peer)
        self.transport.write(self.data)
        #self.transport.loseConnection()

    ## We cant accepting connection except from Tor
    def dataReceived(self, data):
        if data == "OK":
            print "The data was send successfully == " , data
        elif data == "FAIL":
            print "The data wasn t send successfully == " , data
        else:
            pass
        self.transport.loseConnection()

    ## is called when a connection could not be established
    def connectionFailed(self,  reason):
        peer = self.transport.getPeer()
        print "Connection failed to Client" + str(peer)
        print "Reason was : ", reason
        reactor.stop()

    ## is called when a connection was made and then disconnected
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ Disconnected from Client at " +str(peer)
        self.transport.loseConnection()


class ClientToClientFactory(ClientFactory):


    def startedConnecting(self, connector):
        print '~~ Start connection to Client ~~'

    def __init__(self , data ):
        self.data = data

    def buildProtocol(self , addr):
        #print "Building Client To Cleint  Protocol connect"
        return ClientToClientProtocol(self.data )



def clientTOclient(args):
    client_to_client_factory = ClientToClientFactory(args.message)
    reactor.connectTCP(CLIENT_HOST,CLIENT_PORT,client_to_client_factory)
    reactor.run()

if __name__ == '__main__':
    clientTOclient()
