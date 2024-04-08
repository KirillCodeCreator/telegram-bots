from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN

# залы
HALL1, HALL2, HALL3, HALL4 = range(4)


async def start(update, context):
    await update.message.reply_text(
        "Добро пожаловать! Пожалуйста, сдайте верхнюю одежду в гардероб!")
    return await goto_hall1(update, context)


async def stop(update, context):
    await update.message.reply_text("Всего доброго, не забудьте забрать верхнюю одежду в гардеробе!",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def goto_hall1(update, context):
    keyboard = [["2"], ["Выйти"]]
    msg = "В данном зале представлены картины Древней Греции\n" \
          "Переходы в залы:\n" \
          "2 - Амфоры"
    await update.message.reply_text(
        msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return HALL1


async def goto_hall2(update, context):
    keyboard = [["3"]]
    msg = "В данном зале представлены амфоры Древней Греции\n" \
          "Переходы в залы:\n" \
          "3 - Оружие"
    await update.message.reply_text(
        msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return HALL2


async def goto_hall3(update, context):
    keyboard = [["4", "1"]]
    msg = "В данном зале представлено оружие Древней Греции\n" \
          "Переходы в залы:\n" \
          "1 - Картины\n" \
          "4 - Монеты"
    await update.message.reply_text(
        msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return HALL3


async def goto_hall4(update, context):
    keyboard = [["1"]]
    msg = "В данном зале представлены монеты Древней Греции\n" \
          "Переходы в залы:\n" \
          "1 - Картины"
    await update.message.reply_text(
        msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return HALL4


async def hall1(update, context):
    msg_text = update.message.text
    if msg_text == "2":
        return await goto_hall2(update, context)
    elif msg_text == "Выйти":
        return await stop(update, context)


async def hall2(update, context):
    msg_text = update.message.text
    if msg_text == "3":
        return await goto_hall3(update, context)


async def hall3(update, context):
    msg_text = update.message.text
    if msg_text == "4":
        return await goto_hall4(update, context)
    elif msg_text == "1":
        return await goto_hall1(update, context)


async def hall4(update, context):
    msg_text = update.message.text
    if msg_text == "1":
        return await goto_hall1(update, context)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            HALL1: [MessageHandler(filters.TEXT, hall1)],
            HALL2: [MessageHandler(filters.TEXT, hall2)],
            HALL3: [MessageHandler(filters.TEXT, hall3)],
            HALL4: [MessageHandler(filters.TEXT, hall4)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
