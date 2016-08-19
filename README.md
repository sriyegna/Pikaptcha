#pikaptcha - Mass Pokemon Go Account Creator and ToS verifier
==============================================================


Description
-----------
Automatically creates Pokemon Trainer Club accounts, and reads the ToS making them usable after the recent Niantic patch.
Text files will be created in the directory that pikaptcha is run from. Pikaptcha can be run globally (so you do not have to be in any specific folder to run it)

Installation
------------
**Windows users**

Install all the necessary prerequisites as listed here:

http://pgm.readthedocs.io/en/develop/basic-install/windows.html
According to ^^, you should either let python set the environment paths or set it yourself. You need
C:\Python27 and C:\Python27\Scripts

You will also need to download the chromedriver.exe:

http://chromedriver.storage.googleapis.com/2.23/chromedriver_win32.zip

Unzip and paste the chromedriver.exe file in "C:\Python27\Scripts" Folder.

Finally, open up your command prompt and paste this command:

    pip install git+https://github.com/sriyegna/pikaptcha

If you are still having troubles, you can join us at discord channel https://discord.gg/VvwyS
Please let us know what your issue is, instead of just saying it doesnt work. Copying the error code you receive is very helpful.

**Linux users/OSX**

(OSX prerequisites)Selenium support:

    brew install chromedriver
(Ubuntu and variants prerequisites)

    sudo apt-get install chromium-browser


(Everyone from this point)
From your terminal run::

    pip install git+https://github.com/sriyegna/pikaptcha

If you have both python2 and python3 installed::

    pip2 install git+https://github.com/sriyegna/pikaptcha

If given permission errors::

    sudo pip2 install git+https://github.com/sriyegna/pikaptcha

Updating to the latest version
------------------------------

    pip install --upgrade git+https://github.com/sriyegna/pikaptcha

Uninstalling
------------

    pip uninstall pikaptcha

Usage
-----
**Command line interface:**

After installing the package run 'pikaptcha' from the terminal to create a new accounts.
Optional parameters include *--username*, *--password*, *--email*, *--count*, *--recaptcha*
Use *--help* for command line interface help.

usernames.txt file is created in the current working directory.

Example 1 (Create entirely random new account)::

    ~pikaptcha -r %RECAPTCHAKEY%
    Created new account:
      Username:  traynagmoh
      Password:  rossstrubhep
      Email   :  fantsniskflast@gastsnub.com
      
Example 2 (Create 2 accounts with the same password)::

    ~pikaptcha -p password -c 2 -r %RECAPTCHAKEY%
    Created new account:
      Username:  trodbectflik
      Password:  password
      Email   :  prepsteptcruct@gastsnub.com
    Created new account:
      Username:  truzplospduv
      Password:  password
      Email   :  linkslampnob@gastsnub.com
      
Example 3 (Create a new account with specified parameters)::

    ~pikaptcha --username=mycustomusername --password=hunter2 --email=verifiable@lackmail.ru -r %RECAPTCHAKEY%
    Created new account:
      Username:  mycusttruzplospduv:trodbectflikomusername
      Password:  hunter2
      Email   :  verifiable@lackmail.ru

Example 4 (Create a new account with mail using "plus trick")::

    ~pikaptcha -m myemail+@gmail.com -r %RECAPTCHAKEY%
    Created new account:
      Username:  wongblofttez
      Password:  password
      Email   :  myemail+swuchdranflost@gmail.com
	  
	  
Common Issues
-------------
Cannot find chrome binary. Chrome should be installed to the default directory in C. Ensure that it is. If it is, try uninstalling and reinstalling.

Cannot find PgoApi module.
	~pip install git+https://github.com/keyphact/pgoapi.git

Chromedriver not found. Your chromedriver.exe file is either not in C:\python27\scripts OR you did put the file there but you do not have an environment path setup for C:\python27\scripts

pip is not recognized as an internal or external command. You do not have an environment path setup for C:\python27\scripts OR python 2.7.12 is not installed

'git is not recognized as an internal or external command. You did not install GIT

selenium not found
	~pip install selenium
