import argparse
import sys

import pikaptcha
from pikaptcha.ptcexceptions import *

from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException, ServerSideRequestThrottlingException
import pprint
import time
import threading
import getopt


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

    return parser.parse_args(args)


def entry():
    """Main entry point for the package console commands"""
    args = parse_arguments(sys.argv[1:])
    for x in range(0,args.count):
        try:
            account_info = pikaptcha.random_account(args.username, args.password, args.email, args.birthday, args.plusmail, args.recaptcha)
            
            print('  Username:  {}'.format(account_info["username"]))
            print('  Password:  {}'.format(account_info["password"]))
            print('  Email   :  {}'.format(account_info["email"]))
            print('\n')
            
            # Accept Terms Service
            
            accept_tos(account_info["username"], account_info["password"])
            # Append usernames 
            with open("usernames.txt", "a") as ulist:
                ulist.write(account_info["username"]+":"+account_info["password"]+"\n")
                ulist.close()
        # Handle account creation failure exceptions
        except PTCInvalidPasswordException as err:
            print('Invalid password: {}'.format(err))
        except (PTCInvalidEmailException, PTCInvalidNameException) as err:
            print('Failed to create account! {}'.format(err))
        except PTCException as err:
            print('Failed to create account! General error:  {}'.format(err))

def accept_tos(username, password):
    flag = False
    while not flag:
        try:
            api = PGoApi()
            #Set spawn to NYC
            api.set_position(40.7127837, -74.005941, 0.0)
            api.login('ptc', username, password)
            time.sleep(0.5)
            req = api.create_request()
            req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
            response = req.call()
            print('Accepted Terms of Service for {}'.format(username))
            flag = True
        except ServerSideRequestThrottlingException:
            print('This happens, just restart')
