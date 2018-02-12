
import os
import hashlib

#Our Repos
import bar_tunnel.common.generate_keys as gen

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

class RegisterFilterer(baseFilterer):
    """
    For each service we make a filterer to format the data in a specific
    manner that server can understand.Furthermore when we want to change
    the format we just change this methods e.g
    (args.service + "!!!!" + args.nym + "!!!!" ... )

    """
    def format(self ,args):

        formated_data = args.service + "||||" + args.nym + "||||" + args.pk

        return formated_data

class LogInFilterer(baseFilterer):
    def format(self ,args):

        formated_data = args.service + "||||" + args.nym + "||||" + args.pk + "||||" + args.bridge_pk + "||||" + args.IP + "||||" + args.cluster

        return formated_data

class ExchangeFilterer(baseFilterer):

    def format(self , args ):

        formated_data = args.service + "||||" + args.nymj + "||||" + args.cij

        return formated_data



if __name__ == "__main__":
    #filterer()
    pass
