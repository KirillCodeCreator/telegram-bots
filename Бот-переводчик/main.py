from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, filters, Application
# Command to install googletrans: pip install googletrans==3.1.0a0
from translate import Translator

from config import BOT_TOKEN

START_KEYBOARD = ReplyKeyboardMarkup(
    [["ru-en", "en-ru"]], one_time_keyboard=False
)
AVAILABLE_LANGUAGES = ["ru", "en"]

translatorEn = Translator(from_lang="ru", to_lang="en")
translatorRu = Translator(from_lang="en", to_lang="ru")


def translate(from_lang, to_lang, word):
    global translatorEn
    global translatorRu
    if to_lang == "en":
        return translatorEn.translate(word)
    else:
        return translatorRu.translate(word)


async def echo(update, context):
    message = update.message.text
    languages = message.split("-")

    if len(languages) == 2 and [e in AVAILABLE_LANGUAGES for e in languages]:
        context.user_data["from"], context.user_data["to"] = languages
        await update.message.reply_text(f"Выбрано направление перевода {message}")
    else:
        from_lang = context.user_data.get("from", None)
        to_lang = context.user_data.get("to", None)
        if from_lang and to_lang:
            await update.message.reply_text(translate(from_lang, to_lang, message), reply_markup=START_KEYBOARD)


async def start(update, context):
    await update.message.reply_text(
        "Выберите направление перевода и напишите текст для перевода на выбранный вами язык."
        " Направление перевода по умолчанию: ru-en",
        reply_markup=START_KEYBOARD
    )
    context.user_data["from"], context.user_data["to"] = "ru", "en"


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
