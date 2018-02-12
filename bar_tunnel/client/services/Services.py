from twisted.internet import ssl, reactor

##### Redirect to TOR Network imports
from txsocksx.client import SOCKS5ClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint , SSL4ClientEndpoint

import os
import hashlib
from Crypto import Random

#Our Repos
import bar_tunnel.common.generate_keys as gen
from txsocksx.tls import TLSWrapClientEndpoint


class baseService():

    def read_file(self ,path):
        f = open(path)   # Make a new file in output mode >>>
        text = f.read()  # Read entire file into a string >>> text 'Hello\nworld\n'
        f.close()
        return text

    def write_file(self ,path,nym):
        f = open(path,"w")   # Make a new file in output mode >>>
        text = f.write(nym)  # Read entire file into a string >>> text 'Hello\nworld\n'
        f.close()

    #Return a path of a file
    def dirc(self ,ex_file,back,file):
        dir_of_executable = os.path.dirname(ex_file)
        path = os.path.abspath(os.path.join(dir_of_executable, back)) + file
        return path

    #Return the ascii of the pk file
    def check_pk(self ,pk):
        if pk != None:
            return pk
        elif pk == None:
            gen.generate_rsa_key(4096)
            pk = self.read_file(self.dirc(__file__, "../../../keys" , "/public_key.pem"))
            return pk
        else:
            print "Something bad happen with the pk file "
            return

    def compute_cluster(self,nym,pk):
        nym_pki = nym + "||||" + pk
        hi = hashlib.sha256(nym_pki).hexdigest()
        
        #print int(hi, 16)

        # (b)Use the public system params M , m , Nmin , Nmax to find the cluster
        if int(hi, 16) % 2 == 0:
            cluster = "Bar1"
            #print "Server : " ,cluster
        else:
            cluster = "Bar2"
            #print "Server : " ,cluster
        return cluster

    def format(self ,args):
        """
        Here we format the data to ensure a specific format that can
        manipulate by the bar0 and bar server .
        """
        pass

    def TLS_TOR_conn(self,bar_server,bar_port):
        # Connect to TOR network
        torServerEndpoint = TCP4ClientEndpoint(reactor, "127.0.0.1", 9050)
        torEndpoint = SOCKS5ClientEndpoint(bar_server, bar_port, torServerEndpoint)

        #Use SSL - TLS to encrypt the connection between You and the server
        tlsEndpoint = TLSWrapClientEndpoint(ssl.ClientContextFactory(),torEndpoint)
        return tlsEndpoint

    def gen_key(self):
        '''
        Generates a new label or shared key.
        '''

        rpool =  Random.new()
        Random.atfork()
        return rpool.read(16).encode("hex")
