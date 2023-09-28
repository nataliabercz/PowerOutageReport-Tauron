import json
import unittest
from io import StringIO
from mock import patch, MagicMock, call
from configuration_loader import ConfigurationLoader
from global_variables import FILE_DOESNT_EXIST, WRONG_FILE, MISSING_OR_EMPTY_PARAMETER, WRONG_PARAMETER_TYPE_IN_FILE
from test_power_outage_report_data import correct_configuration_one_address, correct_configuration_multiple_addresses


class TestConfigurationLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.configuration_loader_cls = ConfigurationLoader()

    @patch('logging.error')
    @patch.object(ConfigurationLoader, '_validate')
    @patch.object(ConfigurationLoader, '_load_json', return_value=correct_configuration_one_address)
    def test_read_from_file(self, mock_load_json: MagicMock, mock_validate: MagicMock, mock_error: MagicMock) -> None:
        file = StringIO(json.dumps(correct_configuration_one_address))
        file.close = MagicMock()
        with patch('builtins.open', return_value=file) as mock_open:
            configuration = self.configuration_loader_cls.read_from_file('configuration.json')
            mock_open.assert_called_once_with('configuration.json', encoding='utf-8')
            mock_load_json.assert_called_once_with(file)
            mock_validate.assert_called_once_with(correct_configuration_one_address)
            file.close.assert_called_once_with()
            mock_error.assert_not_called()
            self.assertEqual(configuration, correct_configuration_one_address)

    @patch('logging.error')
    @patch.object(ConfigurationLoader, '_validate')
    @patch.object(ConfigurationLoader, '_load_json', return_value=correct_configuration_one_address)
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_read_from_file_error(self, mock_open: MagicMock, mock_load_json: MagicMock,
                                  mock_validate: MagicMock, mock_error: MagicMock) -> None:
        with self.assertRaises(SystemExit) as e:
            self.configuration_loader_cls.read_from_file('configuration.json')
        mock_open.assert_called_once_with('configuration.json', encoding='utf-8')
        mock_load_json.assert_not_called()
        mock_validate.assert_not_called()
        mock_error.assert_called_once_with(FILE_DOESNT_EXIST)
        self.assertEqual(e.exception.code, 1)

    @patch('json.load', return_value=correct_configuration_one_address)
    def test_load_json(self, mock_json_load: MagicMock) -> None:
        configuration = self.configuration_loader_cls._load_json(correct_configuration_one_address)
        mock_json_load.assert_called_once_with(correct_configuration_one_address)
        self.assertEqual(configuration, correct_configuration_one_address)

    @patch('logging.error')
    @patch('json.load', side_effect=json.JSONDecodeError('json decode error', 'doc', 0))
    def test_load_json_error(self, mock_json_load: MagicMock, mock_error: MagicMock) -> None:
        file = StringIO(json.dumps('not_valid_json'))
        with self.assertRaises(SystemExit) as e:
            configuration = self.configuration_loader_cls._load_json(file)
            self.assertEqual(configuration, None)
        mock_json_load.assert_called_once_with(file)
        mock_error.assert_called_once_with(WRONG_FILE)
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    @patch.object(ConfigurationLoader, '_check_type')
    @patch.object(ConfigurationLoader, '_check_value_and_type')
    def test_validate_one_address(self, mock_check_value_and_type: MagicMock, mock_check_type: MagicMock,
                                  mock_error: MagicMock) -> None:
        self.configuration_loader_cls._validate(correct_configuration_one_address)
        mock_check_value_and_type.assert_has_calls([
            call(correct_configuration_one_address, ('sender_email', str)),
            call(correct_configuration_one_address, ('sender_email_password', str)),
            call(correct_configuration_one_address, ('addresses', list)),
            call(correct_configuration_one_address['addresses'][0], ('street_name', str)),
            call(correct_configuration_one_address['addresses'][0], ('house_number', str)),
            call(correct_configuration_one_address['addresses'][0], ('city', str)),
            call(correct_configuration_one_address['addresses'][0], ('receivers_emails', list))
        ])
        mock_check_type.assert_called_once_with('receiver@mail.com', "address['receivers_emails'][0]", str)
        mock_error.assert_not_called()

    @patch('logging.error')
    @patch.object(ConfigurationLoader, '_check_type')
    @patch.object(ConfigurationLoader, '_check_value_and_type')
    def test_validate_multiple_addresses(self, mock_check_value_and_type: MagicMock, mock_check_type: MagicMock,
                                         mock_error: MagicMock) -> None:
        self.configuration_loader_cls._validate(correct_configuration_multiple_addresses)
        mock_check_value_and_type.assert_has_calls([
            call(correct_configuration_multiple_addresses, ('sender_email', str)),
            call(correct_configuration_multiple_addresses, ('sender_email_password', str)),
            call(correct_configuration_multiple_addresses, ('addresses', list)),
            call(correct_configuration_multiple_addresses['addresses'][0], ('street_name', str)),
            call(correct_configuration_multiple_addresses['addresses'][0], ('house_number', str)),
            call(correct_configuration_multiple_addresses['addresses'][0], ('city', str)),
            call(correct_configuration_multiple_addresses['addresses'][0], ('receivers_emails', list)),
            call(correct_configuration_multiple_addresses['addresses'][1], ('street_name', str)),
            call(correct_configuration_multiple_addresses['addresses'][1], ('house_number', str)),
            call(correct_configuration_multiple_addresses['addresses'][1], ('city', str)),
            call(correct_configuration_multiple_addresses['addresses'][1], ('receivers_emails', list))
        ])
        mock_check_type.assert_has_calls([
            call('receiver@mail.com', "address['receivers_emails'][0]", str),
            call('receiver1@mail.com', "address['receivers_emails'][0]", str),
            call('receiver2@mail.com', "address['receivers_emails'][1]", str)
        ])
        mock_error.assert_not_called()

    @patch('logging.error')
    @patch.object(ConfigurationLoader, '_check_type')
    @patch.object(ConfigurationLoader, '_check_value_and_type')
    def test_validate_error_not_dictionary(self, mock_check_value_and_type: MagicMock, mock_check_type: MagicMock,
                                           mock_error: MagicMock) -> None:
        with self.assertRaises(SystemExit) as e:
            self.configuration_loader_cls._validate([])
        mock_check_value_and_type.assert_not_called()
        mock_check_type.assert_not_called()
        mock_error.assert_called_once_with(WRONG_FILE)
        self.assertEqual(e.exception.code, 1)

    @patch.object(ConfigurationLoader, '_check_type')
    @patch.object(ConfigurationLoader, '_check_value')
    def test_check_value_and_type(self, mock_check_value: MagicMock, mock_check_type: MagicMock) -> None:
        self.configuration_loader_cls._check_value_and_type(correct_configuration_one_address, ('sender_email', str))
        mock_check_value.assert_called_once_with('sender@mail.com', 'sender_email')
        mock_check_type.assert_called_once_with('sender@mail.com', 'sender_email', str)

    @patch('logging.error')
    def test_check_value(self, mock_error: MagicMock) -> None:
        self.configuration_loader_cls._check_value('sender@mail.com', 'sender_email')
        mock_error.assert_not_called()

    @patch('logging.error')
    def test_check_value_error(self, mock_error: MagicMock) -> None:
        with self.assertRaises(SystemExit) as e:
            self.configuration_loader_cls._check_value('', 'sender_email')
        mock_error.assert_called_once_with(MISSING_OR_EMPTY_PARAMETER.format('sender_email'))
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    def test_check_type(self, mock_error: MagicMock) -> None:
        self.configuration_loader_cls._check_type('sender@mail.com', 'sender_email', str)
        mock_error.assert_not_called()

    @patch('logging.error')
    def test_check_type_error(self, mock_error: MagicMock) -> None:
        with self.assertRaises(SystemExit) as e:
            self.configuration_loader_cls._check_type(123, f"address['receivers_emails'][0]", str)
        mock_error.assert_called_once_with(WRONG_PARAMETER_TYPE_IN_FILE.format(f"address['receivers_emails'][0]", str))
        self.assertEqual(e.exception.code, 1)
