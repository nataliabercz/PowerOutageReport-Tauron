import unittest
import responses
from mock import MagicMock, patch
from request_sender import RequestSender
from global_variables import URL, WRONG_REQUEST
from test_power_outage_report_data import test_response, test_response_adjusted


class TestRequestSender(unittest.TestCase):
    def setUp(self) -> None:
        self.request_sender_cls = RequestSender()

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', return_value=123456)
    @responses.activate
    def test_send_request(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json=[{'GAID': 123456, 'Name': 'City'}], status=200)
        response = self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_called_once_with('[{"GAID": 123456, "Name": "City"}]')
        mock_error.assert_not_called()
        self.assertEqual(response, 123456)

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', return_value=123456)
    @patch('requests.Session.get', side_effect=Exception('some error'))
    def test_send_request_error(self, mock_request_get: MagicMock, mock_convert_response: MagicMock,
                                mock_error: MagicMock) -> None:
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_request_get.assert_called_once_with(URL.format('enum/geo/cities?partName=City&_=1695307034194'))
        mock_convert_response.assert_not_called()
        mock_error.assert_called_once_with('some error')
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', return_value=123456)
    @responses.activate
    def test_send_request_error_status_code(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json='not found', status=404)
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_not_called()
        mock_error.assert_called_once_with(WRONG_REQUEST.format(404))
        self.assertEqual(e.exception.code, 1)

    @patch('logging.error')
    @patch.object(RequestSender, '_convert_response', side_effect=SyntaxError("'{' was never closed"))
    @responses.activate
    def test_send_request_error_converting(self, mock_convert_response: MagicMock, mock_error: MagicMock) -> None:
        responses.add(responses.GET, URL.format('enum/geo/cities?partName=City&_=1695307034194'),
                      json='{"AddressPoint":null,"OutageItems":[]', status=200)
        with self.assertRaises(SystemExit) as e:
            self.request_sender_cls.send_request('enum/geo/cities', {'partName': 'City', '_': 1695307034194})
        mock_convert_response.assert_called_once_with('"{\\"AddressPoint\\":null,\\"OutageItems\\":[]"')
        mock_error.assert_called_once_with("'{' was never closed")
        self.assertEqual(e.exception.code, 1)

    def test_convert_response(self) -> None:
        self.assertEqual(self.request_sender_cls._convert_response(test_response), test_response_adjusted)
