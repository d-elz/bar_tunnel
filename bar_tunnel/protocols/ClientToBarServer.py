from twisted.internet import reactor , task
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import NetstringReceiver
from threading import Timer

import bar_tunnel.common.aes as aes
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.protocols.ClientToClient import ClientToClientFactory , ClientToClientProtocol
from  bar_tunnel.protocols.BarWebProxyServer import BarWebProxyServerFactory
from bar_tunnel.client.operations import DatabaseOperationClient
import time
import bar_tunnel.common.rsa as rsa
##### Redirect to TOR Network imports
from argparse import Namespace
from datetime import datetime
from bar_tunnel.client.services.Services import baseService

import string
import random

buffer = []

class ClientToBarServerProtocol(NetstringReceiver):



    def __init__(self , data , deffered , factory):
        self.data = data
        self.d = deffered
        self.factory = factory

    def connectionMade(self):
        peer = self.transport.getPeer()
        host = self.transport.getHost()
        self.count_received_messages = 0
        print "~~ Connected to Bar-Server at " +str(peer)

        if self.data[:9] == "BROADCAST":
            print "~~ Sending data to Bar-Server at " +str(peer)
            self.sendString(self.data)
            self.transport.loseConnection()
        elif self.data[:5] == "LogIn":
            print "~~ Successfull Log In to Bar-Server at " +str(peer)
            self.sendString(self.data)
            rt = RepeatedTimer(self.factory.delay, self.delayMessage, self)  # it auto-starts, no need of rt.start()
            self.rt = rt

        else:
            print "You must specify a service : [BROADCAST] or [LogIn]"
            self.transport.loseConnection()

    ## We cant accepting connection except from Tor
    def stringReceived(self, data):

        #Filter the data to get only if the lij and the encryption fit the user
        doc = DatabaseOperationClient()

        print str(self.count_received_messages) +".GETTING MESSAGE: Encrypted Data"
        row = doc.select_list(data.split("||||")[0])
        if row: #if the label is in the List continue
                    #Decrypt ([pki,kix,lix]; <lix,cx>) to get ki'x , li'x ,lix,IPy|cy
            print "DECRYPTING MESSAGE:"
            aesAlgoD = aes.AESCipher(row[0]["shared_key"])
            plaintext = aesAlgoD.aes_decrypt( data.split("||||")[1] )
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
                clientTOclient(plaintext.split("||||")[4],str(client_host),client_port)
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
                    #proxy_factory = BarWebProxyServerFactory( plaintext.split("||||")[3])
                    #reactor.connectTCP("127.0.0.1",8000,proxy_factory)

        else:
            print "This message isn t for you .Dropping.."
            print "--------------------------------------"
        self.count_received_messages = self.count_received_messages + 1
        #self.transport.loseConnection()

    def broadcast_message(self,bar_server,data):
        self.sendString(data)

    ## is called when a connection could not be established
    def connectionFailed(self,  reason):
        peer = self.transport.getPeer()
        print "Connection failed to Bar-Server" + str(peer)
        print "Reason was : ", reason
        #self.factory.reactor.stop()

    ## is called when a connection was made and then disconnected
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ Disconnected from Bar-Server at " +str(peer)
        self.transport.loseConnection()
        self.rt.stop() # Stopping dummy messager
        #self.factory.reactor.stop()

    def delayMessage(self,connection):

        if self.bufferIsLoaded():
            connection.sendString(buffer[0])
            buffer.remove(buffer[0])
        else:
            connection.sendString(self.dummyMessageGenerator())

    def bufferIsLoaded(self):
        if len(buffer)==0:
            return False
        else:
            return True

    def string_generator(self,size,chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def dummyMessageGenerator(self):
        doc = DatabaseOperationClient()
        #A dummy message generator.Generate a 600 digit arbitary string for constructing a stream of 761 bytes .

        random_byte_list = [643,random.randrange(100,643,1)]

        random_packet_bytes = random.choice(random_byte_list)
        aesAlgo = aes.AESCipher(doc.gen_key())
        dummy_message = self.string_generator(random_packet_bytes)
        cx = aesAlgo.aes_encrypt( dummy_message)
        broadcast_data = "BROADCAST||||" + doc.gen_key()+"||||"+cx
        return broadcast_data


class ClientToBarServerFactory(ClientFactory):
    #protocol = ClientToBarServerProtocol

    def startedConnecting(self, connector):
        print '~~ Start connection to BAR Server ~~'

    def __init__(self , data ,deffered , delay):
        self.data = data
        self.delay = delay
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

def trigger_bcp(route):
    buffer.append(route)

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

if __name__ == '__main__':
    BarServer()
