import requests
import logging
import telegram
import os
import argparse
from datetime import datetime
import time
import json


token = os.environ("TELEGRAM_TOKEN")
devman_token = os.environ("DEVMAN_TOKEN")
chat_id = os.environ('CHAT_ID')
bot = telegram.Bot(token=token)
longpool_api = 'https://dvmn.org/api/long_polling/'
headers = {"Authorization": devman_token}

class JsonDataError(ValueError):
  pass


def get_data(url, headers, timestamp):
  params={'timestamp': timestamp}
  try:
    response = requests.get(url, headers=headers, params=params)
  except (requests.exceptions.ReadTimeout, ConnectionError):
    pass
  response.raise_for_status()
  json_data = response.json()
  if 'error' in json_data:
    raise JsonDataError('Данные поступили с ошибкой внутри')
  return json_data


def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser()
  parser.add_argument('--chat_id', help='Ваш ID в телеграмм', default=chat_id)
  args = parser.parse_args()
  timestamp = time.time()

  while True: 
    json_data = get_data(longpool_api, headers, timestamp)
    if json_data['status'] == 'found':
      lesson_url = json_data['new_attempts'][0]['lesson_url']
      bot.send_message(
        chat_id=args.chat_id,
        text=f'Преподаватель проверил работу!\nПосмотреть можно по ссылке:https://dvmn.org{lesson_url}'
        )
      timestamp = json_data['last_attempt_timestamp']
    if json_data['status'] == 'timeout':
      timestamp = json_data['timestamp_to_request']

if __name__ == '__main__':
  print('Start')
  main()
