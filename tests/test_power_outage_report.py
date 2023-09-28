import unittest
import requests
import datetime
from mock import call, patch, MagicMock
from address import Address
from power_outage_report import PowerOutageReport
from global_variables import JSON_CONFIGURATION_FILE_PATH, CONNECTION_ERROR, CONNECTION_ERROR_RETRYING
from test_power_outage_report_data import correct_configuration_one_address, correct_configuration_multiple_addresses, \
    outage_items


class TestPowerOutageReport(unittest.TestCase):
    def setUp(self) -> None:
        self.power_outage_report_cls = PowerOutageReport()

    @patch.object(PowerOutageReport, '_try_to_execute_function')
    @patch.object(PowerOutageReport, '_send_outage_report')
    @patch('email_sender.EmailSender.set_receivers_info')
    @patch('address.Address.set_street_id')
    @patch('address.Address.set_city_id')
    @patch('address.Address.set_address_data')
    @patch('email_sender.EmailSender.set_sender_info')
    @patch('configuration_loader.ConfigurationLoader.read_from_file', return_value=correct_configuration_one_address)
    def test_send_outage_report_one_address(self, mock_read_from_file: MagicMock, mock_set_sender_info: MagicMock,
                                            mock_set_address_data: MagicMock, mock_set_city_id: MagicMock,
                                            mock_set_street_id: MagicMock, mock_set_receivers_info: MagicMock,
                                            mock_send_outage_report: MagicMock,
                                            mock_try_to_execute_function: MagicMock) -> None:
        self.power_outage_report_cls.send_outage_report()
        mock_read_from_file.assert_called_once_with(JSON_CONFIGURATION_FILE_PATH)
        mock_set_sender_info.assert_called_once_with(correct_configuration_one_address)
        mock_set_address_data.assert_called_once_with(correct_configuration_one_address['addresses'][0])
        mock_set_receivers_info.assert_called_once_with(correct_configuration_one_address['addresses'][0])
        mock_try_to_execute_function.assert_has_calls([
            call(mock_set_city_id), call(mock_set_street_id), call(mock_send_outage_report)
        ])

    @patch.object(PowerOutageReport, '_try_to_execute_function')
    @patch.object(PowerOutageReport, '_send_outage_report')
    @patch('email_sender.EmailSender.set_receivers_info')
    @patch('address.Address.set_street_id')
    @patch('address.Address.set_city_id')
    @patch('address.Address.set_address_data')
    @patch('email_sender.EmailSender.set_sender_info')
    @patch('configuration_loader.ConfigurationLoader.read_from_file',
           return_value=correct_configuration_multiple_addresses)
    def test_send_outage_report_multiple_addresses(self, mock_read_from_file: MagicMock,
                                                   mock_set_sender_info: MagicMock, mock_set_address_data: MagicMock,
                                                   mock_set_city_id: MagicMock, mock_set_street_id: MagicMock,
                                                   mock_set_receivers_info: MagicMock,
                                                   mock_send_outage_report: MagicMock,
                                                   mock_try_to_execute_function: MagicMock) -> None:
        self.power_outage_report_cls.send_outage_report()
        mock_read_from_file.assert_called_once_with(JSON_CONFIGURATION_FILE_PATH)
        mock_set_sender_info.assert_called_once_with(correct_configuration_multiple_addresses)
        mock_set_address_data.assert_has_calls([call(correct_configuration_multiple_addresses['addresses'][0]),
                                                call(correct_configuration_multiple_addresses['addresses'][1])
                                                ])
        mock_set_receivers_info.assert_has_calls([call(correct_configuration_multiple_addresses['addresses'][0]),
                                                  call(correct_configuration_multiple_addresses['addresses'][1])
                                                  ])
        mock_try_to_execute_function.assert_has_calls([
            call(mock_set_city_id), call(mock_set_street_id), call(mock_send_outage_report),
            call(mock_set_city_id), call(mock_set_street_id), call(mock_send_outage_report)
        ])

    @patch('logging.error')
    @patch.object(PowerOutageReport, '_retry')
    @patch('address.Address.set_city_id')
    def test_try_to_execute_function(self, mock_function: MagicMock, mock_retry: MagicMock, mock_error: MagicMock) -> None:
        self.power_outage_report_cls.retries = 3
        self.power_outage_report_cls._try_to_execute_function(mock_function)
        mock_function.assert_called_once_with()
        mock_retry.assert_not_called()
        mock_error.assert_not_called()
        self.assertEqual(self.power_outage_report_cls.retries, 5)

    @patch('logging.error')
    @patch.object(PowerOutageReport, '_retry')
    @patch('address.Address.set_city_id', side_effect=requests.ConnectionError)
    def test_try_to_execute_function_error(self, mock_function: MagicMock, mock_retry: MagicMock,
                                           mock_error: MagicMock) -> None:
        self.power_outage_report_cls.retries = 3
        self.power_outage_report_cls._try_to_execute_function(mock_function)
        mock_function.assert_called_once_with()
        mock_error.assert_called_once_with(CONNECTION_ERROR_RETRYING.format(self.power_outage_report_cls.sleep_time,
                                                                            self.power_outage_report_cls.retries))
        mock_retry.assert_called_once_with(mock_function)
        self.assertEqual(self.power_outage_report_cls.retries, 3)

    @patch('logging.error')
    @patch.object(PowerOutageReport, '_try_to_execute_function')
    @patch('time.sleep')
    @patch('address.Address.set_city_id')
    def test_retry(self, mock_function: MagicMock, mock_time_sleep: MagicMock, mock_try_to_execute_function: MagicMock,
                   mock_error: MagicMock) -> None:
        self.power_outage_report_cls.retries = 3
        self.power_outage_report_cls._retry(mock_function)
        mock_time_sleep.assert_called_once_with(self.power_outage_report_cls.sleep_time)
        mock_try_to_execute_function.assert_called_once_with(mock_function)
        mock_error.assert_not_called()
        self.assertEqual(self.power_outage_report_cls.retries, 2)

    @patch('logging.error')
    @patch.object(PowerOutageReport, '_try_to_execute_function')
    @patch('time.sleep')
    @patch('address.Address.set_city_id')
    def test_retry_error(self, mock_function: MagicMock, mock_time_sleep: MagicMock,
                         mock_try_to_execute_function: MagicMock, mock_error: MagicMock) -> None:
        self.power_outage_report_cls.retries = 0
        with self.assertRaises(SystemExit) as e:
            self.power_outage_report_cls._retry(mock_function)
        mock_time_sleep.assert_not_called()
        mock_try_to_execute_function.assert_not_called()
        mock_error.assert_called_once_with(CONNECTION_ERROR)
        self.assertEqual(e.exception.code, 1)

    @patch('email_sender.EmailSender.prepare_and_send_email')
    @patch.object(PowerOutageReport, '_get_outage_information', return_value=outage_items)
    def test__send_outage_report(self, mock_get_outage_information: MagicMock,
                                 mock_prepare_and_send_email: MagicMock) -> None:
        self.power_outage_report_cls._send_outage_report()
        mock_get_outage_information.assert_called_once_with()
        mock_prepare_and_send_email.assert_called_once_with(outage_items)

    @patch('request_sender.RequestSender.send_request')
    @patch('power_outage_report.datetime')
    def test_get_outage_information(self, mock_date: MagicMock, mock_send_request: MagicMock) -> None:
        mock_date.now.return_value = datetime.datetime(2023, 9, 22, 17, 0, 0, 0)
        payload = {'cityGAID': Address.city_id, 'streetGAID': Address.street_id, 'houseNo': Address.house_number,
                   'fromDate': '2023-09-22T17:00:00', 'toDate': '2023-09-27T17:00:00', 'flatNo': '',
                   '_': 1695394800000}
        self.power_outage_report_cls._get_outage_information()
        mock_date.now.assert_called_once_with()
        mock_send_request.assert_called_once_with('outages/address', payload)
