import time
from url import *
        
def auto_captcha(captchakey, captchatimeout, gkey, count):
    # Now to automatically handle captcha
    print(str(count) + ". Starting autosolve recaptcha")
        
    #Ask 2captcha to solve this captcha
    recaptcharesponse = "Failed"
    while(recaptcharesponse == "Failed" or recaptcharesponse == "ERROR_NO_SLOT_AVAILABLE"):
        recaptcharesponse = openurl("http://2captcha.com/in.php?key=" + captchakey + "&method=userrecaptcha&googlekey=" + gkey)

    #Remove OK:    
    captchaid = recaptcharesponse[3:]
    
    #Wait for 2captcha to provide solved captcha
    recaptcharesponse = "CAPCHA_NOT_READY"
    print str(count) + ". We will wait 10 seconds for captcha to be solved by 2captcha"
    start_time = int(time.time())
    timedout = False
    while recaptcharesponse == "CAPCHA_NOT_READY":
        time.sleep(10)            
        elapsedtime = int(time.time()) - start_time
        if elapsedtime > captchatimeout:
            print(str(count) + ". Captcha timeout reached. Exiting.")
            timedout = True
            break
        print str(count) + ". Captcha still not solved, waiting another 10 seconds."
        recaptcharesponse = "Failed"
        while(recaptcharesponse == "Failed"):
            recaptcharesponse = openurl("http://2captcha.com/res.php?key=" + captchakey + "&action=get&id=" + captchaid)
    return {'timedout':timedout, 'recaptcharesponse':recaptcharesponse}