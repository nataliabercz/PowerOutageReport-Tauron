import ast
import logging
import requests
import urllib.parse
from typing import Dict, Any

from global_variables import URL, WRONG_REQUEST, WRONG_REQUEST_STATUS_CODE


class RequestSender:
    def __init__(self) -> None:
        self.request = requests.Session()

    def send_request(self, url_postfix: str, payload: Dict[str, Any]) -> Any:
        try:
            response = self.request.get(URL.format(url_postfix + '?' + urllib.parse.urlencode(payload)))
            if response.status_code == 200:
                return self._convert_response(response.text)
            else:
                logging.error(WRONG_REQUEST_STATUS_CODE.format(response.status_code))
                exit(1)
        except (SyntaxError, ValueError, AttributeError):
            logging.error(WRONG_REQUEST)
            exit(1)

    @staticmethod
    def _convert_response(response: str) -> Any:
        return ast.literal_eval(response.replace(':f', ':F').replace(':t', ':T').replace(':null', ':""'))
