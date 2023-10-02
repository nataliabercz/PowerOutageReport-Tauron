import os

URL = 'https://www.tauron-dystrybucja.pl/waapi/{}'

JSON_CONFIGURATION_FILE = 'configuration.json'
JSON_CONFIGURATION_FILE_PATH = f'{os.path.dirname(os.path.realpath(__file__))}/data/{JSON_CONFIGURATION_FILE}'
IN_FILE = f'in `{JSON_CONFIGURATION_FILE}` file.'
FILE_DOESNT_EXIST = f"The `{JSON_CONFIGURATION_FILE}` file doesn't exist."
WRONG_FILE = f'The `{JSON_CONFIGURATION_FILE}` file is not correct.'
MISSING_OR_EMPTY_PARAMETER = 'The parameter: `{}` is missing or empty ' + IN_FILE
WRONG_STREET_NAME_OR_CITY = 'The street name: `{}` or city `{}` is not correct ' + IN_FILE
WRONG_PARAMETER_TYPE = 'The parameter: `{}` should have `{}` type '
WRONG_PARAMETER_TYPE_IN_FILE = 'The parameter: `{}` should have `{}` type ' + IN_FILE

AUTHENTICATION_FAILURE = 'Authentication ERROR. Check `sender_email` and `sender_email_passwords` ' + IN_FILE

WRONG_REQUEST = 'Wrong request!'
WRONG_REQUEST_STATUS_CODE = WRONG_REQUEST + 'Status code: {}.'
CONNECTION_ERROR = 'Connection ERROR.'
CONNECTION_ERROR_RETRYING = CONNECTION_ERROR + 'Retrying in {}s... {}'

EMAIL_TITLE = '[TAURON] Planned power outage - {}'
EMAIL_WAS_SENT = 'The email was sent to: {}'
