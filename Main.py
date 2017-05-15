import smtplib
import os
import authemail

from os.path import join, dirname
from dotenv import load_dotenv
from email.mime.text import MIMEText

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

recipient = os.environ.get("RECIPIENT")
from_email = os.environ.get("FROM_EMAIL")
mail_host = os.environ.get("MAIL_HOST")
if not os.environ.get("USE_SMTP"):
    use_smtp = False
    username = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASS")
else:
    use_smtp = True

# get JSON from EZTV

# process it, checking for new episodes of the chosen shows

msg = MIMEText("This is a test message") # To be replaced with details of the new show and links
msg['Subject'] = 'New episodes have been found!'
msg['From'] = from_email
msg['To'] = recipient

if use_smtp:
    s = smtplib.SMTP(mail_host)
    s.sendmail(from_email, recipient, msg.as_string())
    s.quit()
