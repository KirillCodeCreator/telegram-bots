import json
import random

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN

FILE_LOADED, TEST_STARTED = range(2)

json_bytes = None


async def init_test(update, context):
    json_data = json.loads(json_bytes)
    try:
        if not all(map(lambda test: "question" in test and "response" in test, json_data["test"])):
            raise KeyError()
    except KeyError:
        await update.message.reply_text("Неверный файл!")
    if len(json_data["test"]) < 10:
        context.chat_data["quest_count"] = len(json_data["test"])
    else:
        context.chat_data["quest_count"] = 10
    context.chat_data["test"] = json_data["test"]
    context.chat_data["correct"] = 0


async def parse_json(update, context):
    global json_bytes
    file = await update.message.document.get_file()
    json_bytes = await file.download_as_bytearray()
    await init_test(update, context)
    await update.message.reply_text(
        "Файл с тестами заружен, используйте /start для начала тестирования")
    return FILE_LOADED


async def question(update, context):
    q_count = len(context.chat_data["test"])
    data = context.chat_data["test"].pop(random.randrange(q_count))
    context.chat_data["response"] = data["response"]
    context.chat_data["quest_count"] -= 1
    await update.message.reply_text(data["question"])


async def start(update, context):
    await update.message.reply_text("Тест запущен!", reply_markup=ReplyKeyboardRemove())
    await question(update, context)
    return TEST_STARTED


async def answer(update, context):
    reply = update.message.text
    if reply == "/stop":
        return await stop_work(update, context)
    if reply.lower() == context.chat_data["response"].lower():
        await update.message.reply_text("Правильно!")
        context.chat_data["correct"] += 1
    else:
        await update.message.reply_text("Неправильно!")
    if context.chat_data["quest_count"] > 0:
        return await question(update, context)
    else:
        await update.message.reply_text(
            f"Правильных {context.chat_data['correct']} ответов")
        return await stop(update, context)


async def stop_work(update, context):
    del context.chat_data["test"]
    del context.chat_data["correct"]
    del context.chat_data["quest_count"]
    del context.chat_data["response"]
    keyboard = [["/start"]]
    await update.message.reply_text("Тест остановлен!",
                                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    await init_test(update, context)
    return FILE_LOADED


async def stop(update, context):
    keyboard = [["/start"]]
    await update.message.reply_text("До встречи!",
                                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    await init_test(update, context)
    return FILE_LOADED


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(
            filters.Document.MimeType("application/json"), parse_json)],
        states={
            FILE_LOADED: [CommandHandler("start", start)],
            TEST_STARTED: [MessageHandler(filters.TEXT, answer)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
