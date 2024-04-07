# Импортируем необходимые классы.
import locale
import logging
import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Application, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN

locale.setlocale(locale.LC_ALL, "ru")

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

timers = {
    "30 секунд": lambda: 30,
    "1 минута": lambda: 60,
    "5 минут": lambda: 300,
}

exit_var = [["вернуться назад"]]

dices = {
    "кинуть один шестигранный кубик": lambda: [random.randint(1, 6)],
    "кинуть 2 шестигранных кубика одновременно": lambda: [random.randint(1, 6) for _ in range(2)],
    "кинуть 20-гранный кубик": lambda: [random.randint(1, 20)],
}

start_markup = ReplyKeyboardMarkup(
    [["/dice", "/timer"]], one_time_keyboard=True
)
dice_markup = ReplyKeyboardMarkup(
    [[e] for e in dices.keys()] + exit_var, one_time_keyboard=False
)
timer_markup = ReplyKeyboardMarkup(
    [[e] for e in timers.keys()] + exit_var, one_time_keyboard=True
)
close_markup = ReplyKeyboardMarkup(
    [["/close"]], one_time_keyboard=True
)


async def start(update, context):
    await update.message.reply_text("Cтартовая клавиатура", reply_markup=start_markup)


async def dice(update, context):
    await update.message.reply_text("Клавиатура для кидания кубика", reply_markup=dice_markup)


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать...")


async def timer(update, context):
    await update.message.reply_text(
        "Клавиатура для выбора таймера",
        reply_markup=timer_markup
    )


async def message(update, context):
    msg = update.message.text
    if msg == "вернуться назад":
        await start(update, context)

    elif msg in dices.keys():
        await update.message.reply_text(" ".join([str(e) for e in dices[msg]()]))
    elif msg in timers.keys():
        due = timers[msg]()

        await update.message.reply_text(f"засек {msg}")
        set_timer(context, update.message.chat_id, due, msg)

        await update.message.reply_text(
            "Если необходимо отменить таймер - нажмите кнопку!",
            reply_markup=close_markup
        )


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(context, chat_id, due, msg):
    remove_job_if_exists(
        str(chat_id),
        context
    )

    context.job_queue.run_once(task, due, chat_id=chat_id, name=str(chat_id), data=msg)


async def task(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"{job.data} истекло",
                                   reply_markup=timer_markup)


async def unset_timer(update, context):
    chat_id = update.message.chat_id
    remove_job_if_exists(str(chat_id), context)
    await context.bot.send_message(chat_id, text=f"Таймер отменен",
                                   reply_markup=timer_markup)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("close", unset_timer))

    text_handler = MessageHandler(filters.TEXT, message)
    application.add_handler(text_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
