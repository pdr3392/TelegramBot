import telebot
import datetime
from decouple import config
import finnhub
from time import sleep
import datetime
import schedule
import time


bot = telebot.TeleBot(config('TELEGRAM_BOT_KEY'), parse_mode='HTML')
#some_id = int('-1001515068629')
some_id = int('-537806206')

class Apihandler:
    def __init__(self, finnhub_client):
        self.finnhub_client = finnhub.Client(api_key=finnhub_client)

    def get_news(self, time_setter):
        news_list = []
        for item in self.finnhub_client.general_news('general', min_id=0):
            date_parsed = datetime.datetime.fromtimestamp(item['datetime'])
            item_hour = str(datetime.datetime.fromtimestamp(
                item['datetime'])).split(' ')[1][0:2]
            if str(date_parsed).split(' ')[0] == str(datetime.date.today()) and int(item_hour) >= time_setter:
                news_list.append(
                    f"{item['source']}: {item['headline']} \n {item['url']} \n {date_parsed} \n\n")
        return news_list

def function_to_run():
    api = Apihandler(config('FINNHUBCLIENT_API_KEY'))
    
    if datetime.datetime.now().hour == 7:
        for item in api.get_news(0):
            bot.send_message(some_id, item)
            sleep(4)
    elif datetime.datetime.now().hour == 11:
        for item in api.get_news(7):
            bot.send_message(some_id, item)
            sleep(4)
    elif datetime.datetime.now().hour == 15:
        for item in api.get_news(11):
            bot.send_message(some_id, item)
            sleep(4)
    elif datetime.datetime.now().hour == 19:
        for item in api.get_news(15):
            bot.send_message(some_id, item)
            sleep(4)

if __name__ == "__main__":
    schedule.every().day.at("07:00").do(function_to_run)
    schedule.every().day.at("11:00").do(function_to_run)
    schedule.every().day.at("15:00").do(function_to_run)
    schedule.every().day.at("19:00").do(function_to_run)
    schedule.every().day.at("15:33").do(function_to_run)

    while True:
        schedule.run_pending()
        time.sleep(1)