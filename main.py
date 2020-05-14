import requests
import logging
import telegram
import os
import argparse
from datetime import datetime
import time
import json
from time import sleep


tg_token = os.getenv("BOT_TOKEN")
devman_token = os.getenv("DEVMAN_TOKEN")
chat_id = os.getenv('TG_CHAT_ID')
bot = telegram.Bot(token=tg_token)
longpool_api = 'https://dvmn.org/api/long_polling/'
headers = {"Authorization": f'Token {devman_token}'}

class JsonDataError(ValueError):
  pass

class TelegramLogsHandler(logging.Handler):

  def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot
  
  def emit(self, record):
      log_entry = self.format(record)
      self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_data(url, headers, timestamp):
  params={'timestamp': timestamp}
  try:
    response = requests.get(url, headers=headers, params=params)
  except (requests.exceptions.ReadTimeout, ConnectionError):
    sleep(300)
    return
  response.raise_for_status()
  json_data = response.json()
  if 'error' in json_data:
    raise JsonDataError('Данные поступили с ошибкой внутри')
  return json_data




def main():
  timestamp = time.time()
  while True:
    try:
      logger = logging.getLogger('Logger')
      logger.setLevel(logging.WARNING)
      logger.addHandler(TelegramLogsHandler(bot, chat_id))
      logger.error('Бот запущен')

      parser = argparse.ArgumentParser()
      parser.add_argument('--chat_id', help='Ваш ID в телеграмм', default=chat_id)
      args = parser.parse_args()

      while True:
        json_data = get_data(longpool_api, headers, timestamp)
        print(json_data)
        if json_data['status'] == 'found':
          lesson_url = json_data['new_attempts'][0]['lesson_url']
          bot.send_message(
            chat_id=args.chat_id,
            text=f'Преподаватель проверил работу!\nПосмотреть можно по ссылке:https://dvmn.org{lesson_url}'
            )
          timestamp = json_data['last_attempt_timestamp']
        if json_data['status'] == 'timeout':
          timestamp = json_data['timestamp_to_request']
    except Exception:
      logger.exception('Бот упал с ошибкой:')
      sleep(30)

if __name__ == '__main__':
  main()

