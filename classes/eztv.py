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

class Eztv:
    """An EZTV class"""
    
    verbose = False
    use_env = True
    #args = parser.parse_args()
    api_root = "https://eztv.ag/api/get-torrents"
    last_seen_torrent = 0
    max_torrents = 5
    logger = verboselogs.VerboseLogger('%(prog)s')
    verboseLevel = 0
    plain_text = ""
    rich_text = ""
    
    def __init__(self, args):
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
        
        if args.verbose:
            verboseLevel = args.verbose

        if self.verboseLevel >= 3:
            self.logger.setLevel(logging.SPAM)
        elif self.verboseLevel >= 2:
            self.logger.setLevel(logging.DEBUG)
        elif self.verboseLevel >= 1:
            self.logger.setLevel(logging.VERBOSE)

        if args.quiet:
            self.logger.setLevel(logging.NOTSET)

        if args.env == "False":
            use_env = False
        else:
            use_env = True
        if use_env:
            if args.env:
                dotenv_path = join(dirname(args.env), '.env')
            else:
                dotenv_path = join(dirname(__file__), '../.env')
            load_dotenv(dotenv_path)
            self.recipient = os.environ.get("RECIPIENT")
            self.from_email = os.environ.get("FROM_EMAIL")
            self.mail_host = os.environ.get("MAIL_HOST")
            self.mail_port = os.environ.get("MAIL_PORT")
            self.mail_subject = os.environ.get("MAIL_SUBJECT")
            self.max_torrents = int(os.environ.get("MAX_TORRENTS"))
            self.show_list = os.environ.get("SHOW_LIST").split(",")
            self.rich_mail = os.environ.get("FULL_RICH_MAIL") or args.rich
            self.use_smtp = os.environ.get("USE_SMTP") or args.smtp
            if os.environ.get("API_ROOT"):
                api_root = os.environ.get("API_ROOT")
        else:
            self.rich_mail = args.rich
            self.use_smtp = args.smtp

        if args.recipient:
            self.recipient = args.recipient
        if args.sender:
            self.from_email = args.sender
        if args.host:
            self.mail_host = args.host
        if args.port:
            self.mail_port = args.port
        if args.subject:
            self.mail_subject = args.subject
        if not self.use_smtp:
            self.username = os.environ.get("MAIL_USER")
            self.password = os.environ.get("MAIL_PASS")
        if args.max:
            self.max_torrents = args.max
        if args.shows:
            self.show_list = args.show
        if args.api:
            self.api_root = args.api

    def get_torrents(self):
        while last_fetched_torrent_id[0] > last_seen_torrent:
            self.logger.debug("Currently on page %d, last fetched torrent: %d" % (page, last_fetched_torrent_id[0]))
            for torrent in request[-1].json()['torrents']:
                if any(show in torrent['title'] for show in show_list):
                    torrent_found = True
                    if rich_mail:
                        self.rich_text += "<a rel=\"nofollow\" href=\"" + \
                            str(torrent['magnet_url']) + "\">" + \
                            str(torrent['title']) + "</a><br>\r\n"
                    else:
                        self.rich_text += str(torrent['title']) + ":\t" + \
                            str(torrent['magnet_url']) + "<br><br>\r\n"
                    self.plain_text += str(torrent['title']) + "\t" + \
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
                    
    def get_checkpoint(self):
        checkpoint_file = open('last_torrent', 'r')
        self.last_seen_torrent = int(checkpoint_file.readline())
        checkpoint_file.close()
        self.logger.debug("last_seen_torrent: %d" % self.last_seen_torrent)
        return self.last_seen_torrent
        
    def set_checkpoint(self, last_seen_torrent):
        checkpoint_file = open('last_torrent', 'w')
        checkpoint_file.write(str(last_seen_torrent))
        checkpoint_file.close()
    
    def send_email(self):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.mail_subject
            msg['From'] = self.from_email
            msg['To'] = self.recipient
            part1 = MIMEText(self.plain_text, 'plain')
            part2 = MIMEText(self.rich_text, 'html')
            msg.attach(part1)
            msg.attach(part2)

            s = SMTP(self.mail_host)

            if not self.use_smtp:
                s.login(self.username, self.password)

            s.sendmail(self.from_email, self.recipient, msg.as_string())
            s.quit()
            self.logger.info("Success, email with torrents sent to %s" % self.recipient)
        except SMTPRecipientsRefused as e:
            self.logger.critical("Recipients were refused\n")
            self.logger.critical(e)
            exit(1)
        except SMTPHeloError:
            self.logger.critical("The mail server didn't reply to our HELO, exiting\n")
            exit(1)
        except SMTPSenderRefused:
            self.logger.critical(
                "The mail server doesn't allow this user to send mail. Are you sure this user exits?\n")
            exit(1)
        except SMTPDataError:
            self.logger.critical(
                "The server replied with an unxpected error code. exiting\n")
            exit(1)
        except BaseException as e:
            self.logger.critical("An unhandled error occured. The program will now quit\n")
            self.logger.critical("> " + str(e) + "\n")
            exit(1)
