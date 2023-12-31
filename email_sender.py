import sys
import logging
import smtplib
import imaplib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import unidecode
import pytz

from global_variables import EMAIL_TITLE, EMAIL_WAS_SENT, AUTHENTICATION_FAILURE, WRONG_PARAMETER_TYPE


class EmailSender:
    sent_messages_number = 20
    sender_email = None
    sender_email_password = None
    receivers_emails = None
    email_title = None
    street_name = None
    start_date = None

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
        start = datetime.strftime(start_time.date(), '%d/%m/%Y')
        end = datetime.strftime(end_time.date(), '%d/%m/%Y')

        utcnow = pytz.timezone('utc').localize(datetime.utcnow())
        timezone_shift = timedelta(hours=utcnow.astimezone().hour - utcnow.hour)

        self.start_date = str((start_time + timezone_shift).time())

        return f'From: {self.sender_email}\nTo: {self._join_receivers_emails()}\n' \
               f'Subject: {self.email_title}\n\n' \
               f'AREA: {unidecode.unidecode(outage_item["Message"])}\n' \
               f'START: {start}\nEND: {end}\n' \
               f'DURATION: {self.start_date} - {(end_time + timezone_shift).time()}'

    def _send_email(self, email_text: str) -> None:
        try:
            if not self._check_if_email_was_sent():
                server = smtplib.SMTP_SSL('smtp.gmail.com')
                server.ehlo()
                server.login(self.sender_email, self.sender_email_password)
                server.sendmail(self.sender_email, self.receivers_emails, email_text)
                server.close()
        except imaplib.IMAP4.error:
            logging.error(AUTHENTICATION_FAILURE)

    def _check_if_email_was_sent(self) -> bool:
        server = imaplib.IMAP4_SSL('imap.gmail.com')
        server.login(self.sender_email, self.sender_email_password)
        for item in server.list()[1]:
            if 'Sent' in str(item):
                try:
                    return self._check_sent_emails(server, str(item).rsplit('"')[-2])
                except TypeError:
                    logging.error(WRONG_PARAMETER_TYPE.format(
                        f'sent_messages_number = {self.sent_messages_number}', int))
                    sys.exit(1)
        return False

    def _check_sent_emails(self, server: imaplib.IMAP4_SSL, sent_folder: str) -> bool:
        _, messages_number = server.select(f'"{sent_folder}"')
        for i in range(int(messages_number[0]), int(messages_number[0]) - self.sent_messages_number, -1):
            if i > 0:
                _, message = server.fetch(str(i), '(RFC822)')
                if all(substring in str(message[0]) for substring in [self.email_title, self._join_receivers_emails(),
                                                                      self.start_date]):
                    return True
        return False

    def _join_receivers_emails(self) -> str:
        return ', '.join(self.receivers_emails)
