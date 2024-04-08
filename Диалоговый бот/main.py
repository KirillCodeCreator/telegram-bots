from telegram import Update
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN


async def start(update, context):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос.\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "Или пропустить данный вопрос, послав команду /skip.\n"
        "В каком городе вы живёте?")
    return 1


async def first_response(update, context):
    message = update.message.text

    if message == "/skip":
        await update.message.reply_text("Какая погода у вас за окном?")
    elif message == "/stop":
        return await stop(update, context)
    else:
        await update.message.reply_text(
            "Какая погода в городе {message}?".format(**locals()))

    return 2


async def second_response(update, context):
    weather = update.message.text
    print(weather)
    await update.message.reply_text("Спасибо за участие в опросе! Всего доброго!")
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Опрос прерван. Спасибо за участие.")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT, second_response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
