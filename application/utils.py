import logging
import random
import string

import telegram

from application import errors

log = logging.getLogger('bot')


def catch_error(func):
    def wrapper(update: telegram.Update, *args, **kwargs):
        try:
            return func(update, *args, **kwargs)
        except errors.BotError as e:
            if update.message:
                update.message.reply_text(e.text, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                update.effective_chat.send_message(e.text, parse_mode=telegram.ParseMode.MARKDOWN)

        except Exception:
            error_id = hex(random.randint(10 ** 5, 10 ** 6))[2:]
            log.exception(f'Error {error_id} occured in method {func.__name__}')
            update.message.reply_text(f'I\'m sorry. Something goes wrong.\n'
                                      f'Please, notify me (@pirotech) and specify error id {error_id}',
                                      parse_mode=telegram.ParseMode.MARKDOWN)

    return wrapper


def generate_group_id():
    """
    >>> import re
    >>> assert re.fullmatch(r'[0-9A-Z]{6}', generate_group_id())
    >>> assert re.fullmatch(r'[0-9A-Z]{6}', generate_group_id())
    >>> assert re.fullmatch(r'[0-9A-Z]{6}', generate_group_id())
    >>> assert re.fullmatch(r'[0-9A-Z]{6}', generate_group_id())
    >>> assert re.fullmatch(r'[0-9A-Z]{6}', generate_group_id())
    >>> assert re.fullmatch(r'[0-9A-Z]{6}', generate_group_id())
    """
    return ''.join(random.sample(string.digits + string.ascii_uppercase, k=6))
