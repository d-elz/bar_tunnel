
##### SSL - TLS import
from argparse import Namespace
from twisted.web import http, proxy
from bar_tunnel.client.services.BCPService import bcp_service

class BarWebProxyClientRequest(proxy.ProxyRequest):

    def __init__(self,factory):
        self.factory = factory

    def process(self):
        """
        Called by a channel to let you proccess the request.
        You can overwrite this method for your own cause.
        Here we take the request and passing from the TOr Network
        """
        print self.factory
        self.factory.new("asdf")
        if self.getAllHeaders()['host'][-4:] == ".bar":
            pseudonym = self.getAllHeaders()['host'][:-4]
            print("Request from %s for %s" % (
                self.getClientIP(), self.getAllHeaders()['host'])   )
            print self.method
            print self.uri
            print self.path
            print self.args
            try:
                #proxy.ProxyRequest.process(self)
                #from bar_tunnel.tunnels import tunneling as tun

                print self.getAllHeaders()['host'][:-4]
                print "aaaaaaaaaaaaaaaaaaaaaaaaaaa"
                print self.getAllHeaders()
                args = Namespace()
                #args.nym = self.proxy_factory.nym
                #args.pk = self.proxy_factory.pk
                args.client = self.getAllHeaders()['host'][:-4]
                args.message = self.getAllHeaders()['host']
                bcp_service(args)
            except KeyError:
                print("HTTPS is not supported at the moment!")
        else:
            print "The connection isn t for you scam!"

    def connectionLost(self,reason):
        print "COnnection Lost"
#class BarWebProxyClient(Protocol):
#    def dataReceived(self, data):
#        print "Proxy Server get the HTTP packet"
#        self.proxy_bar_network(data)

#    def connectionMade(self):
#        print "Connection made to Proxy Server"

#    def proxyTo_Bar_network(self,http_packet):
#        print "Sending the data to Bar"

#class BarWebProxyFactory(http.HTTPFactory):
	#protocol = BarWebProxyClientRequest



class BarWebProxyClient(proxy.Proxy):

    def __init__(self,proxy_factory):
        self.proxy_factory = proxy_factory
    #requestFactory = BarWebProxyClientRequest

    def dataReceived(self,data):

        args = Namespace()
        args.nym = self.proxy_factory.pseudonym
        args.pk = self.proxy_factory.public_key
        args.bar_server_host = self.proxy_factory.bar_server_host
        args.bar_server_port = self.proxy_factory.bar_server_port
        args.client = "jjj"
        if ".bar" not in data:
            pass
        else:
            print "This is the data for bar server ", data
            print "Send data to bar net"
            args.message = data
            bcp_service(args)
    #def lineReceived(self,data):
    #    print "Line "
    #    print data.


    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ End Proxy Request from browser at " +str(peer)
        self.transport.loseConnection()

class BarWebProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        print "Start BarWebProxyFactory"
        return BarWebProxyClient(self)

    def set_pseudonym(self, pseudonym):
        self.pseudonym = pseudonym

    def set_public_key(self, public_key):
        self.public_key = public_key

    def set_bar_server(self, bar_server):
        self.bar_server_host = bar_server.split(":")[0]
        self.bar_server_port = bar_server.split(":")[1]




if __name__ == '__main__':
    broadcast_message("something")
