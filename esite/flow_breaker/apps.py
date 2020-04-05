from django.apps import AppConfig
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
from telegram.utils.request import Request
from django.conf import settings
from pydub import AudioSegment
import os


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




class FlowBreakerConfig(AppConfig):
    name = 'esite.flow_breaker'



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
    def start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')


    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def echo(self, update, context):
        """Echo the user message."""

        file = bot.getFile(update.message.voice.file_id)
        print ("file_id: " + str(update.message.voice.file_id))
        file.download('voice.ogg')

        bot.send_audio(chat_id=chat_id, audio=open('./Go.mp3', 'rb'))
      #  update.message.reply_text(update.message.text)


    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)


    def ready(self):
        
        print(settings.TELEGRAM_BOT_TOKEN)
        request = Request(connect_timeout=200, read_timeout=200)
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, request=request)
        updates = bot.get_updates()
        print([u.message.text for u in updates])
        chat_id =  bot.get_updates()[-1].message.chat_id



        song = AudioSegment.from_mp3("esite/flow_breaker/Go.mp3")
        song.export("mashup.ogg", format="ogg")

        bot.send_message(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")
        #bot.send_audio(chat_id=chat_id, audio=open('esite/flow_breaker/Go.mp3', 'rb'))
        bot.send_voice(chat_id=chat_id, voice=open('mashup.ogg', 'rb'))
        
        os.remove("mashup.ogg")
        
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater("1155985628:AAEzVNBpXFz4hRFqIIggt6f7FuObRP8PxLQ", use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", help))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.echo))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2020 miraculix-org Florian Kleber

        