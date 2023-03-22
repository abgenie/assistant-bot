import os
import requests
from dotenv import load_dotenv
from data import filename

load_dotenv()
TOKEN = os.environ.get('botToken')
CHAT_ID = os.environ.get('chatId')

url_send_message = f'https://api.telegram.org/bot{TOKEN}/sendMessage'


def main():
    with open(filename, 'r', encoding='utf8') as f:
        message = f.read()

    if len(message) <= 3500:
        send_message_from_bot(message)
    else:
        while len(message) > 3500:
            # Помещаем в индекс конец строки, заканчивающийся ссылкой в диапазоне (3000 - 3450)
            index = message.index('</a>', 3000, 3450) + 4
            part_of_message = message[:index]
            send_message_from_bot(part_of_message)
            message = message[index + 1:]
            if len(message) <= 3500:
                send_message_from_bot(message)

    f = open(filename, 'w', encoding='utf8')
    f.close()


def send_message_from_bot(bot_message: str) -> None:
    """Отправляет сообщение от бота"""
    json = {'chat_id': CHAT_ID, 'parse_mode': 'HTML', 'text': bot_message}
    requests.post(url_send_message, json=json)


if __name__ == '__main__':
    main()
