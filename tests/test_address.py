import unittest
from mock import patch, MagicMock
from address import Address
from global_variables import WRONG_STREET_NAME_OR_CITY
from test_power_outage_report_data import correct_configuration_one_address, test_response_adjusted


class TestAddress(unittest.TestCase):
    def setUp(self) -> None:
        self.address_cls = Address()

    @patch.object(Address, '_set_street_id')
    @patch.object(Address, '_set_city_id')
    def test_set_address_data(self, mock_set_city_id: MagicMock, mock_set_street_id: MagicMock) -> None:
        self.address_cls.set_address_data(correct_configuration_one_address['addresses'][0])
        mock_set_city_id.assert_called_once_with()
        mock_set_street_id.assert_called_once_with()
        self.assertEqual(self.address_cls.street_name, 'StreetName')
        self.assertEqual(self.address_cls.house_number, 'HouseNumber')
        self.assertEqual(self.address_cls.city, 'City')

    @patch('time.time', return_value=1695307034.1945698)
    @patch.object(Address, '_set_attribute')
    def test_set_city_id(self, mock_set_attribute: MagicMock, mock_time: MagicMock) -> None:
        self.address_cls.city = 'City'
        self.address_cls._set_city_id()
        mock_set_attribute.assert_called_once_with('city_id', 'enum/geo/cities',
                                                   {'partName': 'City', '_': 1695307034194})
        mock_time.assert_called_once_with()

    @patch('time.time', return_value=1695307034.1945698)
    @patch.object(Address, '_set_attribute')
    def test_set_street_id(self, mock_set_attribute: MagicMock, mock_time: MagicMock) -> None:
        self.address_cls.street_name = 'StreetName'
        self.address_cls.city_id = 123456
        self.address_cls._set_street_id()
        mock_set_attribute.assert_called_once_with('street_id', 'enum/geo/streets',
                                                   {'partName': 'StreetName', 'ownerGAID': 123456, '_': 1695307034194})
        mock_time.assert_called_once_with()

    @patch.object(Address, '_get_response', return_value='[{"GAID":234567,"Name":"City"}]')
    def test_set_attribute(self, mock_get_response: MagicMock) -> None:
        self.address_cls._set_attribute('city_id', 'enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_get_response.assert_called_once_with('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        self.assertEqual(self.address_cls.city_id, 234567)

    @patch('logging.error')
    @patch.object(Address, '_get_response', side_effect=IndexError)
    def test_set_attribute_error(self, mock_get_response: MagicMock, mock_error: MagicMock) -> None:
        self.address_cls.street_name = 'StreetName'
        self.address_cls.city = 'WrongCity'
        with self.assertRaises(SystemExit) as e:
            self.address_cls._set_attribute('city_id', 'enum/geo/cities', {'partName': 'WrongCity', '_': 1695307034194})
        mock_get_response.assert_called_once_with('enum/geo/cities', {'partName': 'WrongCity', '_': 1695307034194})
        mock_error.assert_called_once_with(WRONG_STREET_NAME_OR_CITY.format('StreetName', 'WrongCity'))
        self.assertEqual(self.address_cls.city_id, None)
        self.assertEqual(e.exception.code, 1)

    @patch('request_sender.RequestSender.send_request', return_value=test_response_adjusted)
    def test_get_response(self, mock_send_request: MagicMock) -> None:
        response = self.address_cls._get_response('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_send_request.assert_called_once_with('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        self.assertEqual(response, test_response_adjusted)