import time
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

from address import Address
from email_sender import EmailSender
from request_sender import RequestSender
from configuration_loader import ConfigurationLoader
from global_variables import JSON_CONFIGURATION_FILE_PATH, CONNECTION_ERROR, CONNECTION_ERROR_RETRYING


class PowerOutageReport:
    days_before = 5
    retries = 5
    sleep_time = 20

    def __init__(self) -> None:
        self.address = Address()
        self.email_sender = EmailSender()
        self.request_sender = RequestSender()
        self.configuration_loader = ConfigurationLoader()

    def send_outage_report(self) -> None:
        configuration = self.configuration_loader.read_from_file(JSON_CONFIGURATION_FILE_PATH)
        self.email_sender.set_sender_info(configuration)
        for address_data in configuration.get('addresses'):
            self.address.set_address_data(address_data)
            self._try_to_execute_function(self.address.set_city_id)
            self._try_to_execute_function(self.address.set_street_id)
            self.email_sender.set_receivers_info(address_data)
            self.email_sender.street_name = self.address.street_name
            self._try_to_execute_function(self._send_outage_report)

    def _try_to_execute_function(self, function: Any) -> None:
        try:
            function()
            self.retries = 5
        except requests.ConnectionError:
            logging.error(CONNECTION_ERROR_RETRYING.format(self.sleep_time, self.retries))
            self._retry(function)

    def _retry(self, function) -> None:
        if self.retries > 0:
            self.retries -= 1
            time.sleep(self.sleep_time)
            self._try_to_execute_function(function)
        else:
            logging.error(CONNECTION_ERROR)
            exit(1)

    def _send_outage_report(self) -> None:
        self.email_sender.prepare_and_send_email(self._get_outage_information())

    def _get_outage_information(self) -> List[Dict[str, Any]]:
        now = datetime.now()
        payload = {'cityGAID': self.address.city_id, 'streetGAID': self.address.street_id,
                   'houseNo': self.address.house_number, 'fromDate': now.isoformat(),
                   'toDate': (now + timedelta(days=self.days_before)).isoformat(),
                   'flatNo': '', '_': int(now.timestamp() * 1000)}
        return self.request_sender.send_request('outages/address', payload)['OutageItems']


if __name__ == '__main__':
    power_outage_report = PowerOutageReport()
    power_outage_report.send_outage_report()
