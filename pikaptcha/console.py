import argparse
import sys

import pikaptcha
from pikaptcha.ptcexceptions import *

from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException, ServerSideRequestThrottlingException, NotLoggedInException
import pprint
import time
import threading
import getopt
import urllib2
import imaplib
import string


def parse_arguments(args):
    """Parse the command line arguments for the console commands.
    Args:
      args (List[str]): List of string arguments to be parsed.
    Returns:
      Namespace: Namespace with the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Pokemon Trainer Club Account Creator'
    )
    parser.add_argument(
        '-u', '--username', type=str, default=None,
        help='Username for the new account (defaults to random string).'
    )
    parser.add_argument(
        '-p', '--password', type=str, default=None,
        help='Password for the new account (defaults to random string).'
    )
    parser.add_argument(
        '-e', '--email', type=str, default=None,
        help='Email for the new account (defaults to random email-like string).'
    )
    parser.add_argument(
        '-m', '--plusmail', type=str, default=None,
        help='Email template for the new account. Use something like aaaa+@gmail.com (defaults to nothing).'
    )
    parser.add_argument(
        '-av', '--autoverify', type=bool, default=False,
        help='Append the argument -av True if you want to use autoverify with +mail.'
    )
    parser.add_argument(
        '-b', '--birthday', type=str, default=None,
        help='Birthday for the new account. Must be YYYY-MM-DD. (defaults to a random birthday).'
    )
    parser.add_argument(
        '-c','--count', type=int,default=1,
        help='Number of accounts to generate.'
    )
    parser.add_argument(
        '-r','--recaptcha', type=str, default=None,
        help='Your 2captcha key from settings'
    )
    parser.add_argument(
        '-gp','--googlepass', type=str, default=None,
        help='This is the password for the google account you are using with plusmail'
    )    
    parser.add_argument(
        '-t','--textfile', type=str, default="usernames.txt",
        help='This is the location you want to save usernames.txt'
    )    
    parser.add_argument(
        '-l','--location', type=str, default="40.7127837,-74.005941",
        help='This is the location that will be spoofed when we verify TOS'
    )        

    return parser.parse_args(args)


def entry():
    """Main entry point for the package console commands"""
    args = parse_arguments(sys.argv[1:])
    if args.recaptcha != None:
        captchabal = urllib2.urlopen("http://2captcha.com/res.php?key=" + args.recaptcha + "&action=getbalance").read()
        print("Your 2captcha balance is: " + captchabal)
        print("This run will cost you approximately: " + str(float(args.count)*0.003))
    if (args.recaptcha != None and float(captchabal) < float(args.count)*0.003):
        print("It does not seem like you have enough balance for this run. Lower the count or increase your balance.")
        sys.exit()
    else:
        if (args.autoverify == True):
            with open(args.textfile, "a") as ulist:
                ulist.write("The following accounts use the email address: " + args.plusmail[:len(args.plusmail)-11] + "@gmail.com\n")
                ulist.close()
        for x in range(0,args.count):
            print("Making account #" + str(x+1))
            try:
                account_info = pikaptcha.random_account(args.username, args.password, args.email, args.birthday, args.plusmail, args.recaptcha)
                
                print('  Username:  {}'.format(account_info["username"]))
                print('  Password:  {}'.format(account_info["password"]))
                print('  Email   :  {}'.format(account_info["email"]))
                
                # Accept Terms Service
                accept_tos(account_info["username"], account_info["password"], args.location)
    
                # Verify email
                if (args.autoverify == True):
                    email_verify(args.plusmail, args.googlepass)
                
                # Append usernames 
                with open(args.textfile, "a") as ulist:
                    ulist.write(account_info["username"]+":"+account_info["password"]+"\n")
                    ulist.close()
            # Handle account creation failure exceptions
            except PTCInvalidPasswordException as err:
                print('Invalid password: {}'.format(err))
            except (PTCInvalidEmailException, PTCInvalidNameException) as err:
                print('Failed to create account! {}'.format(err))
            except PTCException as err:
                print('Failed to create account! General error:  {}'.format(err))

def accept_tos(username, password, location):
        try:
                accept_tos_helper(username, password, location)
        except ServerSideRequestThrottlingException as e:
                print('Server side throttling, Waiting 10 seconds.')
                time.sleep(10)
                accept_tos_helper(username, password, location)
        except NotLoggedInException as e1:
                print('Could not login, Waiting for 10 seconds')
                time.sleep(10)
                accept_tos_helper(username, password, location)

def accept_tos_helper(username, password, location):
        api = PGoApi()
        location = location.replace(" ", "")
        location = location.split(",")
        api.set_position(float(location[0]), float(location[1]), 0.0)
        api.login('ptc', username, password)
        time.sleep(1)
        req = api.create_request()
        req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
        response = req.call()
        print('Accepted Terms of Service for {}'.format(username))

def proc_mail(M):
    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return
    else:
        for num in data[0].split():
            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                print "Error getting message "
                return
            bodymsg = (M.fetch(num, "(UID BODY[TEXT])"))[1][0][1]
            validkey_index = bodymsg.find("https://club.pokemon.com/us/pokemon-trainer-club/activated/")
            if validkey_index != -1:
                validlink = bodymsg[validkey_index:validkey_index+94]
                try:
                    validate_response = urllib2.urlopen(validlink)
                    validate_response = validate_response.getcode()
                    print "Verified email and trashing Email with key: " + validlink[60:] + "\n"
                    M.store(num,'+X-GM-LABELS', '\\Trash')
                except urllib2.URLError:
                    print "Unable to verify email.\n"
                    M.store(num,'+X-GM-LABELS', '\\Trash')

def email_verify(plusmail, googlepass):
    time.sleep(5)
    #Waiting 5 seconds before checking email
    email_address = plusmail[:len(plusmail)-11] + "@gmail.com"
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