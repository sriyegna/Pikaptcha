from createaccount import *
import threading
from Queue import Queue
from jibber import *
from gmailv import *

def run_thread(q):
    while True:
        acc = q.get()
        acc.createaccount()
        q.task_done()


def pikaptcha(username, password, email, googpass, count, captchakey, captchatimeout, outputfile, lines, startnum, proxyaddress, location, av, tos, instances):
    threads = []
    accinfo = [None]*(instances+1)      
    q = Queue(maxsize=0)
    num_threads = instances
    
    for i in range(num_threads):
        t = threading.Thread(target=run_thread, args=(q,), name=(i))
        t.setDaemon(True)       
        t.start()
        
    for x in range(count):
        if (lines != None):
            username = ((lines[x]).split(":"))[0]
            password = ((lines[x]).split(":"))[1]        
        accdet = random_account(username, password, email, count)
        acc = Account(accdet['username'], accdet['password'], accdet['email'], accdet['birthday'], captchakey, captchatimeout, proxyaddress, (x+1), av, googpass, location, tos, outputfile)                
        q.put(acc)
        
    q.join()
    
    try:
        if av == 1:
            email_verify(email, googpass)
    except:
        print("Unable to verify email")
        import traceback
        print("Generic Exception: " + traceback.format_exc())      
    
    print("COMPLETED")
        
