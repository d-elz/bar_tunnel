from bar_tunnel.common.db import Bardb
from Crypto import Random

class baseClient(object):
    """
    This class is the main class of the Client
    operations.
    @param
    """
    def __init__(self):
        pass

class Client(baseClient):
    """
    This class is the main class of the Client
    operations.
    @param
    """
    def __init__(self):
        pass

    def client_operation(self,data):
        """
        Here is the class for every Client
        """
        pass

    def gen_key(self):
        '''
        Generates a new label or shared key.
        '''

        rpool =  Random.new()
        Random.atfork()
        return rpool.read(16).encode("hex")

    def logs(Filename):
        self.fp = open(Filename, 'a')
        log = "Bar[" + time.asctime(time.localtime()) + "] from "+ str(peer) + " with method: " + "\r"
        self.fp.write(log)

class DatabaseOperationClient(Client):
    def __init__(self):
        pass

    def checking_pseudonym(self,pseudonym):
        get_where_dict = { "nym" : pseudonym ,}
        db = Bardb()
        check = db.select_entries("List", get_where_dict)
        if check :
            print "There is a user with the same pseudonym"
            return True
        else:
            print "There isn t a user with the same pseudonym"
            return False


    def insert_list(self,nym,pk,shared_key,label):
        get_where_dict = { "nym" : nym ,
                            "pk" : pk ,
                            "shared_key" : shared_key ,
                            "label": label,
                            }
        db = Bardb()
        row_public_list = db.insert_entry("List", get_where_dict)
        print "The data was successfully added to database "
        #self.logs("logs")
        return row_public_list


    def delete_list(self,nym):#maybe if the user ISP change IP we have problem
        get_where_dict = { "nym" : nym ,}
        db = Bardb()
        row_active_list = db.delete_entries("List", get_where_dict)
        return row_active_list

    def check_update_nym(self, nym ,pk, shared_key , label):
        get_where_dict = { "nym" : nym ,}
        set_where_dict = { "shared_key" : shared_key ,
                            "label" : label,
                            }
        db = Bardb()
        check = db.select_entries("List", get_where_dict)
        if check :
            print "We allready contact this user . Now we update the keys!"
            #return False
            row_list = db.update_entries("List", get_where_dict , set_where_dict)
        else:
            print "First time you communicate with this user!"
            self.insert_list(nym,pk,shared_key,label)
            #return True
    def updata_list(self ,label, shared_key_new , label_new):
        get_where_dict = { "label" : label ,}
        set_where_dict = { "shared_key" : shared_key_new ,
                            "label" : label_new,
                            }
        db = Bardb()
        check = db.select_entries("List", get_where_dict)
        if check :
            print "We allready contact this user . Now we update the keys!"
            #return False
            row_list = db.update_entries("List", get_where_dict , set_where_dict)

    def select_list(self,label):
        get_where_dict = {"label" : label,}
        db = Bardb()
        row = db.select_entries("List", get_where_dict)
        return row

    def check_update_list(self, nym, cij):
        get_where_dict = { "nym" : nym ,}
        set_where_dict = { "cij" : cij ,
                            }
        db = Bardb()
        check = db.select_entries("List", get_where_dict)
        if check :
            print "There is a user with the same pseudonym"
            #return False
            row_list = db.update_entries("List", get_where_dict , set_where_dict)
        else:
            print "Nobody has the same name .You can proceed!"
            self.insert_exchange_key_list(nym,cij)
                #return True
