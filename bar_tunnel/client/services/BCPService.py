from twisted.internet import ssl, reactor , defer
from bar_tunnel.client.Filter import *

import requests
import json

import base64
import random

#Our Repos
from bar_tunnel.common.db import Bardb
from bar_tunnel.client.services.Services import baseService
from bar_tunnel.client.operations import DatabaseOperationClient
from bar_tunnel.common import aes
import bar_tunnel.common.rsa as rsa

import urllib2
class BCPService(baseService):

    """
    @method bar_route(): find and construct a bar routing path
    @method bar_route_encrypt_info()
    @method broacast_communication_protocol()
    """
    #Find if the user have change keys with friend
    def check_exchange_key(self ,nymi, nymj , pk):
        get_where_dict = {"nym" : nymj,}
        db = Bardb()
        row = db.select_entries("List", get_where_dict)

        if row:
            kiz = row[0]['shared_key']
            liz = row[0]['label']
            return kiz,liz
        else :
            print "You must exchanges keys first with client. Use the exchange_key operation!"
            return -1 , -1



    def bar_route(self,args):
        """

        """
        print "Construction BAR Onion routing .Please wait..."
        doc = DatabaseOperationClient()

        DOMAIN = urllib2.urlopen('http://ip.42.pl/raw').read() + ":2400" # use domain name insted(django project)

        #Get the Public List and the Active LIst from the BAR0(from the bulletin board of the BAR OFFICIAL site))
        url = 'http://'+ DOMAIN +'/bar/active_client/'
        r = requests.get(url)
        active_users = json.loads(r.content)

        url = 'http://'+ DOMAIN +'/bar/public_client/'
        r = requests.get(url)
        public_users = json.loads(r.content)

        #GET nymi ,pki
        nymi = args.nym
        pki = args.pk

            #Get nymj and pkj
        nymj = args.client
        pkj=""
        for public_user in public_users:
            if public_user.get("nym") == nymj:
                pkj = public_user.get("pk")
                break

        if not pkj:
            print "The user not exist.Is not register!"
            return -1

        kij,lij = self.check_exchange_key(nymi,nymj,pkj)
        if kij == -1:
            print "You have not exchange keys with the machine you wish to contact"
            return -1

        #Get the Cluster(Bar Server of the Uj)

        # a) Run log in to assign to cluster/Bar[n]

        # b) Compute hj to identify the logical
        #   partition of the indent receiver uj,
        #   e.g belonging to Cluster-y/Bar[n].
        clusterj = self.compute_cluster(nymj,pkj)
        #Exit Users - Uy(Paper)
        # c) Select from Active List a random Uy
        #   user belonging to Cluster-y/Bar[n]
        bridge_key_y = ""
        for i in range(1,20): # make 20 tries , if not find a user with clusterj aboart
            pick_random_user = random.choice(active_users)
            print pick_random_user.get("bar_server")
            if pick_random_user.get("bar_server") == clusterj:
                IPy = pick_random_user.get("ip")
                bridge_key_y = pick_random_user.get("bridge_pk")
                break

        if not bridge_key_y:
            print "There isn t a loggin user from the cluster you want to communicate (" + clusterj + ") . Try again later."
            return -1

        #Entry User - Ux(Paper)
        db = Bardb()
        list_users = db.select_entries("List")

        #Find our cluster
        clusteri = self.compute_cluster(nymi,pki)
        lix = ""
        for i in range(1,20):
            pick_random_user = random.choice(list_users)

            nymx = pick_random_user.get("nym")
            pkx = pick_random_user.get("pk")
            clusterx = self.compute_cluster(nymx,pkx)
            if clusteri == clusterx:
                kix = pick_random_user.get("shared_key")
                lix = pick_random_user.get("label")
                break
        if not lix:
            print "We cant find a user from your cluster.It isn t safe to broadcast the message"
            return -1

        #Data we sending back
        args.kij = str(kij)
        args.lij = str(lij)
        args.lij_new = doc.gen_key()# f) Choose random keys k'iz l'iz
        args.kij_new = doc.gen_key()# f) Choose random keys k'iz l'iz

        args.bridge_key_y = bridge_key_y
        args.IPy = str(IPy)

        args.kix_new = doc.gen_key()# f) Choose random keys k'iz l'iz
        args.lix_new = doc.gen_key()# f) Choose random keys k'iz l'iz
        args.lix = str(lix)
        args.kix = str(kix)

        doc.updata_list(args.lix,args.kix_new ,args.lix_new)
        doc.updata_list(args.lij ,args.kij_new ,args.lij_new)
        return args




    def bar_route_encrypt_info(self,args,message):

        # g) Encrypt ( [pkj,kij,lij] , k'ij, l'ij , m ) to get (lij,cij)
        plaintextj = args.lij + "||||"+ args.lij_new + "||||"+ args.kij_new +  "||||" + message
        cj = aes.aes_encrypt(args.kij,plaintextj)

        # h) Compute cy = enc-bridge_key-cy[lij,cj] using [id , IPj , b_keyj ] in Active List
        plaintexty = args.lij + "||||" + cj

        cy = rsa.encrypt(args.bridge_key_y,plaintexty)
        #bridge_pkey_y =open("/home/bar/GitHub2/tor_tunnel/keys/private_key.pem").read()
        #decrypt_data = rsa.decryption(bridge_pkey_y,cy)
        #print decrypt_data
        # i) Encrypt ( [pkx,kix,lix] , k'ix, l'ix , (IPy,Cy) ) to get (lix,cix)
        IP_Cy = args.IPy + "||||" + cy
        plaintextx = args.kix_new + "||||"+ args.lix_new + "||||"+ args.lix +  "||||" + IP_Cy
        cx = aes.aes_encrypt(args.kix,plaintextx)

        # j) Broadcast (lix,cix)
        formated_data =  args.lix + "||||" + cx # args.service + "|" + nymj + "|" + cij

        # k) UpdateListEntry ( Listi; [pkj , kij , lij] )
        #doc.check_update_nym("jjjj","",kij_new,lij_new)

        return formated_data

    def format(self , args):
        """
        This is the method that incarnate the BAR Network.
        Build the onion (bar route) and encrypted the
        message.
        """
        bar_route_args = self.bar_route(args)
        if bar_route_args != -1:
            encrypted_message = self.bar_route_encrypt_info(bar_route_args,args.message)
        else:
            return -1
        return encrypted_message

def bcp_conn(bcp_args):

    bcp = BCPService()
    constructing_route = bcp.format(bcp_args)

    if constructing_route != -1:
        broadcast_data = "BROADCAST||||" + constructing_route
        bar_server_factory = ClientToBarServerFactory(broadcast_data,"d")
        reactor.connectTCP(bcp_args.bar_server_host,int(bcp_args.bar_server_port),bar_server_factory)
    else:
        print "Something not works in bar route construction"


def bcp_service(args):
    bcp_conn(args)
