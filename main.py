import telebot
import requests
import json
import finnhub
import time
import datetime
from tabulate import tabulate
from decouple import config
import finnhub
import time
import datetime
import sys
from tabulate import tabulate


bot = telebot.TeleBot(config('TELEGRAM_BOT_KEY'))
res = requests.get('http://localhost:4000/api/news')
resnewsletter = json.loads(res.content)


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
          if str(date_parsed).split(' ')[0] == str(datetime.date.today()):
              news_list.append(f"{item['source']}: {item['headline']} \n {item['url']} \n {date_parsed} \n\n")
      return news_list


    def get_ticker(self, ticker):
        try:
            coname = f"{self.lista_symbols[ticker]}"
        except Exception as exc:
            coname = f"Empresa não cadastrada no banco de dados (razão social não foi encontrada), Symbol: {exc}"

        result = f"""Symbol - {coname}
                Current Value: {self.finnhub_client.quote({ticker})['c']}
                Change: {self.finnhub_client.quote(f'{ticker}')['d']}
                Change %: {self.finnhub_client.quote(f'{ticker}')['dp']}%"""

        return result

    def get_sentiment(self, ticker):
        ticker_func = self.finnhub_client.stock_social_sentiment(f'{ticker}')

        try:
            print(f"{self.lista_symbols[ticker]}\n")
        except Exception as exc:
            print(
                f"Empresa não cadastrada no banco de dados (razão social não foi encontrada), Symbol: {exc}\n")

        print('Reddit Sentiment:')
        for item in ticker_func['reddit']:
            date_parsed = item['atTime']
            if item != '' and str(date_parsed).split(' ')[0] == str(datetime.date.today()):
                print(f"{item['atTime']}:\nMention: {item['mention']}\n" +
                      f"Positive Score: {item['positiveScore']}\n" +
                      f"Positive Mention: {item['positiveMention']}\n" +
                      f"Negative Score:{item['negativeScore']}\n" +
                      f"Negative Mention: {item['negativeMention']}\n" +
                      f"Score: {item['score']}\n\n")

        print('\n\nTwitter Sentiment:')

        for item in ticker_func['twitter']:
            date_parsed = item['atTime']
            if item != '' and str(date_parsed).split(' ')[0] == str(datetime.date.today()):
                print(f"{item['atTime']}:\nMention: {item['mention']}\n" +
                      f"Positive Score: {item['positiveScore']}\n" +
                      f"Positive Mention: {item['positiveMention']}\n" +
                      f"Negative Score:{item['negativeScore']}\n" +
                      f"Negative Mention: {item['negativeMention']}\n" +
                      f"Score: {item['score']}\n\n")

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
        table = tabulate(results, headers=["E", "V", "Vv", "%"])

        return table

@bot.message_handler(commands=['start', 'help', 'stocks', 'check'])
def process_comand(message):
    if message.text == '/start':
        bot.reply_to(message, 'Interações permitidas:\n\n'
                              '/help\n'
                              '/stocks\n'
                              '/check')
    elif message.text == '/help':
        bot.reply_to(message, 'Fui desenvolvido para auxiliar nossos leitores. Valorizamos muito nossa linha editorial '
                              'e acreditamos que você poderia encontrar atualizações e opiniões sobre o mercado financeiro '
                              'em diversos outros lugares da internet, ou seja: você deve estar aqui porque se importa '
                              'com a gente e valoriza nosso trabalho. Esse carinho significa o mundo para nós. \n'
                              'Sendo assim, estou aqui para te enviar notícias e papéis que chamaram nossa atenção, '
                              'além de encaminhar as atualizações de nosso website de nossa página do Instagram. \n\n'
                              'Para mais informações acesse:\nhttps://coiinews.com.br/index.php\nhttps://www.instagram.com/coiinews/')
    elif message.text == '/stocks':
        api = Apihandler(config('FINNHUBCLIENT_API_KEY'))
        bot.reply_to(message, 'Legenda: E = empresa; V = Valor do papel; Vv = variação; % = variação em % \n' + api.parse_table(api.format_results(api.retrieve_and_validate())))
    elif message.text == '/check':
        placeholder = 'test'
        bot.reply_to(message, placeholder)
    else:
        bot.reply_to(message, 'teste1')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.chat.type == 'private':
        bot.reply_to(message,
                     '*blip* *blip* *blop* Essa interação não é permitida. Sugiro que converse com nossos adminsitradores: \n\n'
                     '@pedrocorreia3392 *blip* *blip* *blop*')


bot.polling()
