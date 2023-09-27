import pytz
import logging
import smtplib
import imaplib
import unidecode
from typing import List, Dict, Any
from datetime import datetime, timedelta

from global_variables import EMAIL_TITLE, EMAIL_WAS_SENT


class EmailSender:
    sent_messages_number = 10
    sender_email = None
    sender_email_password = None
    receivers_emails = None
    email_title = None
    street_name = None

    def set_sender_info(self, configuration: Dict[str, Any]) -> None:
        self.sender_email = configuration.get('sender_email')
        self.sender_email_password = configuration.get('sender_email_password')

    def set_receivers_info(self, address_data: Dict[str, Any]) -> None:
        self.receivers_emails = address_data.get('receivers_emails')

    def prepare_and_send_email(self, outage_items: List[Dict[str, Any]]) -> None:
        self._set_email_title()
        for outage_item in outage_items:
            if self.street_name in outage_item['Message']:
                email_text = self._prepare_email_data(outage_item)
                self._send_email(email_text)
                logging.info(EMAIL_WAS_SENT.format(self._join_receivers_emails()))

    def _set_email_title(self) -> None:
        self.email_title = EMAIL_TITLE.format(unidecode.unidecode(self.street_name))

    def _prepare_email_data(self, outage_item: Dict[str, Any]) -> str:
        start_time = datetime.strptime(outage_item['StartDate'], '%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(outage_item['EndDate'], '%Y-%m-%dT%H:%M:%SZ')
        start_date = datetime.strftime(start_time.date(), '%d/%m/%Y')
        end_date = datetime.strftime(end_time.date(), '%d/%m/%Y')

        utcnow = pytz.timezone('utc').localize(datetime.utcnow())
        timezone_shift = timedelta(hours=utcnow.astimezone().hour - utcnow.hour)

        return f'From: {self.sender_email}\nTo: {self._join_receivers_emails()}\n' \
               f'Subject: {self.email_title}\n\n' \
               f'AREA: {unidecode.unidecode(outage_item["Message"])}\n' \
               f'START: {start_date}\nEND: {end_date}\n' \
               f'DURATION: {(start_time + timezone_shift).time()} - {(end_time + timezone_shift).time()}'

    def _send_email(self, email_text: str) -> None:
        if not self._check_if_email_was_sent():
            server = smtplib.SMTP_SSL('smtp.gmail.com')
            server.ehlo()
            server.login(self.sender_email, self.sender_email_password)
            server.sendmail(self.sender_email, self.receivers_emails, email_text)
            server.close()

    def _check_if_email_was_sent(self) -> bool:
        server = imaplib.IMAP4_SSL('imap.gmail.com')
        server.login(self.sender_email, self.sender_email_password)
        for item in server.list()[1]:
            if 'Sent' in str(item):
                return self._check_sent_emails(server, str(item).rsplit('"')[-2])
        return False

    def _check_sent_emails(self, server: imaplib.IMAP4_SSL, sent_folder: str) -> bool:
        status, messages_number = server.select(f'"{sent_folder}"')
        for i in range(int(messages_number[0]), int(messages_number[0]) - self.sent_messages_number, -1):
            if i > 0:
                status, message = server.fetch(str(i), '(RFC822)')
                if self.email_title in str(message[0]) and self._join_receivers_emails() in str(message[0]):
                    return True
        return False

    def _join_receivers_emails(self) -> str:
        return ', '.join(self.receivers_emails)
