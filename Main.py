# Import smtplib for the actual sending function
import smtplib
import os

from os.path import join, dirname
from dotenv import load_dotenv
from email.mime.text import MIMEText

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Create a text/plain message
msg = MIMEText("This is a test message")

recipient = os.environ.get("RECIPIENT")
from_email = os.environ.get("FROM_EMAIL")
# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'This is a test message'
msg['From'] = from_email
msg['To'] = recipient

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP('localhost')
s.sendmail(from_email, recipient, msg.as_string())
s.quit()

