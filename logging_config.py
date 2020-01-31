# -*- coding: utf-8 -*-

import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'facility': 'user',
            'address': '/dev/log',            
        },
    },
    'loggers': {
        'scrapper': {
            'handlers': ['syslog'],
            'level': 'DEBUG',
        }
    }
}

logging.config.dictConfig(LOGGING)
_logger = logging.getLogger('scrapper')