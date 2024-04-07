# Импортируем необходимые классы.
import datetime
import locale
import logging

from telegram.ext import Application, MessageHandler, filters, CommandHandler

from config import BOT_TOKEN

locale.setlocale(locale.LC_ALL, "ru")

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!",
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


async def echo(update, context):
    await update.message.reply_text(f'Я получил сообщение {update.message.text}')


async def cmd_time(update, context):
    today = datetime.datetime.today().strftime("%X")
    await update.message.reply_text(today)


async def cmd_date(update, context):
    today = datetime.datetime.today().strftime("%A, %d %B %Y")
    await update.message.reply_text(today)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", cmd_time))
    application.add_handler(CommandHandler("date", cmd_date))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()


if __name__ == '__main__':
    main()
