#!/usr/bin/python

# Author: https://github.com/maksaraswat/
# Source: https://github.com/maksaraswat/Python/blob/master/authemail.py

import smtplib
import logging
import string
import os

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

if not os.environ.get("LOG_LOCATION"):
    log_location = "/var/log/syslog"
else:
    log_location = os.environ.get("LOG_LOCATION")

# This is for logging any exceptions and/or errors. It will be logged in /var/log/syslog with message similar to
# '2014-08-18 16:24:58,064 ERROR service_start global name 'sendeail' is not defined'
logging.basicConfig(filename=log_location, format='%(asctime)s %(levelname)s %(funcName)s %(message)s', level=logging.ERROR)

# This function is used for sending authenticated email. 
def sendemail(status,To, From, Server, port, username, password, bodymessage):
    try:    
        SUBJECT = status
        TO = To
        FROM = From
        text = bodymessage
        BODY = string.join(( "From: %s" % FROM, "To: %s" % TO, "Subject: %s" % SUBJECT , "", text), "\r\n")
        server = smtplib.SMTP()
        server.connect(Server, port)
        server.starttls()
        server.login(username, password)        
        server.sendmail(FROM, [TO], BODY)
        server.quit()
    except Exception as e:
        logging.error(e)
        
def main():
    sendemail(status,To, From, Server, port, username, password, bodymessage)       

if __name__ == '__main__':
    main()
