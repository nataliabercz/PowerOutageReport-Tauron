import unittest
import responses
from mock import MagicMock, patch
from request_sender import RequestSender
from global_variables import URL, WRONG_REQUEST, WRONG_REQUEST_STATUS_CODE
from test_power_outage_report_data import test_response, test_response_adjusted


class TestRequestSender(unittest.TestCase):
    def setUp(self) -> None:
        self.request_sender_cls = RequestSender()

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', return_value=[{'GAID': 123456, 'Name': 'City'}])
    @responses.activate
    def test_send_request(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json="[{'GAID':123456,'Name':'City'}]", status=200)
        response = self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_called_once_with('"[{\'GAID\':123456,\'Name\':\'City\'}]"')
        mock_error.assert_not_called()
        self.assertEqual(response, [{'GAID': 123456, 'Name': 'City'}])

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', return_value=[{'GAID': 123456, 'Name': 'City'}])
    @responses.activate
    def test_send_request_status_code_error(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json='not found', status=404)
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_not_called()
        mock_error.assert_called_once_with(WRONG_REQUEST_STATUS_CODE.format(404))
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', side_effect=SyntaxError)
    @responses.activate
    def test_send_request_syntax_error(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json='{"AddressPoint":null,"OutageItems":[]', status=200)
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_called_once_with('"{\\"AddressPoint\\":null,\\"OutageItems\\":[]"')
        mock_error.assert_called_once_with(WRONG_REQUEST)
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', side_effect=ValueError)
    @responses.activate
    def test_send_request_value_error(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json='{"AddressPoint":null,"OutageItems":[]', status=200)
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_called_once_with('"{\\"AddressPoint\\":null,\\"OutageItems\\":[]"')
        mock_error.assert_called_once_with(WRONG_REQUEST)
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', side_effect=AttributeError)
    @responses.activate
    def test_send_request_attribute_error(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json='{"AddressPoint":null,"OutageItems":[]', status=200)
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_called_once_with('"{\\"AddressPoint\\":null,\\"OutageItems\\":[]"')
        mock_error.assert_called_once_with(WRONG_REQUEST)
        self.assertEqual(e.exception.code, 1)

    def test_convert_response(self) -> None:
        self.assertEqual(self.request_sender_cls._convert_response(test_response), test_response_adjusted)
