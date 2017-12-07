from twisted.internet import ssl, reactor , defer
from twisted.internet.protocol import Factory, Protocol ,ClientFactory , ServerFactory

"""
Protocol for the communication with BAR Coordinator(BAR0).
Making a connection with BAR0 and waiting for the ok message( 0 or -1 )
to make another connection to Bar server using the Log In Service

"""

class ClientToBar0Protocol(Protocol):

    def __init__(self , data ,deferred,login_args):
        self.data = data
        self.d = deferred
        self.login_args = login_args
        #Not working
    #def makeConnection(self,connector):
        #print "Try to establish a connection"
        #print "Send forst hello message"
        #self.transport.write("HEllo From CLient")
        #pass

    def connectionMade(self):
        peer = self.transport.getPeer()
        host = self.transport.getHost()
        print "~~ Connected to Bar-Coordinator at " +str(peer)
        self.transport.write(self.data)
        #self.transport.loseConnection()

    ## We cant accepting connection except from Tor
    def dataReceived(self, data):
        #Getting message from the Register Service of BAR0
        if data.split('||||')[0] == "Register":
            if data.split('||||')[1] == "0":
                print "Successfull registration!"
            elif data.split('||||')[1] == "-1":
                print "Unsuccessfull registration!"
            else:
                print "Register : bad Request"
        #Getting message from the LogIn Service of BAR0
        elif data.split('||||')[0] == "LogIn":
            #When the server return -1 the user can t logged in for some reason
            if data.split("||||")[1] != "-1":
                print "Bar0 Server : You successfull log in"
                self.bar_server = data.split("||||")[1]
                self.d.callback(self) # calling the bar_server_conn function of the tunnelling.py file to connect to
            elif data.split("||||")[1] == "-1":
                print "Bar0 Server : You can t log in "

            else:
                print "Not possible operation!"
        #Getting message from the ExchangeKey Service of BAR0
        elif data.split('||||')[0] == "ExchangeKey":
            print data.split('||||')[1]
        else:
            print "Garbage: " + data
        self.transport.loseConnection()

    ## is called when a connection could not be established
    def connectionFailed(self,connector,  reason):
        peer = self.transport.getPeer()
        print "Connection failed to Bar-Coordinator " + str(peer)
        print "Reason was : ", reason
        reactor.stop()

    ## is called when a connection was made and then disconnected
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        print "~~ Disconnected from Bar-Coordinator at " +str(peer)
        self.transport.loseConnection()
        #reactor.stop()


class ClientToBar0Factory(ClientFactory):

        #Not working for some reason
    def startedConnecting(self, connector):
        print '~~ Start connection to BAR Coordinator ~~'

    def __init__(self , data ,deferred,login_args):
        self.data = data
        self.d = deferred
        self.login_args = login_args

    def buildProtocol(self , addr):
        #print "Client To Bar0 Protocol connect"
        return ClientToBar0Protocol(self.data , self.d , self.login_args)

        #Not working for some reason
    def clientConnectionFailed(self, connector, reason):
        #print "Connection failed."
        #ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        pass

        #Not working for some reason
    def clientConnectionLost(self, connector, reason):
        #print "Connection lost."
        #ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        pass
