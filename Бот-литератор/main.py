from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN

WAITING, WAITING_SUPHLER = range(2)

POEM_LINES = """Я вас любил: любовь еще, быть может,
В душе моей угасла не совсем;
Но пусть она вас больше не тревожит;
Я не хочу печалить вас ничем.
Я вас любил безмолвно, безнадежно,
То робостью, то ревностью томим;
Я вас любил так искренно, так нежно,
Как дай вам Бог любимой быть другим."""


async def start(update, context):
    context.chat_data["poem_lines"] = POEM_LINES.split("\n")[::-1]
    await update.message.reply_text(context.chat_data["poem_lines"].pop(),
                              reply_markup=ReplyKeyboardRemove())
    return WAITING


async def stop(update, context):
    await update.message.reply_text("Работа завершена",
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def check_poem_end(update, context):
    return not context.chat_data["poem_lines"]


async def wait_str(update, context):
    msg_text = update.message.text
    if msg_text == "/stop":
        return await stop(update, context)
    if msg_text == context.chat_data["poem_lines"][-1]:
        context.chat_data["poem_lines"].pop()
        try:
            await update.message.reply_text(context.chat_data["poem_lines"].pop())
            if not context.chat_data["poem_lines"]:
                raise IndexError()
        except IndexError:
            await update.message.reply_text(
                "Ура!\nНапишите '/start', чтобы повторить")
            return await stop(update, context)
        return WAITING
    else:
        keyboard = [["/suphler"]]
        await update.message.reply_text("нет, не так",
                                  reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                   resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return WAITING_SUPHLER


async def suphler(update, context):
    await update.message.reply_text("Подсказка: " + context.chat_data["poem_lines"][-1],
                              reply_markup=ReplyKeyboardRemove())
    return WAITING


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING: [MessageHandler(filters.TEXT, wait_str)],
            WAITING_SUPHLER: [CommandHandler("suphler", suphler), MessageHandler(filters.TEXT, wait_str)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
