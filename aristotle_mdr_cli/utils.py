from netrc import netrc
from requests.auth import AuthBase

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',  # Set in as_cli()
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',  # Set in as_cli()
            'class': 'logging.FileHandler',
            'filename': 'migrater.log',
            'mode': 'w',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'transform': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    }
}


class AristotleCommand(object):
    logger = None

    @classmethod
    def logger_setup(cls):
        import logging.config
        logging.config.dictConfig(LOGGING)
        cls.logger = logging.getLogger(cls.__name__)

    def get_auth(self, url):
        """Get login credentials from .netrc"""
        nrc = netrc()
        auth = nrc.authenticators(url.split("//", 1)[-1])
        if auth:
            return auth[2]
        else:
            return None

    def ac_url(self, url):
        if url.startswith("ac://"):
            subdomain = url.replace("ac://", "https://", 1)
            url = f"{subdomain}.aristotlecloud.io"
        elif url == ".":
            url = "localhost"
        return url


class TokenAuth(AuthBase):
    """Attaches HTTP Token Authentication to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return self.token == getattr(other, 'token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = f"Token {self.token}"
        return r
