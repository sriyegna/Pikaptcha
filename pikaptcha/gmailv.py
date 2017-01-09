import time
import imaplib
import string
import urllib2
from pikaptcha.url import *


def proc_mail(M):
    rv, data = M.search(None, "ALL")
    if rv!= 'OK':
        print "No messages found!"
        return
    else:
        start_time = time.clock()
        for num in data[0].split():
            if (time.clock() - start_time) > 30:
                print("It has been more than 30 seconds. Please use an email address with an empty inbox.")
            rv, data = M.fetch(num, '(RFC822)')
            if rv!= 'OK':
                print "Error getting message."
                return
            subjmsg = M.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT)])')
            subjmsg = subjmsg[1][0][1]
            if subjmsg.find("Trainer_Club_Activation") != -1:
                bodymsg = (M.fetch(num, "(UID BODY[TEXT])"))[1][0][1]
                validkey_index = bodymsg.find("https://club.pokemon.com/us/pokemon-trainer-club/activated/")
                if validkey_index != -1:
                    validlink = bodymsg[validkey_index:validkey_index+94]
                    validlink = validlink.replace("\r", "") \
                                         .replace("\n", "") \
                                         .replace("=", "")
                    try:
                        validate_response = "Failed"
                        while(validate_response == "Failed"):
                            validate_response = activateurl(validlink)
                        print "Verified email and trashing Email with key: " + validlink[60:] + "\n"
                        M.store(num,'+X-GM-LABELS', '\\Trash')
                    except urllib2.URLError:
                        print "Unable to verify email.\n"
                        M.store(num,'+X-GM-LABELS', '\\Trash')

def email_verify(plusmail, googlepass):
    time.sleep(5)
    #Waiting 5 seconds before checking email
    email_address = plusmail
    M = imaplib.IMAP4_SSL('imap.gmail.com')    
    try:
        M.login(email_address, googlepass)
        print "Logged in to: " + email_address

        rv, mailboxes = M.list()
        rv, data = M.select("INBOX")
        if rv == 'OK':
            print "Processing mailbox..."
            proc_mail(M)
            M.close()
        M.logout()
    except imaplib.IMAP4.error:
        print "Unable to login to: " + email_address + ". Was not verified\n"
