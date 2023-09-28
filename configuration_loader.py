import json
import logging
from typing import Tuple, Dict, Any, IO, TypeVar, Type

from global_variables import FILE_DOESNT_EXIST, WRONG_FILE, MISSING_OR_EMPTY_PARAMETER, WRONG_PARAMETER_TYPE_IN_FILE

T = TypeVar('T')


class ConfigurationLoader:
    def read_from_file(self, file_name: str) -> Dict[str, Any]:
        try:
            with open(file_name, encoding='utf-8') as file:
                configuration = self._load_json(file)
                self._validate(configuration)
                return configuration
        except FileNotFoundError:
            logging.error(FILE_DOESNT_EXIST)
            exit(1)

    @staticmethod
    def _load_json(file: IO) -> Dict[str, Any]:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            logging.error(WRONG_FILE)
            exit(1)

    def _validate(self, configuration: Dict[str, Any]) -> None:
        if not isinstance(configuration, dict):
            logging.error(WRONG_FILE)
            exit(1)
        for item in [('sender_email', str), ('sender_email_password', str), ('addresses', list)]:
            self._check_value_and_type(configuration, item)
        for address_data in configuration.get('addresses'):
            for item in [('street_name', str), ('house_number', str), ('city', str), ('receivers_emails', list)]:
                self._check_value_and_type(address_data, item)
            for i, receivers_emails in enumerate(address_data['receivers_emails']):
                self._check_type(receivers_emails, f"address['receivers_emails'][{i}]", str)

    def _check_value_and_type(self, dictionary: Dict[str, Any], item: Tuple[str, Type[T]]) -> None:
        parameter_name = item[0]
        parameter_value = dictionary.get(parameter_name, None)
        self._check_value(parameter_value, parameter_name)
        self._check_type(parameter_value, parameter_name, item[1])

    @staticmethod
    def _check_value(parameter_value: Any, parameter_name: str) -> None:
        if not parameter_value:
            logging.error(MISSING_OR_EMPTY_PARAMETER.format(parameter_name))
            exit(1)

    @staticmethod
    def _check_type(parameter_value: Any, parameter_name: str, parameter_type: Type[T]) -> None:
        if not isinstance(parameter_value, parameter_type):
            logging.error(WRONG_PARAMETER_TYPE_IN_FILE.format(parameter_name, parameter_type))
            exit(1)
