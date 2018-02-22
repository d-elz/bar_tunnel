#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

from bar_tunnel.client.services.LogIn import login_service
from bar_tunnel.client.services.Register import register_service
from bar_tunnel.client.services.ExchangeKey import exchange_key_service

import re

from bar_tunnel.client.services.Services import baseService

def parse_cli():

    #Function to filter and accepto only 3 15 character names and alphanumeric pseudonyms
    def filter_nym(nym):
        if len(nym) > 2 and len(nym) < 16:
                if re.match(r'^[A-Z]|[a-z]|[0-9]$' , nym):
                    return nym
                else:
                    return None
        else:
            print "You must reg a nym between 3 and 15 characters"
            return None

    def filter_delay(delay):
        if delay < 1 and delay > 20:
            pass
        else:
            print "You must give a delay between 1 and 20 seconds"
            return None

    parser = argparse.ArgumentParser(
    prog = "Bar Tunnel", # %(prog)s : used to display the prog variable whenever you want
    usage = """%(prog)s ->"""
,
description="""

          #########              #########          #########
        #         ##           # ####### #         #         #
       #         ##          # # ##### # #        #         #
      # #######            # # # ### # # #       #########
     #         ##        # # # # # # # # #      # #
    #          ##      # # #         # # #     #   #
   #         ##      # # #   TUNNEL  # # #    #     #
  ###########      # # #             # # #   #       #


This is a bar client . Follow the commands to register to Bar Network

python2  bin/register --nym Darth Yoda --pk_file /home/path/to/pk/file

You have to put optionaly host port of the bar server and
your own public key if you want so . If you dont know how to
generate a public and a private key pair we can
provide you and genarate one public and private key pair

Start Tor first "sudo systemctl start tor "

    """,
    epilog = "This is the best way to register to Bar Network",
    )

    subparsers = parser.add_subparsers(title='subcommands',
                                    description='This is the subcommands',
                                    help='additional help',
                                    dest = 'operation')

    register_parser = subparsers.add_parser('register')
    login_parser = subparsers.add_parser('login')
    exchange_key_parser = subparsers.add_parser('exchange_key')

    register_parser.add_argument('--nym',  help='Your own unique pseudonym to register to Bar server', required=True , type = filter_nym)
    register_parser.add_argument('--pk', help='The path of your public key file . If you dont have leave it blank to auto genarate a key pair for you',type=file)
    #register_parser.add_argument('--bar0',  help='The IP of the BAR server', required=True )
    #subparsers = register_parser.add_subparsers(help='sub-command help', dest='register_operation')

    #newuser_register_parser = subparsers.add_parser('newuser', help='Subparser for registring a new user.')

    login_parser.add_argument('--nym',  help='Your own unique pseudonym to login to Bar server' , type = filter_nym)
    login_parser.add_argument('--pk', help='The path of your public key file.If you didn t import it -we did- and is inside keys folder',type=file)
    login_parser.add_argument('--listenport', help='This is the port for CLient to CLiet communication to forward the message to bar server',type=int)
    login_parser.add_argument('--proxyport', help='This is the proxy port for the bcp connection',type=int)
    login_parser.add_argument('--delaymessage', help='Give the gummy messager delay in seconds', type=int)

    exchange_key_parser.add_argument('--nym',  help='Your own unique pseudonym to register/login to Bar server',  type = filter_nym)
    exchange_key_parser.add_argument('--fnym',  help='The psuedonym of the friend you wish to talk', required=True , type = filter_nym)

    return parser

BAR0 = "bar0.cs.unipi.gr"#urllib2.urlopen('http://ip.42.pl/raw').read() #put domain name when is uploaded
BAR0_PORT = 443
def register(args):

    args.service = "Register"
    args.serverport = BAR0_PORT
    args.bar0 = BAR0

    if not args.nym:
        print "You need to specify a pseudonym with --nym. Aborting..."
        return

    if args.pk:
        public_key = open(args.pk.name)   # Make a new file in output mode >>>
        args.pk = public_key.read()


    register_service(args)

def login(args):

    args.serverport = BAR0_PORT
    args.bar0 = BAR0
    args.service = "LogIn"
    #args.listenport = 0
    baseS = baseService()

    #Put an exception somewhere here!
    if not args.nym:
        args.nym = baseS.read_file(baseS.dirc(__file__,"../keys","/pseudonym"))

    if not args.pk:
        args.pk = baseS.read_file(baseS.dirc(__file__, "../keys", "/public_key.pem"))
    else:
        args.pk = baseS.read_file(args.pk.name)

    if not args.proxyport:
        print "You need to specify a proxyport  with --proxyport. Aborting..."
        return

    if not args.delaymessage:
        args.delaymessage = 5


    #if not args.listenport:
    #    print "You need to specify a listener port for CLient to CLiet communication. Aborting..."
    #    return


    login_service(args)

def exchange_key(args):
    '''

    '''
    args.service = "ExchangeKey"
    args.serverport = BAR0_PORT
    args.bar0 = BAR0
    baseS = baseService()

    if not args.nym:
        args.nym = baseS.read_file(baseS.dirc(__file__, "../keys", "/pseudonym"))


    if not args.fnym:
        print "You need to specify a public key path file with --pk. Aborting..."
        return

    exchange_key_service(args)


def caller(func, args):

    return func(args)


def pybar():

    operations = {
        "register": register,
        "login":login,
        "exchange_key":exchange_key
    }

    parser = parse_cli() # get the parser object
    args = parser.parse_args() # put to args all the user info (--nym and --pk)
    if type(operations[args.operation]) is dict: # if inside the operation dictionary the args.operation is dictionary
        caller(operations[args.operation][getattr(args, args.operation + "_operation")], args) # operations[register][args.register_operation] getattr(x, 'foobar') is equivalent to x.foobar
    else: # if is not a dict and is (e.g "register": register )
        caller(operations[args.operation], args)

def run():
    pybar()
