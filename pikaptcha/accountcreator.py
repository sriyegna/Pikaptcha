import time
import string
import random
import datetime
import urllib2

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pikaptcha.jibber import *
from pikaptcha.ptcexceptions import *
from pikaptcha.url import *

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


def _random_string(length=15):
    return generate_words(3)

def _random_email(local_length=10, sub_domain_length=5, top_domain=".com"):
    return "{local}@{sub_domain}{top_domain}".format(
        local=_random_string(local_length),
        sub_domain=_random_string(sub_domain_length),
        top_domain=top_domain
    )


def _random_birthday():
    start = datetime.datetime(1980, 1, 1)
    end = datetime.datetime(1990, 12, 31)
    diff = end - start
    random_duration = random.randint(0, diff.total_seconds())
    birthday = start + datetime.timedelta(seconds=random_duration)
    return "{year}-{month:0>2}-{day:0>2}".format(year=birthday.year, month=birthday.month, day=birthday.day)


def _validate_birthday(birthday):
    # raises PTCInvalidBirthdayException if invalid
    # split by -
    # has to be at least 2002 and after 1910
    # char length 10
    try:
        assert len(birthday) == 10

        # Ensure birthday is delimited by -
        # Ensure birthday is zero-padded
        year, month, day = birthday.split("-")
        assert year is not None and month is not None and day is not None
        assert len(year) == 4 and year.isdigit()
        assert len(month) == 2 and month.isdigit()
        assert len(day) == 2 and day.isdigit()

        # Check year is between 1910 and 2002, and also that it's a valid date
        assert datetime.datetime(year=1910, month=1, day=1) <= datetime.datetime(year=int(year), month=int(month), day=int(day)) <= datetime.datetime(year=2002, month=12, day=31)

    except (AssertionError, ValueError):
        raise PTCInvalidBirthdayException("Invalid birthday!")
    else:
        return True


def _validate_password(password):
    # Check that password length is between 6 and 15 characters long
    if len(password) < 6 or len(password) > 15:
        raise PTCInvalidPasswordException('Password must be between 6 and 15 characters.')
    return True


def create_account(username, password, email, birthday, captchakey2, captchatimeout):
    if password is not None:
        _validate_password(password)

    print("Attempting to create user {user}:{pw}. Opening browser...".format(user=username, pw=password))
    if captchakey2 != None:
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = user_agent
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
    else:
        driver = webdriver.Chrome()
        driver.set_window_size(600, 600)

    # Input age: 1992-01-08
    print("Step 1: Verifying age using birthday: {}".format(birthday))
    driver.get("{}/sign-up/".format(BASE_URL))
    assert driver.current_url == "{}/sign-up/".format(BASE_URL)
    elem = driver.find_element_by_name("dob")

    # Workaround for different region not having the same input type
    driver.execute_script("var input = document.createElement('input'); input.type='text'; input.setAttribute('name', 'dob'); arguments[0].parentNode.replaceChild(input, arguments[0])", elem)

    elem = driver.find_element_by_name("dob")
    elem.send_keys(birthday)
    elem.submit()
    # Todo: ensure valid birthday

    # Create account page
    print("Step 2: Entering account details")
    assert driver.current_url == "{}/parents/sign-up".format(BASE_URL)

    user = driver.find_element_by_name("username")
    user.clear()
    user.send_keys(username)

    elem = driver.find_element_by_name("password")
    elem.clear()
    elem.send_keys(password)

    elem = driver.find_element_by_name("confirm_password")
    elem.clear()
    elem.send_keys(password)

    elem = driver.find_element_by_name("email")
    elem.clear()
    elem.send_keys(email)

    elem = driver.find_element_by_name("confirm_email")
    elem.clear()
    elem.send_keys(email)

    driver.find_element_by_id("id_public_profile_opt_in_1").click()
    driver.find_element_by_name("terms").click()

    if captchakey2 == None:
        #Do manual captcha entry
        print("You did not pass a 2captcha key. Please solve the captcha manually.")
        elem = driver.find_element_by_class_name("g-recaptcha")
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        # Waits 1 minute for you to input captcha
        try:
            WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element_value((By.NAME, "g-recaptcha-response"), ""))
            print("Captcha successful. Sleeping for 1 second...")
            time.sleep(1)
        except TimeoutException, err:
            print("Timed out while manually solving captcha")
    else:
        # Now to automatically handle captcha
        print("Starting autosolve recaptcha")
        html_source = driver.page_source
        gkey_index = html_source.find("https://www.google.com/recaptcha/api2/anchor?k=") + 47
        gkey = html_source[gkey_index:gkey_index+40]
        recaptcharesponse = "Failed"
        while(recaptcharesponse == "Failed"):
            recaptcharesponse = openurl("http://2captcha.com/in.php?key=" + captchakey2 + "&method=userrecaptcha&googlekey=" + gkey)
        captchaid = recaptcharesponse[3:]
        recaptcharesponse = "CAPCHA_NOT_READY"
        elem = driver.find_element_by_class_name("g-recaptcha")
        print"We will wait 10 seconds for captcha to be solved by 2captcha"
        start_time = int(time.time())
        timedout = False
        while recaptcharesponse == "CAPCHA_NOT_READY":
            time.sleep(10)            
            elapsedtime = int(time.time()) - start_time
            if elapsedtime > captchatimeout:
                print("Captcha timeout reached. Exiting.")
                timedout = True
                break
            print "Captcha still not solved, waiting another 10 seconds."
            recaptcharesponse = "Failed"
            while(recaptcharesponse == "Failed"):
                recaptcharesponse = openurl("http://2captcha.com/res.php?key=" + captchakey2 + "&action=get&id=" + captchaid)
        if timedout == False:       
            solvedcaptcha = recaptcharesponse[3:]
            captchalen = len(solvedcaptcha)
            elem = driver.find_element_by_name("g-recaptcha-response")
            elem = driver.execute_script("arguments[0].style.display = 'block'; return arguments[0];", elem)
            elem.send_keys(solvedcaptcha)      
            print "Solved captcha"
    try:
        user.submit()
    except StaleElementReferenceException:
        print("Error StaleElementReferenceException!")

    try:
        _validate_response(driver)
    except:
        print("Failed to create user: {}".format(username))
        print("sleeping for 240 seconds")
        time.sleep(240)
        driver.close()
        raise

    print("Account successfully created.")
    driver.close()
    return True


def _validate_response(driver):
    url = driver.current_url
    if url in SUCCESS_URLS:
        return True
    elif url == DUPE_EMAIL_URL:
        raise PTCInvalidEmailException("Email already in use.")
    elif url == BAD_DATA_URL:
        if "Enter a valid email address." in driver.page_source:
            raise PTCInvalidEmailException("Invalid email.")
        else:
            raise PTCInvalidNameException("Username already in use.")
    else:
        raise PTCException("Generic failure. User was not created.")


def random_account(username=None, password=None, email=None, birthday=None, plusmail=None, recaptcha=None, captchatimeout=1000):
    try_username = _random_string() if username is None else str(username)
    password = _random_string() if password is None else str(password)
    try_email = _random_email() if email is None else str(email)
    captchakey2 = None if recaptcha is None else str(recaptcha)
    if plusmail is not None:
        pm = plusmail.split("@")
        try_email = pm[0] + "+" + try_username + "@" + pm[1]
    try_birthday = _random_birthday() if birthday is None else str(birthday)

    if birthday is not None:
        _validate_birthday(try_birthday)

    account_created = False
    while not account_created:
        try:
            account_created = create_account(try_username, password, try_email, try_birthday, captchakey2, captchatimeout)
        except PTCInvalidNameException:
            if username is None:
                try_username = _random_string()
            else:
                raise
        except PTCInvalidEmailException:
            if email is None:
                try_email = _random_email()
            else:
                raise

    return {
        "username": try_username,
        "password": password,
        "email": try_email
    }
