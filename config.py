import logging
import os

DEBUG = False
LOG_LEVEL = logging.INFO

BOT_TOKEN = None
DB_DSN = None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# local

for var in set(locals()):
    if not var.startswith('_') and os.environ.get(var) is not None:
        locals().update({var: os.environ.get(var)})

