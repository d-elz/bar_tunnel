from twisted.internet import ssl, reactor , defer
from twisted.internet.protocol import Factory, Protocol ,ClientFactory , ServerFactory
from twisted.protocols.basic import NetstringReceiver

import bar_tunnel.common.aes as aes
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.protocols.ClientToClient import ClientToClientFactory , ClientToClientProtocol
from  bar_tunnel.protocols.BarWebProxyServer import BarWebProxyServerFactory

class ClientToBarServerProtocol(NetstringReceiver):

    def __init__(self , data , deffered , factory):
        self.data = data
        self.d = deffered
        self.factory = factory

    def connectionMade(self):
        peer = self.transport.getPeer()
        host = self.transport.getHost()
        print "~~ Connected to Bar-Server at " +str(peer)

        if self.data[:9] == "BROADCAST":
            print "~~ Sending data to Bar-Server at " +str(peer)
            self.sendString(self.data)
            self.transport.loseConnection()
        elif self.data[:5] == "LogIn":
            print "~~ Successfull Log In to Bar-Server at " +str(peer)
            self.sendString(self.data)
        else:
            print "You must specify a service : [BROADCAST] or [LogIn]"
            self.transport.loseConnection()

    ## We cant accepting connection except from Tor
    def stringReceived(self, data):

        #Filter the data to get only if the lij and the encryption fit the user
        doc = DatabaseOperationClient()
        print "GETTING MESSAGE: " + data
        row = doc.select_list(data.split("||||")[0])
        if row: #if the label is in the List continue
                    #Decrypt ([pki,kix,lix]; <lix,cx>) to get ki'x , li'x ,lix,IPy|cy
            print "DECRYPTING MESSAGE:"
            plaintext = aes.aes_decrypt(row[0]["shared_key"] , data.split("||||")[1] )
            #If the encrypted message has 5 variables e.g [ ki'x , li'x ,lix, IPy, cy]
            #then you are the first node of the BCP routing
            if len(plaintext.split("||||"))  == 5:
                #UpdateListEntry (Listx;[pki,ki'x,li'x])
                kix_new= plaintext.split("||||")[0]
                lix_new= plaintext.split("||||")[1]
                lix= plaintext.split("||||")[2]
                doc.updata_list(lix,kix_new,lix_new)

                #Send cy to the anddress IPy
                CLIENT_IP= plaintext.split("||||")[3]
                client_host =CLIENT_IP.split(":")[0]
                client_port = int(CLIENT_IP.split(":")[1])
                print "SENDING TO CLIENT:" ,CLIENT_IP
                clientTOclient(plaintext.split("||||")[4],client_host,client_port)
            #if the encrypted message hasn t got 5  variables you are the receiver
            else:
                if data.split("||||")[0] == plaintext.split("||||")[0]:
                    print "You are the receiver of this message"
                    print "The message is this" , plaintext.split("||||")[3]

                    #UpdateListEntry (Listj;[pkj,ki'j,li'j])
                    kix_new= plaintext.split("||||")[2]
                    lix_new= plaintext.split("||||")[1]
                    lix= plaintext.split("||||")[0]
                    doc.updata_list(lix,kix_new,lix_new)

                    #Prepei na chekarei an einai client h server
                    proxy_factory = BarWebProxyServerFactory( plaintext.split("||||")[3])
                    reactor.connectTCP("127.0.0.1",8000,proxy_factory)

        else:
            print "This message isn t for you .Dropping.."

        #self.transport.loseConnection()

    def broadcast_message(self,bar_server,data):
        self.sendString(data)

    ## is called when a connection could not be established
    def connectionFailed(self,  reason):
        peer = self.transport.getPeer()
        print "Connection failed to Bar-Server" + str(peer)
        print "Reason was : ", reason
        reactor.stop()

    ## is called when a connection was made and then disconnected
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ Disconnected from Bar-Server at " +str(peer)
        self.transport.loseConnection()


class ClientToBarServerFactory(ClientFactory):
    #protocol = ClientToBarServerProtocol

    def startedConnecting(self, connector):
        print '~~ Start connection to BAR Server ~~'

    def __init__(self , data ,deffered):
        self.data = data
        self.d = deffered

    def buildProtocol(self , addr):
        #print "Client To Bar Server Protocol connect"
        return ClientToBarServerProtocol(self.data ,self.d , self)

    def broadcast_message(self,bar_server,data):
        self.factory.bar_server.sendString(data)


    def set_listener(self, listener_factory):
        self.listener_factory = listener_factory

    def set_ip(self, ip):
        self.ip = ip

    def set_listen_port(self, listen_port):
        self.listen_port = listen_port

    def set_pseudonym(self, pseudonym):
        self.pseudonym = pseudonym

    def set_public_key(self, public_key):
        self.public_key = public_key

    def clientConnectionMade(self, client):
        self.client = client

def clientTOclient(data,client_host,client_port):
    client_to_client_factory = ClientToClientFactory(data)
    reactor.connectTCP(client_host,client_port,client_to_client_factory)


if __name__ == '__main__':
    BarServer()
