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
from smtplib import SMTP, SMTPRecipientsRefused, SMTPHeloError, SMTPSenderRefused, SMTPDataError

if sys.version_info[0] > 2:
    sys.stderr.write("Python3 not fully supported yet\n")
    exit(1)

parser = argparse.ArgumentParser(
    description="Python based tool for getting torrents of shows from eztv",
    prog="eztv-notifier",
    epilog="Values passed as arguments override the .env")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-v', '--verbose', action="store_true",
                    help="Generates more output for debugging")
parser.add_argument(
    '-e',
    '--env',
    nargs='?',
    help="Sets the path to the .env file. If the string is 'False', then the program will not look for a .env file (not recommended). Default is the directory the file is running in.")
parser.add_argument(
    '-r',
    '--recipient',
    help="Specifies what email address the script should send to.")
parser.add_argument(
    '-s',
    '--sender',
    help="Specifies what email address the script should send from.")
parser.add_argument(
    '--smtp',
    action="store_true",
    help="If set, the script will try using SMTP instead of logging in.")
parser.add_argument(
    '--host',
    help="Specifies the address of the mail host to send from. IP:PORT format not accepted")
parser.add_argument(
    '--port',
    help="Specifies the port of the mail host to send from.")
parser.add_argument(
    '-u',
    '--user',
    help="The username to log into the mail host. Not used for SMTP.")
parser.add_argument(
    '-p',
    '--password',
    help="The password to log into the mail host. Not used for SMTP.")
parser.add_argument(
    '--subject',
    help="The subject line of the email to be sent.")
parser.add_argument(
    '--rich',
    action="store_true",
    help="If set, the email will be formatted with full HTML. May not work in all clients (GMail strips magnet links for example).")
parser.add_argument(
    '--max',
    help="The max number of torrents to get per requeset to eztv.")
parser.add_argument(
    '--shows',
    nargs="*",
    help="A list of the shows to search for on eztv, space seperated, may be encapuslated in double quotes.")
parser.add_argument(
    '-a',
    '--api',
    help="Set the root of the API. e.g. ./Main --api https://eztv.ag/api/get-torrents")

verbose = False
setup_error = False
use_env = True
args = parser.parse_args()
api_root = "https://eztv.ag/api/get-torrents"

if args.verbose:
    verbose = True
if args.env == "False":
    use_env = False
if use_env:
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
    max_torrents = int(os.environ.get("MAX_TORRENTS"))
    show_list = os.environ.get("SHOW_LIST").split(",")
    rich_mail = os.environ.get("FULL_RICH_MAIL") or args.rich
    use_smtp = os.environ.get("USE_SMTP") or args.smtp
    if os.environ.get("API_ROOT"):
        api_root = os.environ.get("API_ROOT")
else:
    rich_mail = args.rich
    use_smtp = args.smtp

if args.recipient:
    recipient = args.recipient
if args.sender:
    from_email = args.sender
if args.host:
    mail_host = args.host
if args.port:
    mail_port = args.port
if args.subject:
    mail_subject = args.subject
if not use_smtp:
    username = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASS")
if args.max:
    max_torrents = args.max
if args.shows:
    show_list = args.show
if args.api:
    api_root = args.api

file = open('last_torrent', 'r')
last_seen_torrent = int(file.readline())
file.close()

# get JSON from EZTV
request = []
request.append(
    requests.get(
        api_root +
        '?limit=' +
        str(max_torrents) +
        '&page=1'))
if request[-1].status_code == 200:
    file = open('last_torrent', 'w')
    newest_torrent = str(
        request[-1].json()['torrents'][0]['date_released_unix'])
    file.write(newest_torrent)
    file.close()
else:
    sys.stderr.write(request[-1].status_code + "\n")
    exit(1)

last_fetched_torrent_id = [0]
last_fetched_torrent_id[0] = int(
    request[-1].json()['torrents'][max_torrents - 1]['date_released_unix'])
torrent_found = False
page = 1
plain_text = "New Torrents available:\n"
rich_text = "New Torrents available:<br>\n"

if verbose:
    print "Last seen torrent: %d" % last_seen_torrent

while last_fetched_torrent_id[0] > last_seen_torrent:
    if verbose:
        print "Currently on page %d, last fetched torrent: %d" % (page, last_fetched_torrent_id[0])
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
            api_root +
            '?limit=' +
            str(max_torrents) +
            '&page=' +
            str(page)))

if not torrent_found:
    if verbose:
        print "No new torrents found, exiting."
    exit(0)

try:
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
except SMTPRecipientsRefused as e:
    sys.stderr.write("Recipients were refused\n")
    sys.stderr.write(e)
    exit(1)
except SMTPHeloError:
    sys.stderr.write("The mail server didn't reply to our HELO, exiting\n")
    exit(1)
except SMTPSenderRefused:
    sys.stderr.write(
        "The mail server doesn't allow this user to send mail. Are you sure this user exits?\n")
    exit(1)
except SMTPDataError:
    sys.stderr.write(
        "The server replied with an unxpected error code. exiting\n")
    exit(1)
except BaseException as e:
    sys.stderr.write("An unhandled error occured. The program will now quit\n")
    sys.stderr.write("> " + str(e) + "\n")
    exit(1)
