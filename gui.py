from Tkinter import *
from tkFileDialog import *
import imaplib
import string
from url import *
from pikaptcha import *

glob_inputfile = None
glob_outputfile = "user.txt"


def exitfn():
    sys.exit()
    
def proxyfn():
    filename = askopenfilename(defaultextension=".txt")
    global glob_proxyfile
    glob_proxyfile = filename

def openfn():
    filename = askopenfilename(defaultextension=".txt")
    global glob_inputfile
    glob_inputfile = filename

def savefn():
    filename = asksaveasfilename(defaultextension=".txt")
    global glob_outputfile
    glob_outputfile = filename
    
def verify_autoverify(email_address, googlepass):
    if email_address == "":
        print "You have to specify an email if you are using autoverify"
    if googlepass == "":
        print "You have to specify a google pass if you are using autoverify"
    if email_address.find("gmail") == -1:
        print "Use a gmail address"
    else:
        M = imaplib.IMAP4_SSL('imap.gmail.com')    
        try:
            M.login(email_address, googlepass)
            print "Email credentials valid"
            M.logout()
        except imaplib.IMAP4.error:
            print "Unable to login to: " + email_address
            
def verify_count(count, startnum):
    try:
        count = int(count)
        startnum = int(startnum)
        return True
    except:
        print "Count or startnum is not an integer"
        
def verify_instances(instances, count):
    try:
        instances = int(instances)
        if not isinstance(count/instances, int):
            print("# of accounts must be a multiple of instances")
            sys.exit()
        return instances
    except:
        print("Error verifying instance")
        
def verify_2captcha(captchakey, count):
    captchabal = "Failed"
    while(captchabal == "Failed"):
        captchabal = openurl("http://2captcha.com/res.php?key=" + str(captchakey) + "&action=getbalance")
        if captchabal == "ERROR_KEY_DOES_NOT_EXIST":
            print("Invalid 2Captcha key given")
            sys.exit()
    print("Your 2captcha balance is: " + captchabal)
    print("This run will cost you approximately: " + str(float(count)*0.003))    
    if (float(captchabal) < float(count)*0.003):
        print("It does not seem like you have enough balance for this run. Lower the count or increase your balance.")
        
def verify_timeout(captchatimeout):
    try:
        captchatimeout = int(captchatimeout)
        if not isinstance(captchatimeout, int):
            print "Timeout is invalid"
            sys.exit()
    except:
        print "Timeout is invalid"

def validate_username(username):
    if len(username) > 0 and len(username) <= 15:
        print "Valid user"
        return True
    else:
        print "Invalid User"
        sys.exit()
        return False
    
def runbutton():
    try:
        username = glob_user.get()
        password = glob_pass.get()
        email = glob_email.get()
        captchakey = glob_recaptcha.get()
        captchatimeout = glob_captchatimeout.get()
        count = glob_count.get()
        startnum = glob_startnum.get()
        inputfile = glob_inputfile
        outputfile = glob_outputfile
        location = glob_location.get()
        av = glob_av.get()
        tos = glob_tos.get()
        googpass = glob_googpass.get()
        instances = glob_instances.get()
        proxy = glob_proxy.get()
                        
        #Verify username
        if username == "":
            username = None
        else:
            if not validate_username(username):
                sys.exit()
                
        if password == "":
            password = None
        
        #Verify email    
        if email == "":
            email = None
        elif email.find("@gmail") == -1 and av == 1:
            print("You chose autoverify but didn't give a gmail address.")
            sys.exit()
        elif email.find("@gmail") != 1 and av == 1:
            verify_autoverify(email, googpass)
            
        #Verify and parse location
        if location == "":
            location = ["43.659221", "-79.389857"]
        else:
            location = location.split(",")
            location = location.split(" ")       
        
        #Verify count & startnum
        if count == "":
            count = 1
        if startnum == "":
            startnum = 1
        if count != "" or startnum != "":
            if not verify_count(count, startnum):
                sys.exit()
            else:
                count = int(count)
                startnum = int(startnum)
        
        #Verify Captcha
        if captchakey == "":
            captchakey = None
        else:
            verify_2captcha(captchakey, count)
            
        #Verify captchatimeout
        if captchatimeout == "":
            captchatimeout = 1000
        else:
            verify_timeout(captchatimeout)
        
        #Read input file
        lines = None
        if inputfile != None:
            print("Reading accounts from: " + inputfile)
            lines = [line.rstrip('\n') for line in open(inputfile, "r")]
            count = len(lines)        
            
        #Verify Proxy    
        if proxy == "":
            proxy = None
            
        #Verify instances
        if instances == "":
            instances = 1
        else:
            try:
                instances = int(instances)
            except:
                print("Invalid instances value given")
                
        email = "dopoke4584@gmail.com"
        googpass = "sonicspeed"
        count = 3
        captchakey = "34ee7a4cd3121b207f84028304ef2ed9"
        instances = "2"
        
        print("Creating " + str(count) + " accounts.")
        pikaptcha(username, password, email, googpass, count, captchakey, captchatimeout, outputfile, lines, startnum, proxy, location, av, tos, int(instances))
    except:
        import traceback
        print("Generic Exception: " + traceback.format_exc())                            
        print("Run Stopped")
        

root = Tk()
root.title("Pikaptcha")
Label(root, text="Username").grid(row=0)
Label(root, text="Password").grid(row=1)
Label(root, text="Email").grid(row=2)
Label(root, text="Email Password").grid(row=3)
Label(root, text="2Captcha Key").grid(row=4)
Label(root, text="Captcha Timeout").grid(row=5)
Label(root, text="# of Accounts").grid(row=6)
Label(root, text="Start #").grid(row=7)
Label(root, text="# of instances").grid(row=8)
Label(root, text="Location").grid(row=9)
Label(root, text="HTTP Proxy").grid(row=10)

glob_user = Entry(root)
glob_pass = Entry(root)
glob_email = Entry(root)
glob_googpass = Entry(root)
glob_recaptcha = Entry(root)
glob_captchatimeout = Entry(root)
glob_count = Entry(root)
glob_startnum = Entry(root)
glob_instances = Entry(root)
glob_location = Entry(root)
glob_proxy = Entry(root)

glob_user.grid(row=0, column=1)
glob_pass.grid(row=1, column=1)
glob_email.grid(row=2, column=1)
glob_googpass.grid(row=3, column=1)
glob_recaptcha.grid(row=4, column=1)
glob_captchatimeout.grid(row=5, column=1)
glob_count.grid(row=6, column=1)
glob_startnum.grid(row=7, column=1)
glob_instances.grid(row=8, column=1)
glob_location.grid(row=9, column=1)
glob_proxy.grid(row=10, column=1)

glob_av = IntVar()
glob_tos = IntVar()
Checkbutton(root, text="Auto-Verify", variable=glob_av).grid(row=11, sticky=W)
Checkbutton(root, text="Complete TOS", variable=glob_tos).grid(row=11, column = 1, sticky=W)

Button(root, text='Input File', command=openfn).grid(row=12, column = 0, sticky=W, pady=4, padx = 4)
Button(root, text='Output File', command=savefn).grid(row=12, column = 1, sticky=W, pady=4, padx = 4)
Button(root, text='Quit', command=root.quit).grid(row=13, column = 0, sticky=W, pady=4, padx = 4)
Button(root, text="Run", command=runbutton).grid(row=13, column=1, sticky=W, pady=4)

mainloop()