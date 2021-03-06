import logging

from telegram.ext import (CommandHandler, Updater, CallbackContext, CallbackQueryHandler)
import telegram

from application import config, errors, utils
from application.storage import Storage

log = logging.getLogger('bot')

start_understand_keyboard = telegram.InlineKeyboardMarkup([[
    telegram.InlineKeyboardButton('I\'m start understanding!', callback_data='1')]])
stop_understand_keyboard = telegram.InlineKeyboardMarkup([[
    telegram.InlineKeyboardButton('I\'m stop understanding :(', callback_data='0')]])
keyboards = {
    False: start_understand_keyboard,
    True: start_understand_keyboard,
}


class Group:
    id: str

    def __init__(self, author_id: int):
        self.id = utils.generate_group_id()
        self.owner_id = author_id

    @classmethod
    def new(cls, author_id: int):
        group = cls(author_id)
        Storage.add_group(group.id)
        return group


def start(update: telegram.Update, context):
    update.message.reply_text('Hello, I\'m help speakers explain you everything.\n'
                              'If you stop understanding, hit "I stop understand" button and speaker can see it.\n'
                              'Start right know! Join you group with command /join *GROUP_CODE*',
                              parse_mode=telegram.ParseMode.MARKDOWN)


@utils.catch_error
def join_group(update: telegram.Update, context: CallbackContext):
    if len(context.args) < 1:
        raise errors.JoinNotEnoghtArgument
    group_id: str = context.args[0].strip().upper()
    if not group_id.isalnum():
        raise errors.InvalidGroupId
    if not Storage.add_user_to_group(group_id, update.effective_user.id):
        raise errors.GroupNotFound
    update.message.reply_text(f'Ok! Now you *understanding*!',
                              reply_markup=stop_understand_keyboard,
                              parse_mode=telegram.ParseMode.MARKDOWN)


@utils.catch_error
def keyboard_callback(update: telegram.Update, context: CallbackContext):
    state = Storage.get_user_state(update.effective_user.id)
    if state is None:
        raise errors.UserHaveNoActiveGroup
    query = update.callback_query
    new_state = bool(int(query.data))
    if not state ^ new_state:
        return
    Storage.set_user_state(update.effective_user.id, new_state)
    if new_state:
        query.edit_message_text(text=f'Ok! Now you *understanding*!', reply_markup=stop_understand_keyboard,
                                parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        query.edit_message_text(text=f'Ok! Now you *not understanding* :(', reply_markup=start_understand_keyboard,
                                parse_mode=telegram.ParseMode.MARKDOWN)


def new_group(update: telegram.Update, context: CallbackContext):
    group = Group.new(update.effective_user.id)
    update.message.reply_text(f'Group created with id *{group.id}*.\n'
                              f'Show it your members.',
                              parse_mode=telegram.ParseMode.MARKDOWN)


def error(update, context):
    log.error('Update "%s" caused error "%s"', update, context.error)


def main():
    """Run bot."""
    assert config.BOT_TOKEN
    updater = Updater(config.BOT_TOKEN, use_context=True)

    Storage.init()

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("join", join_group, pass_args=True, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("new", new_group, pass_args=True, pass_chat_data=True))
    updater.dispatcher.add_handler(CallbackQueryHandler(keyboard_callback))
    dispatcher.add_error_handler(error)

    log.info('Bot started')
    updater.start_polling()

    updater.idle()
    log.info(f'Bot shutdown...')
    Storage.close()


if __name__ == '__main__':
    main()
