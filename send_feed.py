import os
import requests
from datetime import date

from dotenv import load_dotenv

from data import filename

load_dotenv()
TOKEN = os.environ.get('botToken')
CHAT_ID = os.environ.get('chatId')

url_send_message = f'https://api.telegram.org/bot{TOKEN}/sendMessage'


def send_message_from_bot(bot_message: str) -> None:
    """Отправляет сообщение от бота"""
    json = {'chat_id': CHAT_ID, 'parse_mode': 'HTML', 'text': bot_message}
    r = requests.post(url_send_message, json=json)
    if not r.status_code == 200:
        with open('log.txt', 'a', encoding='utf8'):
            f.write(f'{date.today()} ERROR (send_feed.py -> send_message_from_bot()): Код ответа при отправке сообщения "{r.status_code}"')


with open(filename, 'r', encoding='utf8')as f:
    message = f.read()

if len(message) <= 3500:
    send_message_from_bot(message)
else:
    while len(message) > 3500:
        index = message.index('</a>', 3000, 3450) + 4
        part_of_message = message[:index]
        send_message_from_bot(part_of_message)
        message = message[index + 1:]
        if len(message) <= 3500:
            send_message_from_bot(message)
