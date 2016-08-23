import time
import string
from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException, ServerSideRequestThrottlingException, NotLoggedInException

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