import uuid

import requests
from telegram import (Chat, InlineKeyboardButton, InlineKeyboardMarkup,
                      Message, Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Filters, MessageHandler, Updater)
from telegram.utils.helpers import create_deep_linked_url

from translator_bot import HEROKU, LOGGER, PORT, TOKEN
from translator_bot.sql.translate import get_translation, save_translation

to_lang = 'hi'
source_lang = 'en'
base_url = 'https://libretranslate.de/'


def start(update: Update, context: CallbackContext):
    if not isinstance(update.effective_chat, Chat):
        raise TypeError
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a translate bot! Send me any message to see how I work!")


def translate_it(update: Update, context: CallbackContext):
    if not isinstance(update.effective_message, Message) or not isinstance(
            update.effective_chat, Chat):
        raise TypeError("This function only works with messages")
    text = update.effective_message.text

    # Translator
    params = {'source': source_lang, 'target': to_lang, 'q': text}
    r = requests.post(base_url + 'translate', params=params)
    result = r.json()
    translated = result['text']
    uid = uuid.uuid4().int
    save_translation(uid, translated)
    keyboard = [[
        InlineKeyboardButton("Translate to Hindi!", callback_data=uid)
    ]]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=InlineKeyboardMarkup(keyboard))


def translate_callback(update: Update, context: CallbackContext):
    payload = update.callback_query.data
    url = create_deep_linked_url(context.bot.username, payload)
    update.callback_query.answer(url=url)


def translated_message(update: Update, context: CallbackContext):
    if not isinstance(update.effective_message, Message):
        raise TypeError("This function only works with messages")
    payload = int(context.args[0]) if context.args is not None else 0
    translation = get_translation(payload)
    update.effective_message.reply_text(translation)


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CallbackQueryHandler(translate_callback, pattern='^[0-9]+'))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.update.edited_message,
                       translate_it))
    dispatcher.add_handler(
        CommandHandler('start', translated_message,
                       Filters.regex(pattern='^[0-9]+')))
    dispatcher.add_handler(CommandHandler('start', start))

    updater.start_webhook(listen='0.0.0.0',
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=HEROKU + TOKEN)


if __name__ == '__main__':
    LOGGER.info('Running in heroku mode')
    main()
