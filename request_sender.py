import sys
import ast
import logging
import urllib.parse
from typing import Dict, Any
import requests

from global_variables import URL, WRONG_REQUEST, WRONG_REQUEST_STATUS_CODE


class RequestSender:
    def __init__(self) -> None:
        self.request = requests.Session()

    def send_request(self, url_postfix: str, payload: Dict[str, Any]) -> Any:
        try:
            response = self.request.get(URL.format(url_postfix + '?' + urllib.parse.urlencode(payload)))
            if not response.status_code == 200:
                logging.error(WRONG_REQUEST_STATUS_CODE.format(response.status_code))
                sys.exit(1)
            return self._convert_response(response.text)
        except (SyntaxError, ValueError, AttributeError):
            logging.error(WRONG_REQUEST)
            sys.exit(1)

    @staticmethod
    def _convert_response(response: str) -> Any:
        return ast.literal_eval(response.replace(':f', ':F').replace(':t', ':T').replace(':null', ':""'))
