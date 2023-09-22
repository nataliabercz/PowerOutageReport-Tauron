import ast
import time
import logging
from typing import Dict, Any
from request_sender import RequestSender
from global_variables import WRONG_STREET_NAME_OR_CITY


class Address:
    street_name = None
    house_number = None
    city = None
    city_id = None
    street_id = None

    def __init__(self) -> None:
        self.request_sender = RequestSender()

    def set_address_data(self, address_data: Dict[str, Any]) -> None:
        self.street_name = address_data.get('street_name')
        self.house_number = address_data.get('house_number')
        self.city = address_data.get('city')
        self._set_city_id()
        self._set_street_id()

    def _set_city_id(self) -> None:
        self._set_attribute('city_id', 'enum/geo/cities', {'partName': self.city, '_': int(time.time() * 1000)})

    def _set_street_id(self) -> None:
        self._set_attribute('street_id', 'enum/geo/streets', {'partName': self.street_name, 'ownerGAID': self.city_id,
                                                              '_': int(time.time() * 1000)})

    def _set_attribute(self, variable_name: str, url_postfix: str, payload: Dict[str, Any]) -> None:
        try:
            setattr(self, variable_name, ast.literal_eval(self._get_response(url_postfix, payload))[0]['GAID'])
        except IndexError:
            logging.error(WRONG_STREET_NAME_OR_CITY.format(self.street_name, self.city))
            exit(1)

    def _get_response(self, url_postfix: str, payload: Dict[str, Any]) -> str:
        return self.request_sender.send_request(url_postfix, payload)
