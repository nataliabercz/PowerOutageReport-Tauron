import json
import logging
from typing import Tuple, Dict, Any, IO, TypeVar, Type

from global_variables import FILE_DOESNT_EXIST, WRONG_FILE, MISSING_OR_EMPTY_PARAMETER, WRONG_PARAMETER_TYPE

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

    @staticmethod
    def _check_value_and_type(dictionary: Dict[str, Any], item: Tuple[str, Type[T]]) -> None:
        parameter = dictionary.get(item[0], None)
        if not parameter:
            logging.error(MISSING_OR_EMPTY_PARAMETER.format(item[0]))
            exit(1)
        if not isinstance(parameter, item[1]):
            logging.error(WRONG_PARAMETER_TYPE.format(item[0], item[1]))
            exit(1)
