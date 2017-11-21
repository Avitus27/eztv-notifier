#!/usr/bin/python

import os
import json
import requests
import sys

from os.path import join, dirname
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from smtplib import SMTP

if sys.version_info[0] > 2:
    print("Python3 not fully supported yet")
    exit(1)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

recipient = os.environ.get("RECIPIENT")
from_email = os.environ.get("FROM_EMAIL")
mail_host = os.environ.get("MAIL_HOST")
mail_port = os.environ.get("MAIL_PORT")
mail_subject = os.environ.get("MAIL_SUBJECT")
if not os.environ.get("FULL_RICH_MAIL"):
    rich_mail = False
else:
    rich_mail = True
if not os.environ.get("USE_SMTP"):
    use_smtp = False
    username = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASS")
else:
    use_smtp = True

max_torrents = int(os.environ.get("MAX_TORRENTS"))

show_list = os.environ.get("SHOW_LIST")
show_list = show_list.split(",")

file = open('last_torrent', 'r')
last_seen_torrent = int(file.readline())
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
    exit(1)

last_fetched_torrent_id = [0]
last_fetched_torrent_id[0] = int(
    request[-1].json()['torrents'][max_torrents - 1]['date_released_unix'])
torrent_found = False
page = 1
plain_text = "New Torrents available:\n"
rich_text = "New Torrents available:<br>\n"

while last_fetched_torrent_id[0] > last_seen_torrent:
    for torrent in request[-1].json()['torrents']:
        if any(show in torrent['title'] for show in show_list):
            torrent_found = True
            if rich_mail:
                rich_text += "<a rel=\"nofollow\" href=\"" + \
                    str(torrent['magnet_url']) + "\">" + \
                    str(torrent['title']) + "</a><br>\r\n"
            else:
                rich_text += str(torrent['title']) + \
                    ":\t" + str(torrent['magnet_url']) + "<br><br>\r\n"
            plain_text += str(torrent['title']) + "\t" + \
                str(torrent['magnet_url']) + "\r\n\r\n"

    last_fetched_torrent_id[0] = int(request[-1].json(
    )['torrents'][max_torrents - 1]['date_released_unix'])
    page += 1
    request.append(
        requests.get(
            'https://eztv.ag/api/get-torrents?limit=' +
            str(max_torrents) +
            '&page=' +
            str(page)))

if not torrent_found:
    print("None found")
    exit(0)

msg = MIMEMultipart('alternative')
msg['Subject'] = mail_subject
msg['From'] = from_email
msg['To'] = recipient
part1 = MIMEText(plain_text, 'plain')
part2 = MIMEText(rich_text, 'html')
msg.attach(part1)
msg.attach(part2)

s = SMTP(mail_host)

if not use_smtp:
    s.login(username, password)

s.sendmail(from_email, recipient, msg.as_string())
s.quit()
