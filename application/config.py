import logging
import os

LOG_LEVEL = 'INFO'

BOT_TOKEN = None
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)

# local

for var in set(locals()):
    if not var.startswith('_') and os.environ.get(var) is not None:
        locals().update({var: os.environ.get(var)})

