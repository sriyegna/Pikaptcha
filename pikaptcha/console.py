import argparse
import sys

import pikaptcha
from pikaptcha.ptcexceptions import *
#from pikaptcha.tos import *
from pikaptcha.gmailv import *
from pikaptcha.url import *

#from pgoapi.exceptions import AuthException, ServerSideRequestThrottlingException, NotLoggedInException
import pprint
import threading
import getopt
import urllib2
import imaplib
import string
import re


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
        help='Email template for the new account. Use something like aaaa@gmail.com (defaults to nothing).'
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
        '-gm', '--googlemail', type=str, default=None,
        help='This is the mail for the google account when auto verify is activate (Only required if plus mail is different from google mail)'
    )
    parser.add_argument(
        '-gp','--googlepass', type=str, default=None,
        help='This is the password for the google account and is require to activate auto verify when using the plus mail'
    )    
    parser.add_argument(
        '-t','--textfile', type=str, default="usernames.txt",
        help='This is the location you want to save usernames.txt'
    )
    parser.add_argument(
        '-of','--outputformat', type=str, default="compact",
        help='If you choose compact, you get user:pass. If you choose pkgo, you get -u user -p pass'
    )
    parser.add_argument(
        '-it','--inputtext', type=str, default=None,
        help='This is the location you want to read usernames in the format user:pass'
    ) 
    parser.add_argument(
        '-sn','--startnum', type=int, default=None,
        help='If you specify both -u and -c, it will append a number to the end. This allows you to choose where to start from'
    )
    parser.add_argument(
        '-ct','--captchatimeout', type=int, default=1000,
        help='Allows you to set the time to timeout captcha and forget that account (and forgeit $0.003).'
    )
    parser.add_argument(
        '-l','--location', type=str, default="40.7127837,-74.005941",
        help='This is the location that will be spoofed when we verify TOS'
    )
    parser.add_argument(
        '-px','--proxy', type=str, default=None,
        help='Proxy to be used when accepting the Terms of Services. Must be host:port (ex. 1.1.1.1:80). Must be a HTTPS proxy.'
    )        

    return parser.parse_args(args)

def _verify_autoverify_email(settings):
    if (settings['args'].googlepass is not None and settings['args'].plusmail == None and settings['args'].googlemail == None):
        raise PTCInvalidEmailException("You have to specify a plusmail (--plusmail or -m) or a google email (--googlemail or -gm) to use autoverification.")

def _verify_plusmail_format(settings):
    if (settings['args'].plusmail != None and not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", settings['args'].plusmail)):
        raise PTCInvalidEmailException("Invalid email format to use with plusmail.")

def _verify_twocaptcha_balance(settings):
    if (settings['args'].recaptcha != None and settings['balance'] == 'ERROR_KEY_DOES_NOT_EXIST'):
        raise PTCTwocaptchaException("2captcha key does not exist.")
    if (settings['args'].recaptcha != None and float(settings['balance']) < float(settings['args'].count)*0.003):
        raise PTCTwocaptchaException("It does not seem like you have enough balance for this run. Lower the count or increase your balance.")

def _verify_settings(settings):
    verifications=[_verify_autoverify_email, _verify_plusmail_format, _verify_twocaptcha_balance]
    for verification in verifications:
        try:
            verification(settings)
        except PTCException, e:
            print e.message
            print "Terminating."
            sys.exit()
    return True

def entry():
    """Main entry point for the package console commands"""
    args = parse_arguments(sys.argv[1:])
    captchabal = None
    if args.recaptcha != None:
        captchabal = "Failed"
        while(captchabal == "Failed"):
            captchabal = openurl("http://2captcha.com/res.php?key=" + args.recaptcha + "&action=getbalance")
        print("Your 2captcha balance is: " + captchabal)
        print("This run will cost you approximately: " + str(float(args.count)*0.003))

    username = args.username    
    
    if args.inputtext != None:
        print("Reading accounts from: " + args.inputtext)
        lines = [line.rstrip('\n') for line in open(args.inputtext, "r")]
        args.count = len(lines)
        
    if _verify_settings({'args':args, 'balance':captchabal}):
        if (args.googlepass is not None):
            with open(args.textfile, "a") as ulist:
                ulist.write("The following accounts use the email address: " + args.plusmail + "\n")
                ulist.close()
        for x in range(0,args.count):
            print("Making account #" + str(x+1))
            if ((args.username != None) and (args.count != 1) and (args.inputtext == None)):
                if(args.startnum == None):
                    username = args.username + str(x+1)
                else:
                    username = args.username + str(args.startnum+x)
            if (args.inputtext != None):
                username = ((lines[x]).split(":"))[0]
                args.password = ((lines[x]).split(":"))[1]
            error_msg = None
            try:
                try:
                    account_info = pikaptcha.random_account(username, args.password, args.email, args.birthday, args.plusmail, args.recaptcha, args.captchatimeout)
                    
                    print('  Username:  {}'.format(account_info["username"]))
                    print('  Password:  {}'.format(account_info["password"]))
                    print('  Email   :  {}'.format(account_info["email"]))
                    
                    # Accept Terms Service
                    #accept_tos(account_info["username"], account_info["password"], args.location, args.proxy)
        
                    # Verify email
                    if (args.googlepass is not None):
                        if (args.googlemail is not None):
                            email_verify(args.googlemail, args.googlepass)
                        else:
                            email_verify(args.plusmail, args.googlepass)

                    # Append usernames 
                    with open(args.textfile, "a") as ulist:
                        if args.outputformat == "pkgo":
                            ulist.write(" -u " + account_info["username"]+" -p "+account_info["password"]+"")
                        elif args.outputformat == "pkgocsv":
                            ulist.write("ptc,"+account_info["username"]+","+account_info["password"]+"\n")
                        else:
                            ulist.write(account_info["username"]+":"+account_info["password"]+"\n")
                        
                        ulist.close()
                # Handle account creation failure exceptions
                except PTCInvalidPasswordException as err:
                    error_msg = 'Invalid password: {}'.format(err)
                except (PTCInvalidEmailException, PTCInvalidNameException) as err:
                    error_msg = 'Failed to create account! {}'.format(err)
                except PTCException as err:
                    error_msg = 'Failed to create account! General error:  {}'.format(err)
            except Exception:
                import traceback
                error_msg = "Generic Exception: " + traceback.format_exc()
            if error_msg:
                if args.count == 1:
                    sys.exit(error_msg)
                print(error_msg)
        with open(args.textfile, "a") as ulist:
            ulist.write("\n")
            ulist.close()
