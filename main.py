import logging
import os

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, PollAnswerHandler

import exceptions
import locations
import shots

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TOTAL_VOTER_COUNT = 1

async def start(update, context):
    message = '''Привет\n\n'
        Отправить локацию: /location\n
        Получить последнюю локацию: /where\n"
        Указать укол: /shot'''

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def echo(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def location(update, context):
    button = [[KeyboardButton("Поделиться локацией!", request_location=True)]]
    message = "Нажмите кнопку"
    await update.message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )


async def receive_location(update, context):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    try:
        answer = locations.add_location(longitude, latitude)
    except exceptions.NotAnswers as e:
        answer = str(e)

    await update.message.reply_text(answer)


async def see_location(update, context):
    message = locations.see_location()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def poll(update, context):
    questions = ["Левая", "Правая"]
    message = await context.bot.send_poll(
        update.effective_chat.id,
        "Куда?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )

    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }

    context.bot_data.update(payload)


async def receive_poll_answer(update, context):
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    try:
        questions = answered_poll["questions"]
    except KeyError:
        return

    selected_options = answer.option_ids
    answer_string = questions[selected_options[0]] if selected_options else ""

    try:
        answer = shots.add_shot(answer_string)
    except exceptions.NotAnswers as e:
        answer = str(e)

    await context.bot.send_message(
        answered_poll["chat_id"],
        f"Для {update.effective_user.mention_html()}: {answer}",
        parse_mode=ParseMode.HTML,
    )
    answered_poll["answers"] += 1

    if answered_poll["answers"] == TOTAL_VOTER_COUNT:
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])


async def unknown(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Неизвестная команда!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    location_handler = CommandHandler('location', location)
    application.add_handler(location_handler)

    see_location_handler = CommandHandler('last', see_location)
    application.add_handler(see_location_handler)

    receive_location_handler = MessageHandler(filters.LOCATION, receive_location)
    application.add_handler(receive_location_handler)

    application.add_handler(CommandHandler("shot", poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()

