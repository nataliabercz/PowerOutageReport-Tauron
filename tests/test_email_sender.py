import unittest
import smtplib
import imaplib
from datetime import datetime, timedelta
import pytz
from mock import call, patch, MagicMock

from test_power_outage_report_data import correct_configuration_one_address, correct_configuration_multiple_addresses, \
    EMAIL_TEMPLATE, SENT_EMAILS_FOLDER, SENT_EMAILS_MESSAGE_BYTES
from global_variables import EMAIL_TITLE, EMAIL_WAS_SENT, AUTHENTICATION_FAILURE, WRONG_PARAMETER_TYPE
from email_sender import EmailSender


class TestEmailSender(unittest.TestCase):
    def setUp(self) -> None:
        self.email_sender_cls = EmailSender()

    def test_set_sender_info(self) -> None:
        self.email_sender_cls.set_sender_info(correct_configuration_one_address)
        self.assertEqual(self.email_sender_cls.sender_email, 'sender@mail.com')
        self.assertEqual(self.email_sender_cls.sender_email_password, 'password')

    def test_set_receivers_info(self) -> None:
        self.email_sender_cls.set_receivers_info(correct_configuration_one_address['addresses'][0])
        self.assertEqual(self.email_sender_cls.receivers_emails, ['receiver@mail.com'])

        self.email_sender_cls.set_receivers_info(correct_configuration_multiple_addresses['addresses'][1])
        self.assertEqual(self.email_sender_cls.receivers_emails, ['receiver1@mail.com', 'receiver2@mail.com'])

    @patch('logging.info')
    @patch.object(EmailSender, '_send_email')
    @patch.object(EmailSender, '_prepare_email_data', return_value=EMAIL_TEMPLATE)
    @patch.object(EmailSender, '_set_email_title', return_value=EMAIL_TITLE.format('StreetName'))
    def test_prepare_and_send_email(self, mock_set_email_title: MagicMock, mock_prepare_email_data: MagicMock,
                                    mock_send_email: MagicMock,mock_info: MagicMock) -> None:
        outage_items = [{'OutageId': 'id_1', 'StartDate': 's_date_1', 'EndDate': 'e_date_1', 'Message': 'StreetName'},
                        {'OutageId': 'id_2', 'StartDate': 's_date_2', 'EndDate': 'e_date_2', 'Message': 'OtherStreet'}]
        self.email_sender_cls.street_name = 'StreetName'
        self.email_sender_cls.receivers_emails = correct_configuration_one_address['addresses'][0]['receivers_emails']
        self.email_sender_cls.prepare_and_send_email(outage_items)
        mock_set_email_title.assert_called_once_with()
        mock_prepare_email_data.assert_called_once_with(outage_items[0])
        mock_send_email.assert_called_once_with(EMAIL_TEMPLATE)
        mock_info.assert_called_once_with(EMAIL_WAS_SENT.format(', '.join(self.email_sender_cls.receivers_emails)))

    @patch('logging.info')
    @patch.object(EmailSender, '_send_email')
    @patch.object(EmailSender, '_prepare_email_data')
    @patch.object(EmailSender, '_set_email_title')
    def test_prepare_and_send_email_empty(self, mock_set_email_title: MagicMock, mock_prepare_email_data: MagicMock,
                                          mock_send_email: MagicMock, mock_info: MagicMock) -> None:
        self.email_sender_cls.prepare_and_send_email([])
        mock_set_email_title.assert_called_once_with()
        mock_prepare_email_data.assert_not_called()
        mock_send_email.assert_not_called()
        mock_info.assert_not_called()

    def test_set_email_title(self) -> None:
        self.email_sender_cls.street_name = 'Street Ą'
        self.email_sender_cls._set_email_title()
        self.assertEqual(self.email_sender_cls.email_title, EMAIL_TITLE.format('Street A'))

    def test_prepare_email_data(self) -> None:
        utcnow = pytz.timezone('utc').localize(datetime.utcnow())
        timezone_shift = timedelta(hours=utcnow.astimezone().hour - utcnow.hour)
        start = datetime.strptime('05:00:00', '%H:%M:%S')
        end = datetime.strptime('14:00:00', '%H:%M:%S')
        self.email_sender_cls.street_name = 'StreetName'
        self.email_sender_cls.email_title = EMAIL_TITLE.format(self.email_sender_cls.street_name)
        self.email_sender_cls.sender_email = correct_configuration_one_address['sender_email']
        self.email_sender_cls.receivers_emails = correct_configuration_one_address['addresses'][0]['receivers_emails']
        outage_items = {'StartDate': '2023-09-27T05:00:00Z', 'EndDate': '2023-09-27T14:00:00Z', 'Message': 'msg'}
        email_data = self.email_sender_cls._prepare_email_data(outage_items)
        self.assertEqual(email_data, EMAIL_TEMPLATE.format('sender@mail.com', 'receiver@mail.com', 'StreetName', 'msg',
                                                           '27/09/2023', '27/09/2023', (start + timezone_shift).time(),
                                                           (end + timezone_shift).time()))

    @patch('logging.error')
    @patch.object(EmailSender, '_check_if_email_was_sent', return_value=False)
    def test_send_email(self, mock_check_if_email_was_sent: MagicMock, mock_error: MagicMock) -> None:
        self.email_sender_cls.sender_email = correct_configuration_one_address['sender_email']
        self.email_sender_cls.sender_email_password = correct_configuration_one_address['sender_email_password']
        self.email_sender_cls.receivers_emails = correct_configuration_one_address['addresses'][0]['receivers_emails']
        mock_server = MagicMock()
        smtplib.SMTP_SSL = MagicMock(return_value=mock_server)
        self.email_sender_cls._send_email(EMAIL_TEMPLATE.format('example@mail.com',
                                                                'receiver1@mail.com, receiver2@mail.com',
                                                                'StreetName', 'msg', '26/09/2023', '26/09/2023',
                                                                '07:00:00', '16:00:00'))
        mock_check_if_email_was_sent.assert_called_once_with()
        mock_server.ehlo.assert_called_once_with()
        mock_server.login.assert_called_once_with(self.email_sender_cls.sender_email,
                                                  self.email_sender_cls.sender_email_password)
        mock_server.sendmail.assert_called_once_with('sender@mail.com', ['receiver@mail.com'],
                                                     EMAIL_TEMPLATE.format('example@mail.com',
                                                                           'receiver1@mail.com, receiver2@mail.com',
                                                                           'StreetName', 'msg', '26/09/2023',
                                                                           '26/09/2023', '07:00:00', '16:00:00'))
        mock_server.close.assert_called_once_with()
        mock_error.assert_not_called()

    @patch('logging.error')
    @patch.object(EmailSender, '_check_if_email_was_sent', return_value=True)
    def test_send_email_already_sent(self, mock_check_if_email_was_sent: MagicMock, mock_error: MagicMock) -> None:
        mock_server = MagicMock()
        smtplib.SMTP_SSL = MagicMock(return_value=mock_server)
        self.email_sender_cls._send_email(EMAIL_TEMPLATE.format('example@mail.com',
                                                                'receiver1@mail.com, receiver2@mail.com',
                                                                'StreetName', 'msg', '26/09/2023', '26/09/2023',
                                                                '07:00:00', '16:00:00'))
        mock_check_if_email_was_sent.assert_called_once_with()
        mock_server.ehlo.assert_not_called()
        mock_server.login.assert_not_called()
        mock_server.send_mail.assert_not_called()
        mock_server.close.assert_not_called()
        mock_error.assert_not_called()

    @patch('logging.error')
    @patch.object(EmailSender, '_check_if_email_was_sent', side_effect=imaplib.IMAP4.error)
    def test_send_email_error(self, mock_check_if_email_was_sent: MagicMock, mock_error: MagicMock) -> None:
        mock_server = MagicMock()
        smtplib.SMTP_SSL = MagicMock(return_value=mock_server)
        self.email_sender_cls._send_email(EMAIL_TEMPLATE.format('example@mail.com',
                                                                'receiver1@mail.com, receiver2@mail.com',
                                                                'StreetName', 'msg', '26/09/2023', '26/09/2023',
                                                                '07:00:00', '16:00:00'))
        mock_check_if_email_was_sent.assert_called_once_with()
        mock_server.ehlo.assert_not_called()
        mock_server.login.assert_not_called()
        mock_server.send_mail.assert_not_called()
        mock_server.close.assert_not_called()
        mock_error.assert_called_once_with(AUTHENTICATION_FAILURE)

    @patch('logging.error')
    @patch.object(EmailSender, '_check_sent_emails', return_value=True)
    def test_check_if_email_was_sent_true(self, mock_check_sent_emails: MagicMock, mock_error: MagicMock) -> None:
        self.email_sender_cls.sender_email = correct_configuration_one_address['sender_email']
        self.email_sender_cls.sender_email_password = correct_configuration_one_address['sender_email_password']
        mock_server = MagicMock()
        imaplib.IMAP4_SSL = MagicMock(return_value=mock_server)
        mock_server.list.return_value = ('OK', [b'(\\HasNoChildren) "/" "INBOX"',
                                                b'(\\HasNoChildren \\Junk) "/" "[Gmail]/"Spam',
                                                b'(\\HasNoChildren \\Important) "/" "[Gmail]/Important"',
                                                b'(\\Drafts \\HasNoChildren) "/" "[Gmail]/Drafts"',
                                                b'(\\Flagged \\HasNoChildren) "/" "[Gmail]/Starred"',
                                                b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"'])
        email_was_sent = self.email_sender_cls._check_if_email_was_sent()
        mock_server.login.assert_called_once_with(self.email_sender_cls.sender_email,
                                                  self.email_sender_cls.sender_email_password)
        mock_server.list.assert_called_once_with()
        mock_check_sent_emails.assert_called_once_with(mock_server, '[Gmail]/Sent Mail')
        mock_error.assert_not_called()
        self.assertEqual(email_was_sent, True)

    @patch('logging.error')
    @patch.object(EmailSender, '_check_sent_emails', return_value=False)
    def test_check_if_email_was_sent_false(self, mock_check_sent_emails: MagicMock, mock_error: MagicMock) -> None:
        self.email_sender_cls.sender_email = correct_configuration_one_address['sender_email']
        self.email_sender_cls.sender_email_password = correct_configuration_one_address['sender_email_password']
        mock_server = MagicMock()
        imaplib.IMAP4_SSL = MagicMock(return_value=mock_server)
        mock_server.list.return_value = ('OK', [b'(\\HasNoChildren) "/" "INBOX"',
                                                b'(\\HasNoChildren \\Junk) "/" "[Gmail]/"Spam',
                                                b'(\\HasNoChildren \\Important) "/" "[Gmail]/Important"',
                                                b'(\\Drafts \\HasNoChildren) "/" "[Gmail]/Drafts"',
                                                b'(\\Flagged \\HasNoChildren) "/" "[Gmail]/Starred"',
                                                b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"'])
        email_was_sent = self.email_sender_cls._check_if_email_was_sent()
        mock_server.login.assert_called_once_with(self.email_sender_cls.sender_email,
                                                  self.email_sender_cls.sender_email_password)
        mock_server.list.assert_called_once_with()
        mock_check_sent_emails.assert_called_once_with(mock_server, SENT_EMAILS_FOLDER)
        mock_error.assert_not_called()
        self.assertEqual(email_was_sent, False)

    @patch('logging.error')
    @patch.object(EmailSender, '_check_sent_emails', side_effect=TypeError)
    def test_check_if_email_was_sent_error(self, mock_check_sent_emails: MagicMock, mock_error: MagicMock) -> None:
        self.email_sender_cls.sent_messages_number = 20.5
        self.email_sender_cls.sender_email = correct_configuration_one_address['sender_email']
        self.email_sender_cls.sender_email_password = correct_configuration_one_address['sender_email_password']
        mock_server = MagicMock()
        imaplib.IMAP4_SSL = MagicMock(return_value=mock_server)
        mock_server.list.return_value = ('OK', [b'(\\HasNoChildren) "/" "INBOX"',
                                                b'(\\HasNoChildren \\Junk) "/" "[Gmail]/"Spam',
                                                b'(\\HasNoChildren \\Important) "/" "[Gmail]/Important"',
                                                b'(\\Drafts \\HasNoChildren) "/" "[Gmail]/Drafts"',
                                                b'(\\Flagged \\HasNoChildren) "/" "[Gmail]/Starred"',
                                                b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"'])
        with self.assertRaises(SystemExit) as error:
            self.email_sender_cls._check_if_email_was_sent()
        mock_server.login.assert_called_once_with(self.email_sender_cls.sender_email,
                                                  self.email_sender_cls.sender_email_password)
        mock_server.list.assert_called_once_with()
        mock_check_sent_emails.assert_called_once_with(mock_server, SENT_EMAILS_FOLDER)
        mock_error.assert_called_once_with(WRONG_PARAMETER_TYPE.format('sent_messages_number = 20.5', int))
        self.assertEqual(error.exception.code, 1)

    def test_check_sent_emails_was_sent_true(self) -> None:
        self.email_sender_cls.email_title = EMAIL_TITLE.format('StreetName')
        self.email_sender_cls.receivers_emails = correct_configuration_one_address['addresses'][0]['receivers_emails']
        mock_server = MagicMock()
        imaplib.IMAP4_SSL = MagicMock(return_value=mock_server)
        mock_server.select.return_value = ('OK', [b'100'])
        mock_server.fetch.return_value = ('OK', [(b'100 (RFC822 {939}', SENT_EMAILS_MESSAGE_BYTES), b')'])
        email_was_sent = self.email_sender_cls._check_sent_emails(mock_server, f'{SENT_EMAILS_FOLDER}')
        mock_server.select.assert_called_once_with(f'"{SENT_EMAILS_FOLDER}"')
        mock_server.fetch.assert_called_once_with('100', '(RFC822)')
        self.assertEqual(email_was_sent, True)

    def test_check_sent_emails_was_sent_false(self) -> None:
        self.email_sender_cls.sent_messages_number = 10
        self.email_sender_cls.email_title = EMAIL_TITLE.format('StreetName')
        self.email_sender_cls.receivers_emails = correct_configuration_one_address['addresses'][0]['receivers_emails']
        mock_server = MagicMock()
        imaplib.IMAP4_SSL = MagicMock(return_value=mock_server)
        mock_server.select.return_value = ('OK', [b'100'])
        mock_server.fetch.return_value = ('OK', [(b'100 (RFC822 {939}', b'some msg'), b')'])
        email_was_sent = self.email_sender_cls._check_sent_emails(mock_server, f'{SENT_EMAILS_FOLDER}')
        mock_server.select.assert_called_once_with(f'"{SENT_EMAILS_FOLDER}"')
        mock_server.fetch.assert_has_calls([call('100', '(RFC822)'), call('99', '(RFC822)'), call('98', '(RFC822)'),
                                            call('97', '(RFC822)'), call('96', '(RFC822)'), call('95', '(RFC822)'),
                                            call('94', '(RFC822)'), call('93', '(RFC822)'), call('92', '(RFC822)'),
                                            call('91', '(RFC822)')])
        self.assertEqual(email_was_sent, False)

    def test_check_sent_emails_was_sent_no_sent_mails(self) -> None:
        self.email_sender_cls.email_title = EMAIL_TITLE.format('StreetName')
        self.email_sender_cls.receivers_emails = correct_configuration_one_address['addresses'][0]['receivers_emails']
        mock_server = MagicMock()
        imaplib.IMAP4_SSL = MagicMock(return_value=mock_server)
        mock_server.select.return_value = ('OK', [b'0'])
        email_was_sent = self.email_sender_cls._check_sent_emails(mock_server, f'{SENT_EMAILS_FOLDER}')
        mock_server.select.assert_called_once_with(f'"{SENT_EMAILS_FOLDER}"')
        mock_server.fetch.assert_not_called()
        self.assertEqual(email_was_sent, False)

    def test_join_receivers_emails(self) -> None:
        self.email_sender_cls.receivers_emails = \
            correct_configuration_multiple_addresses['addresses'][1]['receivers_emails']
        self.assertEqual(self.email_sender_cls._join_receivers_emails(), 'receiver1@mail.com, receiver2@mail.com')
