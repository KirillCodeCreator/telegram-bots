import requests
from telegram import Update
from telegram.ext import MessageHandler, filters, Application

from config import BOT_TOKEN


def get_ll_spn_toponym(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    lower_corner = [float(e) for e in envelope["lowerCorner"].split()]
    upper_corner = [float(e) for e in envelope["upperCorner"].split()]

    delta_x = upper_corner[0] - lower_corner[0]
    delta_y = upper_corner[1] - lower_corner[1]

    return ",".join(toponym["Point"]["pos"].split()), ",".join([str(delta_x), str(delta_y)])


async def geocoder(update, context):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": update.message.text
    })

    if not response:
        await update.message.reply_text(
            "Ошибка выполнения HTTP запроса\n"
            f"HTTP статус: {response.status_code} ({response.reason})"
        )
        return

    results = response.json()["response"]["GeoObjectCollection"]["featureMember"]
    if len(results) == 0:
        await update.message.reply_text(
            f"Не удалось найти место по переданному тексту: {update.message.text}. Проверьте, может вы ошиблись в написании."
        )
        return

    toponym = results[0]["GeoObject"]
    ll, spn = get_ll_spn_toponym(toponym)
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map&pt={ll},pm2rdm"
    await context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption=f"Найдено запрошенное место: {toponym['name']}, {toponym['description']}"
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, geocoder))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
