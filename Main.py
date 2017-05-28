import smtplib
import os
import authemail
import json
import requests
import sys

from os.path import join, dirname
from dotenv import load_dotenv
from email.mime.text import MIMEText

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

recipient = os.environ.get("RECIPIENT")
from_email = os.environ.get("FROM_EMAIL")
mail_host = os.environ.get("MAIL_HOST")
mail_port = os.environ.get("MAIL_PORT")
mail_subject = os.environ.get("MAIL_SUBJECT")
if not os.environ.get("USE_SMTP"):
    use_smtp = False
    username = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASS")
else:
    use_smtp = True

max_torrents = os.environ.get("MAX_TORRENTS")

file = open('last_torrent', 'r')
last_seen_torrent = file.readline()
#print( last_torrent )
file.close()

# get JSON from EZTV
request = requests.get('https://eztv.ag/api/get-torrents?limit=' + max_torrents + '&page=1')
if request.status_code == 200:
    file = open('last_torrent', 'w')
    newest_torrent = str(request.json()['torrents'][0]['id'])
    file.write(newest_torrent)
    file.close()
    #print(newest_torrent)
    #print(last_torrent == newest_torrent)
    exit()
else:
    print(request.status_code)
    exit()

last_fetched_torrent_id = sys.maxint
#last_fetched_torrent_id = (int) request.json()['torrents'][max_torrents - 1]['id']
page = 1
while not last_fetched_torrent_id <= last_seen_torrent:

    pass
# process it, checking for new episodes of the chosen shows
message_text = "Placeholder text"

msg = MIMEText(message_text) # To be replaced with details of the new show and links
msg['Subject'] = mail_subject
msg['From'] = from_email
msg['To'] = recipient

if use_smtp:
    s = smtplib.SMTP(mail_host)
    s.sendmail(from_email, recipient, msg.as_string())
    s.quit()
else:
    authemail.sendemail(mail_subject, recipient, from_email, mail_host, mail_port, username, password, message_text)
