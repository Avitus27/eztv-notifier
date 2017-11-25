#!/usr/bin/python

import os
import json
import requests
import sys
import argparse

from os.path import join, dirname
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from smtplib import SMTP

##RECIPIENT="admin@localhost"
##FROM_EMAIL="admin@localhost"
##USE_SMTP="True" # Use an empty string for False, anything else for True
##MAIL_HOST="localhost"
##MAIL_PORT=25
##MAIL_USER="user"
##MAIL_PASS="password"
##MAIL_SUBJECT="New episodes have been found!"
##FULL_RICH_MAIL=""
##
##MAX_TORRENTS=10 # Max number of torrents per request to EZTV
### lower value results in smaller, but possibly more, responses
##
##SHOW_LIST="XYZ,ABC"

parser = argparse.ArgumentParser(description="Python based tool for getting torrents of shows from eztv", prog="eztv-notifier")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-v', '--verbose', action="store_true", help="Generates more output for debugging")
parser.add_argument('-e', '--env', help="Sets the path to the .env file. Default is the directory the file is running in.")
parser.add_argument('-r', '--recipient', help="Specifies what email address the script should send to.")
parser.add_argument('-f', '--from', help="Specifies what email address the script should send from.")
parser.add_argument('--smtp', action="store_true", help="If set, the script will try using SMTP instead of logging in.")
parser.add_argument('--host', help="Specifies the address of the mail host to send from. IP:PORT format not accepted")
parser.add_argument('--port', help="Specifies the port of the mail host to send from.")
parser.add_argument('-u', '--user', help="The username to log into the mail host. Not used for SMTP.")
parser.add_argument('-p', '--password', help="The password to log into the mail host. Not used for SMTP.")
parser.add_argument('-s', '--subject', help="The subject line of the email to be sent.")
parser.add_argument('--rich', action="store_true", help="If set, the email will be formatted with full HTML. May not work in all clients (GMail strips magnet links for example).")
parser.add_argument('--max', help="The max number of torrents to get per requeset to eztv.")
parser.add_argument('--shows', help="A list of the shows to search for on eztv.")


verbose = False;
args = parser.parse_args()
if args.verbose:
	verbose = True

if sys.version_info[0] > 2:
    print("Python3 not fully supported yet")
    exit(1)

if args.env:
	dotenv_path = join(dirname(args.env), '.env')
else:
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
