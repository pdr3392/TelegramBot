import telebot
import requests
import json

bot = telebot.TeleBot('1940656574:AAHBrsdUv55sD2jy7TGwOJfCuT7WrwDlFJ0')
res = requests.get('http://localhost:4000/api/news')
resnewsletter = json.loads(res.content)


@bot.message_handler(commands=['start', 'help', 'stocks', 'newsletter'])
def process_comand(message):
    if message.text == '/start':
        bot.reply_to(message, 'Interações permitidas:\n\n'
                              '/help\n'
                              '/stocks\n'
                              '/newsletter')
    elif message.text == '/help':
        bot.reply_to(message, 'Fui desenvolvido para auxiliar nossos leitores. Valorizamos muito nossa linha editorial '
                              'e acreditamos que você poderia encontrar atualizações e opiniões sobre o mercado financeiro '
                              'em diversos outros lugares da internet, ou seja: você deve estar aqui porque se importa '
                              'com a gente e valoriza nosso trabalho. Esse carinho significa o mundo para nós. \n'
                              'Sendo assim, estou aqui para te enviar notícias e papéis que chamaram nossa atenção, '
                              'além de encaminhar as atualizações de nosso website de nossa página do Instagram. \n\n'
                              'Para mais informações acesse:\nhttps://coiinews.com.br/index.php\nhttps://www.instagram.com/coiinews/')
    elif message.text == '/stocks':
        bot.reply_to(message, 'teste1')
    else:
        for item in resnewsletter:
            bot.reply_to(message, f"{resnewsletter[item]['title']}:\n{resnewsletter[item]['url']}\nIdioma: {resnewsletter[item]['lang']}")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.chat.type == 'private':
        bot.reply_to(message,
                     '*blip* *blip* *blop* Essa interação não é permitida. Sugiro que converse com nossos adminsitradores: \n\n'
                     '@pedrocorreia3392 *blip* *blip* *blop*')


bot.polling()
