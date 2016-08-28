import time
import string
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException, ServerSideRequestThrottlingException, NotLoggedInException

def accept_tos(username, password, location, proxy):
    try:
        accept_tos_helper(username, password, location, proxy)
    except ServerSideRequestThrottlingException as e:
        print('Server side throttling, Waiting 10 seconds.')
        time.sleep(10)
        accept_tos_helper(username, password, location, proxy)
    except NotLoggedInException as e1:
        print('Could not login, Waiting for 10 seconds')
        time.sleep(10)
        accept_tos_helper(username, password, location, proxy)

def accept_tos_helper(username, password, location, proxy):
    print "Trying to accept Terms of Service for {}.".format(username)
    failMessage = "Maybe the HTTPS proxy is not working? {} did not accept Terms of Service.".format(username)

    api = PGoApi()
    if proxy != None:
        api.set_proxy({"https":proxy})

    location = location.replace(" ", "")
    location = location.split(",")
    api.set_position(float(location[0]), float(location[1]), 0.0)
    api.set_authentication(provider = 'ptc', username = username, password = password)
    response = api.app_simulation_login()
    if response == None:
        print "Servers do not respond to login attempt. " + failMessage
        return

    time.sleep(1)
    req = api.create_request()
    req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
    response = req.call()
    if response == None:
        print "Servers do not respond to accepting the ToS. " + failMessage
        return

    print('Accepted Terms of Service for {}'.format(username))