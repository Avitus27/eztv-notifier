#!/usr/bin/python2.7

import os
import requests
import sys
import argparse
import logging
import verboselogs

from os.path import join, dirname
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from smtplib import SMTP, SMTPRecipientsRefused, SMTPHeloError, SMTPSenderRefused, SMTPDataError
from classes.eztv import Eztv

if sys.version_info[0] > 2:
    sys.stderr.write("Python3 not fully supported yet\n")
    exit(1)

VERSION = "1.2"
PROG_NAME = "eztv-notifier"

parser = argparse.ArgumentParser(
    description="Python based tool for getting torrents of shows from eztv",
    prog=PROG_NAME,
    epilog="Values passed as arguments override the .env")
parser.add_argument(
    '--version',
    action='version',
    version='%(PROG_NAME)s %(VERSION)s' %
    locals())
parser.add_argument('-v', '--verbose', action="count",
                    help="[-v|vv|vvv] Generates more output for debugging. More v, more output.", default=0)
parser.add_argument('-q', '--quiet', action="store_true",
                    help="Disable all output, including critical errors. Overrides verbose setting if set.")
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

args = parser.parse_args()
eztv = Eztv(args)
# get JSON from EZTV
request = []
payload = {'limit': str(eztv.max_torrents), 'page': 1}
request.append(
    requests.get(eztv.api_root, params=payload))
eztv.logger.debug("Current Request String: %s" % request[-1].url)

if request[-1].status_code == 200:
    eztv.logger.debug("First request successful")
    eztv.logger.spam("Response Content: %s" % request[-1].json())
    checkpoint_file = open('last_torrent', 'w')
    newest_torrent = str(
        request[-1].json()['torrents'][0]['date_released_unix'])
    checkpoint_file.write(newest_torrent)
    checkpoint_file.close()
else:
    eztv.logger.critical(request[-1].status_code + "\n")
    exit(1)

last_fetched_torrent_id = [0]
last_fetched_torrent_id[0] = int(
    request[-1].json()['torrents'][eztv.max_torrents - 1]['date_released_unix'])
torrent_found = False
page = 1
plain_text = "New Torrents available:\n"
rich_text = "New Torrents available:<br>\n"

eztv.logger.debug("Last seen torrent: %d" % eztv.last_seen_torrent)

try:
    while last_fetched_torrent_id[0] > last_seen_torrent:
        eztv.logger.debug(
            "Currently on page %d, last fetched torrent: %d" %
            (page, last_fetched_torrent_id[0]))
        for torrent in request[-1].json()['torrents']:
            if any(show in torrent['title'] for show in show_list):
                torrent_found = True
                if rich_mail:
                    rich_text += "<a rel=\"nofollow\" href=\"" + \
                        str(torrent['magnet_url']) + "\">" + \
                        str(torrent['title']) + "</a><br>\r\n"
                else:
                    rich_text += str(torrent['title']) + ":\t" + \
                        str(torrent['magnet_url']) + "<br><br>\r\n"
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
except Exception as e:
    eztv.logger.critical(str(e))


if not torrent_found:
    eztv.logger.info("No new torrents found, exiting.")
    exit(0)
