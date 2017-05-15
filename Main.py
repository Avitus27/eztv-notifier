# Import smtplib for the actual sending function
import smtplib
import os

from os.path import join, dirname
from dotenv import load_dotenv
from email.mime.text import MIMEText

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

recipient = os.environ.get("RECIPIENT")
from_email = os.environ.get("FROM_EMAIL")

# get JSON from EZTV

# process it, checking for new episodes of the chosen shows

msg = MIMEText("This is a test message") # To be replaced with details of the new show and links
msg['Subject'] = 'New episodes have been found!'
msg['From'] = from_email
msg['To'] = recipient

s = smtplib.SMTP('localhost')
s.sendmail(from_email, recipient, msg.as_string())
s.quit()
