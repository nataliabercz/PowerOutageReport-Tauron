import os

URL = 'https://www.tauron-dystrybucja.pl/waapi/{}'

JSON_CONFIGURATION_FILE = 'configuration.json'
JSON_CONFIGURATION_FILE_PATH = '{}/data/{}'.format(os.path.dirname(os.path.realpath(__file__)), JSON_CONFIGURATION_FILE)
IN_FILE = 'in `{}` file.'.format(JSON_CONFIGURATION_FILE)
FILE_DOESNT_EXIST = "The `{}` file doesn't exist".format(JSON_CONFIGURATION_FILE)
WRONG_FILE = 'The `{}` file is not correct.'.format(JSON_CONFIGURATION_FILE)
MISSING_OR_EMPTY_PARAMETER = 'The parameter: `{}` is missing or empty ' + IN_FILE
WRONG_STREET_NAME_OR_CITY = 'The street name: `{}` or city `{}` is not correct ' + IN_FILE
WRONG_PARAMETER_TYPE = 'The parameter: `{}` should have `{}` type ' + IN_FILE

WRONG_REQUEST = 'Wrong request! Status code: {}.'
CONNECTION_ERROR = 'Connection ERROR.'
CONNECTION_ERROR_RETRYING = CONNECTION_ERROR + 'Retrying in {}s... {}'

EMAIL_TITLE = '[TAURON] Planned power outage - {}'
EMAIL_WAS_SENT = 'The email was sent to: {}'
