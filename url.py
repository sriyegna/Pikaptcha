import urllib2
import time

def openurl(address):
    try:
        urlresponse = urllib2.urlopen(address).read()
        if urlresponse == "ERROR_NO_SLOT_AVAILABLE":
            print "Received No Slot Available from 2captcha. Wait 3s. Maybe increase your 2captcha rate?"
            time.sleep(3)        
        return urlresponse        
    except urllib2.HTTPError, e:
        print("HTTPError = " + str(e.code))
    except urllib2.URLError, e:
        print("URLError = " + str(e.code))
    except Exception:
        import traceback
        print("Generic Exception: " + traceback.format_exc())
    print("Request to " + address + "failed.")    
    return "Failed"

def activateurl(address):
    try:
        urlresponse = urllib2.urlopen(address)
        return urlresponse
    except urllib2.HTTPError, e:
        print("HTTPError = " + str(e.code))
    except urllib2.URLError, e:
        print("URLError = " + str(e.code))
    except Exception:
        import traceback
        print("Generic Exception: " + traceback.format_exc())
    print("Request to " + address + "failed.")    
    return "Failed"