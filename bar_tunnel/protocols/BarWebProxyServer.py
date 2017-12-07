
from twisted.internet import protocol

class BarWebProxyServer(protocol.Protocol):

    def __init__(self,proxy_factory):
        self.proxy_factory = proxy_factory
    #requestFactory = BarWebProxyClientRequest

    def connectionMade(self):
        peer = self.transport.getPeer()
        host = self.transport.getHost()
        print "~~ Connected to Bar-Server at " +str(peer)
        self.transport.write(self.proxy_factory.data )

    def dataReceived(self,data):
        peer = self.transport.getPeer()
        print "Received data from " + str(peer)
        print data


    def ConnectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ End Proxy Request from browser at " +str(peer)
        self.transport.loseConnection()

class BarWebProxyServerFactory(protocol.ServerFactory):

    def __init__(self,data):
        self.data = data

    def startedConnection(self, addr):
        print "Start BarWebProxyServerFactory"

    def buildProtocol(self, addr):
        print "Start BarWebProxyServerFactory"
        return BarWebProxyServer(self)

    def clientConnectionLost(self , connector , reason):
        print "~~ End Proxy Request from browser at "
