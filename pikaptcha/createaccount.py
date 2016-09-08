from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from captcha import *
from ptcexceptions import *
from tos import *

user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")
BASE_URL = "https://club.pokemon.com/us/pokemon-trainer-club"

# endpoints taken from PTCAccount
SUCCESS_URLS = (
    'https://club.pokemon.com/us/pokemon-trainer-club/parents/email',  # This initially seemed to be the proper success redirect
    'https://club.pokemon.com/us/pokemon-trainer-club/sign-up/',  # but experimentally it now seems to return to the sign-up, but still registers
)

# As both seem to work, we'll check against both success destinations until I have I better idea for how to check success
DUPE_EMAIL_URL = 'https://club.pokemon.com/us/pokemon-trainer-club/forgot-password?msg=users.email.exists'
BAD_DATA_URL = 'https://club.pokemon.com/us/pokemon-trainer-club/parents/sign-up'

class Account:
    'This class creates accounts'
    count = 0
    
    def __init__(self, username, password, email, birthday, captchakey, captchatimeout, proxyaddress, accnum, av, googpass, location, tos, outputfile):
        self.username = username
        self.password = password
        self.email = email
        self.birthday = birthday
        self.captchakey = captchakey
        self.captchatimeout = captchatimeout
        self.proxyaddress = proxyaddress
        self.accnum = accnum
        self.av = av
        self.tos = tos
        self.googpass = googpass
        self.location = location
        self.outputfile = outputfile
        Account.count += 1
        
    def createaccount(self):
        print(str(self.accnum) + ". Attempting to create user {user}:{pw}. Opening browser...".format(user=self.username, pw=self.password))
        driver = self.open_driver()
        self.first_page(driver)
        self.second_page(driver)
        
        #Verify response
        try:
            self.validate_response(driver)
        except:
            print(str(self.accnum) + ". Failed to get to last page")
        
        #Accept TOS
        if self.tos == 1:
            try:
                accept_tos(self.username, self.password, self.location, self.proxyaddress)
            except:
                print(str(self.accnum) + ". Unable to accept TOS")
                import traceback
                print(str(self.accnum) + ". Generic Exception: " + traceback.format_exc())
                
        with open(self.outputfile, "a") as ulist:
            ulist.write(self.username + ":" + self.password + "\n")        
                     
        
    def open_driver(self):
        #If using 2captcha, set user_agent for headless browser
        if self.captchakey != None:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = user_agent        
        
        #Set the starting service arguments for proxy
        if self.proxyaddress != None:
            if self.captchakey != None:
                service_args = ["--proxy=" + self.proxyaddress, '--proxy-type=' + "http"]
            else:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--proxy-server=%s' % self.proxyaddress)
                
        if self.captchakey != None:
            if self.proxyaddress != None:
                driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
            else:
                driver = webdriver.PhantomJS(desired_capabilities=dcap)
        else:
            if self.proxyaddress != None:
                driver = webdriver.Chrome(chrome_options=chrome_options)
            else:
                driver = webdriver.Chrome()
            driver.set_window_size(600, 600)
        return driver
            
        
    def first_page(self, driver):
        print("Creating account #: " + str(self.accnum))
        print(str(self.accnum) + ". Verifying age using birthday: {}".format(self.birthday))
        driver.get("{}/sign-up/".format(BASE_URL))
        
        #Verifying we go to birthday page
        if driver.current_url != "{}/sign-up/".format(BASE_URL):
            print(str(self.accnum) + ". Could not get to signup page.\n")
        assert driver.current_url == "{}/sign-up/".format(BASE_URL)
        
        elem = driver.find_element_by_name("dob")
        
        # Region workaround
        driver.execute_script("var input = document.createElement('input'); input.type='text'; input.setAttribute('name', 'dob'); arguments[0].parentNode.replaceChild(input, arguments[0])", elem)
        
        elem = driver.find_element_by_name("dob")
        elem.send_keys(self.birthday)
        elem.submit()
        
    def second_page(self, driver):
        print(str(self.accnum) + ". Entering account details")
        
        #Verifying we got to second page
        if driver.current_url != "{}/parents/sign-up".format(BASE_URL):
            print(str(self.accnum) + ". Could not get to second page.\n")
        assert driver.current_url == "{}/parents/sign-up".format(BASE_URL)        
        
        #Entering account data
        user = driver.find_element_by_name("username")
        user.clear()
        user.send_keys(self.username)
        
        elem = driver.find_element_by_name("password")
        elem.clear()
        elem.send_keys(self.password)        
        
        elem = driver.find_element_by_name("confirm_password")
        elem.clear()
        elem.send_keys(self.password)        
        
        elem = driver.find_element_by_name("email")
        elem.clear()
        elem.send_keys(self.email)        

        elem = driver.find_element_by_name("confirm_email")
        elem.clear()
        elem.send_keys(self.email)        

        #Checking boxes
        driver.find_element_by_id("id_public_profile_opt_in_1").click()
        driver.find_element_by_name("terms").click()
        

        #Captcha Solve
        if self.captchakey == None:
            #Manual captcha
            print(str(self.accnum) + ". Waiting 60s for you to solve captcha manually.\n")
            elem = driver.find_element_by_class_name("g-recaptcha")
            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
            #Waiting 1 min for captcha solve
            try:
                WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element_value((By.NAME, "g-recaptcha-response"), ""))
                print(str(self.accnum) + ". Captcha successful. Sleeping for 1 second...")
                time.sleep(1)
            except TimeoutException, err:
                print(str(self.accnum) + ". Timed out while manually solving captcha\n")
            except:
                print(str(self.accnum) + ". Timed out waiting for chrome")
        else: #auto captcha
            #Find sitekey. Apparently the same always, but I'm not taking chances
            html_source = driver.page_source
            gkey_index = html_source.find("https://www.google.com/recaptcha/api2/anchor?k=") + 47
            gkey = html_source[gkey_index:gkey_index+40]            

            #Autosolve captcha
            captchasolve = auto_captcha(self.captchakey, self.captchatimeout, gkey, self.accnum)

            if captchasolve['timedout'] == False:       
                solvedcaptcha = (captchasolve['recaptcharesponse'])[3:]
                elem = driver.find_element_by_name("g-recaptcha-response")
                elem = driver.execute_script("arguments[0].style.display = 'block'; return arguments[0];", elem)
                elem.clear()
                elem.send_keys(solvedcaptcha)      
                print str(self.accnum) + ". Solved captcha"
                
        try:
            user.submit()
        except StaleElementReferenceException:
            print(str(self.accnum) + ". Error StaleElementReferenceException")
        except:
            print(str(self.accnum) + ". General Exception while submitting")
            
        
    def validate_response(self, driver):
        url = driver.current_url
        if url in SUCCESS_URLS:
            return True
        elif url == DUPE_EMAIL_URL:
            raise PTCInvalidEmailException("Email already in use.\n")
        elif url == BAD_DATA_URL:
            if "Enter a valid email address." in driver.page_source:
                raise PTCInvalidEmailException("Invalid email.\n")
            else:
                raise PTCInvalidNameException("Username already in use.\n")
        else:
            raise PTCException("Generic failure. User was not created.")

        
        
 