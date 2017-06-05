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
max_torrents = int(max_torrents)

show_list = os.environ.get("SHOW_LIST")

file = open('last_torrent', 'r')
last_seen_torrent = int(file.readline())
#print( last_torrent )
file.close()

# get JSON from EZTV
request = []
request.append(
    requests.get(
        'https://eztv.ag/api/get-torrents?limit=' +
        str(max_torrents) +
        '&page=1'))
if request[-1].status_code == 200:
    file = open('last_torrent', 'w')
    newest_torrent = str(
        request[-1].json()['torrents'][0]['date_released_unix'])
    file.write(newest_torrent)
    file.close()
else:
    print(request[-1].status_code)
    exit()

#last_fetched_torrent_id = sys.maxint
# Need to think about using this or the above
last_fetched_torrent_id = [0]
last_fetched_torrent_id[0] = int(
    request[-1].json()['torrents'][max_torrents - 1]['date_released_unix'])
torrent_found = False
page = 1
message_text = ""

print(
    "last_seen_torrent: " +
    str(last_seen_torrent) +
    "\r\nlast_fetched_torrent_id: " +
    str(last_fetched_torrent_id[0]))

while last_fetched_torrent_id[0] > last_seen_torrent:
    # TODO: These lines need to be redone.
    print("Page: " + str(page))
    print("last_seen_torrent: " + str(last_seen_torrent))
    print("last_fetched_torrent_id: " + str(last_fetched_torrent_id[0]))
    for torrent in request[-1].json()['torrents']:
        if any(show in torrent['title'] for show in show_list):
            torrent_found = True
            # print(torrent)
            print("Torrent Found!")
            message_text += "<a href=\"" + \
                str(torrent['magnet_url']) + "\">" + \
                str(torrent['title']) + "</a>\r\n"

#        if request.json()['torrents'][id]['title']
    last_fetched_torrent_id[0] = int(request[-1].json(
    )['torrents'][max_torrents - 1]['date_released_unix'])
    page += 1
    request.append(
        requests.get(
            'https://eztv.ag/api/get-torrents?limit=' +
            str(max_torrents) +
            '&page=' +
            str(page)))
# process it, checking for new episodes of the chosen shows

if not torrent_found:
    print("None found")
    exit()

# To be replaced with details of the new show and links
msg = MIMEText(message_text)
msg['Subject'] = mail_subject
msg['From'] = from_email
msg['To'] = recipient

if use_smtp:
    s = smtplib.SMTP(mail_host)
    s.sendmail(from_email, recipient, msg.as_string())
    s.quit()
else:
    authemail.sendemail(
        mail_subject,
        recipient,
        from_email,
        mail_host,
        mail_port,
        username,
        password,
        message_text)
