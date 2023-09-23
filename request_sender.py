import logging
import requests
import urllib.parse
from typing import Dict, Any
from global_variables import URL, WRONG_REQUEST


class RequestSender:
    def __init__(self) -> None:
        self.request = requests.Session()

    def send_request(self, url_postfix: str, payload: Dict[str, Any]) -> str:
        try:
            response = self.request.get(URL.format(url_postfix + '?' + urllib.parse.urlencode(payload)))
            if response.status_code == 200:
                return self._adjust_response(response.text)
            else:
                logging.error(WRONG_REQUEST.format(response.status_code))
                exit(1)
        except Exception as e:
            logging.error(str(e))
            exit(1)

    @staticmethod
    def _adjust_response(response: str) -> str:
        return response.replace(':f', ':F').replace(':t', ':T').replace(':null', ':""')
