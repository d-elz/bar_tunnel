from twisted.internet import ssl, reactor , defer
from twisted.internet.protocol import Factory, Protocol ,ClientFactory , ServerFactory
from twisted.protocols.basic import NetstringReceiver

from bar_tunnel.protocols.ClientToBarServer import ClientToBarServerFactory , ClientToBarServerProtocol

##### Redirect to TOR Network imports
from txsocksx.client import SOCKS5ClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint , SSL4ClientEndpoint

from txtorcon import endpoints as tor_endpoint
##### SSL - TLS import
from txsocksx.tls import TLSWrapClientEndpoint

import time
import optparse
import os

#import delay message
from bar_tunnel.protocols.ClientToBarServer import trigger_bcp
from bar_tunnel.client.operations import DatabaseOperationClient
import bar_tunnel.common.rsa as rsa
import base64
import requests
import json
protoc = "Listener"

class ListenerProtocol(Protocol):

    def __init__(self ,factory,bar_server,bar_server_port,login):
        self.bar_server = bar_server
        self.bar_server_port = bar_server_port
        self.factory = factory
        self.login = login

    def decrypt_exchange_messages(self,nymi):
        exchange_keys = self.get_exchange_keys(nymi)
        private_key = self.read_file(self.dirc(__file__, "../../../keys" , "/private_key.pem"))
        for exchange_key in exchange_keys:
            cij = exchange_key.get("cij")
            self.decrypt_message(cij,private_key)


    def decrypt_message(self,encrypt_message_b64,private_key):
        db_client = DatabaseOperationClient()
        cij =  base64.b64decode(encrypt_message_b64)

        decrypted_message = ""
        for encrypt_message in cij.split('////'):
            de_block, correct_decrypt = rsa.decrypt(private_key, encrypt_message)
            decrypted_message += de_block[:200]
        if correct_decrypt:
            nymj = decrypted_message.split("||||")[0]
            pkj = decrypted_message.split("||||")[1]
            kij = decrypted_message.split("||||")[2]
            lij = decrypted_message.split("||||")[3]
            sij = decrypted_message.split("||||")[4]
            print "There is the data " , nymj , pkj , kij , lij , sij , decrypted_message

        else:
            print "Wrong key or data!"

    def dataReceived(self, data):
        print "GETTING DATA:"
        
        #decrypt_data , correct_decrypt = rsa.decrypt(self.login.bridge_pk,data)
        private_key = self.read_file(self.dirc(__file__, "../../../keys", "/private_key.pem"))

        decrypt_data = self.decrypt_message(data, private_key)

        #if correct_decrypt:
        print "SENDING TO:" + str(self.bar_server) + ":" + str(self.bar_server_port)
        #print "BAR Server : " + str(self.bar_server) + ":" + str(self.bar_server_port)
        #broadcast_message(decrypt_data,self.bar_server,self.bar_server_port)
        broadcast_data = "BROADCAST||||" + decrypt_data
        trigger_bcp(broadcast_data)

        #else:
        #    print "Wrong key or data!"

        self.transport.loseConnection()

    def connectionMade(self):

        #Here we can make a web service request to bar0 to check
        #if the user who sendthe message is in the active list
        #If it is then is inside the bar network , if not we can t
        #accept the message and we drop it
        print "Checking the connection from BAR Network"
        #if conn != BAR Network
        print "We accept connection only from BAR Network . Dropping..."

        #url = 'http://188.4.169.218:8080/bar/active_client'
        #r=requests.get(url)
        #active_users = json.loads(r.content)

        self.factory.clientConnectionMade(self)

    ## is called when a connection could not be established
    def connectionFailed(self,  reason):
        peer = self.transport.getPeer()
        print "Connection failed to Client" + str(peer)
        print "Reason was : ", reason
        reactor.stop()

    ## is called when a connection was made and then disconnected
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ "+protoc+" Disconnected from Client at " +str(peer)
        self.transport.loseConnection()


class ListenerFactory(ServerFactory):

    def startedConnecting(self, connector):
        print "~~ "+protoc+" -> Start connection to Client ~~"

    def buildProtocol(self , addr):
        #print "Listener Protocol connect"
        return ListenerProtocol(self,self.bar_server,self.bar_server_port, self.login_info )

    def __init__(self, reactor, communicator_factory,login_info ):
        self.reactor = reactor
        self.communicator_factory = communicator_factory
        self.login_info = login_info

    def clientConnectionMade(self, client):
        self.client = client

    def send_message(self, msg):
        self.client.transport.write(msg)

    def set_bar_server_host(self,bar_server):
        self.bar_server = bar_server
    def set_bar_server_port(self,bar_server_port):
        self.bar_server_port = bar_server_port

def broadcast_message(DATA,bar_server,bar_server_port):
    broadcast_data = "BROADCAST||||" + DATA
    bar_server_factory = ClientToBarServerFactory(broadcast_data,"")
    reactor.connectTCP(bar_server,bar_server_port,bar_server_factory)


if __name__ == '__main__':
    broadcast_message("something")
