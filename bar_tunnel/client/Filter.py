
from argparse import Namespace
import os
import hashlib
from twisted.internet import ssl, reactor , defer
#HTTP Reguest
import urllib2
import requests
import json

import base64
import random
from Crypto.Hash import SHA
from Crypto import Random

#Our Repos
from bar_tunnel.common.db import Bardb
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.common import aes , rsa
import bar_tunnel.common.generate_keys as gen
from bar_tunnel.common import signature
import bar_tunnel.common.rsa as rsa
from bar_tunnel.protocols.ClientToBarServer import ClientToBarServerFactory

#Free port
import socket
from contextlib import closing

class baseFilterer():

    def read_file(self ,path):
        f = open(path)   # Make a new file in output mode >>>
        text = f.read()  # Read entire file into a string >>> text 'Hello\nworld\n'
        return text

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
            pk = self.read_file(self.dirc(__file__, "../../keys" , "/public_key.pem"))
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

class RegisterFilterer(baseFilterer):
    def format(self ,args):

        formated_data = args.service + "||||" + args.nym + "||||" + args.pk

        return formated_data

class LogInFilterer(baseFilterer):

    def format(self ,args):

        formated_data = args.service + "||||" + args.nym + "||||" + args.pk + "||||" + args.bridge_pk + "||||" + args.IP + "||||" + args.cluster

        return formated_data

class LogOutFilterer(baseFilterer):
    def format(self ,args):
        pass

class ExchangeFilterer(baseFilterer):
    """
    """

    def format(self , args ):

        formated_data = args.service + "||||" + args.nymj + "||||" + args.cij

        return formated_data



if __name__ == "__main__":
    #filterer()
    pass
