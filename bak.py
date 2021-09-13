import telebot
import requests
import json
import finnhub
import time
import datetime
from decouple import config
import finnhub
import time
import datetime
import sys
from prettytable import PrettyTable


bot = telebot.TeleBot(config('TELEGRAM_BOT_KEY'), parse_mode='HTML')


class Apihandler:
    def __init__(self, finnhub_client):
        self.finnhub_client = finnhub.Client(api_key=finnhub_client)
        self.lista_symbols = {
            'JPM': 'NYSE: JP Morgan',
            'HSBC': 'NYSE: HSBC',
            'C': 'NYSE: Citigroup Inc.',
            'MA': 'NYSE: Mastercard',
            'AAPL': 'NASDAQ: Apple',
            'GOOGL': 'NASDAQ: Google',
            'MSFT': 'NASDAQ: Microsoft',
            'FB': 'NASDAQ: Facebook',
            'PFE': 'NYSE: Pfizer',
            'TSLA': 'NASDAQ: Tesla',
            'NVDA': 'NASDAQ: Nvidia',
            'AMZN': 'NASDAQ: Amazon',
            'HOOD': 'NASDAQ: Robinhood',
            'KO': 'NYSE: Coca-Cola',
            'NFLX': 'NASDAQ: Netflix',
            'DIS': 'NYSE: Disney',
            'BABA': 'NASDAQ: Alibaba',
            'WMT': 'NYSE: Walmart',
            'V': 'NYSE: Visa'
        }

    def get_news(self):
        news_list = []
        for item in self.finnhub_client.general_news('general', min_id=0):
            date_parsed = datetime.datetime.fromtimestamp(item['datetime'])
            item_hour = str(datetime.datetime.fromtimestamp(
                item['datetime'])).split(' ')[1][0:2]
            if str(date_parsed).split(' ')[0] == str(datetime.date.today()) and int(item_hour) > 12:
                news_list.append(
                    f"{item['source']}: {item['headline']} \n {item['url']} \n {date_parsed} \n\n")
        return news_list

    def get_ticker(self, ticker):
        try:
            coname = f"{self.lista_symbols[ticker]}"
        except Exception as exc:
            coname = f"Empresa não cadastrada no banco de dados (razão social não foi encontrada), Código: {exc}"

        result = f"""Código - {coname}
                Valor tual: {self.finnhub_client.quote({ticker})['c']}
                Mudança: {self.finnhub_client.quote(f'{ticker}')['d']}
                Valorização %: {self.finnhub_client.quote(f'{ticker}')['dp']}%"""

        return result

    def get_sentiment(self, ticker):
        ticker_func = self.finnhub_client.stock_social_sentiment(f'{ticker}')

        try:
            print(f"{self.lista_symbols[ticker]}\n")
        except Exception as exc:
            print(
                f"Empresa não cadastrada no banco de dados (razão social não foi encontrada), Symbol: {exc}\n")

        sentiment_result = ['reddit result: \n']
        for item in ticker_func['reddit']:
            date_parsed = item['atTime']
            if item != '' and str(date_parsed).split(' ')[0] == str(datetime.date.today()):
                sentiment_result.append(f"{item['atTime']}:\nMention: {item['mention']}\n" +
                                        f"Positive Score: {item['positiveScore']}\n" +
                                        f"Positive Mention: {item['positiveMention']}\n" +
                                        f"Negative Score:{item['negativeScore']}\n" +
                                        f"Negative Mention: {item['negativeMention']}\n" +
                                        f"Score: {item['score']}\n\n")
        sentiment_result.append('\n')

        sentiment_result.append('Twitter Results:\n')

        for item in ticker_func['twitter']:
            date_parsed = item['atTime']
            if item != '' and str(date_parsed).split(' ')[0] == str(datetime.date.today()):
                sentiment_result.append(f"{item['atTime']}:\nMention: {item['mention']}\n" +
                                        f"Positive Score: {item['positiveScore']}\n" +
                                        f"Positive Mention: {item['positiveMention']}\n" +
                                        f"Negative Score:{item['negativeScore']}\n" +
                                        f"Negative Mention: {item['negativeMention']}\n" +
                                        f"Score: {item['score']}\n\n")
        return ''.join(sentiment_result)

    def retrieve_data(self):
        data_temp = []

        for symbol in self.lista_symbols:
            time.sleep(5)
            try:
                data_temp.append(self.get_ticker(symbol))
            except Exception as exc:
                print(exc)
            continue

        return data_temp

    def retrieve_and_validate(self):
        test_result = self.retrieve_data()
        while (len(test_result) != len(self.lista_symbols)):
            test_result = self.retrieve_data()

        return test_result

    def format_results(self, results):
        formatted_results = []

        for item in results:
            formatted_line = []
            for line in item.split('\n'):
                formatted_line.append(line.strip().replace('Symbol - ', '')
                                      .replace('Current Value: ', 'US$')
                                      .replace('Change: ', '')
                                      .replace('Change %:', ''))
            formatted_results.append(formatted_line)

        return formatted_results

    def parse_table(self, results):
        table = PrettyTable()
        table.field_names=["E", "V", "Vv", "%"]
        for item in results:
            table.add_row(item)


        table.align = 'r'
        print(table)
        return f"<pre>{table}</pre>"


@ bot.message_handler(commands=['start', 'help', 'stocks', 'check', 'news', 'sentiment'])
def process_comand(message):
    if message.text == '/start':
        bot.reply_to(message, 'Interações permitidas:\n\n'
                              '/help\n'
                              '/stocks\n'
                              '/news\n'
                              '/check + ativo (/check AAPL)')
    elif message.text == '/help':
        bot.reply_to(message, 'Fui desenvolvido para auxiliar nossos leitores. Valorizamos muito nossa linha editorial '
                              'e acreditamos que você poderia encontrar atualizações e opiniões sobre o mercado financeiro '
                              'em diversos outros lugares da internet, ou seja: você deve estar aqui porque se importa '
                              'com a gente e valoriza nosso trabalho. Esse carinho significa o mundo para nós. \n'
                              'Sendo assim, estou aqui para te enviar notícias e papéis que chamaram nossa atenção, '
                              'além de encaminhar as atualizações de nosso website de nossa página do Instagram. \n\n'
                     )
    elif message.text == '/stocks':
        api = Apihandler(config('FINNHUBCLIENT_API_KEY'))
        bot.reply_to(message, api.parse_table(api.format_results(api.retrieve_and_validate())))
    elif message.text == '/news':
        api = Apihandler(config('FINNHUBCLIENT_API_KEY'))
        for item in api.get_news():
            bot.reply_to(message, item)
            time.sleep(0.5)
    elif message.text.split()[0] == '/sentiment':
        parse_string = message.text.replace(f'{message.text.split()[0]} ', '')
        api = Apihandler(config('FINNHUBCLIENT_API_KEY'))
        bot.reply_to(message, api.get_sentiment(parse_string))
    elif message.text.split()[0] == '/check':
        parse_string = message.text.replace(f'{message.text.split()[0]} ', '')
        api = Apihandler(config('FINNHUBCLIENT_API_KEY'))
        bot.reply_to(message, api.get_ticker(parse_string))


@ bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.chat.type == 'private':
        bot.reply_to(message,
                     '*blip* *blip* *blop* Essa interação não é permitida. Sugiro que converse com nossos adminsitradores: \n\n'
                     '@pedrocorreia3392 *blip* *blip* *blop*')


bot.polling()
