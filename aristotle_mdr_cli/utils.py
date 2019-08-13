from netrc import netrc


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
        auth = nrc.authenticators(url)
        return auth

